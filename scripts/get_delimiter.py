def get_delimiter(filepath: str) -> str:
    with open(filepath, "r") as f:
        for current_line in f:
            if "," in current_line:
                return ","
            elif " " in current_line:
                return " "
            elif "\t" in current_line:
                return "\t"
            else:
                raise ValueError(
                    "Unsupported delimiter: delimiter must be either comma, tab, or whitespace."
                )
