#!/bin/bash

echo "Building simulator..."
make clean
make

echo "=== Running Part A Test ==="
actual_output_A=$(cat tests/partA-input.txt | ./pt_sim.py tests/partA-page-table.txt | grep -v "Enter")
expected_output_A=$(cat tests/partA-expected.txt)

if diff <(echo "$actual_output_A") <(echo "$expected_output_A") > /dev/null; then
    echo "✅ Part A Test Passed"
else
    echo "❌ Part A Test Failed"
    echo "Expected:"
    echo "$expected_output_A"
    echo "Got:"
    echo "$actual_output_A"
fi

echo
echo "=== Running Part B Test ==="
actual_output_B=$(cat tests/partB-input.txt | ./pt_sim.py tests/partB-page-table.txt --clock | grep -v "Enter")
expected_output_B=$(cat tests/partB-expected.txt)

if diff <(echo "$actual_output_B") <(echo "$expected_output_B") > /dev/null; then
    echo "✅ Part B Test Passed"
else
    echo "❌ Part B Test Failed"
    echo "Expected:"
    echo "$expected_output_B"
    echo "Got:"
    echo "$actual_output_B"
fi
