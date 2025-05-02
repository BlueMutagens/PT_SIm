#!/usr/bin/env python3

import sys
import argparse


class PageTableEntry:
    def __init__(self, valid, permissions, frame, used):
        self.valid = valid == '1'
        self.permissions = int(permissions)
        self.frame = int(frame)
        self.used = used == '1'

    def __str__(self):
        return f"valid={1 if self.valid else 0}, perm={self.permissions}, frame={self.frame}, used={1 if self.used else 0}"


class PageTable:
    def __init__(self, n_bits, m_bits, page_size, use_clock=False):
        self.n_bits = n_bits
        self.m_bits = m_bits
        self.page_size = page_size
        self.entries = []
        self.use_clock = use_clock

        # Calculate offset bits (log2 of page size)
        self.offset_bits = 0
        temp = page_size
        while temp > 1:
            self.offset_bits += 1
            temp //= 2

        # Initialize clock hand
        self.clock_hand = 0

    def add_entry(self, entry):
        self.entries.append(entry)

    def translate_address(self, virtual_addr):
        # Calculate page number and offset
        page_number = virtual_addr >> self.offset_bits
        offset = virtual_addr & ((1 << self.offset_bits) - 1)

        # Check if page number is valid
        if page_number >= len(self.entries):
            return "SEGFAULT"

        entry = self.entries[page_number]

        # Check if page is valid
        if not entry.valid:
            if entry.permissions == 0:
                return "SEGFAULT"
            elif not self.use_clock:
                return "DISK"
            else:
                # Handle page fault with clock algorithm
                print("PAGEFAULT")
                frame = self.handle_page_fault(page_number)
                physical_addr = (frame << self.offset_bits) | offset
                return physical_addr

        # Mark the page as used
        entry.used = True

        # Calculate physical address
        physical_addr = (entry.frame << self.offset_bits) | offset
        return physical_addr

    def handle_page_fault(self, page_number):
        # For the first page fault, use the frame in the entry
        if not any(entry.valid for entry in self.entries):
            self.entries[page_number].valid = True
            return self.entries[page_number].frame

        # Use the clock algorithm to find a victim
        while True:
            # Check the current page pointed to by the clock hand
            if self.clock_hand >= len(self.entries):
                self.clock_hand = 0

            entry = self.entries[self.clock_hand]

            # Skip invalid entries
            if not entry.valid:
                self.clock_hand += 1
                continue

            # If the page hasn't been used, select it as the victim
            if not entry.used:
                # Save the frame number before invalidating
                victim_frame = entry.frame

                # Invalidate the victim page
                entry.valid = False

                # Validate the new page and update its frame
                self.entries[page_number].valid = True
                self.entries[page_number].frame = victim_frame
                self.entries[page_number].used = True

                # Move the clock hand
                self.clock_hand += 1

                return victim_frame

            # If the page has been used, give it a second chance
            entry.used = False
            self.clock_hand += 1


def read_page_table_file(filename, use_clock=False):
    with open(filename, 'r') as f:
        # Read first line for system parameters
        first_line = f.readline().strip()
        while not first_line:  # Skip blank lines
            first_line = f.readline().strip()

        n_bits, m_bits, page_size = map(int, first_line.split())
        page_table = PageTable(n_bits, m_bits, page_size, use_clock)

        # Read page table entries
        for line in f:
            line = line.strip()
            if not line:  # Skip blank lines
                continue

            valid, permissions, frame, used = line.split()
            page_table.add_entry(PageTableEntry(valid, permissions, frame, used))

    return page_table


def main():
    parser = argparse.ArgumentParser(description='Page Table Simulator')
    parser.add_argument('input_file', help='Input file containing page table description')
    parser.add_argument('--clock', action='store_true',
                        help='Use Clock algorithm for page replacement')
    args = parser.parse_args()

    # Read and parse the page table file
    page_table = read_page_table_file(args.input_file, args.clock)

    # Process virtual addresses from stdin
    print("Enter virtual addresses (decimal or hex with 0x prefix):")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            # Parse virtual address
            if line.startswith('0x'):
                virtual_addr = int(line[2:], 16)
            else:
                virtual_addr = int(line)

            # Translate address
            result = page_table.translate_address(virtual_addr)
            if isinstance(result, int):
                print(f"0x{result:x}")  # Print physical address in hex
            else:
                print(result)  # Print DISK, SEGFAULT, or PAGEFAULT

        except ValueError:
            print("Invalid address format")


if __name__ == "__main__":
    main()