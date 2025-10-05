char get_delimiter(string filepath)
{
    // Read in selected file
    ifstream edgelist(filepath);
    // Placeholder for line
    string line;

    // Read lines until we find a non-comment line or reach end of file
    while (getline(edgelist, line)) {
        // Skip empty lines
        if (line.empty()) {
            continue;
        }

        // Skip comment lines (lines starting with #)
        if (line[0] == '#') {
            continue;
        }

        // Check for common delimiters (comma, tab, space) in the line
        // and return the appropriate delimiter character
        if (line.find(',') != string::npos) {
            return ',';
        }
        else if (line.find('\t') != string::npos) {
            return '\t';
        }
        else if (line.find(' ') != string::npos) {
            return ' ';
        }
    }

    // If no known delimiter is found, throw an error
    throw invalid_argument("Could not detect filetype for " + filepath);
}