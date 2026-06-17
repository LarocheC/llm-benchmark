from .parser import parse
from .evaluator import evaluate_ast


def evaluate(expression):
    """Evaluate an arithmetic expression string and return the numeric result."""
    return evaluate_ast(parse(expression))
