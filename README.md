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

These utilities help standardize file processing across different programming languages.