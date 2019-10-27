from pathlib import Path
import nbformat
import urllib.parse
import traceback


GITHUB_BASE = 'https://github.com/'
COLAB_BASE = "https://colab.research.google.com/github/"
GITHUB_POSTFIX = ".git"


def find_project_root(start_dir='.'):
    p = Path(start_dir).resolve()
    while p != p.parent:
        git = p / ".git"
        if git.exists() and git.is_dir():
            return p
        p = p.parent
        
    raise FileNotFoundError('not inside a repository', Path(start_dir).resolve())


def is_dot_folder(folder):
    return any([part.startswith('.') for part in folder.parts])


def find_all_notebooks(start_dir='.'):
    root = find_project_root(start_dir)
    return (file for file in root.glob('**/*.ipynb') if not is_dot_folder(file.parent))


def get_colab_base_url(project_root):
    from git import Repo
    repo = Repo(project_root)
    assert not repo.bare
        
    github_url = repo.remotes.origin.url
    # print(github_url)
    assert github_url.startswith(GITHUB_BASE)
    assert github_url.endswith(GITHUB_POSTFIX)
    
    github_url_part = github_url[len(GITHUB_BASE):-len(GITHUB_POSTFIX)] + '/'
    # print(github_url_part)
    
    colab_github_url = urllib.parse.urljoin(COLAB_BASE, github_url_part)
    colab_github_url = urllib.parse.urljoin(colab_github_url, 'blob/master/')
    # print(colab_github_url)
    return colab_github_url


def get_colab_url(notebook_filename, project_root, colab_github_url):   
    relative_filename = Path(notebook_filename).resolve().relative_to(Path(project_root).resolve())
    # print(relative_filename)
    relative_url = urllib.parse.quote(relative_filename.as_posix())
    # print(relative_url)

    full_url = urllib.parse.urljoin(colab_github_url, relative_url)
    return full_url


OPEN_IN_COLAB_MARKDOWN = """
"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({})"
"""

OPEN_IN_COLAB_HTML = """
<a href="{}" target="_blank">
<img src="https://colab.research.google.com/assets/colab-badge.svg" 
     title="Open this file in Google Colab" alt="Colab"/>
</a>
"""

def ensure_colab_button(notebook_filename, project_root, colab_github_url):
    with open(notebook_filename, encoding='utf8') as fin:
        nb = nbformat.read(fin, nbformat.NO_CONVERT)

    cell0 = nb['cells'][0]
    colab_url = get_colab_url(notebook_filename, project_root, colab_github_url)
    button = OPEN_IN_COLAB_HTML.format(colab_url)
    rewrite = False
    if not COLAB_BASE in cell0['source']:
        # add colab button
        colab_cell = nbformat.v4.new_markdown_cell(button)
        nb['cells'].insert(0, colab_cell)
        rewrite = True
    elif cell0['source'] != button:
        DEBUG = True
        if DEBUG:
            import difflib
            print(
                [f"pos {i} {li}"
                 for i, li in enumerate(difflib.ndiff(cell0['source'], button))
                 if li[0] != ' '
                ])

        cell0['source'] = button
        rewrite = True

    if rewrite:
        with open(notebook_filename, "w", encoding="utf8") as f:
            print("adding colab to", notebook_filename)
            nbformat.write(nb, f)



def main(root='.'):
    root = find_project_root(root)
    print('project root:', root)

    notebooks = find_all_notebooks(root)
    colab_base_url = get_colab_base_url(root)
    print('colab:', colab_base_url)
    print()

    for notebook in notebooks:
        print(notebook)
        try:
            ensure_colab_button(notebook, root, colab_base_url)
        except Exception:
            print('\tXXX')
            traceback.print_exc()


if __name__ == '__main__':
    main()