"""Turn an expression string into a flat list of (kind, value) tokens."""


def tokenize(s):
    tokens = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit() or c == ".":
            j = i
            while j < n and (s[j].isdigit() or s[j] == "."):
                j += 1
            text = s[i:j]
            tokens.append(("NUM", float(text) if "." in text else int(text)))
            i = j
            continue
        if s[i:i + 2] == "**":
            tokens.append(("**", "**"))
            i += 2
            continue
        if c in "+-*/()":
            tokens.append((c, c))
            i += 1
            continue
        raise ValueError(f"Unexpected character {c!r} at position {i}")
    return tokens
