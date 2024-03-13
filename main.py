from rhymer import Rhymer
from ete4 import Tree
from ete4.smartview import TreeLayout, TextFace

# Graphical trees created with the help of examples found on the ETE Toolkit documentation:
# https://etetoolkit.github.io/ete/index.html
# (Must download ETE4 and its dependencies to run this code)

# Create Rhymer object with CMU Pronunciation Dictionary
r = Rhymer('cmudict-0.7b', 'cmudict-0.7b.phones')
ete4_id = 0  # Global counter to generate unique IDs for nodes


def main():

    # Get all phonemic tries from the Rhymer
    end_rhyme_trie = r.get_end_rhyme_trie()
    start_rhyme_trie = r.get_start_rhyme_trie()
    end_trie = r.get_end_trie()
    start_trie = r.get_start_trie()

    # Convert the tries to ETE4 trees for visualization
    interactive_phonemic_trees = [trie_to_ete4(end_rhyme_trie), trie_to_ete4(start_rhyme_trie),
                                  trie_to_ete4(end_trie), trie_to_ete4(start_trie)]  # print(interactive_phonemic_trees)

    # Create the layouts for the trees
    default_layout = TreeLayout(name="Default Layout",
                                ts=phoneme_tree_style,
                                ns=phoneme_node_default_layout,
                                active=True,
                                aligned_faces=True)
    word_layout = TreeLayout(name="Word Layout",
                             ts=phoneme_tree_style,
                             ns=phoneme_node_word_layout,
                             active=False,
                             aligned_faces=True)
    aligned_word_layout = TreeLayout(name="Aligned Word Layout",
                                     ts=phoneme_tree_style,
                                     ns=phoneme_node_aligned_word_layout,
                                     active=False,
                                     aligned_faces=True)
    layouts = [default_layout, word_layout, aligned_word_layout]

    # Enter an infinite loop to display the trees and allow the user to change and interact with them
    while True:

        # Display the selected tree
        selected_tree = select_tree()
        interactive_phonemic_trees[selected_tree].explore(include_props=['words', 'phoneme'],
                                                          show_leaf_name=False, keep_server=True, layouts=layouts)

        # Ask the user if they want to continue or quit
        continue_choice = input("Type 'Quit' to exit or press 'Enter' to select another tree: ").strip()
        if continue_choice.lower() == "quit":
            print("Exiting the program. Goodbye!")
            break


def select_tree():
    # Display the available trees and prompt the user to select one
    print("Available trees:")
    print("1. End Rhyme Trie")
    print("2. Start Rhyme Trie")
    print("3. End Trie")
    print("4. Start Trie")
    while True:
        try:
            selection = int(input("Select a tree by entering its number: "))
            if 1 <= selection <= 4:
                return selection - 1
            else:
                print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a valid number.")


def trie_to_ete4(trie_node, ete4_parent=None):
    # Convert a PhonemeTrie to an ETE4 Tree
    if ete4_parent is None:
        ete4_parent = Tree()  # Add the root of the trie
    for trie_val, trie_child in trie_node.children.items():
        global ete4_id
        ete4_id += 1
        ete4_name = f"{trie_val}_{ete4_id}"  # Generate a unique name for the ETE4 node
        ete4_child = ete4_parent.add_child(name=ete4_name)
        ete4_child.add_props(phoneme=trie_val)  # Add the actual phoneme to the ETE4 node
        if len(trie_child.words) > 0:
            ete4_child.add_props(words=trie_child.words)  # Add the words to the ETE4 node
        else:
            ete4_child.add_props(words=[])
        trie_to_ete4(trie_child, ete4_child)  # Recursively add the children
    return ete4_parent


def phoneme_tree_style(tree_style):
    # Set the style for the phoneme trees
    text = TextFace("Phoneme", min_fsize=5, max_fsize=12, width=50, rotation=0)
    tree_style.aligned_panel_header.add_face(text, column=1)
    tree_style.add_legend(
        title="MyLegend",
        variable="discrete",
        colormap={"vowel": "red", "consonant": "blue"}
        )


def phoneme_node_default_layout(node):
    # Set the default layout for the phoneme nodes
    position = 'branch_right'

    if node.is_root:
        node.sm_style['size'] = 5
        node.sm_style['fgcolor'] = 'black'  # Black for the root node
        return

    phoneme = node.props.get('phoneme')
    if r.is_vowel(phoneme):
        if not node.props.get('words'):
            color = '#f96874ff'  # Light red for vowels with no valid words
        else:
            color = 'red'  # Red for vowels with valid words
        node.sm_style['size'] = 5
        node.sm_style['fgcolor'] = color
        node.add_face(TextFace(phoneme, color=color, padding_x=6), column=0, position=position)
    else:
        if not node.props.get('words'):
            color = '#3aafdcff'  # Light blue for consonants with no valid words
        else:
            color = 'blue'  # Blue for consonants with valid words
        node.sm_style['size'] = 5
        node.sm_style['fgcolor'] = color
        node.add_face(TextFace(phoneme, color=color, padding_x=6), column=0, position=position)


def phoneme_node_word_layout(node):
    # Set the word layout for the phoneme nodes
    position = 'branch_right'

    if node.is_root:
        node.sm_style['size'] = 5
        node.sm_style['fgcolor'] = 'black'  # Black for the root node
        return

    phoneme = node.props.get('phoneme')
    if r.is_vowel(phoneme):
        if not node.props.get('words'):
            color = '#f96874ff'  # Light red for vowels with no valid words
        else:
            color = 'red'  # Red for vowels with valid words
            words = ', '.join(node.props.get('words'))
            # Display the valid word list at the bottom of each vowel leaf node's branch
            node.add_face(TextFace(words, color=color, padding_x=6), column=0, position='branch_bottom')
        node.sm_style['size'] = 5
        node.sm_style['fgcolor'] = color
        node.add_face(TextFace(phoneme, color=color, padding_x=6), column=0, position=position)
    else:
        if not node.props.get('words'):
            color = '#3aafdcff'  # Light blue for consonants with no valid words
        else:
            color = 'blue'  # Blue for consonants with valid words
            words = ', '.join(node.props.get('words'))
            # Display the valid word list at the bottom of each consonant leaf node's branch
            node.add_face(TextFace(words, color=color, padding_x=6), column=0, position='branch_bottom')
        node.sm_style['size'] = 5
        node.sm_style['fgcolor'] = color
        node.add_face(TextFace(phoneme, color=color, padding_x=6), column=0, position=position)


def phoneme_node_aligned_word_layout(node):
    # Set the aligned word layout for the phoneme nodes
    position = 'branch_right'

    if node.is_root:
        node.sm_style['size'] = 5
        node.sm_style['fgcolor'] = 'black'  # Black for the root node
        return

    phoneme = node.props.get('phoneme')
    if r.is_vowel(phoneme):
        if not node.props.get('words'):
            color = '#f96874ff'  # Light red for vowels with no valid words
        else:
            color = 'red'  # Red for vowels with valid words
            if node.is_leaf:
                words = ', '.join(node.props.get('words'))
            else:
                words = ' '
            # Display the valid word list to the right of vowel leaf nodes
            node.add_face(TextFace(words, color=color), column=1, position=position)
        node.sm_style['size'] = 5
        node.sm_style['fgcolor'] = color
        node.add_face(TextFace(phoneme, color=color, padding_x=6), column=0, position=position)
    else:
        if not node.props.get('words'):
            color = '#3aafdcff'  # Light blue for consonants with no valid words
        else:
            color = 'blue'  # Blue for consonants with valid words
            if node.is_leaf:
                words = ', '.join(node.props.get('words'))
            else:
                words = ' '
            # Display the valid word list to the right of consonant leaf nodes
            node.add_face(TextFace(words, color=color), column=1, position=position)
        node.sm_style['size'] = 5
        node.sm_style['fgcolor'] = color
        node.add_face(TextFace(phoneme, color=color, padding_x=6), column=0, position=position)


if __name__ == '__main__':
    main()
