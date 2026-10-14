import re


def _is_table_separator(line: str) -> bool:
    return re.fullmatch(r"\|[\s\-:|]+\|", line) is not None


def _is_horizontal_rule(line: str) -> bool:
    return re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", line) is not None


def _clean_line(line: str) -> str:
    line = re.sub(r"^#{1,6}\s+", "", line)
    line = re.sub(r"^>\s?", "", line)
    line = re.sub(r"^\*\s+", "- ", line)
    line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
    line = re.sub(r"__(.+?)__", r"\1", line)
    line = re.sub(r"\*(.+?)\*", r"\1", line)
    line = re.sub(r"`([^`]*)`", r"\1", line)
    line = re.sub(r"\[\[(\d+)\]\]\(#[^)]*\)", r"[\1]", line)
    line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", line)
    return line


def _table_row_to_text(line: str) -> str:
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    return " - ".join(cells)


def markdown_to_plain_text(text: str) -> str:
    result_lines = []
    for line in text.split("\n"):
        line = line.rstrip()
        if _is_table_separator(line):
            continue
        if _is_horizontal_rule(line):
            result_lines.append("")
        elif line.startswith("|"):
            result_lines.append(_clean_line(_table_row_to_text(line)))
        else:
            result_lines.append(_clean_line(line))
    result = "\n".join(result_lines)
    return re.sub(r"\n{3,}", "\n\n", result)
