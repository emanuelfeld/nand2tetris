import re


TOKEN_RE = {
    'a-decimal': re.compile(r"@(?P<value>[\d]+)"),
    'a-symbol':  re.compile(r"@(?P<symbol>.+)"),
    'l':         re.compile(r"\((?P<symbol>.+)\)"),
    'c':         re.compile(r"((?P<dest>.+)=)?(?P<comp>[^;=]+)(;(?P<jump>[A-Z]+))?")
}


class Parser:
    def __init__(self, lines):
        self.lines = lines
        self.parsed = []

    def parse(self):
        for line in self.lines:
            cmd = self.strip(line)
            if cmd:
                self.parsed.append(self.parse_instr(cmd))

    @staticmethod
    def strip(line):
        return line.split('//')[0].strip()

    @staticmethod
    def parse_instr(cmd):
        """
        Returns instruction type and dictionary of symbols, labels, 
        and variables for a line of the program
        """
        
        for instr_type in TOKEN_RE:
            match = re.fullmatch(TOKEN_RE[instr_type], cmd)
            if match:
                return instr_type, match.groupdict('')
