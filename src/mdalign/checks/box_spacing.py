from mdalign.parser import iter_code_blocks
from mdalign.utils import BOX_CHARS, _find_boxes, _is_tree_block

MIN_PAD = 1


def check(lines):
    errors = []
    for _, code_lines in iter_code_blocks(lines):
        errors.extend(_check_spacing(code_lines))
    return errors


def fix(lines):
    result = list(lines)
    for code_indices, _ in iter_code_blocks(result):
        _fix_spacing_in_block(code_indices, result)
    return result


def _get_right_padding(raw, col_left, col_right):
    if col_left >= len(raw) or raw[col_left] != "│":
        return None
    if col_right >= len(raw) or raw[col_right] not in BOX_CHARS:
        return None
    inner = raw[col_left + 1 : col_right]
    if not inner.strip():
        return None
    if any(c in BOX_CHARS for c in inner):
        return None
    return len(inner) - len(inner.rstrip())


def _check_spacing(code_lines):
    errors = []
    if _is_tree_block(code_lines):
        return errors

    for col_left, col_right, _, _, content_indices in _find_boxes(code_lines):
        for ci in content_indices:
            line_idx, raw = code_lines[ci]
            rpad = _get_right_padding(raw, col_left, col_right)
            if rpad is not None and rpad < MIN_PAD:
                errors.append(f"L{line_idx + 1} box right spacing={rpad}, minimum={MIN_PAD}")

    return errors


def _fix_spacing_in_block(code_indices, all_lines):
    code_lines = [(i, all_lines[i].rstrip("\n")) for i in code_indices]
    if _is_tree_block(code_lines):
        return

    for col_left, col_right, opening_ci, closing_ci, content_indices in reversed(_find_boxes(code_lines)):
        min_rpad = None
        for ci in content_indices:
            _, raw = code_lines[ci]
            rpad = _get_right_padding(raw, col_left, col_right)
            if rpad is not None:
                if min_rpad is None or rpad < min_rpad:
                    min_rpad = rpad

        if min_rpad is None or min_rpad >= MIN_PAD:
            continue

        deficit = MIN_PAD - min_rpad
        all_ci = [opening_ci] + content_indices + [closing_ci]
        for ci in all_ci:
            line_idx = code_lines[ci][0]
            raw = all_lines[line_idx].rstrip("\n")
            if col_right >= len(raw):
                continue
            char = raw[col_right]
            insert = "─" * deficit if char in {"┐", "┘"} else " " * deficit
            new_raw = raw[:col_right] + insert + raw[col_right:]
            all_lines[line_idx] = new_raw + "\n"
