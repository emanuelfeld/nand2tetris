import re
from collections import namedtuple


Token = namedtuple('Token', ('type', 'value'))


def escape(value):
    value = re.sub('&', '&amp;', value)
    value = re.sub('<', '&lt;', value)
    value = re.sub('>', '&gt;', value)
    value = re.sub('"', '&quot;', value)
    return value


def is_whitespace(char):
    return re.match(r'\s', char)


class Tokenizer:

    _KEYWORDS = ['class', 'constructor', 'function',
                 'method', 'field', 'static', 'var',
                 'int', 'char', 'boolean', 'void',
                 'true', 'false', 'null', 'this',
                 'let', 'do', 'if', 'else', 'while',
                 'return']

    _SYMBOLS = ["{", "}", "(", ")", "[", "]", ".", ",",
                ";", "+", "-", "*", "/", "&", "|", "<",
                ">", "=", "~"]

    def __init__(self, lines):
        self.lines = lines
        self.tokens = []
        self.xml = []
        self.is_block_comment = False

    def run(self):
        """
        Tokenize file
        """
        for index in range(len(self.lines)):
            _line = self.strip_comment(self.lines[index])
            _tokens = [t for t in self.tokenize_line(_line) if t]
            _xml = [self.token_to_xml(t) for t in _tokens]
            self.tokens.extend(_tokens)
            self.xml.extend(_xml)
        self.xml = ['<tokens>'] + self.xml + ['</tokens>']

    def get_token_type(self, token):
        """
        Return matching Token(type, value) tuple
        """
        token = token.strip()
        if not token:
            pass
        elif token in self._KEYWORDS:
            return Token('keyword', token)
        elif token in self._SYMBOLS:
            return Token('symbol', token)
        elif re.fullmatch(r'"[^"\n]*"', token):
            return Token('stringConstant', token[1:-1])
        elif re.fullmatch(r'[a-zA-Z_][\w_]*', token):
            return Token('identifier', token)
        elif token.isdecimal() and abs(int(token)) in range(32768):
            return Token('integerConstant', token)

    def tokenize_line(self, line):
        """
        Extract all tokens from text in line
        """
        token_value = ''
        is_string = False

        for char in line:
            if char in self._SYMBOLS:
                if token_value:
                    yield self.get_token_type(token_value)
                    token_value = ''
                yield Token('symbol', char)
            elif char == '"':
                is_string = not is_string
                token_value += char
                if not is_string:
                    yield self.get_token_type(token_value)
                    token_value = ''
            elif is_whitespace(char) and token_value and not is_string:
                yield self.get_token_type(token_value)
                token_value = ''
            else:
                token_value += char

        yield self.get_token_type(token_value)

    def strip_comment(self, line):
        """
        Remove comments (single-line or block) from text
        """
        if re.search(r'//.*|/\*\*.*?\*/', line):
            return re.sub(r'//.*|/\*\*.*?\*/', '', line).strip()
        elif re.match(r'/\*\*.*', line):
            self.is_block_comment = True
            return ''
        elif self.is_block_comment:
            if re.match(r'.*\*/', line):
                self.is_block_comment = False
            return ''
        return line.strip()

    @staticmethod
    def token_to_xml(token):
        """
        Reformat token tuple as XML
        """
        return f'<{token.type}> {escape(token.value)} </{token.type}>'
