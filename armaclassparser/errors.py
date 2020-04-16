class PreProcessingError(Exception):
    pass


class ParsingError(Exception):
    pass


class UnexpectedTokenError(ParsingError):
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual
        super().__init__(
            "expected token {} but got {} on line {}, col {} in {}".format(expected, actual.token_type, actual.line_no,
                                                                           actual.line_pos, actual.file_path))


class UnexpectedStatementError(ParsingError):
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual
        super().__init__(
            "expected statement {} but got {} on line {}, col {}".format(expected, actual.type, actual.line_no,
                                                                         actual.line_pos))


class MissingTokenError(ParsingError):
    def __init__(self, target, source=None):
        if source:
            super().__init__("reached end of file while looking for token {}, closing {}".format(target, source))
        else:
            super().__init__("reached end of file while looking for token {}".format(target))
        self.target = target
        self.source = source
