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
        if entry.permissions == 0:
            return "SEGFAULT"
        # Mark the page as used
        entry.used = True

        # Calculate physical address
        physical_addr = (entry.frame << self.offset_bits) | offset
        return physical_addr

    def handle_page_fault(self, page_number):
    # Use the clock algorithm to find a victim
        while True:
            if self.clock_hand >= len(self.entries):
                self.clock_hand = 0

            candidate = self.entries[self.clock_hand]

            # Skip invalid entries
            if not candidate.valid:
                self.clock_hand += 1
                continue

            # Found a victim if not used
            if not candidate.used:
                victim_frame = candidate.frame
                candidate.valid = False

                # Replace victim with the new page
                new_entry = self.entries[page_number]
                new_entry.valid = True
                new_entry.used = True
                new_entry.frame = victim_frame

                self.clock_hand += 1
                return victim_frame

            # Otherwise, give second chance
            candidate.used = False
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
    print("Welcome to PT-Sim, the page table simulator")
    print("Using input file", args.input_file)
    print("Enter virtual addresses (decimal or hex with 0x prefix):")
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                line = line.split()[0]  # Remove inline comments or trailing tokens
                if line.lower().startswith('0x'):
                    virtual_addr = int(line, 16)
                else:
                    virtual_addr = int(line)

                result = page_table.translate_address(virtual_addr)
                if isinstance(result, int):
                    print(f"0x{result:02x}")
                else:
                    print(result)

            except ValueError:
                print("Invalid address format")

    except KeyboardInterrupt:
        print("\n[INFO] User exited with Ctrl+C.")


if __name__ == "__main__":
    main()