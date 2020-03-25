from enum import Enum


class Literal(Enum):
    STRING_LITERAL = 'STRING'
    NUMBER_LITERAL = 'NUMBER'


class Symbol(Enum):
    L_CURLY = '{'
    R_CURLY = '}'
    L_ROUND = '('
    R_ROUND = ')'
    L_SQUARE = '['
    R_SQUARE = ']'
    SEMICOLON = ';'
    COLON = ':'
    EQUALS = '='
    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    DIV = '/'
    HASH = '#'
    COMMENT = '//'
    MCOMMENT_START = '/*'
    MCOMMENT_END = '*/'
    NEWLINE = '\n'
    TAB = '\t'
    WHITESPACE = ' '
    QUOTE = "'"
    DOUBLE_QUOTES = '"'
    COMMA = ','


class Keyword(Enum):
    CLASS = 'class'
    INCLUDE = 'include'


class Token:
    def __init__(self, token_type, line_no, line_pos, value=None):
        self.token_type = token_type
        self.line_no = line_no
        self.line_pos = line_pos
        self.value = value

    def __repr__(self):
        if self.token_type in [Literal.STRING_LITERAL, Literal.NUMBER_LITERAL]:
            return '<line: %s, pos: %s, %s(%s)>' % (self.line_no, self.line_pos, self.token_type, self.value)
        else:
            return '<line: %s, pos: %s, %s>' % (self.line_no, self.line_pos, self.token_type)

    def __str__(self):
        if self.token_type in [Literal.STRING_LITERAL, Literal.NUMBER_LITERAL]:
            return self.value
        else:
            return '%s' % self.token_type.value

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.token_type == other.token_type \
                   and self.line_no == other.line_no \
                   and self.line_pos == other.line_pos \
                   and self.value == other.value
        else:
            return False


class Lexer:
    def __init__(self, input_data):
        self.input = input_data
        self.length = len(input_data)
        self.position = 0
        self.line_no = 1
        self.line_pos = 0
        self.tokens = []
        self.char = None

    def has_next(self):
        return self.position < self.length

    def next(self):
        if not self.has_next():
            raise RuntimeError('reached end of input')

        if self.char == '\n':
            self.line_no += 1
            self.line_pos = 0

        self.position += 1
        self.char = self.input[self.position - 1]
        self.line_pos += 1

        return self.char

    def peek(self, length=1):
        start = max(0, self.position)
        end = min(self.position + length, self.length)
        return self.input[start:end]

    def add_token(self, token_type, value=None):
        line_no = self.line_no
        line_pos = self.line_pos

        if token_type in [Symbol.MCOMMENT_START, Symbol.MCOMMENT_END, Symbol.COMMENT]:
            line_pos -= 1
        elif token_type in [Literal.NUMBER_LITERAL, Literal.STRING_LITERAL]:
            line_pos -= len(value) - 1
        elif token_type == Keyword.CLASS:
            line_pos -= len('class') - 1
        elif token_type == Keyword.INCLUDE:
            line_pos -= len('#include') - 1

        token = Token(token_type, line_no, line_pos, value)
        self.tokens.append(token)

    def tokenize(self):
        while self.has_next():
            next_char = self.next()

            if next_char == '{':
                self.add_token(Symbol.L_CURLY)

            elif next_char == '}':
                self.add_token(Symbol.R_CURLY)

            elif next_char == '(':
                self.add_token(Symbol.L_ROUND)

            elif next_char == ')':
                self.add_token(Symbol.R_ROUND)

            elif next_char == '[':
                self.add_token(Symbol.L_SQUARE)

            elif next_char == ']':
                self.add_token(Symbol.R_SQUARE)

            elif next_char == ';':
                self.add_token(Symbol.SEMICOLON)

            elif next_char == ':':
                self.add_token(Symbol.COLON)

            elif next_char == '=':
                self.add_token(Symbol.EQUALS)

            elif next_char == '+':
                self.add_token(Symbol.PLUS)

            elif next_char == '-':
                peeked_char = self.peek()
                if peeked_char.isdecimal():
                    number_literal = next_char
                    while self.has_next():
                        peeked_char = self.peek()
                        if peeked_char.isdecimal() or peeked_char == '.':
                            number_literal += self.next()
                        else:
                            break
                    self.add_token(Literal.NUMBER_LITERAL, number_literal)
                else:
                    self.add_token(Symbol.MINUS)

            elif next_char == '*':
                peeked_char = self.peek()
                if peeked_char == "/":
                    # case: */
                    self.add_token(Symbol.MCOMMENT_END)
                    self.next()
                else:
                    self.add_token(Symbol.MULT)

            elif next_char == '#':
                if self.peek(7) == 'include':
                    for i in range(0, 7):
                        self.next()
                    self.add_token(Keyword.INCLUDE)
                else:
                    self.add_token(Symbol.HASH)

            elif next_char == '/':
                peeked_char = self.peek()
                if peeked_char == '/':
                    # case: //
                    self.add_token(Symbol.COMMENT)
                    self.next()
                elif peeked_char == '*':
                    # case: /*
                    self.add_token(Symbol.MCOMMENT_START)
                    self.next()
                else:
                    # case: /
                    self.add_token(Symbol.DIV)

            elif next_char == '\n':
                self.add_token(Symbol.NEWLINE)

            elif next_char == '\t':
                self.add_token(Symbol.TAB)

            elif next_char == ' ':
                self.add_token(Symbol.WHITESPACE)

            elif next_char == '"':
                self.add_token(Symbol.DOUBLE_QUOTES)

            elif next_char == "'":
                self.add_token(Symbol.QUOTE)

            elif next_char == ",":
                self.add_token(Symbol.COMMA)

            elif next_char.isdecimal():
                # parse number
                number_literal = next_char
                while self.has_next():
                    peeked_char = self.peek()
                    if peeked_char.isdecimal() or peeked_char == '.':
                        number_literal += self.next()
                    else:
                        break
                self.add_token(Literal.NUMBER_LITERAL, number_literal)

            elif next_char.isalpha():
                # parse letters and numbers
                string_literal = next_char
                while self.has_next():
                    peeked_char = self.peek()
                    if peeked_char.isdecimal() or peeked_char.isalpha() or peeked_char in '._!%&?':
                        string_literal += self.next()
                    else:
                        break

                if string_literal == 'class':
                    self.add_token(Keyword.CLASS)
                else:
                    self.add_token(Literal.STRING_LITERAL, string_literal)

            else:
                raise ValueError('unknown symbol {} encountered at line {}, column {}'.format(next_char,
                                                                                              self.line_no,
                                                                                              self.line_pos))

        return self.tokens
