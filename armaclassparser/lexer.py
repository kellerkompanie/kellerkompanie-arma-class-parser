from enum import Enum

STRING_INPUT_FILE = '<STRING>'


class TokenType(Enum):
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
    BACKSLASH = '\\'
    LESS = '<'
    GREATER = '>'
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
    KEYWORD_CLASS = 'class'
    KEYWORD_INCLUDE = 'include'
    KEYWORD_IFDEF = 'ifdef'
    KEYWORD_IFNDEF = 'ifndef'
    KEYWORD_ELSE = 'else'
    KEYWORD_ENDIF = 'endif'
    KEYWORD_DEFINE = 'define'
    KEYWORD_UNDEF = 'undef'
    STRING_LITERAL = 'STRING'
    NUMBER_LITERAL = 'NUMBER'


class Token:
    def __init__(self, token_type, file_name, line_no, line_pos, value=None):
        self.token_type = token_type
        self.file_name = file_name
        self.line_no = line_no
        self.line_pos = line_pos
        self.value = value

    def __repr__(self):
        if self.token_type in [TokenType.STRING_LITERAL, TokenType.NUMBER_LITERAL]:
            return '<line: %s, pos: %s, %s(%s)>' % (self.line_no, self.line_pos, self.token_type, self.value)
        else:
            return '<line: %s, pos: %s, %s>' % (self.line_no, self.line_pos, self.token_type)

    def __str__(self):
        if self.token_type in [TokenType.STRING_LITERAL, TokenType.NUMBER_LITERAL]:
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
    def __init__(self, input_data, file_name):
        self.input = input_data
        self.length = len(input_data)
        self.file_name = file_name
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

        if token_type in [TokenType.MCOMMENT_START, TokenType.MCOMMENT_END, TokenType.COMMENT]:
            line_pos -= 1
        elif token_type in [TokenType.NUMBER_LITERAL, TokenType.STRING_LITERAL]:
            line_pos -= len(value) - 1
        elif token_type == TokenType.KEYWORD_CLASS:
            line_pos -= len('class') - 1
        elif token_type == TokenType.KEYWORD_INCLUDE:
            line_pos -= len('#include') - 1
        elif token_type == TokenType.KEYWORD_IFDEF:
            line_pos -= len('#ifdef') - 1
        elif token_type == TokenType.KEYWORD_IFNDEF:
            line_pos -= len('#ifndef') - 1
        elif token_type == TokenType.KEYWORD_ELSE:
            line_pos -= len('#else') - 1
        elif token_type == TokenType.KEYWORD_ENDIF:
            line_pos -= len('#endif') - 1
        elif token_type == TokenType.KEYWORD_DEFINE:
            line_pos -= len('#define') - 1
        elif token_type == TokenType.KEYWORD_UNDEF:
            line_pos -= len('#undef') - 1

        token = Token(token_type, self.file_name, line_no, line_pos, value)
        self.tokens.append(token)

    def tokenize(self):
        while self.has_next():
            next_char = self.next()

            if next_char == '{':
                self.add_token(TokenType.L_CURLY)

            elif next_char == '}':
                self.add_token(TokenType.R_CURLY)

            elif next_char == '(':
                self.add_token(TokenType.L_ROUND)

            elif next_char == ')':
                self.add_token(TokenType.R_ROUND)

            elif next_char == '[':
                self.add_token(TokenType.L_SQUARE)

            elif next_char == ']':
                self.add_token(TokenType.R_SQUARE)

            elif next_char == ';':
                self.add_token(TokenType.SEMICOLON)

            elif next_char == ':':
                self.add_token(TokenType.COLON)

            elif next_char == '=':
                self.add_token(TokenType.EQUALS)

            elif next_char == '+':
                self.add_token(TokenType.PLUS)

            elif next_char == '\\':
                self.add_token(TokenType.BACKSLASH)

            elif next_char == '<':
                self.add_token(TokenType.LESS)

            elif next_char == '>':
                self.add_token(TokenType.GREATER)

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
                    self.add_token(TokenType.NUMBER_LITERAL, number_literal)
                else:
                    self.add_token(TokenType.MINUS)

            elif next_char == '*':
                peeked_char = self.peek()
                if peeked_char == "/":
                    # case: */
                    self.add_token(TokenType.MCOMMENT_END)
                    self.next()
                else:
                    self.add_token(TokenType.MULT)

            elif next_char == '#':
                peek = self.peek(7)

                found_keyword = False
                for keyword in [TokenType.KEYWORD_INCLUDE, TokenType.KEYWORD_IFDEF, TokenType.KEYWORD_IFNDEF,
                                TokenType.KEYWORD_ELSE, TokenType.KEYWORD_ENDIF, TokenType.KEYWORD_DEFINE,
                                TokenType.KEYWORD_UNDEF]:
                    if peek.startswith(keyword.value):
                        for i in range(0, len(keyword.value)):
                            self.next()
                        self.add_token(keyword)
                        found_keyword = True
                        break

                if not found_keyword:
                    self.add_token(TokenType.HASH)

            elif next_char == '/':
                peeked_char = self.peek()
                if peeked_char == '/':
                    # case: //
                    self.add_token(TokenType.COMMENT)
                    self.next()
                elif peeked_char == '*':
                    # case: /*
                    self.add_token(TokenType.MCOMMENT_START)
                    self.next()
                else:
                    # case: /
                    self.add_token(TokenType.DIV)

            elif next_char == '\n':
                self.add_token(TokenType.NEWLINE)

            elif next_char == '\t':
                self.add_token(TokenType.TAB)

            elif next_char == ' ':
                self.add_token(TokenType.WHITESPACE)

            elif next_char == '"':
                self.add_token(TokenType.DOUBLE_QUOTES)

            elif next_char == "'":
                self.add_token(TokenType.QUOTE)

            elif next_char == ",":
                self.add_token(TokenType.COMMA)

            elif next_char.isdecimal():
                # parse number
                number_literal = next_char
                while self.has_next():
                    peeked_char = self.peek()
                    if peeked_char.isdecimal() or peeked_char == '.':
                        number_literal += self.next()
                    else:
                        break
                self.add_token(TokenType.NUMBER_LITERAL, number_literal)

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
                    self.add_token(TokenType.KEYWORD_CLASS)
                else:
                    self.add_token(TokenType.STRING_LITERAL, string_literal)

            else:
                raise ValueError('unknown symbol {} encountered at line {}, column {}'.format(next_char,
                                                                                              self.line_no,
                                                                                              self.line_pos))

        return self.tokens
