KNOWN_SEGMENTS = {
    'pointer': 3,
    'temp': 5,
    'static': '{filename}.{index}'         
}


UNKNOWN_SEGMENTS = {
    'local': 'LCL',
    'argument': 'ARG',
    'this': 'THIS',
    'that': 'THAT'        
}


OPERANDS = {
    'add': '+',
    'sub': '-',
    'and': '&',
    'or':  '|',
    'neg': '-',
    'not': '!'
}


class Translator:
    def __init__(self, filename):
        self.filename = filename
        self.translated = []
        self.label_counter = -1

    def close(self):
        self.translation = '\n'.join(self.translated) + '\n'

    def write(self, cmd_type, cmd):
        instr = [f'// {cmd}']
        if cmd_type == 'arithmetic':
            instr += self.write_arithmetic(*cmd)
        elif cmd_type == 'push':
            instr += self.write_push(*cmd[1:])
        elif cmd_type == 'pop':
            instr += self.write_pop(*cmd[1:])
        self.translated.extend(instr)

    def write_arithmetic(self, operator):
        """
        If unary arithmetic:
            1. Set Y={operand}Y
        If binary arithmetic:
            1. Set X=X{operand}Y
            2. Decrement SP
        If binary logical:
            1. Set X=X-Y
            2. Decrement SP (Y=X)
            3. Write logical comparison of Y
        """

        instr = ['@SP', 'A=M-1', 'D=M']

        if operator in ['neg', 'not']:
            operand = OPERANDS[operator]
            instr += [f'M={operand}D']

        elif operator in ['add', 'sub', 'and', 'or']:
            operand = OPERANDS[operator]
            instr += ['A=A-1', f'M=M{operand}D',
                     '@SP', 'M=M-1']

        elif operator in ['eq', 'lt', 'gt']:
            instr = ['A=A-1', f'M=M-D',
                     '@SP', 'M=M-1']
            instr += self.write_logical(operator)

        return instr

    def write_logical(self, operator):
        """
        1. Compare Y to zero according to operator
        2. Set Y=0 if false, otherwise Y=-1
        """

        true_label = self.make_unique_label()
        done_label = self.make_unique_label()
        instr = ['@SP', 'A=M-1', 'D=M',
                f'@{true_label}',
                f'D;J{operator.upper()}',
                 '@SP', 'A=M-1', 'M=0',
                f'@{done_label}',
                 '0;JMP',
                f'({true_label})',
                 '@SP', 'A=M-1', 'M=-1',
                f'({done_label})']

        return instr

    def write_push(self, segment, index):
        """
        1. Set D-register to constant or value at RAM address
        2. Store value on top of stack
        3. Increment stack pointer
        """

        if segment == 'constant':
            instr = [f'@{index}', 'D=A']
        else:
            instr = self.get_address(segment, index)
            instr += ['A=D', 'D=M']

        instr += [f'@SP', 'A=M', 'M=D',
                   '@SP', 'M=M+1']

        return instr

    def write_pop(self, segment, index):
        """
        1. Store destination RAM address in R13
        2. Get value at top of stack
        3. Store it at address stored in R13
        4. Decrement pointer
        """

        instr = self.get_address(segment, index)
        instr += self.cache_d('13')

        instr += [f'@SP', 'A=M-1', 'D=M',
                  f'@R13', 'A=M', 'M=D',
                   '@SP', 'M=M-1']

        return instr

    def cache_d(self, cache_address):
        """Store D-register value in cache address"""

        return [f'@{cache_address}', 'M=D']

    def make_unique_label(self):
        self.label_counter += 1
        return f'LABEL$${self.label_counter}'

    def get_address(self, segment, index):
        if segment in KNOWN_SEGMENTS:
            base = KNOWN_SEGMENTS[segment]
            if segment == 'static':
                address = base.format(self.filename, index)
            else:
                address = f'{base + int(index)}'
            return [f'@{address}', 'D=A']
        elif segment in UNKNOWN_SEGMENTS:
            pointer = UNKNOWN_SEGMENTS[segment]
            return [f'@{index}', 'D=A', f'@{pointer}', 'D=M+D']
