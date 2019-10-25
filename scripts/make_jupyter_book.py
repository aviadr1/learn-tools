import shutil
import sys
import os
import argparse
from pathlib import Path

import open_from
import questions
import make_toc
import book_fix_filenames

CONTENT_FOLDER = "content"
DOCS_FOLDER = "docs"

def execute(command, failfast=True):
    print(flush=True)
    print(command, flush=True)
    status = os.system(command)
    print(flush=True)

    if failfast and status != 0:
        raise RuntimeError("The command returned status", status, command)

    return status

def is_verbose(verbose):
    return " --verbose" if verbose else ""


def header(comment):
    print()
    print(comment)
    print('-' * 10)


def perform(args):

    verbose = args['verbose']
    failfast = args['failfast']
    root = open_from.find_project_root(args['root']).resolve()

    docs = root / DOCS_FOLDER
    docs_content = docs / CONTENT_FOLDER

    current_dir = Path('.').resolve()
    try:
        print("project root:", root)
        os.chdir(str(root))

        try:
            ### see: https://stackoverflow.com/questions/5139290/how-to-check-if-theres-nothing-to-be-committed-in-the-current-branch
            # prevent running if there are local unstaged changes
            execute('git diff --exit-code' + is_verbose(verbose), failfast)
            # prevent running if there are changes that are staged but not committed
            execute('git diff --cached --exit-code' + is_verbose(verbose), failfast)
            # prevent untracked files in your content working tree that aren't ignored
            execute(f'git ls-files {CONTENT_FOLDER} --other --exclude-standard --directory' + is_verbose(verbose), failfast)
            
        except RuntimeError as ex:
            print("PLEASE FIX: there are local git changes", ex, file=sys.stderr)
            sys.exit(1)

        # pull
        execute('git pull' + is_verbose(verbose), failfast)

        # delete docs/content
        try: 
            shutil.rmtree(str(docs_content))
        except FileNotFoundError:
            pass

        header("make nice filenames")
        book_fix_filenames.main(content=root / CONTENT_FOLDER)

        header("convert solutions to questions")
        questions.perform(args)

        # update open in collab
        header("update open in collab")
        open_from.main(root=root)

        # 2. copy content
        header("copying content and running jupyter-book")
        shutil.copytree(root / CONTENT_FOLDER, docs_content)

        # 3. create toc
        execute(f'jupyter-book toc {docs}')

        # 4. make hierarchial toc
        make_toc.main(root=root)

        # 5. build jupyter-book
        execute(f'jupyter-book build --overwrite {docs}', failfast)

        # 6. git commit and push
        header("git commit and push")
        execute(f'git add {CONTENT_FOLDER}/.' + is_verbose(verbose), failfast)
        execute(f'git add {DOCS_FOLDER}/.' + is_verbose(verbose), failfast)
        ### see https://stackoverflow.com/questions/8123674/how-to-git-commit-nothing-without-an-error
        any_changes = execute('git diff-index --quiet HEAD', failfast=False)
        if any_changes != 0:
            execute('git commit -m "update jupyter-book"' + is_verbose(verbose), failfast)
            execute('git push' + is_verbose(verbose), failfast)
        else:
            print('nothing to commit or push')

    finally:
        os.chdir(str(current_dir))

def main():
    parser = argparse.ArgumentParser(description='prepare jupyter-book from site')
    parser.add_argument('--root', default=".", help="root folder for repository")
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--no-failfast', dest="failfast", action='store_false')
    questions.add_args(parser)
    args = vars(parser.parse_args())
    perform(args)


if __name__ == '__main__':
    main()
