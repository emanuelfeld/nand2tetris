import os
import sys

from asm_parser import Parser
from asm_translator import Translator


if __name__ == '__main__':
    inpath = os.path.abspath(sys.argv[1])
    outpath = inpath.split('.')[0] + '.hack'

    with open(inpath, 'r') as infile:
        lines = infile.readlines()
        parser = Parser(lines)

    parser.parse()
    translator = Translator()

    for instr_type, kwargs in parser.parsed:
        translator.assign_label_address(instr_type, kwargs)

    for instr_type, kwargs in parser.parsed:
        translator.assign_symbol_address(instr_type, kwargs)

    with open(outpath, 'w') as outfile:
        outfile.write(translator.translated)
