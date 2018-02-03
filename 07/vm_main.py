import os
import sys

from vm_parser import Parser
from vm_translator import Translator


if __name__ == '__main__':
    inpath = os.path.abspath(sys.argv[1])
    outpath = inpath.split('.')[0] + '.asm'
    filename = inpath.split('.')[0].split('/')[-1]

    with open(inpath, 'r') as infile:
        lines = infile.readlines()
        parser = Parser(lines)
    
    translator = Translator(filename)

    while parser.has_more_commands():
        cmd = parser.advance()
        cmd_type = parser.get_cmd_type()
        translator.write(cmd_type, cmd)

    translator.close()

    with open(outpath, 'w') as outfile:
        outfile.write(translator.translation)
