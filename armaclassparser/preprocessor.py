from armaclassparser import MissingTokenError
from armaclassparser.lexer import Lexer, TokenType


class PreProcessor:
    def __init__(self, file_path):
        self.tokens = None
        self.file_path = file_path

    def preprocess(self):
        with open(self.file_path, 'r') as fp:
            input_data = fp.read()

        self.tokens = Lexer(input_data, self.file_path).tokenize()
        self._remove_comments()

    def _remove_comments(self):
        removals = []
        for i in range(0, len(self.tokens)):
            token = self.tokens[i]
            if token.token_type == TokenType.COMMENT:
                start = i
                while i < len(self.tokens):
                    token = self.tokens[i]
                    if token.token_type == TokenType.NEWLINE:
                        # we want to preserve the newline token, hence i - 1
                        removals.append((start, i - 1,))
                        break
                    elif i == len(self.tokens) - 1:
                        # comment is also finished if we reach end of file
                        removals.append((start, i,))
                        break
                    else:
                        i += 1
            elif token.token_type == TokenType.MCOMMENT_START:
                start = i
                while i < len(self.tokens):
                    token = self.tokens[i]
                    if token.token_type == TokenType.MCOMMENT_END:
                        removals.append((start, i,))
                        break
                    elif i == len(self.tokens) - 1:
                        raise MissingTokenError(TokenType.MCOMMENT_END)
                    else:
                        i += 1

        for start, end in removals:
            del self.tokens[start:end + 1]
