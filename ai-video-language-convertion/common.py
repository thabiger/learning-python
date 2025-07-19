def extract_args_section(docstring):
    if not docstring:
        return ""
    lines = docstring.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.lstrip().startswith("Args:"))
    except ValueError:
        return ""
    args_lines = []
    for line in lines[start:]:
        args_lines.append(line)
        if line.strip() == "" or line.strip() == '"""':
            break
    return "\n".join(args_lines[:-1])  # Exclude "Returns:" line
