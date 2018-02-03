ARITHMETIC_OPERATIONS = ['add', 'sub', 'or', 'and', 'not', 'neg']
LOGICAL_OPERATIONS =['eq', 'lt', 'gt']

class Parser:
    def __init__(self, lines):
        self.index = 0
        self.lines = []
        for line in lines:
            line = self.strip_line(line)
            if line:
                self.lines.append(line.split())

    def has_more_commands(self):
        return self.index < len(self.lines)

    def advance(self):
        self.current = self.lines[self.index]
        self.index += 1
        return self.current

    def get_cmd_type(self):
        if self.current[0] in ARITHMETIC_OPERATIONS:
            return 'arithmetic'
        elif self.current[0] in LOGICAL_OPERATIONS:
            return 'logical'
        else:
            return self.current[0]

    def strip_line(self, line):
        return line.split('//')[0].strip()
