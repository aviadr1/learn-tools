import nbformat
import glob
import argparse
import re
from pathlib import Path

def convert(solutions_file, questions_file, magic):
    nb = nbformat.read(solutions_file, as_version=4)

    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue

        is_part_of_question = False
        content = cell['source']
        for line in content.splitlines():                
            match = re.search(magic, line)
            if match is not None:
                print('\t', line)
                is_part_of_question = True
                break

        if not is_part_of_question:
            cell['source'] = ""

    # change the 'name' of the notebook to 
    colab_metadata = nb.setdefault('metadata', {}).setdefault('colab', {})
    colab_metadata['name'] = str(Path(questions_file).name)

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