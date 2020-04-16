import os
import sys

from armaclassparser.errors import UnexpectedTokenError, PreProcessingError, MissingTokenError
from armaclassparser.lexer import TokenType, Token, Lexer
from armaclassparser.parser import TokenProcessor


class Define:
    def __init__(self, name, right_side, args=None):
        self.name = name
        self.right_side = right_side
        self.args = args

    def has_args(self) -> bool:
        return self.args is not None and len(self.args) > 0


class PreProcessor(TokenProcessor):
    def __init__(self, tokens, file_path):
        """
        :param tokens:
        :param file_path:
        """
        TokenProcessor.__init__(self, tokens)
        self.file_path = file_path
        self.defines = {}

    def preprocess(self) -> list:
        """
        Runs the pre-processor on the input:
            1. removes comments (multi-line + single line)
            2. replaces #include directives
            3. removes escaped newlines
            4. processes directives (#define,...) and macro usages

        :return: list of tokens - the input after pre-processing
        """
        self._remove_comments()
        self._replace_includes()
        self._remove_escaped_newlines()
        self._process_directives()

        return self.tokens

    def _resolve_include_file_path(self, include_file_path) -> str:
        """
        Lookup the file path of an #include directive and resolve to an absolute path. For relative paths (e.g.,
        #include 'script_component.hpp') the input will be resolved on the file location of the pre-processed file. For
        absolute paths (e.g., #include '\\z\\ace\\...') it will first look on the same drive the currently pre-processed
        file is on and if it cannot be found it will try to look in project drive (P:).

        NOTE: this probably won't work on Linux!

        :param include_file_path: string - the file path to be resolved, e.g., 'script_component.hpp'
        :return: string - absolute file path of the resolved file
        """
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
                    raise PreProcessingError(msg)
                return path_on_p_drive
        else:
            # relative file path, e.g., 'script_component.hpp'
            current_absolute_file_path = os.path.abspath(self.file_path)
            current_absolute_directory = os.path.dirname(current_absolute_file_path)
            dst_file_path = os.path.join(current_absolute_directory, include_file_path)
            if not os.path.isfile(dst_file_path):
                msg = 'could not resolve relative include {} in file {}'.format(dst_file_path, self.file_path)
                raise PreProcessingError(msg)
            return dst_file_path

    def _parse_include_file_path(self) -> str:
        """
        Parses the right-side of an #include statement, e.g., "script_component.hpp".

        :return: string - the string value of the right-side, e.g., "script_component.hpp"
        """
        tokens = [self.token()]

        if tokens[0].token_type not in [TokenType.DOUBLE_QUOTES, TokenType.LESS]:
            raise UnexpectedTokenError([TokenType.DOUBLE_QUOTES, TokenType.LESS], tokens[0])

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

        raise MissingTokenError(tokens[0].token_type)

    def _replace_includes(self):
        """
        Processes #include directives by parsing the included file and inserting it contents in place of the #include.
        """
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
                with open(dst_file_path, 'r', encoding='utf-8', newline=None) as fp:
                    input_data = fp.read()
                tokens = Lexer(input_data, dst_file_path).tokenize()

                preprocessor = PreProcessor(tokens, dst_file_path)
                preprocessor.defines = self.defines
                tokens = preprocessor.preprocess()

                # replace include statement with included content
                del self.tokens[include_start:include_end]
                self.tokens = self.tokens[:include_start] + tokens + self.tokens[include_start:]
                self.index += len(tokens) - (include_end - include_start)

            elif token.token_type in [TokenType.COMMENT, TokenType.MCOMMENT_START, TokenType.MCOMMENT_END]:
                msg = 'expected comments to have been handled already, but found {}'.format(repr(token))
                raise PreProcessingError(msg)
            else:
                self.index += 1

    def _remove_escaped_newlines(self):
        """
        Removes all newline symbols which are escaped using \\, such as might happen for macro definitions.
        """
        self.index = 0
        while self.index < len(self.tokens):
            if self.token().token_type == TokenType.BACKSLASH:
                next_token = self.tokens[self.index + 1]
                if next_token.token_type == TokenType.NEWLINE:
                    del self.tokens[self.index:self.index + 2]
            self.index += 1

    def _remove_comments(self):
        """
        Removes all multi- and single line comments.
        """
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
        """
        Deletes all tokens between [start_index:end_index] including the token at end_index, then updates self.index.

        :param start_index: int - index at which to start deleting (inclusive)
        :param end_index: int - index until which to delete (inclusive)
        """
        del self.tokens[start_index:end_index + 1]
        self.index -= end_index - start_index

    def _process_define(self):
        """
        Processes #define directives, e.g., #define EXP(x) x * x. The resulting Define object is put into the
        map of defines (self.defines) for later lookup.
        """
        start_index = self.index
        self.expect(TokenType.KEYWORD_DEFINE)
        self.expect_next([TokenType.WHITESPACE, TokenType.TAB])
        self.skip_whitespaces()
        macro_name = self.expect(TokenType.WORD).value

        self.expect_next([TokenType.L_ROUND, TokenType.WHITESPACE, TokenType.TAB, TokenType.NEWLINE])
        args = []
        if self.token().token_type == TokenType.L_ROUND:
            self.expect_next(TokenType.WORD)
            while self.index < len(self.tokens):
                arg_word = self.expect(TokenType.WORD)
                args.append(arg_word.value)
                next_token = self.tokens[self.index + 1]
                if next_token.token_type == TokenType.COMMA:
                    self.expect_next(TokenType.COMMA)
                    self.expect_next([TokenType.WORD, TokenType.TAB, TokenType.WHITESPACE])
                    if self.token().token_type in [TokenType.TAB, TokenType.WHITESPACE]:
                        self.skip_whitespaces()
                elif next_token.token_type == TokenType.R_ROUND:
                    self.expect_next(TokenType.R_ROUND)
                    self.next()
                    break
                else:
                    raise PreProcessingError(
                        'unexpected token while parsing args of #define: {}'.format(next_token))

        self.skip_whitespaces()

        # parse right side
        right_side = []
        while self.index < len(self.tokens) and self.token().token_type != TokenType.NEWLINE:
            if self.token().token_type != TokenType.DOUBLE_HASH:
                right_side.append(self.token())
            self.index += 1

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
        """
        Processes #undef directives and removes them from the mapping (self.defines).
        """
        start_index = self.index
        self.expect(TokenType.KEYWORD_UNDEF)
        self.expect_next([TokenType.WHITESPACE, TokenType.TAB])
        self.skip_whitespaces()
        macro_name = self.expect(TokenType.WORD).value

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

    def _skip_until(self, break_tokens):
        """
        Skips all tokens until one of the break tokens is encountered. The skipped tokens are deleted.

        :param break_tokens: list of tokens - the tokens on which to stop skipping
        """
        while self.index < len(self.tokens) and self.token().token_type not in break_tokens:
            del self.tokens[self.index]

        if self.index == len(self.tokens):
            raise PreProcessingError('reached EOF while skipping until {}'.format(break_tokens))

        self.expect(break_tokens)

    def _process_until(self, break_tokens):
        """
        Processes all tokens until one of the break tokens is encountered.

        :param break_tokens: list of tokens - the tokens on which to stop processing
        """
        while self.index < len(self.tokens) and self.token().token_type not in break_tokens:
            self._process_next()

        if self.index == len(self.tokens) - 1:
            raise PreProcessingError('reached EOF while processing until {}'.format(break_tokens))

        self.expect(break_tokens)

    def _process_if_else(self):
        """
        Processes and replaces #ifdef, #ifndef, #else, #endif directives in place.
        """
        start_index = self.index
        if_token = self.expect([TokenType.KEYWORD_IFDEF, TokenType.KEYWORD_IFNDEF])

        self.expect_next([TokenType.WHITESPACE, TokenType.TAB])
        self.skip_whitespaces()
        macro_name = self.expect(TokenType.WORD).value
        self.expect_next(TokenType.NEWLINE)
        self._delete_tokens_update_index(start_index, self.index)

        if (if_token.token_type == TokenType.KEYWORD_IFDEF and macro_name in self.defines) or \
                (if_token.token_type == TokenType.KEYWORD_IFNDEF and macro_name not in self.defines):
            # process until #else or #endif
            self._process_until([TokenType.KEYWORD_ELSE, TokenType.KEYWORD_ENDIF])
            if self.token().token_type == TokenType.KEYWORD_ELSE:
                del self.tokens[self.index]
                self.expect(TokenType.NEWLINE)
                del self.tokens[self.index]
                self._skip_until([TokenType.KEYWORD_ENDIF])
        else:
            # skip until #else or #endif
            self._skip_until([TokenType.KEYWORD_ELSE, TokenType.KEYWORD_ENDIF])
            if self.token().token_type == TokenType.KEYWORD_ELSE:
                del self.tokens[self.index]
                self.expect(TokenType.NEWLINE)
                del self.tokens[self.index]
                self._process_until([TokenType.KEYWORD_ENDIF])

        # #endif was reached in any case, ignore and delete including newline
        del self.tokens[self.index]
        self.expect(TokenType.NEWLINE)
        del self.tokens[self.index]

    def _expand_macro(self, tokens):
        """
        Takes a macro in form of tokens and expands it based on the current defines.

        :param tokens: list of tokens - the input macro, must be entire macro including parenthesis,
                                        e.g., "EGVAR(main,variable)"
        :return: list of tokens - the macro after expansion
        """
        # macros can be nested, so treat the macro as self-sustained unit that has to be processed
        macro_processor = PreProcessor(tokens, self.file_path)
        macro_processor.defines = self.defines  # keep all defines up to this point
        macro_key = macro_processor.expect(TokenType.WORD).value
        define = self.defines[macro_key]  # lookup the definition of the macro we are about to expand

        if define.has_args():
            # if this macro has arguments we need to parse all of them in order to know with which tokens to replace
            # the arguments of the macro
            macro_processor.expect_next(TokenType.L_ROUND)
            macro_processor.next()
            arg_values = {}  # map argument -> tokens
            for i in range(0, len(define.args) - 1):
                # if macro has more than 1 argument parse first the 'inner' ones which are succeeded by a ,
                arg_value = []
                while macro_processor.token().token_type != TokenType.COMMA:
                    arg_value += macro_processor._process_next()
                arg_values[define.args[i]] = arg_value
                macro_processor.expect(TokenType.COMMA)
                macro_processor.next()

            # parse the last argument individually as it will be ended by ) instead of ,
            arg_value = []
            while macro_processor.token().token_type != TokenType.R_ROUND:
                arg_value += macro_processor._process_next()
            arg_values[define.args[-1]] = arg_value
            macro_processor.expect(TokenType.R_ROUND)

            # right side can be nested, so process it as an independent unit
            right_side_processor = PreProcessor(define.right_side.copy(), file_path='<MACRO>')
            right_side_processor.defines = self.defines
            for key, value in arg_values.items():
                # little trick: we treat all of the previously parsed arguments
                right_side_processor.defines[key] = Define(key, value)
            right_side_processor._process_directives()
            replacement = right_side_processor.tokens

            return replacement

        else:
            # simple macro, just return processed right side
            right_side_processor = PreProcessor(define.right_side.copy(), file_path='<MACRO>')
            right_side_processor.defines = self.defines
            right_side_processor._process_directives()
            replacement = right_side_processor.tokens
            return replacement

    def _process_macro_usage(self):
        """
        Processes one macro usage, e.g., "ADDON" or "EGVAR(main,variable)", replaces the old macro directive with the
        expanded version and updates index accordingly.

        :return: list of tokens - the expanded macro
        """
        start_index = self.index  # needed to replace the macro tokens we are expanding
        macro_key = self.expect(TokenType.WORD).value
        define = self.defines[macro_key]  # lookup the definition of the macro we are about to expand

        if define.has_args():
            # skip all tokens that belong to the macro, including the arguments and parenthesis
            self.expect_next(TokenType.L_ROUND)
            self.next()
            unclosed_l_rounds = 1
            while unclosed_l_rounds != 0:
                if self.token().token_type == TokenType.L_ROUND:
                    unclosed_l_rounds += 1
                elif self.token().token_type == TokenType.R_ROUND:
                    unclosed_l_rounds -= 1
                self.index += 1

            # expand the entire macro and insert it into the tokens + update index
            expanded_macro = self._expand_macro(self.tokens[start_index:self.index])
            self.tokens = self.tokens[:start_index] + expanded_macro + self.tokens[self.index:]
            self.index = start_index + len(expanded_macro)
        else:
            # macro consists of only 1 token, expand it and insert into tokens + update index
            expanded_macro = self._expand_macro([self.token()])

            if self.index > 0:
                previous_token = self.tokens[self.index - 1]
                if previous_token.token_type == TokenType.HASH:
                    # special case of stringify, e.g., #define QUOTE(var) #var -> QUOTE(hello) -> "hello"
                    l_quote = Token(TokenType.DOUBLE_QUOTES, previous_token.file_path, previous_token.line_no,
                                    previous_token.line_pos)
                    r_quote = Token(TokenType.DOUBLE_QUOTES, previous_token.file_path, previous_token.line_no,
                                    previous_token.line_pos)
                    expanded_macro = [l_quote] + expanded_macro + [r_quote]
                    self.index -= 1
                    del self.tokens[self.index]
                    start_index -= 1

            self.tokens = self.tokens[:start_index] + expanded_macro + self.tokens[start_index + 1:]
            self.index = self.index + len(expanded_macro)

        return expanded_macro

    def _process_next(self):
        """
        Processes next token or pre-processor directive. If token is a pre-processor directive it will be processed and
        replaced/deleted. Leaves all other tokens as is.
        Returns a list of all tokens that replaced the processed one, e.g., in case of macro expansion it will hold the
        newly added tokens. For pre-processor directives #define, #undef and #if/else it will return empty list, as
        these are simply processed and then removed. All other tokens are left as is and returned as [token].

        :return: list of tokens after replacement
        """
        if self.token().token_type == TokenType.KEYWORD_DEFINE:
            self._process_define()
            return []
        elif self.token().token_type == TokenType.KEYWORD_UNDEF:
            self._process_undefine()
            return []
        elif self.token().token_type in [TokenType.KEYWORD_IFDEF, TokenType.KEYWORD_IFNDEF]:
            self._process_if_else()
            return []
        elif self.token().token_type == TokenType.WORD:
            if self.token().value in self.defines:
                return self._process_macro_usage()

        token = self.token()
        self.index += 1
        return [token]

    def _process_directives(self):
        """
        Processes all pre-processor directives (except #include) and leaves all other tokens as is.
        """
        self.index = 0
        while self.index < len(self.tokens):
            self._process_next()
