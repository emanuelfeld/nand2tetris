COMP_BIN = {
    '0':   '0101010',
    '1':   '0111111',
    '-1':  '0111010',
    'D':   '0001100',
    'A':   '0110000',
    '!D':  '0001101',
    '!A':  '0110001',
    '-D':  '0001111',
    '-A':  '0110011',
    'D+1': '0011111',
    'A+1': '0110111',
    'D-1': '0001110',
    'A-1': '0110010',
    'D+A': '0000010',
    'D-A': '0010011',
    'A-D': '0000111',
    'D&A': '0000000',
    'D|A': '0010101',
    'M':   '1110000',
    '!M':  '1110001',
    '-M':  '1110011',
    'M+1': '1110111',
    'M-1': '1110010',
    'D+M': '1000010',
    'D-M': '1010011',
    'M-D': '1000111',
    'D&M': '1000000',
    'D|M': '1010101'
}


DEST_BIN = {
    '':    '000',
    'M':   '001',
    'D':   '010',
    'MD':  '011',
    'A':   '100',
    'AM':  '101',
    'AD':  '110',
    'AMD': '111'
}


JUMP_BIN = {
    '':    '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}


DEFAULT_SYMBOL_TABLE = {
    'SP':     0,
    'LCL':    1,
    'ARG':    2,
    'THIS':   3,
    'THAT':   4,
    'R0':     0,
    'R1':     1,
    'R2':     2,
    'R3':     3,
    'R4':     4,
    'R5':     5,
    'R6':     6,
    'R7':     7,
    'R8':     8,
    'R9':     9,
    'R10':    10,
    'R11':    11,
    'R12':    12,
    'R13':    13,
    'R14':    14,
    'R15':    15,
    'SCREEN': 16384,
    'KBD':    24576
}


class Translator:
    def __init__(self):
        self.symbol_table = DEFAULT_SYMBOL_TABLE
        self.translated = ''
        self.next_rom_address = 0
        self.next_ram_address = 16

    def write_binary(self, instr_type, kwargs):
        """
        Returns binarized A- and C-instructions
        """
        
        def convert_decimal(n):
            return bin(n)[2:].zfill(16)

        def convert_c_instruction(comp, dest, jump):
            return '111' + COMP_BIN[comp] + DEST_BIN[dest] + JUMP_BIN[jump]

        if instr_type == 'c':
            return convert_c_instruction(**kwargs)
        elif instr_type == 'a-decimal':
            dec_address = int(kwargs['value'])
            return convert_decimal(dec_address)
        elif instr_type == 'a-symbol':
            symbol = kwargs['symbol']
            dec_address = self.symbol_table[symbol]
            return convert_decimal(dec_address)

    def assign_label_address(self, instr_type, kwargs):
        """
        Adds ROM address to symbol table if program label
        """
        
        if instr_type == 'l':
            label = kwargs['symbol']
            self.symbol_table[label] = self.next_rom_address
        else:
            self.next_rom_address += 1

    def assign_symbol_address(self, instr_type, kwargs):
        """
        Adds RAM addresses to symbol table if new A-instruction symbol
        Converts instruction to binary, if not label
        """
        
        if instr_type == 'a-symbol':
            symbol = kwargs['symbol']
            if symbol not in self.symbol_table:
                self.symbol_table[symbol] = self.next_ram_address
                self.next_ram_address += 1

        if instr_type != 'l':
            hack = self.write_binary(instr_type, kwargs)
            self.translated += hack + '\n'
