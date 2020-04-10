import os

import armaclassparser
from armaclassparser import MissingTokenError
from armaclassparser.lexer import TokenType
from armaclassparser.parser import TokenProcessor


class PreProcessor(TokenProcessor):
    def __init__(self, tokens, file_path):
        TokenProcessor.__init__(self, tokens)
        self.file_path = file_path

    def preprocess(self):
        print('pre-processing', self.file_path)
        self._remove_comments()
        self._replace_includes()
        return self.tokens

    def _resolve_include_file_path(self, include_file_path):
        if include_file_path.startswith('\\'):
            # absolute file path, e.g., '\z\ace\addons\main\script_mod.hpp'
            drive, _ = os.path.splitdrive(self.file_path)
            path_on_current_drive = os.path.join(drive, include_file_path)
            if os.path.isfile(path_on_current_drive):
                return path_on_current_drive
            else:
                # file could not be found on current drive, use p-drive instead
                path_on_p_drive = os.path.join('P:', include_file_path)
                if not os.path.isfile(path_on_p_drive):
                    msg = 'could not resolve absolute include "{}" in file {}'.format(include_file_path, self.file_path)
                    raise armaclassparser.PreProcessingError(msg)
                return path_on_p_drive
        else:
            # relative file path, e.g., 'script_component.hpp'
            current_absolute_file_path = os.path.abspath(self.file_path)
            current_absolute_directory = os.path.dirname(current_absolute_file_path)
            dst_file_path = os.path.join(current_absolute_directory, include_file_path)
            if not os.path.isfile(dst_file_path):
                msg = 'could not resolve relative include {} in file {}'.format(dst_file_path, self.file_path)
                raise armaclassparser.PreProcessingError(msg)
            return dst_file_path

    def _parse_include_file_path(self):
        tokens = [self.token()]

        if tokens[0].token_type not in [TokenType.DOUBLE_QUOTES, TokenType.LESS]:
            raise armaclassparser.UnexpectedTokenError([TokenType.DOUBLE_QUOTES, TokenType.LESS], tokens[0])

        self.index += 1
        while self.index < len(self.tokens):
            token = self.tokens[self.index]
            if token.token_type == tokens[0].token_type:
                tokens.append(token)
                self.index += 1
                return ''.join(token.value for token in tokens[1:-1])
            else:
                tokens.append(token)
                self.index += 1

        raise armaclassparser.MissingTokenError(tokens[0].token_type)

    def _replace_includes(self):
        self.index = 0
        while self.index < len(self.tokens):
            token = self.token()
            if token.token_type == TokenType.KEYWORD_INCLUDE:
                include_start = self.index
                self.expect(TokenType.KEYWORD_INCLUDE)
                self.expect_next(TokenType.WHITESPACE)
                self.index += 1
                include_file_path = self._parse_include_file_path()
                include_end = self.index

                dst_file_path = self._resolve_include_file_path(include_file_path)
                tokens = armaclassparser.parse_from_file(dst_file_path)
                preprocessor = PreProcessor(tokens, dst_file_path)
                tokens = preprocessor.preprocess()

                # replace include statement with included content
                del self.tokens[include_start:include_end]
                self.tokens = self.tokens[0:include_start] + tokens + self.tokens[include_start:]
                self.index += len(tokens)

            elif token.token_type in [TokenType.COMMENT, TokenType.MCOMMENT_START, TokenType.MCOMMENT_END]:
                msg = 'expected comments to have been handled already, but found {}'.format(repr(token))
                raise armaclassparser.ParsingError(msg)
            else:
                self.index += 1

    def _remove_comments(self):
        removals = []
        self.index = 0
        while self.has_next():
            if self.token().token_type == TokenType.COMMENT:
                start = self.index
                while self.has_next():
                    self.next()
                    if self.token().token_type == TokenType.NEWLINE:
                        # we want to preserve the newline token, hence i - 1
                        removals.append((start, self.index - 1,))
                        break
                    elif not self.has_next():
                        # comment is also finished if we reach end of file
                        removals.append((start, self.index,))
                        break
            elif self.token().token_type == TokenType.MCOMMENT_START:
                start = self.index
                while self.has_next():
                    self.next()
                    if self.token().token_type == TokenType.MCOMMENT_END:
                        removals.append((start, self.index,))
                        break
                    elif not self.has_next():
                        # reached end of file without encountering comment end
                        raise MissingTokenError(TokenType.MCOMMENT_END)
            else:
                self.next()

        for start, end in reversed(removals):
            del self.tokens[start:end + 1]
