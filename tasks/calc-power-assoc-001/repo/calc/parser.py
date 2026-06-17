"""Recursive-descent parser: tokens -> nested-tuple AST.

Grammar (precedence low -> high):
    expr   := term   (('+' | '-') term)*
    term   := factor (('*' | '/') factor)*
    factor := unary  exponentiation
    unary  := '-' unary | atom
    atom   := NUM | '(' expr ')'
"""
from .tokenizer import tokenize


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos][0] if self.pos < len(self.tokens) else None

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse(self):
        node = self.expr()
        if self.pos != len(self.tokens):
            raise ValueError("Unexpected trailing tokens")
        return node

    def expr(self):
        node = self.term()
        while self.peek() in ("+", "-"):
            op = self.advance()[0]
            node = (op, node, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.peek() in ("*", "/"):
            op = self.advance()[0]
            node = (op, node, self.factor())
        return node

    def factor(self):
        node = self.unary()
        # Exponentiation, evaluated left-to-right.
        while self.peek() == "**":
            self.advance()
            node = ("**", node, self.unary())
        return node

    def unary(self):
        if self.peek() == "-":
            self.advance()
            return ("neg", self.unary())
        return self.atom()

    def atom(self):
        tok = self.peek()
        if tok == "(":
            self.advance()
            node = self.expr()
            if self.peek() != ")":
                raise ValueError("Expected ')'")
            self.advance()
            return node
        if tok == "NUM":
            return ("num", self.advance()[1])
        raise ValueError(f"Unexpected token {tok!r}")


def parse(expression):
    return Parser(tokenize(expression)).parse()
