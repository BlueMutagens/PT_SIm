#!/usr/bin/env python3

import sys
import argparse

class PageTableEntry:
    def __init__(self, valid, permissions, frame, used):
        self.valid = valid == '1'
        self.permissions = int(permissions)
        self.frame = int(frame)
        self.used = used == '1'

class PageTable:
    def __init__(self, n_bits, m_bits, page_size):
        self.n_bits = n_bits
        self.m_bits = m_bits
        self.page_size = page_size
        self.entries = []
        self.page_bits = self._calculate_page_bits()
        self.offset_bits = self._calculate_offset_bits()

    def _calculate_page_bits(self):
        return self.n_bits - self._calculate_offset_bits()

    def _calculate_offset_bits(self):
        return self.page_size.bit_length() - 1

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
            else:
                return "DISK"

        # Calculate physical address
        physical_addr = (entry.frame << self.offset_bits) | offset
        return physical_addr

def read_page_table_file(filename):
    with open(filename, 'r') as f:
        # Read first line for system parameters
        first_line = f.readline().strip()
        while not first_line:  # Skip blank lines
            first_line = f.readline().strip()
        
        n_bits, m_bits, page_size = map(int, first_line.split())
        page_table = PageTable(n_bits, m_bits, page_size)

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
    args = parser.parse_args()

    # Read and parse the page table file
    page_table = read_page_table_file(args.input_file)

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
                print(result)  # Print DISK or SEGFAULT

        except ValueError:
            print("Invalid address format")

if __name__ == "__main__":
    main() 