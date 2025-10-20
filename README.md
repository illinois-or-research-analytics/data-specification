# Data Specification

This repository defines standardized data formats for modules developed by our group to ensure native interoperability.

## Contents

The specifications in this repository cover:

1. **General File Format**
   - Character-delimited text files

2. **Graph Data Formats**
   - Edgelist format (directed and undirected graphs)
   - Nodelist format (with node attributes)

3. **Clustering Data Format**
   - Cluster membership format

For detailed specifications, see [formats.md](formats.md).

## Utility Scripts

The [scripts](scripts/) directory contains utilities for working with the data formats:

- **Delimiter Detection** - Tools to automatically detect delimiters in data files
  - `get_delimiter.py` (Python implementation)
  - `get_delimiter.cpp` (C++ implementation)

## Installation
We use pixi to manage dependencies. To install all dependencies, run the following command:
```bash
pixi install
```

To activate the shell, run the following command:
```bash
pixi shell
```

### External Modules
The pipeline requires several external modules to function. To setup these external modules, run the following command:
```bash
bash easy_install.sh
```

This will install the external modules in the `downloaded_programs` directory and will only need to be run once. The external modules include:
- [CC](https://github.com/MinhyukPark/constrained-clustering)
- [CM++](https://github.com/illinois-or-research-analytics/cm_pipeline)
- [DSC](https://github.com/illinois-or-research-analytics/DSC)
- [AOC](https://github.com/illinois-or-research-analytics/aocv2_rs)

## Testing
To test the pipeline with the example datasets, run the following command:
```bash
bash test.sh
```

This will run the pipeline with the example datasets and save the results in the `test-script-out` directory.