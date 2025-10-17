#!/bin/bash
mkdir -p test-script-out
rm test-script-out/*

test_inputs=("examples/edgelist.csv")
pipelines=("ikc+aoc" "infomap+cc" "infomap+wcc" "leiden+cc" "leiden+cm" "sbm")
for test_input in "${test_inputs[@]}"; do
    for pipeline in "${pipelines[@]}"; do
        echo "Running examples/$pipeline.json"
        python pipeline.py examples/$pipeline.json $test_inputs -o test-script-out/result-$pipeline.csv

        if [ ! -f test-script-out/result-$pipeline.csv ]; then
            echo "Error: $pipeline did not produce a valid output at test-script-out/result-$pipeline.csv"
            exit 1
        fi
    done
done

echo "All tests passed!"