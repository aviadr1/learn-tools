import shutil
import os
import argparse
from pathlib import Path

import open_from
import questions
import make_toc
import book_fix_filenames

def execute(command):
    print()
    print(command)
    os.system(command)
    print()


def perform(args):

    root = open_from.find_project_root(args['root']).resolve()

    docs = root / 'docs'
    docs_content = docs / 'content'

    current_dir = Path('.').resolve()
    try:
        os.chdir(str(root))

        # pull
        execute('git pull')


        # delete docs/content
        try: 
            shutil.rmtree(str(docs_content))
        except FileNotFoundError:
            pass

        # make nice filenames
        book_fix_filenames.main(content=root / 'content')

        # questions
        questions.perform(args)

        # update open in collab
        open_from.main(root=root)

        # 2. copy content
        shutil.copytree(root / 'content', docs_content)

        # 3. create toc
        execute('jupyter-book toc ' + str(docs))

        # 4. make hierarchial toc
        make_toc.main(root=root)

        # 5. build jupyter-book
        execute('jupyter-book build ' + str(docs))

        # 6. git commit and push
        execute('git add docs/.'  )
        execute('git commit -m "update jupyter-book"' )
        execute('git push')

    finally:
        os.chdir(str(current_dir))

def main():
    parser = argparse.ArgumentParser(description='prepare jupyter-book from site')
    parser.add_argument('--root', default=".", help="root folder for repository")
    questions.add_args(parser)
    args = vars(parser.parse_args())
    perform(args)


if __name__ == '__main__':
    main()