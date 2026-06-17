"""Evaluate a nested-tuple AST produced by the parser."""


def evaluate_ast(node):
    op = node[0]
    if op == "num":
        return node[1]
    if op == "neg":
        return -evaluate_ast(node[1])
    left = evaluate_ast(node[1])
    right = evaluate_ast(node[2])
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        return left / right
    if op == "**":
        return left ** right
    raise ValueError(f"Unknown operator {op!r}")
