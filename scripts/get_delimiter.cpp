char get_delimiter(std::string filepath) {
    // Read in selected file
    std::ifstream edgelist(filepath);
    // Placeholder for line
    std::string line;

    // Read lines until we find a non-comment line or reach end of file
    while (std::getline(edgelist, line)) {
        // Find acceptable delimiters
        if (line.find(',') != std::string::npos) {
            return ',';
        }
        else if (line.find('\t') != std::string::npos) {
            return '\t';
        }
        else if (line.find(' ') != std::string::npos) {
            return ' ';
        }
    }

    // If no known delimiter is found, throw an error
    throw std::invalid_argument("Could not detect filetype for " + filepath);
}