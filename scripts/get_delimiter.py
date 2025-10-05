def get_delimiter(filepath: str) -> str:
    with open(filepath, "r") as f:
        for line in f:
            current_line = line.strip()

            if not current_line or current_line.startswith(
                "#"
            ):  # skip empty line and comments
                continue

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
