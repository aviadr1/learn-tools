import os
from pathlib import Path


def find_content_root(start_dir='.'):
    p = Path(start_dir).resolve()
    while p != p.parent:
        config = p / "_config.yml"
        if config.exists() :
            content = p / "content"
            
            print("config:", config)
            print("content:", content)

            assert content.exists()
            assert content.is_dir()
            return content
        p = p.parent
        
    raise FileNotFoundError('not inside a content folder', Path(start_dir).resolve())


def is_dot_folder(folder):
    return any([part.startswith('.') for part in folder.parts])
        

def find_all_notebooks(root):
    #root = find_content_root(start_dir)
    return (file for file in root.glob('**/*.ipynb') if not is_dot_folder(file.parent))


def fix_filename(filename):
    stem = str(filename.stem)
    trans = str.maketrans(' .,[]()', '_______', '')
    stem = stem.translate(trans)
    stem = stem.replace('_-', '-').replace('-_', '-').replace('__', '_')
    return filename.with_name(stem).with_suffix(filename.suffix)


def make_toc(site_root):
    _build = site_root / '_build'
    assert data.exists()
    assert data.is_dir()

    



def main(content=None):
    #parser = argparse.ArgumentParser(description='fix filenames for jupyter-book support')
    #args = vars(parser.parse_args())
    if not content: 
        try:
            content = find_content_root(content)
        except FileNotFoundError:
            content = Path('.').resolve()
            print('not inside content folder, use current folder',  content, '?' )
            if input('Y/N:').upper() != 'Y':
                raise
    else:
        content = Path(content).resolve()
        print(content)
        assert content.exists()
        assert content.is_dir()

    notebooks = find_all_notebooks(content)
    for nb in notebooks:
        fixed_nb = fix_filename(nb)
        if fixed_nb != nb:
            print (nb, '-->>', fixed_nb)
            os.rename(nb, fixed_nb)



if __name__ == '__main__':
    main()