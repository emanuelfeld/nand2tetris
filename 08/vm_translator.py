# we know these at runtime
KNOWN_SEGMENTS = {
    'pointer': 3,
    'temp': 5,
}


# these have their base addresses (re)set later
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
    'not': '!',
    'lt': '-',
    'eq': '-',
    'gt': '-'
}


class Translator:
    def __init__(self):
        self.label_counter = -1
        self.translated = []

    def set_filename(self, filename):
        self.filename = filename

    def close(self):
        self.translation = '\n'.join(self.translated) + '\n'

    def write(self, instr):
        instr = map(lambda x: x.strip(), instr.split('\n'))
        instr = list(filter(None, instr))
        self.translated.extend(instr)

    def translate(self, cmd_type, cmd):
        self.write(f'// {cmd}')

        if cmd_type == 'arithmetic':
            self.write_arithmetic(*cmd)
        elif cmd_type == 'logical':
            self.write_logical(*cmd)
        elif cmd_type == 'push':
            self.write_push(*cmd[1:])
        elif cmd_type == 'pop':
            self.write_pop(*cmd[1:])
        elif cmd_type == 'label':
            self.write_label(cmd[1])
        elif cmd_type == 'if-goto':
            self.write_if(cmd[1])
        elif cmd_type == 'goto':
            self.write_goto(cmd[1])
        elif cmd_type == 'call':
            self.write_call(*cmd[1:])
        elif cmd_type == 'return':
            self.write_return()
        elif cmd_type == 'function':
            self.write_function(*cmd[1:])

    def write_init(self):
        """
        Bootstrap/initialize VM
        """

        self.write(f"""
            @256
            D=A
            @SP
            M=D
            """)

        self.write_call('Sys.init', '0')

    def write_label(self, label):
        self.write(f"""
            ({label}$label)
            """)

    def write_arithmetic(self, operator):
        """
        D = *(SP-1)
        If unary arithmetic:
            1. Set M = {operand} D
        If binary arithmetic:
            1. Set *(SP-2) = *(SP-2) {operand} *(SP-1)
            2. SP = SP - 1
        """

        operand = OPERANDS[operator]
        self.write(f"""
            @SP
            A=M-1
            D=M
            """)

        if operator in ['neg', 'not']:
            self.write(f"""
                M={operand}D
                """)
        else:
            self.write(f"""
                A=A-1
                M=M{operand}D
                @SP
                M=M-1
                """)

    def write_logical(self, operator):
        """
        1. *(SP-2) = *(SP-2) - *(SP-1)
        2. Compare *(SP-2) to zero
        3. *(SP-2) = -1 if True, else 0
        4. SP = SP - 1
        """

        self.write_arithmetic('sub')

        true_label = self.make_unique_label()
        done_label = self.make_unique_label()

        self.write(f"""
            @SP
            A=M-1
            D=M
            @{true_label}
            D;J{operator.upper()}
            @SP
            A=M-1
            M=0
            @{done_label}
            0;JMP
            ({true_label})
            @SP
            A=M-1
            M=-1
            ({done_label})
            """)

    def write_push(self, segment, index=0):
        """
        1. D = constant or *(segment base + index)
        2. *(SP) = D
        3. SP = SP + 1
        """

        if segment == 'constant':
            self.write(f"""
                @{index}
                D=A
                """)

        elif segment == 'static':
            self.write(f"""
                @{self.filename}.{index}
                D=M
                """)

        else:
            self.get_ram_address(segment, index)
            self.write(f"""
                A=D
                D=M
                """)

        self.write_push_d()

    def write_pop(self, segment, index):
        """
        If static:
            1. D = pop()
            2. *(segment base + index) = D
        Else:
            1. R13 = segment base + index
            2. D = pop()
            3. *(R13) = D
        """

        if segment == 'static':
            self.write_pop_d()
            self.write(f"""
                @{self.filename}.{index}
                M=D
                """)
        else:
            self.get_ram_address(segment, index)
            self.write(f"""
                @R13
                M=D
                """)
            self.write_pop_d()
            self.write(f"""
                @R13
                A=M
                M=D
                """)

    def write_if(self, label):
        """
        If *(SP-1) != 0, jump to label
        """

        self.write_pop_d()
        self.write(f"""
            @{label}$label
            D;JNE
            """)

    def write_goto(self, label):
        """
        Jump to label
        """

        self.write(f"""
            @{label}$label
            0;JMP
            """)

    def write_call(self, fn, nargs):
        """
        Call function fn, stating that nargs arguments have already
        been pushed onto the stack by the caller
        """

        return_label = self.make_unique_label() 
        self.write(f"""
            @{return_label}
            D=A
            """)
        self.write_push_d()

        for segment in ['local', 'argument', 'this', 'that']:
            self.get_ram_address(segment, '0')
            self.write_push_d()

        self.write(f"""
            @SP
            D=M
            @{int(nargs)+5}
            D=D-A
            @ARG
            M=D
            @SP
            D=M
            @LCL
            M=D
            @{fn}
            0;JMP
            ({return_label})
            """)

    def write_return(self):
        """
        Return to the calling function
        """

        self.write("""
            @LCL
            D=M
            @FRAME
            M=D
            @5
            A=D-A
            D=M
            @RET
            M=D
            @SP
            AM=M-1
            D=M
            @ARG
            A=M
            M=D
            @ARG
            D=M+1
            @SP
            M=D
            """)

        for idx, symbol in enumerate(['THAT', 'THIS', 'ARG', 'LCL']):
            self.write(f"""
                @FRAME
                D=M
                @{idx+1}
                A=D-A
                D=M
                @{symbol}
                M=D
                """)

        self.write(f"""
            @RET
            A=M
            0;JMP
            """)

    def write_function(self, fn, nlocals):
        """
        Write function label and give room for nlocals in stack
        """

        self.write(f'({fn})')

        for _ in range(int(nlocals)):
            self.write_push('constant', '0')

    def write_push_d(self):
        """
        1. *(SP) = D
        2. SP = SP + 1
        """

        self.write("""
            @SP
            A=M
            M=D
            @SP
            M=M+1
            """)

    def write_pop_d(self):
        """
        1. SP = SP - 1
        2. D = *(SP)
        """

        self.write(f"""
            @SP
            AM=M-1
            D=M
            """)

    def get_ram_address(self, segment, index=0):
        """
        Offset the base RAM address of a segment
        """

        if segment in UNKNOWN_SEGMENTS:
            symbol = UNKNOWN_SEGMENTS[segment]
            self.write(f"""
                @{symbol}
                D=M
                @{index}
                D=D+A
                """)

        elif segment in KNOWN_SEGMENTS:
            base = KNOWN_SEGMENTS[segment]
            address = base + int(index)
            self.write(f"""
                @{address}
                D=A""")

    def make_unique_label(self, text='label'):
        self.label_counter += 1
        return f'{text}.{self.label_counter}'
