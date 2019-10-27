import oyaml as yaml
from copy import deepcopy
from collections import defaultdict
from pprint import pprint
from pathlib import Path
import os

def get_children(node, path="/"):
    if isinstance(node, list):
        for subnode in node:
            yield from get_children(subnode, path)
         
    elif isinstance(node,dict):
        mypath = path
        if node.get('title'):
            mypath += node['title'] + '/'
            #print(3, mypath)
            yield (mypath, node) 

        for name, subnode in node.items():
            yield from get_children(subnode, mypath + name + '/')


def build_tree(toc):
    
    def get_subsection(level):
        return "sub" * level + "sections"

    def put(tree, path, node, level):
        if len(path) == 1:
            #print('node:', node)
            tree[path[0]] = node
        else:
            #print(path[0])
            subtree = tree.setdefault(path[0], { 'title' : path[0].replace('_', ' ')})
            put(subtree.setdefault(get_subsection(level), {}), path[1:], node, level+1)

    tree_toc = {}
    for node in toc:
        if 'url' not in node:
            print(node)
            continue
        url = node['url'].split('/')[1:]
        # print(url)
        put(tree_toc, url, node, 0)

    # cleanup
    for path, child in get_children(tree_toc):
        for key in [key for key in child.keys() if key.endswith('sections')]:
            if isinstance(child[key], dict):
                # print(10, path, key, dict)
                child[key] = list(child[key].values())

    tree_toc = list(tree_toc.values())
    
    return tree_toc


def find_first(node, attribute):
    for path, child in get_children(node):
        if child.get(attribute):
            return (child, child.get(attribute))

def build_urls(tree_toc):
    for path, child in get_children(tree_toc):
        # child['not_numbered'] = True
        if not child.get('url'):
            child['url'] = find_first(child, 'url')[1]
            # child['expand_sections'] = True
            
def main(root = '.'):
    root = Path(root)
    tocfile = root / 'docs' / '_data' / 'toc.yml'

    with open(tocfile) as fin:
        toc = yaml.safe_load(fin)
    tree_toc = build_tree(toc)

    #print(get_children(tree_toc))
    build_urls(tree_toc)
    tmpfile = tocfile.with_name('toc.urls')
    with open(tmpfile, 'w') as fout:
        yaml.dump(tree_toc, fout)

    os.rename(tocfile, tocfile.with_suffix('.bak.yml'))
    os.rename(tmpfile, tocfile)

