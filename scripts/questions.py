import nbformat
import glob
import argparse
import re


def convert(solutions_file, questions_file, magic):
    nb = nbformat.read(solutions_file, nbformat.NO_CONVERT)
    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue

        lines = cell['source']
        match = re.search(magic, lines, re.MULTILINE)
        if match is not None:
            print('\t', match)
            continue

        cell['source'] = ""


    with open(questions_file, "w", encoding="utf8") as questions:
        nbformat.write(nb, questions)

def perform(args):
    for solutions_file in glob.glob(args['files'], recursive=True):
        questions_file = re.sub(args['from'], args['to'], solutions_file)
        print(solutions_file, '-->', questions_file)
        convert(solutions_file, questions_file, args['magic'])


def add_args(parser):
    parser.add_argument('--files', default="**/solutions.ipynb", help="glob pattern for solution files. \n(default: %(default)r)")
    parser.add_argument('--from', default="solutions", help="regex to search for replacable strings in file name. \n(default: %(default)r)" )
    parser.add_argument('--to', default="questions", help="regex to replace strings in file name. \n(default: %(default)r)" )
    parser.add_argument('--magic', default='###[#  \t]*useful', help='regex to locate code that should be kept')


def main():
    parser = argparse.ArgumentParser(description='create juypter notebook question files from notebook solution files')
    add_args(parser)
    args = vars(parser.parse_args())
    perform(args)


if __name__ == '__main__':
    main()    