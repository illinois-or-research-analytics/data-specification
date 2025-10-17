#!/bin/bash

mkdir -p downloaded_programs
cd downloaded_programs

git clone https://github.com/illinois-or-research-analytics/cm_pipeline     # CM
git clone https://github.com/illinois-or-research-analytics/DSC             # DSC
git clone https://github.com/MinhyukPark/constrained-clustering             # CC, WCC
git clone https://github.com/illinois-or-research-analytics/aocv2_rs        # AOC

# CM (& pipeline)
cd cm_pipeline
pip install -r requirements.txt && pip install .
cd ..

# DSC
cp DSC/bin/* ./

# CC, WCC
cd constrained-clustering
./setup.sh
./easy_build_and_compile.sh
cp constrained_clustering ../
cd ..

# AOC
cd aocv2_rs
cargo build --release
cargo install --path .
cd ..