import os
import sys

import armaclassparser
from armaclassparser import MissingTokenError
from armaclassparser.lexer import TokenType
from armaclassparser.parser import TokenProcessor


class Define:
    def __init__(self, name, right_side, args=None):
        self.name = name
        self.right_side = right_side
        self.args = args


class PreProcessor(TokenProcessor):
    def __init__(self, tokens, file_path):
        TokenProcessor.__init__(self, tokens)
        self.file_path = file_path
        self.defines = {}

    def preprocess(self):
        self._remove_comments()
        self._replace_includes()
        self._remove_escaped_newlines()
        self._process_defines()
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

    def _replace_includes(self, recursive=True):
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

                # recursively process the file to be included
                dst_file_path = self._resolve_include_file_path(include_file_path)
                tokens = armaclassparser.parse_from_file(dst_file_path)

                # added to make testing easier
                if recursive:
                    preprocessor = PreProcessor(tokens, dst_file_path)
                    tokens = preprocessor.preprocess()

                # replace include statement with included content
                del self.tokens[include_start:include_end]
                self.tokens = self.tokens[0:include_start] + tokens + self.tokens[include_start:]
                self.index += len(tokens) - (include_end - include_start)

            elif token.token_type in [TokenType.COMMENT, TokenType.MCOMMENT_START, TokenType.MCOMMENT_END]:
                msg = 'expected comments to have been handled already, but found {}'.format(repr(token))
                raise armaclassparser.PreProcessingError(msg)
            else:
                self.index += 1

    def _remove_escaped_newlines(self):
        self.index = 0
        while self.index < len(self.tokens):
            if self.token().token_type == TokenType.BACKSLASH:
                next_token = self.tokens[self.index + 1]
                if next_token.token_type == TokenType.NEWLINE:
                    del self.tokens[self.index:self.index + 2]
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

    def _delete_tokens_update_index(self, start_index, end_index):
        del self.tokens[start_index:end_index + 1]
        self.index -= end_index - start_index

    def _process_define(self):
        start_index = self.index
        self.expect(TokenType.KEYWORD_DEFINE)
        self.expect_next([TokenType.WHITESPACE, TokenType.TAB])
        self.skip_whitespaces()
        macro_name = self.expect(TokenType.STRING_LITERAL).value

        args = []
        if self.next() in [TokenType.L_ROUND]:
            while self.has_next():
                self.next()
                if self.token().token_type == TokenType.STRING_LITERAL:
                    args.append(self.token().value)
                elif self.token().token_type == TokenType.COMMA:
                    if self.tokens[self.index + 1].token_type == TokenType.STRING_LITERAL:
                        raise armaclassparser.PreProcessingError(
                            "expected another arg after ',' symbol, but got {} instead".format(
                                self.tokens[self.index + 1]))
                elif self.token().token_type == TokenType.R_ROUND:
                    self.expect_next([TokenType.WHITESPACE, TokenType.TAB])

                    break
                else:
                    raise armaclassparser.PreProcessingError(
                        'encountered unexpected Token while processing macro args: {}'.format(self.token()))

        self.skip_whitespaces()

        # parse right side
        right_side = []
        while self.token().token_type != TokenType.NEWLINE and self.has_next():
            right_side.append(self.token())
            self.next()

        # map the new define for later
        if macro_name in self.defines:
            msg = 'WARNING: macro {} was already defined, {} on line {}'.format(macro_name,
                                                                                self.token().file_path,
                                                                                self.token().line_no)
            print(msg, file=sys.stderr)
        self.defines[macro_name] = Define(macro_name, right_side, args)

        # define was resolved, delete corresponding tokens
        self._delete_tokens_update_index(start_index, self.index)

    def _process_undefine(self):
        start_index = self.index
        self.expect(TokenType.KEYWORD_UNDEF)
        self.expect_next([TokenType.WHITESPACE, TokenType.TAB])
        self.skip_whitespaces()
        macro_name = self.expect(TokenType.STRING_LITERAL).value

        # remove existing define
        if macro_name in self.defines:
            del self.defines[macro_name]
        else:
            msg = 'WARNING: trying to undefine macro name which was not previously defined: {} in {} on line {}'.format(
                macro_name,
                self.token().file_path,
                self.token().line_no)
            print(msg, file=sys.stderr)

        # undefine was resolved, delete corresponding tokens
        self._delete_tokens_update_index(start_index, self.index)

    def _process_if_else(self):
        self.expect_next([TokenType.WHITESPACE, TokenType.TAB])
        self.skip_whitespaces()
        macro_name = self.expect(TokenType.STRING_LITERAL).value
        if macro_name in self.defines:
            # process until #ENDIF
            pass
        else:
            # skip until #ELSE or #ENDIF
            pass

    def _process_macro_usage(self):
        macro_key = self.expect(TokenType.STRING_LITERAL).value
        define = self.defines[macro_key]
        self.tokens = self.tokens[:self.index] + define.right_side + self.tokens[self.index + 1:]
        self.index += len(define.right_side)

    def _process_defines(self):
        self.index = 0
        while self.has_next():
            if self.token().token_type == TokenType.KEYWORD_DEFINE:
                self._process_define()
            elif self.token().token_type == TokenType.KEYWORD_UNDEF:
                self._process_undefine()
            elif self.token().token_type in [TokenType.KEYWORD_IFDEF, TokenType.KEYWORD_IFNDEF]:
                self._process_if_else()
            elif self.token().token_type == TokenType.STRING_LITERAL:
                if self.token().value in self.defines:
                    self._process_macro_usage()
                else:
                    self.next()
            else:
                self.next()
