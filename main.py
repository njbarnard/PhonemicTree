from rhymer import Rhymer, PhonemeTrie
from ete4 import Tree
from ete4.smartview import TreeLayout, NodeStyle, TextFace

# Graphical trees created with the help of examples found on the ETE Toolkit documentation:
# https://etetoolkit.github.io/ete/index.html
# (Must download ETE4 and its dependencies to run this code)


def main():

    # Create Rhymer object with CMU Pronunciation Dictionary
    r = Rhymer('cmudict-0.7b', 'cmudict-0.7b.phones')
    print(r.phoneme_trie_size())
    print(r.rhymes("cat"))

    # Select a trie from the Rhymer
    phonemic_end_trie = r.get_end_rhyme_trie()
    # phonemic_end_trie = r.get_start_rhyme_trie()
    # phonemic_end_trie = r.get_end_trie()
    # phonemic_end_trie = r.get_start_trie()

    # Convert the trie to an ETE4 tree for visualization
    interactive_phonemic_tree = trie_to_ete4(phonemic_end_trie)
    print(interactive_phonemic_tree)
    # Format and display the interaction phonemic tree
    layouts = get_trie_layouts()
    interactive_phonemic_tree.explore(include_props=['words'], show_leaf_name=True, keep_server=True, layouts=layouts)


def trie_to_ete4(node, parent=None):
    # Convert a PhonemeTrie to an ETE4 Tree
    if parent is None:
        parent = Tree({'name': 'root'})  # Add the root of the trie
    for val, child_node in node.children.items():
        child_tree = parent.add_child(name=val)
        if len(child_node.words) > 0:
            child_tree.add_props(words=child_node.words)
        trie_to_ete4(child_node, child_tree)  # Recursively add the children
    return parent


def get_trie_layouts():
    # Create a layout for the phonemic tree
    tree_layout = TreeLayout(name="Phonemic Trie Layout")
    # tree_layout = TreeLayout(name="Phonemic Trie Layout", ts=modify_tree_style, ns=modify_node_style)
    return [tree_layout]


def modify_tree_style(tree_style):
    # Modify the style of the tree
    tree_style.mode = 'c'


def modify_node_style(node):
    # Modify the style of the nodes

    # Leaf nodes are cyan, circular (default), and size 60
    leaf_style = NodeStyle()
    leaf_style["fgcolor"] = "cyan"
    leaf_style["size"] = 60

    # The root node are red, circular (default), size 50, and has salmon lines
    root_style = NodeStyle()
    root_style["fgcolor"] = "red"
    root_style["size"] = 40
    root_style["vt_line_type"] = 2
    root_style["vt_line_width"] = 10
    root_style["vt_line_color"] = "#FF8C69"

    # Modify the nodes according to their type
    if node.is_leaf:
        node.set_style(leaf_style)
        # if len(node.words) > 0:
        # node.add_face(TextFace(node.words[0], color="blue"), column=0, position='branch_bottom')
    elif node.is_root:
        node.set_style(root_style)
    else:
        pass
    return


if __name__ == '__main__':
    main()
