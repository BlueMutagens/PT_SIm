#!/bin/bash
echo "Welcome to PT-Sim-Clock, the enhanced page table simulator"
echo "Using input file $1"

# Run the Python implementation with clock algorithm
./pt_sim.py --clock "$1"

# This is where you would run your program

# If it were a binary called pt-sim.x, just do
# ./pt-sim.x $1
# and it will read from stdin, as normal


