import os
import sys

from vm_parser import Parser
from vm_translator import Translator


import glob, os

if __name__ == '__main__':
    inpath = os.path.abspath(sys.argv[1])

    if os.path.isfile(inpath):
        vmfiles = [inpath]
        outdir = vmfiles[0].rsplit('/', 1)[0]
        outfilename = vmfiles[0].rsplit('/', 1)[-1].split('.vm')[0]
    else:
        vmfiles = [inpath + '/' + f for f in os.listdir(inpath) if f.endswith('.vm')]
        outdir = vmfiles[0].rsplit('/', 1)[0]
        outfilename = outdir.rsplit('/', 1)[-1]

    outpath =  outdir + '/' + outfilename + '.asm'

    translator = Translator()

    if len(sys.argv) == 3 and sys.argv[2] == '--init':
        translator.write_init()

    for file in vmfiles:
        filename = file.rsplit('.vm', 1)[0].rsplit('/', 1)[-1]
        translator.set_filename(filename)
        with open(file, 'r') as infile:
            lines = infile.readlines()
            parser = Parser(lines)
        
        while parser.has_more_commands():
            cmd = parser.advance()
            cmd_type = parser.get_cmd_type()
            translator.translate(cmd_type, cmd)

    translator.close()

    with open(outpath, 'w') as outfile:
        outfile.write(translator.translation)
