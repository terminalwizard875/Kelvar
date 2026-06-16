import sys
import os
import re
import random
import math
import datetime
from enum import Enum, auto

# Standard Library GUI Imports
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    from tkinter import scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

# Color codes for terminal fallback aesthetics
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"

# =====================================================================
# 1. LEXER / TOKENIZER
# =====================================================================

class TokenType(Enum):
    # Keywords
    LET = auto()
    MUT = auto()         # Rust mutability modifier
    ALLOC = auto()
    FREE = auto()
    PRINT = auto()
    DEBUG = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    REPEAT = auto()
    UNTIL = auto()
    FN = auto()          # Function keyword (Rust/C++)
    RETURN = auto()      # Function return (C/C++/Python/Rust)
    STRUCT = auto()      # Struct keyword
    CLASS = auto()       # Class keyword
    EXTENDS = auto()     # Inheritance keyword
    FOR = auto()         # For loop keyword
    IN = auto()          # Iterator keyword
    IMPORT = auto()      # Import keyword
    YIELD = auto()       # Generator keyword
    
    # Literals & Identifiers
    IDENTIFIER = auto()
    INTEGER = auto()
    FLOAT = auto()       # Float literal
    STRING = auto()
    CHAR = auto()        # Char literal
    TRUE = auto()        # True keyword
    FALSE = auto()       # False keyword
    
    # Operators & Symbols
    ASSIGN = auto()      # =
    PLUS = auto()        # +
    MINUS = auto()       # -
    MUL = auto()         # *
    DIV = auto()         # /
    DEREF = auto()       # * (unary)
    ADDR_OF = auto()     # &
    DOT = auto()         # . (member access)
    COLON = auto()       # : 
    
    # Comparisons
    EQ_COMP = auto()     # ==
    LT = auto()          # <
    GT = auto()          # >
    
    # Logical Operators
    AND = auto()         # and / &&
    OR = auto()          # or / ||
    NOT = auto()         # not / !
    
    # Increment / Decrement
    INC = auto()         # ++
    DEC = auto()         # --
    
    # Delimiters
    LBRACE = auto()      # {
    RBRACE = auto()      # }
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    LBRACKET = auto()    # [
    RBRACKET = auto()    # ]
    COMMA = auto()       # ,
    
    EOF = auto()

class Token:
    def __init__(self, type_: TokenType, value: str, line: int):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', Line {self.line})"

class Lexer:
    KEYWORDS = {
        "let": TokenType.LET,
        "mut": TokenType.MUT,
        "alloc": TokenType.ALLOC,
        "free": TokenType.FREE,
        "print": TokenType.PRINT,
        "debug": TokenType.DEBUG,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "do": TokenType.DO,
        "repeat": TokenType.REPEAT,
        "until": TokenType.UNTIL,
        "fn": TokenType.FN,
        "return": TokenType.RETURN,
        "struct": TokenType.STRUCT,
        "class": TokenType.CLASS,
        "extends": TokenType.EXTENDS,
        "for": TokenType.FOR,
        "in": TokenType.IN,
        "import": TokenType.IMPORT,
        "yield": TokenType.YIELD,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        "and": TokenType.AND,
        "or": TokenType.OR,
        "not": TokenType.NOT,
    }

    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.length = len(source)

    def error(self, message: str):
        raise SyntaxError(f"[Lexer Error Line {self.line}]: {message}")

    def peek(self, offset=0) -> str:
        if self.position + offset >= self.length:
            return ""
        return self.source[self.position + offset]

    def advance(self) -> str:
        char = self.peek()
        self.position += 1
        if char == '\n':
            self.line += 1
        return char

    def tokenize(self) -> list[Token]:
        tokens = []
        while self.position < self.length:
            char = self.peek()

            # Skip Whitespace
            if char.isspace():
                self.advance()
                continue

            # Skip Comments (// line comments)
            if char == '/' and self.peek(1) == '/':
                while self.peek() != '\n' and self.position < self.length:
                    self.advance()
                continue

            # Unary and Binary Multi-character operators
            if char == '=' and self.peek(1) == '=':
                self.advance()
                self.advance()
                tokens.append(Token(TokenType.EQ_COMP, "==", self.line))
                continue
            if char == '+' and self.peek(1) == '+':
                self.advance()
                self.advance()
                tokens.append(Token(TokenType.INC, "++", self.line))
                continue
            if char == '-' and self.peek(1) == '-':
                self.advance()
                self.advance()
                tokens.append(Token(TokenType.DEC, "--", self.line))
                continue
            if char == '&' and self.peek(1) == '&':
                self.advance()
                self.advance()
                tokens.append(Token(TokenType.AND, "&&", self.line))
                continue
            if char == '|' and self.peek(1) == '|':
                self.advance()
                self.advance()
                tokens.append(Token(TokenType.OR, "||", self.line))
                continue

            # Single-character Operators & Symbols
            if char == '=':
                self.advance()
                tokens.append(Token(TokenType.ASSIGN, "=", self.line))
                continue
            if char == '+':
                self.advance()
                tokens.append(Token(TokenType.PLUS, "+", self.line))
                continue
            if char == '-':
                self.advance()
                tokens.append(Token(TokenType.MINUS, "-", self.line))
                continue
            if char == '*':
                self.advance()
                tokens.append(Token(TokenType.MUL, "*", self.line))
                continue
            if char == '/':
                self.advance()
                tokens.append(Token(TokenType.DIV, "/", self.line))
                continue
            if char == '.':
                if self.peek(1).isdigit():
                    pass
                else:
                    self.advance()
                    tokens.append(Token(TokenType.DOT, ".", self.line))
                    continue
            if char == ':':
                self.advance()
                tokens.append(Token(TokenType.COLON, ":", self.line))
                continue
            if char == '&':
                self.advance()
                tokens.append(Token(TokenType.ADDR_OF, "&", self.line))
                continue
            if char == '!':
                self.advance()
                tokens.append(Token(TokenType.NOT, "!", self.line))
                continue
            if char == '<':
                self.advance()
                tokens.append(Token(TokenType.LT, "<", self.line))
                continue
            if char == '>':
                self.advance()
                tokens.append(Token(TokenType.GT, ">", self.line))
                continue
            if char == '{':
                self.advance()
                tokens.append(Token(TokenType.LBRACE, "{", self.line))
                continue
            if char == '}':
                self.advance()
                tokens.append(Token(TokenType.RBRACE, "}", self.line))
                continue
            if char == '(':
                self.advance()
                tokens.append(Token(TokenType.LPAREN, "(", self.line))
                continue
            if char == ')':
                self.advance()
                tokens.append(Token(TokenType.RPAREN, ")", self.line))
                continue
            if char == '[':
                self.advance()
                tokens.append(Token(TokenType.LBRACKET, "[", self.line))
                continue
            if char == ']':
                self.advance()
                tokens.append(Token(TokenType.RBRACKET, "]", self.line))
                continue
            if char == ',':
                self.advance()
                tokens.append(Token(TokenType.COMMA, ",", self.line))
                continue

            # String & Char Literals
            if char in ('"', "'"):
                quote_type = self.advance()
                string_val = ""
                while self.peek() != quote_type and self.position < self.length:
                    string_val += self.advance()
                if self.position >= self.length:
                    self.error("Unterminated literal.")
                self.advance() 
                
                if quote_type == "'" and len(string_val) == 1:
                    tokens.append(Token(TokenType.CHAR, string_val, self.line))
                else:
                    tokens.append(Token(TokenType.STRING, string_val, self.line))
                continue

            # Numeric & Float Literals
            if char.isdigit() or (char == '.' and self.peek(1).isdigit()):
                num_val = ""
                is_float = False
                
                if char == '.':
                    is_float = True
                    num_val += self.advance()
                
                while self.peek().isdigit():
                    num_val += self.advance()
                    
                if not is_float and self.peek() == '.' and self.peek(1).isdigit():
                    is_float = True
                    num_val += self.advance()
                    while self.peek().isdigit():
                        num_val += self.advance()
                        
                if is_float:
                    tokens.append(Token(TokenType.FLOAT, num_val, self.line))
                else:
                    tokens.append(Token(TokenType.INTEGER, num_val, self.line))
                continue

            # Identifiers & Keywords
            if char.isalpha() or char == '_':
                ident_val = ""
                while self.peek().isalnum() or self.peek() == '_':
                    ident_val += self.advance()
                
                tok_type = self.KEYWORDS.get(ident_val, TokenType.IDENTIFIER)
                tokens.append(Token(tok_type, ident_val, self.line))
                continue

            self.error(f"Unexpected character: '{char}'")

        tokens.append(Token(TokenType.EOF, "", self.line))
        return tokens


# =====================================================================
# 2. ABSTRACT SYNTAX TREE (AST) NODES
# =====================================================================

class ASTNode:
    pass

class ProgramNode(ASTNode):
    def __init__(self, statements: list[ASTNode]):
        self.statements = statements

class LetNode(ASTNode):
    def __init__(self, var_name: str, expr: ASTNode, is_mutable: bool, line: int):
        self.var_name = var_name
        self.expr = expr
        self.is_mutable = is_mutable
        self.line = line

class AssignNode(ASTNode):
    def __init__(self, var_name: str, expr: ASTNode, line: int):
        self.var_name = var_name
        self.expr = expr
        self.line = line

class PointerAssignNode(ASTNode):
    def __init__(self, ptr_expr: ASTNode, expr: ASTNode, line: int):
        self.ptr_expr = ptr_expr
        self.expr = expr
        self.line = line

class MemberAssignNode(ASTNode):
    def __init__(self, obj: ASTNode, member: str, expr: ASTNode, line: int):
        self.obj = obj
        self.member = member
        self.expr = expr
        self.line = line

class IndexAssignNode(ASTNode):
    def __init__(self, expr: ASTNode, index: ASTNode, value_expr: ASTNode, line: int):
        self.expr = expr
        self.index = index
        self.value_expr = value_expr
        self.line = line

class IncDecNode(ASTNode):
    def __init__(self, var_name: str, op: str, line: int):
        self.var_name = var_name
        self.op = op 
        self.line = line

class StructDefNode(ASTNode):
    def __init__(self, name: str, fields: list[str], line: int):
        self.name = name
        self.fields = fields
        self.line = line

class ClassDefNode(ASTNode):
    def __init__(self, name: str, parent_name: str, methods: list[ASTNode], line: int):
        self.name = name
        self.parent_name = parent_name
        self.methods = methods
        self.line = line

class ForInNode(ASTNode):
    def __init__(self, var_name: str, iterator_expr: ASTNode, body: ASTNode, line: int):
        self.var_name = var_name
        self.iterator_expr = iterator_expr
        self.body = body
        self.line = line

class ListCompNode(ASTNode):
    def __init__(self, expr: ASTNode, var_name: str, iterator_expr: ASTNode, cond_expr: ASTNode, line: int):
        self.expr = expr
        self.var_name = var_name
        self.iterator_expr = iterator_expr
        self.cond_expr = cond_expr
        self.line = line

class ImportNode(ASTNode):
    def __init__(self, filename: str, line: int):
        self.filename = filename
        self.line = line

class FnNode(ASTNode):
    def __init__(self, name: str, params: list[str], body: ASTNode, line: int):
        self.name = name
        self.params = params
        self.body = body 
        self.line = line

class CallNode(ASTNode):
    def __init__(self, callee: ASTNode, args: list[ASTNode], line: int):
        self.callee = callee 
        self.args = args
        self.line = line

class ReturnNode(ASTNode):
    def __init__(self, expr: ASTNode, line: int):
        self.expr = expr
        self.line = line

class YieldNode(ASTNode):
    def __init__(self, expr: ASTNode, line: int):
        self.expr = expr
        self.line = line

class AllocNode(ASTNode):
    def __init__(self, expr: ASTNode, line: int):
        self.expr = expr
        self.line = line

class FreeNode(ASTNode):
    def __init__(self, var_name: str, line: int):
        self.var_name = var_name
        self.line = line

class PrintNode(ASTNode):
    def __init__(self, expr: ASTNode, line: int):
        self.expr = expr
        self.line = line

class DebugNode(ASTNode):
    def __init__(self, line: int):
        self.line = line

class BinOpNode(ASTNode):
    def __init__(self, left: ASTNode, op: str, right: ASTNode, line: int):
        self.left = left
        self.op = op
        self.right = right
        self.line = line

class UnaryOpNode(ASTNode):
    def __init__(self, op: str, expr: ASTNode, line: int):
        self.op = op 
        self.expr = expr
        self.line = line

class MemberAccessNode(ASTNode):
    def __init__(self, obj: ASTNode, member: str, line: int):
        self.obj = obj
        self.member = member
        self.line = line

class IndexAccessNode(ASTNode):
    def __init__(self, expr: ASTNode, index: ASTNode, line: int):
        self.expr = expr
        self.index = index
        self.line = line

class SliceAccessNode(ASTNode):
    def __init__(self, expr: ASTNode, start: ASTNode, stop: ASTNode, step: ASTNode, line: int):
        self.expr = expr
        self.start = start
        self.stop = stop
        self.step = step
        self.line = line

class ListNode(ASTNode):
    def __init__(self, elements: list[ASTNode], line: int):
        self.elements = elements
        self.line = line

class TupleNode(ASTNode):
    def __init__(self, elements: list[ASTNode], line: int):
        self.elements = elements
        self.line = line

class LiteralNode(ASTNode):
    def __init__(self, value, val_type: str, line: int):
        self.value = value
        self.type = val_type 
        self.line = line

class VarAccessNode(ASTNode):
    def __init__(self, name: str, line: int):
        self.name = name
        self.line = line

class BlockNode(ASTNode):
    def __init__(self, statements: list[ASTNode]):
        self.statements = statements

class IfNode(ASTNode):
    def __init__(self, condition: ASTNode, then_block: BlockNode, else_block: BlockNode, line: int):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
        self.line = line

class WhileNode(ASTNode):
    def __init__(self, condition: ASTNode, body: BlockNode, line: int):
        self.condition = condition
        self.body = body
        self.line = line

class DoWhileNode(ASTNode):
    def __init__(self, body: BlockNode, condition: ASTNode, line: int):
        self.body = body
        self.condition = condition
        self.line = line

class RepeatUntilNode(ASTNode):
    def __init__(self, body: BlockNode, condition: ASTNode, line: int):
        self.body = body
        self.condition = condition
        self.line = line


# =====================================================================
# 3. RECURSIVE DESCENT PARSER
# =====================================================================

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def error(self, token: Token, message: str):
        raise SyntaxError(f"[Parser Error Line {token.line}]: {message} (Found '{token.value}')")

    def peek(self, offset=0) -> Token:
        if self.current + offset >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.current + offset]

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]

    def check(self, type_: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type_

    def match(self, *types: TokenType) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, type_: TokenType, message: str) -> Token:
        if self.check(type_):
            return self.advance()
        self.error(self.peek(), message)

    def parse(self) -> ProgramNode:
        statements = []
        while not self.is_at_end():
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        return ProgramNode(statements)

    def statement(self) -> ASTNode:
        tok = self.peek()
        
        if self.match(TokenType.LET):
            return self.let_statement(tok.line)
        if self.match(TokenType.STRUCT):
            return self.struct_statement(tok.line)
        if self.match(TokenType.CLASS):
            return self.class_statement(tok.line)
        if self.match(TokenType.FOR):
            return self.for_statement(tok.line)
        if self.match(TokenType.IMPORT):
            file_tok = self.consume(TokenType.STRING, "Expected string literal containing file name after 'import'.")
            return ImportNode(file_tok.value, tok.line)
        if self.match(TokenType.FN):
            # Check for anonymous/inline lambda declaration
            if self.check(TokenType.LPAREN):
                self.current -= 1 # Rewind FN and let expression parser handle anonymous lambda
            else:
                return self.fn_statement(tok.line)
        if self.match(TokenType.RETURN):
            return self.return_statement(tok.line)
        if self.match(TokenType.YIELD):
            return self.yield_statement(tok.line)
        if self.match(TokenType.FREE):
            return self.free_statement(tok.line)
        if self.match(TokenType.PRINT):
            return self.print_statement(tok.line)
        if self.match(TokenType.DEBUG):
            return DebugNode(tok.line)
        if self.match(TokenType.IF):
            return self.if_statement(tok.line)
        if self.match(TokenType.WHILE):
            return self.while_statement(tok.line)
        if self.match(TokenType.DO):
            return self.do_while_statement(tok.line)
        if self.match(TokenType.REPEAT):
            return self.repeat_until_statement(tok.line)
        
        if self.check(TokenType.IDENTIFIER) and self.peek(1).type in [TokenType.INC, TokenType.DEC]:
            name = self.advance().value
            op = self.advance().value
            return IncDecNode(name, op, tok.line)

        # Unified generalized assignment vs Expression evaluation
        expr = self.expression()
        if self.match(TokenType.ASSIGN):
            right = self.expression()
            if isinstance(expr, VarAccessNode):
                return AssignNode(expr.name, right, tok.line)
            elif isinstance(expr, MemberAccessNode):
                return MemberAssignNode(expr.obj, expr.member, right, tok.line)
            elif isinstance(expr, IndexAccessNode):
                return IndexAssignNode(expr.expr, expr.index, right, tok.line)
            elif isinstance(expr, UnaryOpNode) and expr.op == "*":
                return PointerAssignNode(expr.expr, right, tok.line)
            raise SyntaxError(f"Line {tok.line}: Invalid assignment target signature.")
            
        return expr

    def let_statement(self, line: int) -> ASTNode:
        is_mutable = False
        if self.match(TokenType.MUT):
            is_mutable = True
            
        var_name = self.consume(TokenType.IDENTIFIER, "Expected variable name.").value
        self.consume(TokenType.ASSIGN, "Expected '=' after variable name.")
        
        if self.match(TokenType.ALLOC):
            expr = self.expression()
            return LetNode(var_name, AllocNode(expr, line), is_mutable, line)
            
        expr = self.expression()
        return LetNode(var_name, expr, is_mutable, line)

    def struct_statement(self, line: int) -> ASTNode:
        name = self.consume(TokenType.IDENTIFIER, "Expected struct model name.").value
        self.consume(TokenType.LBRACE, "Expected '{' to start configuration layout.")
        fields = []
        if not self.check(TokenType.RBRACE):
            fields.append(self.consume(TokenType.IDENTIFIER, "Expected structural property name.").value)
            while self.match(TokenType.COMMA):
                fields.append(self.consume(TokenType.IDENTIFIER, "Expected structural property name.").value)
        self.consume(TokenType.RBRACE, "Expected '}' to seal structural configuration.")
        return StructDefNode(name, fields, line)

    def class_statement(self, line: int) -> ASTNode:
        name = self.consume(TokenType.IDENTIFIER, "Expected class name definition.").value
        parent_name = None
        if self.match(TokenType.EXTENDS):
            parent_name = self.consume(TokenType.IDENTIFIER, "Expected parent object model identifier.").value
            
        self.consume(TokenType.LBRACE, "Expected '{' to store definitions inside object class.")
        methods = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            self.consume(TokenType.FN, "Expected 'fn' keyword for member method.")
            methods.append(self.fn_statement(self.peek().line))
        self.consume(TokenType.RBRACE, "Expected '}' to close class declarations layout.")
        return ClassDefNode(name, parent_name, methods, line)

    def for_statement(self, line: int) -> ASTNode:
        var_name = self.consume(TokenType.IDENTIFIER, "Expected loop variable label identifier.").value
        self.consume(TokenType.IN, "Expected 'in' iterator sequence assignment keyword.")
        iterator_expr = self.expression()
        body = self.block()
        return ForInNode(var_name, iterator_expr, body, line)

    def fn_statement(self, line: int) -> ASTNode:
        name = self.consume(TokenType.IDENTIFIER, "Expected function name.").value
        self.consume(TokenType.LPAREN, "Expected '(' after function identifier.")
        params = []
        if not self.check(TokenType.RPAREN):
            params.append(self.consume(TokenType.IDENTIFIER, "Expected param configuration name.").value)
            while self.match(TokenType.COMMA):
                params.append(self.consume(TokenType.IDENTIFIER, "Expected param configuration name.").value)
        self.consume(TokenType.RPAREN, "Expected ')' after parameter limits setup.")
        body = self.block()
        return FnNode(name, params, body, line)

    def return_statement(self, line: int) -> ASTNode:
        expr = self.expression()
        return ReturnNode(expr, line)

    def yield_statement(self, line: int) -> ASTNode:
        expr = self.expression()
        return YieldNode(expr, line)

    def free_statement(self, line: int) -> ASTNode:
        var_name = self.consume(TokenType.IDENTIFIER, "Expected pointer variable to free.").value
        return FreeNode(var_name, line)

    def print_statement(self, line: int) -> ASTNode:
        expr = self.expression()
        return PrintNode(expr, line)

    def block(self) -> BlockNode:
        self.consume(TokenType.LBRACE, "Expected '{' to start block context space.")
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            statements.append(self.statement())
        self.consume(TokenType.RBRACE, "Expected '}' to finalize scope setup.")
        return BlockNode(statements)

    def expression(self) -> ASTNode:
        return self.logical_or()

    def logical_or(self) -> ASTNode:
        expr = self.logical_and()
        while self.match(TokenType.OR):
            op = self.tokens[self.current - 1].value
            right = self.logical_and()
            expr = BinOpNode(expr, op, right, self.tokens[self.current - 1].line)
        return expr

    def logical_and(self) -> ASTNode:
        expr = self.comparison()
        while self.match(TokenType.AND):
            op = self.tokens[self.current - 1].value
            right = self.comparison()
            expr = BinOpNode(expr, op, right, self.tokens[self.current - 1].line)
        return expr

    def comparison(self) -> ASTNode:
        expr = self.term()
        while self.match(TokenType.LT, TokenType.GT, TokenType.EQ_COMP):
            op = self.tokens[self.current - 1].value
            right = self.term()
            expr = BinOpNode(expr, op, right, self.tokens[self.current - 1].line)
        return expr

    def term(self) -> ASTNode:
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.tokens[self.current - 1].value
            right = self.factor()
            expr = BinOpNode(expr, op, right, self.tokens[self.current - 1].line)
        return expr

    def factor(self) -> ASTNode:
        expr = self.unary()
        while self.match(TokenType.MUL, TokenType.DIV):
            op = self.tokens[self.current - 1].value
            right = self.factor()
            expr = BinOpNode(expr, op, right, self.tokens[self.current - 1].line)
        return expr

    def unary(self) -> ASTNode:
        if self.match(TokenType.MUL): 
            return UnaryOpNode("*", self.unary(), self.tokens[self.current - 1].line)
        if self.match(TokenType.ADDR_OF): 
            return UnaryOpNode("&", self.unary(), self.tokens[self.current - 1].line)
        if self.match(TokenType.NOT): 
            return UnaryOpNode("not", self.unary(), self.tokens[self.current - 1].line)
        return self.postfix()

    def postfix(self) -> ASTNode:
        expr = self.primary()
        while True:
            tok = self.peek()
            if self.match(TokenType.LPAREN):
                args = []
                if not self.check(TokenType.RPAREN):
                    args.append(self.expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.expression())
                self.consume(TokenType.RPAREN, "Expected ')' to seal arguments list block.")
                expr = CallNode(expr, args, tok.line)
            elif self.match(TokenType.DOT):
                member = self.consume(TokenType.IDENTIFIER, "Expected variable field name target after point operator.").value
                expr = MemberAccessNode(expr, member, tok.line)
            elif self.match(TokenType.LBRACKET):
                # Check for list slicing: start:stop:step
                if self.check(TokenType.COLON):
                    start = None
                else:
                    start = self.expression()
                
                if self.match(TokenType.COLON):
                    # It's a slice index!
                    if self.check(TokenType.COLON) or self.check(TokenType.RBRACKET):
                        stop = None
                    else:
                        stop = self.expression()
                    
                    step = None
                    if self.match(TokenType.COLON):
                        if self.check(TokenType.RBRACKET):
                            step = None
                        else:
                            step = self.expression()
                    self.consume(TokenType.RBRACKET, "Expected closing structural square bracket ']'.")
                    expr = SliceAccessNode(expr, start, stop, step, tok.line)
                else:
                    self.consume(TokenType.RBRACKET, "Expected closing structural square bracket ']'.")
                    expr = IndexAccessNode(expr, start, tok.line)
            else:
                break
        return expr

    def primary(self) -> ASTNode:
        tok = self.peek()
        
        # Parse anonymous/inline function definitions (lambdas)
        if self.match(TokenType.FN):
            self.consume(TokenType.LPAREN, "Expected '(' in inline anonymous function definition.")
            params = []
            if not self.check(TokenType.RPAREN):
                params.append(self.consume(TokenType.IDENTIFIER, "Expected lambda parameter name.").value)
                while self.match(TokenType.COMMA):
                    params.append(self.consume(TokenType.IDENTIFIER, "Expected lambda parameter name.").value)
            self.consume(TokenType.RPAREN, "Expected ')' to close anonymous lambda arguments.")
            body = self.block()
            return FnNode("", params, body, tok.line)

        if self.match(TokenType.TRUE):
            return LiteralNode(True, "bool", tok.line)
        if self.match(TokenType.FALSE):
            return LiteralNode(False, "bool", tok.line)
        if self.match(TokenType.INTEGER):
            return LiteralNode(int(tok.value), "int", tok.line)
        if self.match(TokenType.FLOAT):
            return LiteralNode(float(tok.value), "float", tok.line)
        if self.match(TokenType.CHAR):
            return LiteralNode(tok.value, "char", tok.line)
        if self.match(TokenType.STRING):
            return LiteralNode(tok.value, "string", tok.line)
        if self.match(TokenType.IDENTIFIER):
            return VarAccessNode(tok.value, tok.line)
            
        # Lists/Arrays literal extraction + Dynamic List Comprehensions
        if self.match(TokenType.LBRACKET):
            if self.match(TokenType.RBRACKET):
                return ListNode([], tok.line)
            
            first_expr = self.expression()
            
            # Check for Python-style List Comprehension: [ expr for var in list ]
            if self.match(TokenType.FOR):
                var_token = self.consume(TokenType.IDENTIFIER, "Expected loop variable in list comprehension.")
                self.consume(TokenType.IN, "Expected 'in' keyword in list comprehension.")
                iterator_expr = self.expression()
                
                cond_expr = None
                if self.match(TokenType.IF):
                    cond_expr = self.expression()
                    
                self.consume(TokenType.RBRACKET, "Expected matching closing square bracket ']' for list comprehension.")
                return ListCompNode(first_expr, var_token.value, iterator_expr, cond_expr, tok.line)
            
            # Standard List Literal
            elements = [first_expr]
            while self.match(TokenType.COMMA):
                elements.append(self.expression())
            self.consume(TokenType.RBRACKET, "Expected matching closing square matrix bracket for items storage.")
            return ListNode(elements, tok.line)

        # Tuples / Parentheses matching engine
        if self.match(TokenType.LPAREN):
            if self.match(TokenType.RPAREN):
                return TupleNode([], tok.line)
            expr = self.expression()
            if self.match(TokenType.COMMA):
                elements = [expr]
                if not self.check(TokenType.RPAREN):
                    elements.append(self.expression())
                    while self.match(TokenType.COMMA):
                        elements.append(self.expression())
                self.consume(TokenType.RPAREN, "Expected closing tuple bracket symbol setup.")
                return TupleNode(elements, tok.line)
            self.consume(TokenType.RPAREN, "Expected match execution symbol close system configuration.")
            return expr
        
        self.error(tok, "Expected valid expression setup value format configuration node.")


# =====================================================================
# 4. ENVIRONMENT & RUNTIME MEMORY
# =====================================================================

class RuntimeVariable:
    def __init__(self, name: str, val_type: str, value, is_mutable: bool = True):
        self.name = name
        self.type = val_type        # 'int', 'string', 'pointer', 'reference', 'function', 'list', 'tuple', 'struct_def', 'struct_instance', 'class_def', 'class_instance', 'builtin', 'generator', 'float', 'bool', 'char', 'datetime', 'multi_function'
        self.value = value          
        self.is_active = True       
        self.moved_to = None        
        self.is_mutable = is_mutable 

class Environment:
    def __init__(self, parent=None):
        self.variables = {}         
        self.parent = parent

    def define(self, name: str, var: RuntimeVariable):
        self.variables[name] = var

    def lookup(self, name: str) -> RuntimeVariable:
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

class MultiFunction:
    """Helper structure storing overloaded function signatures grouped by arity."""
    def __init__(self, name: str):
        self.name = name
        self.overloads = {}  # arity (int) -> FnNode

    def add_overload(self, fn_node: FnNode):
        self.overloads[len(fn_node.params)] = fn_node


# =====================================================================
# 5. THE RUNTIME & SECURITY SHIELD
# =====================================================================

class KelvarSecurityError(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value, val_type):
        self.value = value
        self.type = val_type

class YieldException(Exception):
    def __init__(self, value, val_type):
        self.value = value
        self.type = val_type

class GeneratorInstance:
    def __init__(self, fn_node, parent_env, args_eval):
        self.fn_node = fn_node
        self.parent_env = parent_env
        self.args_eval = args_eval
        self.exec_env = None
        self.current_stmt_idx = 0
        self.is_exhausted = False
        self.initialized = False

def has_yield(node) -> bool:
    """Helper method that recursively checks if a function has yield operations."""
    if isinstance(node, BlockNode):
        return any(has_yield(s) for s in node.statements)
    if isinstance(node, YieldNode):
        return True
    if isinstance(node, IfNode):
        return has_yield(node.then_block) or (has_yield(node.else_block) if node.else_block else False)
    if isinstance(node, (WhileNode, DoWhileNode, RepeatUntilNode, ForInNode)):
        return has_yield(node.body)
    return False

# Mapping operator symbols to class magic methods for Operator Overloading
OP_MAP = {
    "+": "__add__",
    "-": "__sub__",
    "*": "__mul__",
    "/": "__div__",
    "==": "__eq__",
    "<": "__lt__",
    ">": "__gt__"
}

class KelvarInterpreter:
    def __init__(self, output_callback=None, canvas_widget=None):
        self.heap = {}              
        self.next_address = 0x1000  
        self.global_env = Environment()
        self.address_owners = {}    
        self.output_callback = output_callback
        self.canvas_widget = canvas_widget
        self.setup_builtins()

    def setup_builtins(self):
        # Native Graphics Canvas Bindings
        def _clear():
            if self.canvas_widget: self.canvas_widget.delete("all")
            return None, "void"
        def _rect(x, y, w, h, c):
            if self.canvas_widget: self.canvas_widget.create_rectangle(x, y, x+w, y+h, fill=c, outline=c)
            return None, "void"
        def _circle(x, y, r, c):
            if self.canvas_widget: self.canvas_widget.create_oval(x-r, y-r, x+r, y+r, fill=c, outline=c)
            return None, "void"
        def _line(x1, y1, x2, y2, c):
            if self.canvas_widget: self.canvas_widget.create_line(x1, y1, x2, y2, fill=c)
            return None, "void"
            
        self.global_env.define("draw_clear", RuntimeVariable("draw_clear", "builtin", _clear, False))
        self.global_env.define("draw_rect", RuntimeVariable("draw_rect", "builtin", _rect, False))
        self.global_env.define("draw_circle", RuntimeVariable("draw_circle", "builtin", _circle, False))
        self.global_env.define("draw_line", RuntimeVariable("draw_line", "builtin", _line, False))

        # Core Mathematical & collection utilities Built-ins
        def _len(val):
            if isinstance(val, (list, tuple)):
                return len(val), "int"
            if isinstance(val, str):
                return len(val), "int"
            raise TypeError("len() expects a list, tuple, or string.")

        def _abs(val):
            if isinstance(val, float):
                return abs(val), "float"
            if isinstance(val, int):
                return abs(val), "int"
            raise TypeError("abs() expects an integer or float.")

        def _rand(low, high):
            if not isinstance(low, int) or not isinstance(high, int):
                raise TypeError("rand() expects integer bounds.")
            return random.randint(low, high), "int"

        def _pow(base, exp):
            if isinstance(base, float) or isinstance(exp, float):
                return float(pow(base, exp)), "float"
            return int(pow(base, exp)), "int"

        def _min(a, b):
            if isinstance(a, float) or isinstance(b, float):
                return float(min(a, b)), "float"
            return min(a, b), "int"

        def _max(a, b):
            if isinstance(a, float) or isinstance(b, float):
                return float(max(a, b)), "float"
            return max(a, b), "int"

        def _sqrt(val):
            if isinstance(val, float):
                return math.sqrt(val), "float"
            if isinstance(val, int):
                if val < 0: raise ValueError("sqrt() expects a non-negative number.")
                return int(math.isqrt(val)), "int"
            raise TypeError("sqrt() expects an integer or float.")

        def _str(val):
            return str(val), "string"

        def _int(val):
            try:
                return int(val), "int"
            except ValueError:
                raise ValueError(f"Cannot cast '{val}' to int.")

        def _float(val):
            try:
                return float(val), "float"
            except ValueError:
                raise ValueError(f"Cannot cast '{val}' to float.")

        def _range(*args):
            # Python-style Range Generator: range(start, stop, step)
            if len(args) == 1:
                start, stop, step = 0, args[0], 1
            elif len(args) == 2:
                start, stop, step = args[0], args[1], 1
            elif len(args) == 3:
                start, stop, step = args[0], args[1], args[2]
            else:
                raise TypeError("range() expects 1 to 3 arguments.")
            
            if not isinstance(start, int) or not isinstance(stop, int) or not isinstance(step, int):
                raise TypeError("range() arguments must be integers.")
            if step == 0:
                raise ValueError("range() step must not be zero.")
                
            res = []
            for i in range(start, stop, step):
                res.append((i, "int"))
            return res, "list"

        def _next(gen_obj):
            # Master next() builtin iteration routine targeting native yields and class iterators
            if isinstance(gen_obj, GeneratorInstance):
                return self.resume_generator(gen_obj)
            
            if isinstance(gen_obj, dict) and "methods" in gen_obj and "next" in gen_obj["methods"]:
                # OOP Iterator Protocol Dispatcher
                next_fn = gen_obj["methods"]["next"]
                exec_env = Environment(parent=self.global_env)
                exec_env.define("this", RuntimeVariable("this", "class_instance", gen_obj))
                try:
                    self.execute_block(next_fn.body, exec_env)
                except ReturnException as ret:
                    return ret.value, ret.type
                return None, "void"
            
            raise TypeError("next() expects a native generator or OOP iterator instance.")

        # Temporal Datetime System Built-ins
        def _now():
            now_dt = datetime.datetime.now()
            # Construct a beautiful simulated structural datetime record!
            dt_fields = {
                "year": RuntimeVariable("year", "int", now_dt.year, False),
                "month": RuntimeVariable("month", "int", now_dt.month, False),
                "day": RuntimeVariable("day", "int", now_dt.day, False),
                "hour": RuntimeVariable("hour", "int", now_dt.hour, False),
                "minute": RuntimeVariable("minute", "int", now_dt.minute, False),
                "second": RuntimeVariable("second", "int", now_dt.second, False)
            }
            dt_instance = {
                "struct_name": "DateTime",
                "fields": dt_fields
            }
            return dt_instance, "struct_instance"

        self.global_env.define("len", RuntimeVariable("len", "builtin", _len, False))
        self.global_env.define("abs", RuntimeVariable("abs", "builtin", _abs, False))
        self.global_env.define("rand", RuntimeVariable("rand", "builtin", _rand, False))
        self.global_env.define("pow", RuntimeVariable("pow", "builtin", _pow, False))
        self.global_env.define("min", RuntimeVariable("min", "builtin", _min, False))
        self.global_env.define("max", RuntimeVariable("max", "builtin", _max, False))
        self.global_env.define("sqrt", RuntimeVariable("sqrt", "builtin", _sqrt, False))
        self.global_env.define("str", RuntimeVariable("str", "builtin", _str, False))
        self.global_env.define("int", RuntimeVariable("int", "builtin", _int, False))
        self.global_env.define("float", RuntimeVariable("float", "builtin", _float, False))
        self.global_env.define("range", RuntimeVariable("range", "builtin", _range, False))
        self.global_env.define("next", RuntimeVariable("next", "builtin", _next, False))
        self.global_env.define("now", RuntimeVariable("now", "builtin", _now, False))

    def log_print(self, text, style="normal"):
        if self.output_callback:
            self.output_callback(text, style)
        else:
            if style == "security":
                print(f"{RED}{BOLD}[SECURITY SHIELD]{RESET} {RED}{text}{RESET}")
            elif style == "success":
                print(f"{GREEN}✓ {text}{RESET}")
            elif style == "info":
                print(f"{CYAN}i {text}{RESET}")
            elif style == "bold":
                print(f"{BOLD}{text}{RESET}")
            else:
                print(text)

    def log_security(self, message): self.log_print(message, "security")
    def log_success(self, message): self.log_print(message, "success")
    def log_info(self, message): self.log_print(message, "info")

    def resume_generator(self, gen: GeneratorInstance) -> tuple[any, str]:
        """Runs or resumes a suspended generator instance environment."""
        if gen.is_exhausted:
            raise RuntimeError("StopIteration: Generator sequence is exhausted.")
        
        if not gen.initialized:
            gen.exec_env = Environment(parent=gen.parent_env)
            for param, (v, t) in zip(gen.fn_node.params, gen.args_eval):
                gen.exec_env.define(param, RuntimeVariable(param, t, v, is_mutable=True))
            gen.initialized = True
            
        body_stmts = gen.fn_node.body.statements
        while gen.current_stmt_idx < len(body_stmts):
            stmt = body_stmts[gen.current_stmt_idx]
            gen.current_stmt_idx += 1
            try:
                self.execute(stmt, gen.exec_env)
            except YieldException as ye:
                return ye.value, ye.type
                
        gen.is_exhausted = True
        raise RuntimeError("StopIteration: Generator execution finished.")

    def is_mutable_lhs(self, node: ASTNode, env: Environment) -> bool:
        """Trace LHS expressions back to their source variable to guarantee strict mutability checks."""
        if isinstance(node, VarAccessNode):
            var = env.lookup(node.name)
            return var.is_mutable if var else True
        if isinstance(node, MemberAccessNode):
            return self.is_mutable_lhs(node.obj, env)
        if isinstance(node, IndexAccessNode):
            return self.is_mutable_lhs(node.expr, env)
        if isinstance(node, UnaryOpNode) and node.op == "*":
            return self.is_mutable_lhs(node.expr, env)
        return True

    def evaluate(self, node: ASTNode, env: Environment) -> tuple[any, str]:
        if isinstance(node, LiteralNode):
            return node.value, node.type

        if isinstance(node, VarAccessNode):
            var = env.lookup(node.name)
            if not var:
                raise NameError(f"Undefined variable allocation setup target: '{node.name}'")
            if not var.is_active:
                raise KelvarSecurityError(f"Borrow Check Failed! '{node.name}' was moved to '{var.moved_to}'.")
            return var.value, var.type

        if isinstance(node, ListNode):
            items = [self.evaluate(elem, env) for elem in node.elements]
            return items, "list"

        if isinstance(node, TupleNode):
            items = [self.evaluate(elem, env) for elem in node.elements]
            return tuple(items), "tuple"

        if isinstance(node, IndexAccessNode):
            coll, coll_type = self.evaluate(node.expr, env)
            idx, idx_type = self.evaluate(node.index, env)
            if coll_type not in ["list", "tuple"]:
                raise TypeError(f"Cannot request absolute index layout from raw data target mapping type: '{coll_type}'")
            if idx_type != "int":
                raise TypeError("Matrix storage access addresses require raw valid integers.")
            try:
                return coll[idx][0], coll[idx][1]
            except IndexError:
                raise IndexError("Collection storage query out of allocated index size boundaries.")

        if isinstance(node, SliceAccessNode):
            coll, coll_type = self.evaluate(node.expr, env)
            if coll_type not in ["list", "tuple", "string"]:
                raise TypeError("Slicing operations are only supported across list, tuple, and string formats.")
            
            start_val = None
            if node.start:
                start_val, _ = self.evaluate(node.start, env)
            stop_val = None
            if node.stop:
                stop_val, _ = self.evaluate(node.stop, env)
            step_val = None
            if node.step:
                step_val, _ = self.evaluate(node.step, env)
                
            slice_obj = slice(start_val, stop_val, step_val)
            sliced_res = coll[slice_obj]
            return sliced_res, coll_type

        if isinstance(node, ListCompNode):
            coll, coll_type = self.evaluate(node.iterator_expr, env)
            if coll_type not in ["list", "tuple"]:
                raise TypeError(f"Line {node.line}: List comprehension expects an iterable list or tuple collection.")
            
            result_items = []
            for item in coll:
                val, val_type = item[0], item[1]
                # Build isolated scope context for comprehension variable step
                comp_env = Environment(parent=env)
                comp_env.define(node.var_name, RuntimeVariable(node.var_name, val_type, val, is_mutable=False))
                
                # Check condition if present
                if node.cond_expr:
                    cond_val, _ = self.evaluate(node.cond_expr, comp_env)
                    if cond_val == 0:
                        continue # filter evaluated false, skip item
                
                eval_val, eval_type = self.evaluate(node.expr, comp_env)
                result_items.append((eval_val, eval_type))
                
            return result_items, "list"

        if isinstance(node, MemberAccessNode):
            obj, obj_type = self.evaluate(node.obj, env)
            if obj_type == "struct_instance":
                if node.member not in obj["fields"]:
                    raise AttributeError(f"Struct target model lacks designated field mapping parameter: '{node.member}'")
                var_val = obj["fields"][node.member]
                return var_val.value, var_val.type
            elif obj_type == "class_instance":
                if node.member in obj["fields"]:
                    var_val = obj["fields"][node.member]
                    return var_val.value, var_val.type
                if node.member in obj["methods"]:
                    return (obj["methods"][node.member], obj), "method"
                raise AttributeError(f"Class engine registry lacks designated method or variable field parameter target alignment: '{node.member}'")
            raise TypeError(f"Target variable storage block mapping type '{obj_type}' does not validate sub-property mapping structures setup rules.")

        if isinstance(node, CallNode):
            # Universal Call Dispatcher supporting first-class function values and constructor instantiations
            callee_val, callee_type = self.evaluate(node.callee, env)
            
            # Resolve overloading dispatcher for first-class calls
            if callee_type == "multi_function" or isinstance(callee_val, MultiFunction):
                arity = len(node.args)
                if arity not in callee_val.overloads:
                    raise TypeError(f"No overload of function '{callee_val.name}' takes {arity} arguments.")
                callee_val, callee_type = callee_val.overloads[arity], "function"

            if callee_type == "function":
                fn_node = callee_val
                # Check if it's a yield-based generator function
                if has_yield(fn_node):
                    args_eval = [self.evaluate(a, env) for a in node.args]
                    return GeneratorInstance(fn_node, env, args_eval), "generator"
                
                if len(node.args) != len(fn_node.params):
                    raise TypeError(f"Function expects {len(fn_node.params)} arguments, but {len(node.args)} were given.")
                args_eval = [self.evaluate(a, env) for a in node.args]
                exec_env = Environment(parent=env) # Maintain closure context scoping safely
                for param, (v, t) in zip(fn_node.params, args_eval):
                    exec_env.define(param, RuntimeVariable(param, t, v, is_mutable=True))
                try:
                    self.execute_block(fn_node.body, exec_env)
                except ReturnException as ret:
                    return ret.value, ret.type
                return None, "void"
                
            elif callee_type == "method":
                fn_node, obj_context = callee_val
                
                # Resolve method overloads cleanly
                if isinstance(fn_node, MultiFunction):
                    arity = len(node.args)
                    if arity not in fn_node.overloads:
                        raise TypeError(f"No overload of method '{fn_node.name}' takes {arity} arguments on class '{obj_context['class_name']}'.")
                    fn_node = fn_node.overloads[arity]

                if len(node.args) != len(fn_node.params):
                    raise TypeError(f"Method '{fn_node.name}' expects {len(fn_node.params)} arguments, but {len(node.args)} were given.")
                args_eval = [self.evaluate(a, env) for a in node.args]
                exec_env = Environment(parent=self.global_env)
                exec_env.define("this", RuntimeVariable("this", "class_instance", obj_context))
                for param, (v, t) in zip(fn_node.params, args_eval):
                    exec_env.define(param, RuntimeVariable(param, t, v, is_mutable=True))
                try:
                    self.execute_block(fn_node.body, exec_env)
                except ReturnException as ret:
                    return ret.value, ret.type
                return None, "void"
            elif callee_type == "builtin":
                fn_func = callee_val
                args_eval = [self.evaluate(a, env)[0] for a in node.args]
                return fn_func(*args_eval)
                
            elif callee_type == "class_def":
                cl_node = callee_val
                resolved_methods = {}
                curr_class = cl_node
                
                # Inheritance Method Overloading resolution engine
                while curr_class:
                    for method in curr_class.methods:
                        m_name = method.name
                        if m_name not in resolved_methods:
                            resolved_methods[m_name] = method
                        else:
                            existing = resolved_methods[m_name]
                            if isinstance(existing, FnNode):
                                if len(existing.params) != len(method.params):
                                    mf = MultiFunction(m_name)
                                    mf.add_overload(existing)
                                    mf.add_overload(method)
                                    resolved_methods[m_name] = mf
                            elif isinstance(existing, MultiFunction):
                                if len(method.params) not in existing.overloads:
                                    existing.add_overload(method)
                                    
                    if curr_class.parent_name:
                        p_model = env.lookup(curr_class.parent_name)
                        curr_class = p_model.value if (p_model and p_model.type == "class_def") else None
                    else:
                        curr_class = None
                
                inst_fields = {}
                inst_instance = {"class_name": cl_node.name, "fields": inst_fields, "methods": resolved_methods}
                
                if "init" in resolved_methods:
                    init_fn = resolved_methods["init"]
                    
                    # Resolve Constructor Overloads
                    if isinstance(init_fn, MultiFunction):
                        arity = len(node.args)
                        if arity not in init_fn.overloads:
                            raise TypeError(f"No overloaded constructor 'init' on class '{cl_node.name}' takes {arity} arguments.")
                        init_fn = init_fn.overloads[arity]

                    if len(node.args) != len(init_fn.params):
                        raise TypeError(f"Class initialization lifecycle constructor requires matching {len(init_fn.params)} variables layout alignment.")
                    args_eval = [self.evaluate(a, env) for a in node.args]
                    exec_env = Environment(parent=self.global_env)
                    exec_env.define("this", RuntimeVariable("this", "class_instance", inst_instance))
                    for param, (v, t) in zip(init_fn.params, args_eval):
                        exec_env.define(param, RuntimeVariable(param, t, v))
                    try:
                        self.execute_block(init_fn.body, exec_env)
                    except ReturnException:
                        pass
                return inst_instance, "class_instance"

            elif callee_type == "struct_def":
                st_node = callee_val
                if len(node.args) != len(st_node.fields):
                    raise TypeError(f"Struct constructor layout requires exactly {len(st_node.fields)} elements structure values alignment matches.")
                fields_inst = {}
                for f_name, arg in zip(st_node.fields, node.args):
                    v, t = self.evaluate(arg, env)
                    fields_inst[f_name] = RuntimeVariable(f_name, t, v)
                return {"struct_name": st_node.name, "fields": fields_inst}, "struct_instance"

            elif callee_type == "generator":
                raise TypeError("Generators must be iterated via the next() function.")
                
            raise TypeError(f"Target evaluates to a non-callable layout: {callee_type}")

        if isinstance(node, UnaryOpNode):
            if node.op == "*": 
                val, val_type = self.evaluate(node.expr, env)
                if val_type != "pointer": raise TypeError("Cannot absolute dereference a non-pointer storage register element structure target.")
                if val is None: raise KelvarSecurityError("Null address processing request cancelled by Security Shield.")
                if val not in self.heap: raise KelvarSecurityError(f"Dangling pointer memory tracking validation violation prevented at address registry block index: {hex(val)}")
                return self.heap[val], "int"

            if node.op == "&": 
                if not isinstance(node.expr, VarAccessNode): raise TypeError("Address referencing system queries mandate direct clean storage label targets mapping assignments.")
                tgt = env.lookup(node.expr.name)
                if not tgt: raise NameError(f"Undefined storage context labeling parameters error: '{node.expr.name}'")
                if not tgt.is_active: raise KelvarSecurityError("Cannot create a secure reference coordinate track layout from moved tracking parameters blocks context.")
                return node.expr.name, "reference"

            if node.op == "not": 
                val, _ = self.evaluate(node.expr, env)
                return (0 if val != 0 else 1), "int"

        if isinstance(node, BinOpNode):
            l_val, l_type = self.evaluate(node.left, env)
            
            # Resolve Operator Overloading for class instances
            if l_type == "class_instance" and node.op in OP_MAP:
                magic_method = OP_MAP[node.op]
                if magic_method in l_val["methods"]:
                    method_fn = l_val["methods"][magic_method]
                    r_val, r_type = self.evaluate(node.right, env)
                    
                    if isinstance(method_fn, MultiFunction):
                        if 1 not in method_fn.overloads:
                            raise TypeError(f"Overloaded operator method '{magic_method}' must accept exactly 1 argument.")
                        method_fn = method_fn.overloads[1]
                        
                    exec_env = Environment(parent=self.global_env)
                    exec_env.define("this", RuntimeVariable("this", "class_instance", l_val))
                    if len(method_fn.params) >= 1:
                        exec_env.define(method_fn.params[0], RuntimeVariable(method_fn.params[0], r_type, r_val))
                    try:
                        self.execute_block(method_fn.body, exec_env)
                    except ReturnException as ret:
                        return ret.value, ret.type
                    return None, "void"

            r_val, r_type = self.evaluate(node.right, env)

            if l_type == "pointer" and r_type == "int" and node.op in ["+", "-"]:
                offset = r_val * 4
                new_addr = (l_val + offset) if node.op == "+" else (l_val - offset)
                return new_addr, "pointer"

            # Enable robust float and integer dynamically coerced comparisons & math!
            num_types = ["int", "float"]
            if l_type in num_types and r_type in num_types:
                # Upcast dynamically to float if either side is a float
                if l_type == "float" or r_type == "float":
                    res_type = "float"
                    l_val, r_val = float(l_val), float(r_val)
                else:
                    res_type = "int"
                
                if node.op in ["+", "&&", "and"]: 
                    if node.op in ["&&", "and"]: return (1 if (l_val != 0 and r_val != 0) else 0), "int"
                    return l_val + r_val, res_type
                if node.op == "-": return l_val - r_val, res_type
                if node.op == "*": return l_val * r_val, res_type
                if node.op == "/": 
                    if r_val == 0: raise ZeroDivisionError("Math structure anomaly fault block: Divide by absolute zero prevented.")
                    if res_type == "float":
                        return l_val / r_val, "float"
                    return l_val // r_val, "int"
                if node.op in ["||", "or"]: return (1 if (l_val != 0 or r_val != 0) else 0), "int"
                if node.op == "<": return (1 if l_val < r_val else 0), "int"
                if node.op == ">": return (1 if l_val > r_val else 0), "int"
                if node.op == "==": return (1 if l_val == r_val else 0), "int"

            # String Concatenation & operations support
            if l_type == "string" and r_type == "string" and node.op == "+":
                return l_val + r_val, "string"
            if l_type == "string" and r_type == "string" and node.op == "==":
                return (1 if l_val == r_val else 0), "int"
            
            # Boolean logic operations
            if l_type == "bool" and r_type == "bool":
                if node.op in ["&&", "and"]: return (1 if l_val and r_val else 0), "int"
                if node.op in ["||", "or"]: return (1 if l_val or r_val else 0), "int"
                if node.op == "==": return (1 if l_val == r_val else 0), "int"

            raise TypeError(f"Mismatched operation types dynamically: '{l_type}' {node.op} '{r_type}' is not supported.")

        raise ValueError("Invalid evaluation node.")

    def execute(self, node: ASTNode, env: Environment):
        if isinstance(node, LetNode):
            if isinstance(node.expr, AllocNode):
                val, val_type = self.evaluate(node.expr.expr, env)
                addr = self.next_address
                self.heap[addr] = val
                self.next_address += 4
                env.define(node.var_name, RuntimeVariable(node.var_name, "pointer", addr, is_mutable=node.is_mutable))
                self.address_owners[addr] = node.var_name
                self.log_success(f"Allocated physical state value {val} onto secure simulated segment registry layout at space index: {hex(addr)}")
                return

            if isinstance(node.expr, VarAccessNode):
                src = env.lookup(node.expr.name)
                if src and src.type in ["pointer", "reference", "struct_instance", "class_instance", "list", "tuple", "function", "generator", "multi_function"]:
                    if not src.is_active: raise KelvarSecurityError("Use-after-move structural access fault block activation prevented.")
                    src.is_active = False
                    src.moved_to = node.var_name
                    env.define(node.var_name, RuntimeVariable(node.var_name, src.type, src.value, is_mutable=node.is_mutable))
                    if src.type == "pointer": self.address_owners[src.value] = node.var_name
                    self.log_info(f"Ownership track transferred cleanly. Target mapping register label locks: '{node.expr.name}' -> '{node.var_name}'")
                    return

            val, val_type = self.evaluate(node.expr, env)
            env.define(node.var_name, RuntimeVariable(node.var_name, val_type, val, is_mutable=node.is_mutable))
            self.log_success(f"Bound new registry tracker alignment mapping label space: let {node.var_name} = value structural layout coordinates validation.")
            return

        if isinstance(node, StructDefNode):
            env.define(node.name, RuntimeVariable(node.name, "struct_def", node, is_mutable=False))
            self.log_success(f"Declared structural model outline format setup safely: struct {node.name}")
            return

        if isinstance(node, ClassDefNode):
            env.define(node.name, RuntimeVariable(node.name, "class_def", node, is_mutable=False))
            self.log_success(f"Registered blueprint architecture object outline matrix model layout safely: class {node.name}")
            return

        if isinstance(node, ForInNode):
            coll, coll_type = self.evaluate(node.iterator_expr, env)
            if coll_type not in ["list", "tuple", "string"]:
                raise TypeError("for..in loop expects an iterable list, tuple, or string collection.")
            
            # String conversion to let you loop over single character literals natively
            if coll_type == "string":
                iterable = [(char, "char") for char in coll]
            else:
                iterable = coll

            for item in iterable:
                val, val_type = item[0], item[1]
                loop_env = Environment(parent=env)
                # Create loop iteration variable (mutable inside step context to support mutations like a++)
                loop_env.define(node.var_name, RuntimeVariable(node.var_name, val_type, val, is_mutable=True))
                try:
                    self.execute_block(node.body, loop_env)
                except ReturnException as ret:
                    raise ret 
            return

        if isinstance(node, ImportNode):
            # Modular runtime import file compiler support
            filename = node.filename
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Line {node.line}: Imported file '{filename}' was not found in directory.")
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    import_source = f.read()
                sub_lexer = Lexer(import_source)
                sub_tokens = sub_lexer.tokenize()
                sub_parser = Parser(sub_tokens)
                sub_ast = sub_parser.parse()
                self.execute_block(sub_ast, self.global_env)
                self.log_success(f"Imported modules and variables from '{filename}' successfully.")
            except Exception as e:
                raise RuntimeError(f"Line {node.line}: Failed to fully parse/compile imported module '{filename}': {e}")
            return

        if isinstance(node, AssignNode):
            var = env.lookup(node.var_name)
            if not var: raise NameError(f"Cannot map values data flow into unconfigured labeling track markers: '{node.var_name}'")
            if not var.is_active: raise KelvarSecurityError(f"Secure mutability constraint validation track fault inside moved variable state boundaries: '{node.var_name}'")
            if not var.is_mutable: raise KelvarSecurityError(f"Mutability Violation! Variable '{node.var_name}' is immutable. Declare with 'let mut' to modify.")
            val, val_type = self.evaluate(node.expr, env)
            
            # Dynamic Typing support: replace value and type dynamically!
            var.value = val
            var.type = val_type
            self.log_success(f"Updated value storage mapping profile track registers: '{node.var_name}' data stream rewrite applied.")
            return

        if isinstance(node, MemberAssignNode):
            if not self.is_mutable_lhs(node.obj, env):
                raise KelvarSecurityError("Mutability Violation! Cannot write members of an immutable object context.")
            obj, obj_type = self.evaluate(node.obj, env)
            if obj_type not in ["struct_instance", "class_instance"]:
                raise TypeError("Cannot force deep attribute writes across structural primitive types variables.")
            val, val_type = self.evaluate(node.expr, env)
            obj["fields"][node.member] = RuntimeVariable(node.member, val_type, val)
            self.log_success(f"Updated inner parameter configuration target property state cleanly: entity property member '{node.member}' altered.")
            return

        if isinstance(node, IndexAssignNode):
            if not self.is_mutable_lhs(node.expr, env):
                raise KelvarSecurityError("Mutability Violation! Cannot write index slots of an immutable collection.")
            coll, coll_type = self.evaluate(node.expr, env)
            idx, idx_type = self.evaluate(node.index, env)
            if coll_type != "list": raise TypeError("Tuples feature immutable layouts. Mutating items values maps coordinates checks applies into list models only.")
            if idx_type != "int": raise TypeError("Storage indexing references enforce absolute integer formatting restrictions constraints mapping.")
            val, val_type = self.evaluate(node.value_expr, env)
            try:
                coll[idx] = (val, val_type)
                self.log_success(f"Modified target record coordinates layout content dynamically at structural index track location: [{idx}]")
            except IndexError:
                raise IndexError("Collection boundaries index limits access coordinate tracking overflow error block generated.")
            return

        if isinstance(node, IncDecNode):
            var = env.lookup(node.var_name)
            if not var: raise NameError(f"Undefined math manipulation shorthand register tracking space label coordinate error alignment: '{node.var_name}'")
            if not var.is_active: raise KelvarSecurityError(f"Cannot mutate state parameters inside tracking label blocks flagged as moved.")
            if not var.is_mutable: raise KelvarSecurityError(f"Mutability Violation! Suffix mutation target '{node.var_name}' is immutable.")
            if var.type != "int": raise TypeError("Incremental shortcuts require structural primitive integers configuration alignment targets matches.")
            var.value += (1 if node.op == "++" else -1)
            self.log_success(f"Applied dynamic atomic scalar transformation shift value onto storage registry label: '{node.var_name}' to state value: {var.value}")
            return

        if isinstance(node, PointerAssignNode):
            addr, addr_type = self.evaluate(node.ptr_expr, env)
            if addr_type != "pointer": raise TypeError("Memory operations trace addresses tracks mapping via core active pointer label configurations models.")
            val, val_type = self.evaluate(node.expr, env)
            self.heap[addr] = val
            self.log_success(f"Deref storage write execution step completed onto space address registry index trace path: ({hex(addr)}) = {val}")
            return

        if isinstance(node, FnNode):
            # Save function / overloaded function logic cleanly
            existing = env.lookup(node.name)
            if existing and existing.type == "function":
                # Convert standard function to multi_function overloading set
                multi_fn = MultiFunction(node.name)
                multi_fn.add_overload(existing.value)
                multi_fn.add_overload(node)
                existing.value = multi_fn
                existing.type = "multi_function"
            elif existing and existing.type == "multi_function":
                existing.value.add_overload(node)
            else:
                env.define(node.name, RuntimeVariable(node.name, "function", node, is_mutable=False))
            self.log_success(f"Saved custom system logic framework routing module label setup: fn {node.name}()")
            return

        if isinstance(node, ReturnNode):
            v, t = (None, "void")
            if node.expr: v, t = self.evaluate(node.expr, env)
            raise ReturnException(v, t)

        if isinstance(node, YieldNode):
            v, t = (None, "void")
            if node.expr: v, t = self.evaluate(node.expr, env)
            raise YieldException(v, t)

        if isinstance(node, FreeNode):
            var = env.lookup(node.var_name)
            if not var or var.type != "pointer": raise TypeError("Deallocation requests target active pointer storage models identifiers setup references rules.")
            addr = var.value
            if addr not in self.heap: raise KelvarSecurityError("Double-Free dynamic memory manipulation strategy asset violation aborted by safety shields tracking systems.")
            del self.heap[addr]
            if addr in self.address_owners: del self.address_owners[addr]
            var.value = None
            self.log_success(f"Released simulated memory hardware registers address allocation frame block track: {hex(addr)}")
            return

        if isinstance(node, PrintNode):
            val, vt = self.evaluate(node.expr, env)
            if vt == "pointer": self.log_print(f"[Pointer -> {hex(val)}]", "info")
            elif vt == "reference": self.log_print(f"[Ref -> &{val}]", "info")
            elif vt == "function": self.log_print(f"[Function -> {val.name}]", "info")
            elif vt == "list":
                body = ", ".join([str(x[0]) if x[1] != 'string' else f'"{x[0]}"' for x in val])
                self.log_print(f"[{body}]", "bold")
            elif vt == "tuple":
                body = ", ".join([str(x[0]) if x[1] != 'string' else f'"{x[0]}"' for x in val])
                if len(val) == 1: body += ","
                self.log_print(f"({body})", "bold")
            elif vt == "struct_instance":
                body = ", ".join([f"{k}: {v.value}" for k, v in val["fields"].items()])
                self.log_print(f"struct {val['struct_name']} {{ {body} }}", "bold")
            elif vt == "class_instance":
                body = ", ".join([f"{k}: {v.value}" for k, v in val["fields"].items()])
                self.log_print(f"instance of class {val['class_name']} {{ {body} }}", "bold")
            elif vt == "generator":
                self.log_print(f"[Generator Object -> {val.fn_node.name}]", "info")
            elif vt == "multi_function":
                self.log_print(f"[Overloaded Function -> {val.name}]", "info")
            else: self.log_print(str(val), "bold")
            return

        if isinstance(node, DebugNode):
            self.log_print("\n=== KELVAR RUNTIME SYSTEM STATE ===", "info")
            curr, lvl = env, 0
            while curr:
                self.log_print(f"Scope Level {lvl}:", "info")
                if not curr.variables: self.log_print("  [No variables in this scope]")
                for name, var in curr.variables.items():
                    st = "Active" if var.is_active else f"MOVED to '{var.moved_to}'"
                    mu = "mut" if var.is_mutable else "const"
                    disp = var.value
                    if var.type == "pointer" and var.value: disp = hex(var.value)
                    elif var.type == "function": disp = f"fn {var.value.name}()"
                    elif var.type == "struct_def": disp = f"struct skeleton outline"
                    elif var.type == "class_def": disp = f"class structural model skeleton blueprints"
                    elif var.type == "list": disp = "[" + ", ".join([str(x[0]) for x in var.value]) + "]"
                    elif var.type == "tuple": disp = "(" + ", ".join([str(x[0]) for x in var.value]) + ")"
                    self.log_print(f"  {name}: type={var.type}, mut={mu}, val={disp}, status={st}")
                curr, lvl = curr.parent, lvl + 1
            return

        if isinstance(node, IfNode):
            v, _ = self.evaluate(node.condition, env)
            if v != 0: self.execute_block(node.then_block, env)
            elif node.else_block: self.execute_block(node.else_block, env)
            return

        if isinstance(node, WhileNode):
            while True:
                v, _ = self.evaluate(node.condition, env)
                if v == 0: break
                self.execute_block(node.body, env)
            return

        if isinstance(node, DoWhileNode):
            while True:
                self.execute_block(node.body, env)
                v, _ = self.evaluate(node.condition, env)
                if v == 0: break
            return

        if isinstance(node, RepeatUntilNode):
            while True:
                self.execute_block(node.body, env)
                v, _ = self.evaluate(node.condition, env)
                if v != 0: break
            return

        if isinstance(node, ProgramNode):
            for stmt in node.statements: self.execute(stmt, env)
            return

        self.evaluate(node, env)

    def execute_block(self, block: BlockNode, parent_env: Environment):
        b_env = Environment(parent=parent_env)
        for stmt in block.statements: self.execute(stmt, b_env)


# =====================================================================
# 6. GRAPHICAL USER INTERFACE (KELVAR IDE)
# =====================================================================

class KelvarIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Kelvar Compiler IDLE - Revolution Edition Pro")
        self.root.geometry("1200x750")
        
        # Color Themes Configuration
        self.themes = {
            "VS Code Dark": {"bg": "#1e1e1e", "panel": "#252526", "text": "#d4d4d4", "kw": "#569cd6", "str": "#ce9178", "num": "#b5cea8", "com": "#6a9955"},
            "Ocean Blue": {"bg": "#0f172a", "panel": "#1e293b", "text": "#e2e8f0", "kw": "#38bdf8", "str": "#a3e635", "num": "#f472b6", "com": "#64748b"},
            "IDLE Light": {"bg": "#ffffff", "panel": "#f0f0f0", "text": "#000000", "kw": "#0000ff", "str": "#00aa00", "num": "#ff7700", "com": "#dd0000"},
            "Cyberpunk": {"bg": "#0d0d0d", "panel": "#111111", "text": "#00ff00", "kw": "#ff00ff", "str": "#ffff00", "num": "#00ffff", "com": "#005500"}
        }
        self.current_theme = self.themes["VS Code Dark"]
        
        self.setup_styles()
        self.build_layout()
        self.apply_theme()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

    def build_layout(self):
        # Native window-level Menu Bar implementation (Professional Submenus)
        menubar = tk.Menu(self.root)
        
        # 1. File Submenu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="📁 Open File (.kv)", command=self.open_file)
        filemenu.add_command(label="💾 Save File (.kv)", command=self.save_file)
        filemenu.add_separator()
        filemenu.add_command(label="🚪 Exit Space", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        # 2. Run Submenu
        runmenu = tk.Menu(menubar, tearoff=0)
        runmenu.add_command(label="▶ Run Execution Loop", command=self.run_compiled_code)
        runmenu.add_command(label="🧹 Wipe Editor Workspace", command=self.clear_editor)
        menubar.add_cascade(label="Run", menu=runmenu)
        
        # 3. Themes Submenu
        thememenu = tk.Menu(menubar, tearoff=0)
        for theme_name in self.themes.keys():
            thememenu.add_command(label=theme_name, command=lambda t=theme_name: self.set_theme(t))
        menubar.add_cascade(label="Themes", menu=thememenu)
        
        # 4. Demos Submenu
        demomenu = tk.Menu(menubar, tearoff=0)
        demos = [
            "Mutable & Loops", "For-In Loops", "Comprehension & Dynamic Typing", 
            "Rich Types & DateTime", "Function Recursion", "Rust Move Safety", 
            "C Pointer Arithmetic", "Structs, OOP & Collections", "Graphics Drawing", 
            "Slicing, Functions & Generators", "Overloads & Inline Lambdas"
        ]
        for demo in demos:
            demomenu.add_command(label=demo, command=lambda d=demo: self.load_demo_by_name(d))
        menubar.add_cascade(label="Demos", menu=demomenu)
        
        self.root.config(menu=menubar)

        # Upper Title Panel Header using themed ttk.Frame to support padding
        header = ttk.Frame(self.root, padding=10)
        header.pack(fill=tk.X, side=tk.TOP)
        
        ttk.Label(header, text="🛡| KELVAR COMPILER LABS IDE", font=("Consolas", 14, "bold"), foreground="#2ed573").pack(side=tk.LEFT)
        ttk.Label(header, text=" - Core Infrastructure Engine Workbench", font=("Consolas", 10, "italic"), foreground="#7f8c8d").pack(side=tk.LEFT, pady=3)

        # Main Split Workspace Panels Layout
        paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Column editor pane
        editor_panel = ttk.Frame(paned_window)
        paned_window.add(editor_panel, weight=3)
        
        editor_header = ttk.Frame(editor_panel)
        editor_header.pack(fill=tk.X)
        ttk.Label(editor_header, text="📄 CODE MATRIX WORKSPACE", style="Header.TLabel").pack(side=tk.LEFT, pady=5)
        
        self.editor = scrolledtext.ScrolledText(editor_panel, wrap=tk.WORD, font=("Consolas", 12), bd=0)
        self.editor.pack(fill=tk.BOTH, expand=True, pady=5)
        self.editor.bind("<KeyRelease>", self.highlight_syntax)

        # Right Column inspection panels layout
        right_panel = ttk.Frame(paned_window)
        paned_window.add(right_panel, weight=2)
        right_paned = ttk.PanedWindow(right_panel, orient=tk.VERTICAL)
        right_paned.pack(fill=tk.BOTH, expand=True)

        console_frame = ttk.Frame(right_paned)
        right_paned.add(console_frame, weight=1)
        ttk.Label(console_frame, text="💻 INTERPRETATION OUTPUT LOGIC", style="Header.TLabel").pack(anchor=tk.W, pady=5)
        
        self.console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, font=("Consolas", 10), bd=0, state=tk.DISABLED)
        self.console.pack(fill=tk.BOTH, expand=True, pady=5)
        self.console.tag_config("bold", font=("Consolas", 11, "bold"))
        self.console.tag_config("success", foreground="#2ed573")
        self.console.tag_config("info", foreground="#00a8ff")
        self.console.tag_config("security", foreground="#ff4757", font=("Consolas", 10, "bold"))

        memory_frame = ttk.Frame(right_paned)
        right_paned.add(memory_frame, weight=1)
        ttk.Label(memory_frame, text="🧠 DIAGNOSTICS ARCHITECTURE MATRIX TRACKER", style="Header.TLabel").pack(anchor=tk.W, pady=5)

        notebook = ttk.Notebook(memory_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        stack_tab = ttk.Frame(notebook)
        notebook.add(stack_tab, text=" Variables Stack (Registers) ")
        self.stack_tree = ttk.Treeview(stack_tab, columns=("Name", "Type", "Mutable", "Value", "Status"), show="headings")
        for col in ("Name", "Type", "Mutable", "Value", "Status"): self.stack_tree.heading(col, text=col); self.stack_tree.column(col, width=90, anchor=tk.CENTER)
        self.stack_tree.pack(fill=tk.BOTH, expand=True)

        heap_tab = ttk.Frame(notebook)
        notebook.add(heap_tab, text=" Physical Heap Allocations (RAM) ")
        self.heap_tree = ttk.Treeview(heap_tab, columns=("Address", "Stored Value", "Owner Variable"), show="headings")
        for col in ("Address", "Stored Value", "Owner Variable"): self.heap_tree.heading(col, text=col); self.heap_tree.column(col, width=130, anchor=tk.CENTER)
        self.heap_tree.pack(fill=tk.BOTH, expand=True)
        
        # New Graphics Canvas Tab
        canvas_tab = ttk.Frame(notebook)
        notebook.add(canvas_tab, text=" 🎨 Graphics Canvas ")
        self.canvas_widget = tk.Canvas(canvas_tab, bg="black", highlightthickness=0)
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Sleek, modern flat bottom action status bar (uses basic tk.Frame to allow explicit bg config)
        self.status_bar = tk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=4, ipadx=10)
        
        self.status_label = ttk.Label(self.status_bar, text="Workspace Ready", font=("Consolas", 10))
        self.status_label.pack(side=tk.LEFT)

        self.editor.insert(tk.END, "// Welcome to Kelvar Revolution Pro Sandbox Engine!\n// Choose standard demos from the top 'Demos' menu dropdown selection.\n\nlet mut asset_matrix = [100, 200, 300]\nprint asset_matrix\n")
        self.highlight_syntax()

    def set_theme(self, theme_name):
        self.current_theme = self.themes[theme_name]
        self.apply_theme()
        self.highlight_syntax()

    def apply_theme(self):
        bg = self.current_theme["bg"]
        panel = self.current_theme["panel"]
        fg = self.current_theme["text"]
        
        self.root.configure(bg=bg)
        self.style.configure(".", background=bg, foreground=fg)
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        
        self.editor.configure(bg=bg, fg=fg, insertbackground=fg)
        self.console.configure(bg=panel, fg=fg)
        self.console.tag_config("normal", foreground=fg)
        
        self.style.configure("Treeview", background=panel, fieldbackground=panel, foreground=fg)
        self.style.configure("Treeview.Heading", background=bg, foreground=fg)
        
        self.status_bar.configure(bg=panel)
        self.status_label.configure(background=panel, foreground=fg)

    def highlight_syntax(self, event=None):
        self.editor.tag_remove("kw", "1.0", tk.END)
        self.editor.tag_remove("str", "1.0", tk.END)
        self.editor.tag_remove("num", "1.0", tk.END)
        self.editor.tag_remove("com", "1.0", tk.END)
        
        self.editor.tag_config("kw", foreground=self.current_theme["kw"], font=("Consolas", 12, "bold"))
        self.editor.tag_config("str", foreground=self.current_theme["str"])
        self.editor.tag_config("num", foreground=self.current_theme["num"])
        self.editor.tag_config("com", foreground=self.current_theme["com"], font=("Consolas", 12, "italic"))

        code = self.editor.get("1.0", tk.END)
        
        # Regex mappings for syntax highlights
        for match in re.finditer(r'\b(let|mut|alloc|free|print|debug|if|else|while|do|repeat|until|fn|return|struct|class|extends|for|in|import|yield|true|false|and|or|not)\b', code):
            self.editor.tag_add("kw", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(r'\b\d+(\.\d+)?\b', code):
            self.editor.tag_add("num", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(r'(["\'].*?["\'])', code):
            self.editor.tag_add("str", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(r'(//.*)', code):
            self.editor.tag_add("com", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

    def log_to_gui_console(self, text, style="normal"):
        self.console.config(state=tk.NORMAL)
        marker = "[PANIC] 🛡️ " if style == "security" else "✓ " if style == "success" else "i " if style == "info" else "➔ " if style == "bold" else ""
        self.console.insert(tk.END, f"{marker}{text}\n", style)
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

    def run_compiled_code(self):
        self.console.config(state=tk.NORMAL); self.console.delete("1.0", tk.END); self.console.config(state=tk.DISABLED)
        code = self.editor.get("1.0", tk.END)
        self.status_label.configure(text="Processing and interpreting active code matrix...")
        self.log_to_gui_console("Processing code baseline elements structure tree maps...", "info")
        
        interpreter = KelvarInterpreter(output_callback=self.log_to_gui_console, canvas_widget=self.canvas_widget)
        
        try:
            tokens = Lexer(code).tokenize()
            ast = Parser(tokens).parse()
            interpreter.execute(ast, interpreter.global_env)
            self.status_label.configure(text="Execution Finished cleanly.")
            self.log_to_gui_console("Execution context sealed cleanly with 0 pipeline failures.", "success")
        except KelvarSecurityError as kse: 
            self.status_label.configure(text="Borrow checker security breach detected!")
            self.log_to_gui_console(str(kse), "security")
        except (SyntaxError, TypeError, NameError, IndexError, AttributeError, RuntimeError) as err: 
            self.status_label.configure(text="Interpreter pipeline panic!")
            self.log_to_gui_console(f"Fault Trace Intersection: {err}", "security")
        except Exception as e: 
            self.status_label.configure(text="VM fault collapse!")
            self.log_to_gui_console(f"Unmapped runtime breakdown trace: {e}", "security")
            
        self.update_diagnostics_ui(interpreter)

    def update_diagnostics_ui(self, interpreter):
        for item in self.stack_tree.get_children(): self.stack_tree.delete(item)
        for item in self.heap_tree.get_children(): self.heap_tree.delete(item)

        env = interpreter.global_env
        for name, var in env.variables.items():
            if var.type == "builtin": continue
            mu = "mut" if var.is_mutable else "const"
            st = "Active" if var.is_active else f"MOVED to '{var.moved_to}'"
            disp = var.value
            if var.type == "pointer" and var.value: disp = hex(var.value)
            elif var.type == "function": disp = f"fn {var.value.name}()"
            elif var.type == "struct_def": disp = f"struct skeleton outline"
            elif var.type == "class_def": disp = f"class structural model outline"
            elif var.type == "struct_instance": disp = f"struct data instance model: {var.value['struct_name']}"
            elif var.type == "class_instance": disp = f"class entity record: {var.value['class_name']}"
            elif var.type == "list": disp = "[" + ", ".join([str(x[0]) for x in var.value]) + "]"
            elif var.type == "tuple": disp = "(" + ", ".join([str(x[0]) for x in var.value]) + ")"
            elif var.type == "generator": disp = f"[Generator Object -> {var.value.fn_node.name}]"
            elif var.type == "bool": disp = "true" if var.value else "false"
            elif var.type == "char": disp = f"'{var.value}'"
            self.stack_tree.insert("", tk.END, values=(name, var.type, mu, disp, st))

        for addr, val in sorted(interpreter.heap.items()):
            owner = interpreter.address_owners.get(addr, "Unclaimed")
            self.heap_tree.insert("", tk.END, values=(hex(addr), val, owner))

    def clear_editor(self): self.editor.delete("1.0", tk.END)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".kv",
            filetypes=[("Kelvar Code Files", "*.kv"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    code = file.read()
                self.clear_editor()
                self.editor.insert(tk.END, code)
                self.log_to_gui_console(f"Successfully loaded file: {file_path}", "success")
                self.highlight_syntax()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".kv",
            filetypes=[("Kelvar Code Files", "*.kv"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                code = self.editor.get("1.0", tk.END)
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(code)
                self.log_to_gui_console(f"Successfully saved file to: {file_path}", "success")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def load_demo_by_name(self, selected):
        self.clear_editor()
        
        if selected == "Mutable & Loops":
            self.editor.insert(tk.END, "// Demo: Mutability validation loop logic tracking\nlet mut counter = 0\nrepeat {\n  counter++\n  print counter\n} until counter == 3\n")
        elif selected == "For-In Loops":
            self.editor.insert(tk.END, "// Demo: Iterating elements with For-In loops\nlet mut primes = [2, 3, 5, 7, 11]\n\nfor val in primes {\n  print val\n}\n")
        elif selected == "Comprehension & Dynamic Typing":
            self.editor.insert(tk.END, "// Demo: Dynamic Typing, Range, & List Comprehensions\n\n"
                                      "// 1. Dynamic Typing Demonstration\n"
                                      "let mut dynamic_var = 42\n"
                                      "print \"Dynamic Var (Integer):\"\n"
                                      "print dynamic_var\n\n"
                                      "dynamic_var = \"Now I am a string!\"\n"
                                      "print \"Dynamic Var (String):\"\n"
                                      "print dynamic_var\n\n"
                                      "// 2. Range(start, stop, step) Function\n"
                                      "print \"Generating Range from 2 to 10 with step 2:\"\n"
                                      "let r = range(2, 11, 2)\n"
                                      "print r\n\n"
                                      "// 3. Python-style List Comprehension\n"
                                      "print \"List Comprehension (squares of even numbers in range):\"\n"
                                      "let squares = [x * x for x in r if x > 4]\n"
                                      "print squares\n")
        elif selected == "Rich Types & DateTime":
            self.editor.insert(tk.END, "// Demo: Floats, Chars, Booleans, and Temporal DateTimes\n\n"
                                      "// 1. Boolean Literals & Logical Coercions\n"
                                      "let is_sunny = true\n"
                                      "let is_warm = false\n"
                                      "print \"Sunny:\"\n"
                                      "print is_sunny\n"
                                      "print \"Warm:\"\n"
                                      "print is_warm\n\n"
                                      "// 2. Floats & Math Type Upcasting Coercion\n"
                                      "let mut pi = 3.14\n"
                                      "let offset = 2\n"
                                      "let result = pi + offset // int + float automatically casts to float!\n"
                                      "print \"Casting float coercion results:\"\n"
                                      "print result\n\n"
                                      "// 3. Character Literals\n"
                                      "let custom_char = 'k'\n"
                                      "print \"Char Literal:\"\n"
                                      "print custom_char\n\n"
                                      "// 4. Built-in now() System DateTime Tracking\n"
                                      "let mut current_time = now()\n"
                                      "print \"Current Year:\"\n"
                                      "print current_time.year\n"
                                      "print \"Current Hour:\"\n"
                                      "print current_time.hour\n"
                                      "print \"Current Minute:\"\n"
                                      "print current_time.minute\n")
        elif selected == "Function Recursion":
            self.editor.insert(tk.END, "fn factorial(n) {\n  if n == 1 { return 1 }\n  let mut sub = n - 1\n  let mut total = n * factorial(sub)\n  return total\n}\nprint factorial(5)\n")
        elif selected == "Rust Move Safety":
            self.editor.insert(tk.END, "// Demo: Safety Shield resource lock capture trace rules\nlet mut p1 = alloc 50\nlet mut p2 = p1\n// The following trace generates an error flag block because ownership was shifted to p2\nprint *p1\n")
        elif selected == "C Pointer Arithmetic":
            self.editor.insert(tk.END, "let mut base = alloc 10\nlet mut shift = base + 1\n*shift = 88\nprint *shift\nfree base\n")
        elif selected == "Structs, OOP & Collections":
            self.editor.insert(tk.END, "// Demo: Arrays, Tuples, Structs and Class Inheritance Models\n\n// 1. Array/List structural indexing mutations\nlet mut inventory = [10, 20, 30]\ninventory[1] = 99\nprint inventory\n\n// 2. Immutability Records tracking using Tuples\nlet record_coordinates = (5, \"CoreMatrixAddress\", 15)\nprint record_coordinates\n\n// 3. Struct declarations and attributes update tracking\nstruct Point { x, y }\nlet mut coordinate_node = Point(5, 10)\ncoordinate_node.y = 750\nprint coordinate_node\n\n// 4. Object-Oriented Framework Class Inheritance & Constructor lifecycle hooks\nclass Vehicle {\n  fn init(model_profile) {\n    this.model = model_profile\n  }\n  fn spark() {\n    print \"Standard baseline acoustic alert sound activated.\"\n  }\n}\n\nclass SportsCar extends Vehicle {\n  fn spark() {\n    print \"High performance custom induction engine roar triggered!\"\n  }\n}\n\nlet mut model_instance = SportsCar(\"InterceptorV8\")\nprint model_instance.model\nmodel_instance.spark()\n")
        elif selected == "Graphics Drawing":
            self.editor.insert(tk.END, "// Demo: Interactive Canvas Drawing\ndraw_clear()\nprint \"Rendering visuals on canvas...\"\n\n// Draw shapes using built-in canvas API\ndraw_rect(50, 50, 200, 150, \"blue\")\ndraw_circle(150, 125, 40, \"yellow\")\ndraw_line(50, 50, 250, 200, \"red\")\n\nprint \"Drawing completed! Switch to the 🎨 Graphics Canvas tab to view it!\"\n")
        elif selected == "Slicing, Functions & Generators":
            self.editor.insert(tk.END, "// Demo: Heterogeneous Lists, Slicing, First-Class Functions & Generators\n\n"
                                      "// 1. Heterogeneous Lists (Multiple Data Types)\n"
                                      "let mut mixed = [42, \"Kelvar Pro\", (1, 2), draw_clear]\n"
                                      "print \"Heterogeneous List:\"\n"
                                      "print mixed\n\n"
                                      "// 2. Slicing with strides mixed[1:3]\n"
                                      "print \"Slicing mixed[1:3]:\"\n"
                                      "print mixed[1:3]\n\n"
                                      "// 3. First-Class Functions\n"
                                      "fn double(x) {\n"
                                      "  return x * 2\n"
                                      "}\n"
                                      "fn apply_func(f, val) {\n"
                                      "  return f(val)\n"
                                      "}\n"
                                      "print \"Calling apply_func(double, 10):\"\n"
                                      "print apply_func(double, 10)\n\n"
                                      "// 4. Generator function using the yield statement\n"
                                      "fn count_up() {\n"
                                      "  yield 100\n"
                                      "  yield 200\n"
                                      "  yield 300\n"
                                      "}\n"
                                      "let mut gen = count_up()\n"
                                      "print \"Generator Step 1:\"\n"
                                      "print next(gen)\n"
                                      "print \"Generator Step 2:\"\n"
                                      "print next(gen)\n"
                                      "print \"Generator Step 3:\"\n"
                                      "print next(gen)\n")
        elif selected == "Overloads & Inline Lambdas":
            self.editor.insert(tk.END, "// Demo: Overloading, Operator Methods & Inline Anonymous Functions\n\n"
                                      "// 1. Arity-Based Function Overloading\n"
                                      "fn process(x) {\n"
                                      "  print \"Processing single value:\"\n"
                                      "  print x\n"
                                      "}\n"
                                      "fn process(x, y) {\n"
                                      "  print \"Processing pair sum:\"\n"
                                      "  print x + y\n"
                                      "}\n"
                                      "process(10)\n"
                                      "process(5, 50)\n\n"
                                      "// 2. Inline Anonymous Lambdas\n"
                                      "let mut multiplier = fn(n) { return n * 3 }\n"
                                      "print \"Anonymous multiplier call result:\"\n"
                                      "print multiplier(15)\n\n"
                                      "// 3. Class Operator Overloading & Constructor Overloads\n"
                                      "class Vector2D {\n"
                                      "  // Overloaded Constructor 1\n"
                                      "  fn init(x) {\n"
                                      "    this.x = x\n"
                                      "    this.y = 0\n"
                                      "  }\n"
                                      "  // Overloaded Constructor 2\n"
                                      "  fn init(x, y) {\n"
                                      "    this.x = x\n"
                                      "    this.y = y\n"
                                      "  }\n"
                                      "  // Overloaded mathematical '+' operator method\n"
                                      "  fn __add__(other) {\n"
                                      "    return Vector2D(this.x + other.x, this.y + other.y)\n"
                                      "  }\n"
                                      "}\n"
                                      "let mut vec1 = Vector2D(5, 10)\n"
                                      "let mut vec2 = Vector2D(20, 30)\n"
                                      "let mut vec3 = vec1 + vec2\n"
                                      "print \"Addition Overload Result:\"\n"
                                      "print vec3.x\n"
                                      "print vec3.y\n")
        self.highlight_syntax()

def main():
    if len(sys.argv) > 1:
        interpreter = KelvarInterpreter()
        filename = sys.argv[1]
        try:
            with open(filename, "r") as file: source = file.read()
            tokens = Lexer(source).tokenize()
            ast = Parser(tokens).parse()
            interpreter.execute(ast, interpreter.global_env)
        except Exception as e:
            print(f"Terminal compilation trace fail: {e}")
            sys.exit(1)
        return

    if GUI_AVAILABLE:
        root = tk.Tk()
        app = KelvarIDE(root)
        root.mainloop()
    else:
        print("Graphical interface assets offline fallback mode active.")

if __name__ == "__main__":
    main()