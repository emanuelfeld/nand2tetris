import os
import subprocess
import sys

from jack_tokenizer import Tokenizer
from jack_engine import Engine


def compare_output(file1, file2):
    """
    Compare files line by line, ignoring whitespace
    """
    output = subprocess.getoutput(f"diff -u -b {file1} {file2} | sed -n '12d;/^[-+]/p'")

    if not output.strip():
        name = file1.rsplit('/', 1)[-1]
        print('Equivalent:', name)
    else:
        print(output)


if __name__ == '__main__':
    INPATH = os.path.abspath(sys.argv[1])

    if os.path.isfile(INPATH):
        assert INPATH.endswith('.jack')
        INFILES = [INPATH]
    else:
        INFILES = [INPATH + '/' + f for f in os.listdir(INPATH) if f.endswith('.jack')]

    TEST_DIR = INFILES[0].rsplit('/', 1)[0]
    OUT_DIR = TEST_DIR + '-cmp'

    for file in INFILES:
        filename = file.rsplit('/', 1)[-1].split('.jack')[0]
        parser_outpath = OUT_DIR + '/' + filename + '.xml'
        tokenizer_outpath = OUT_DIR + '/' + filename + 'T.xml'
        parser_outpath_test = TEST_DIR + '/' + filename + '.xml'
        tokenizer_outpath_test = TEST_DIR + '/' + filename + 'T.xml'

        with open(file, 'r') as infile:
            lines = infile.readlines()
            tokenizer = Tokenizer(lines)

        tokenizer.run()

        with open(tokenizer_outpath, 'w') as outfile:
            outfile.write('\n'.join(tokenizer.xml))

        compare_output(tokenizer_outpath_test, tokenizer_outpath)

        engine = Engine(tokenizer.tokens)
        engine.compile_class()

        with open(parser_outpath, 'w') as outfile:
            outfile.write('\n'.join(engine.xml))

        compare_output(parser_outpath_test, parser_outpath)
