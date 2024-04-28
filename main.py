
from rhymer import Rhymer
from ete4 import Tree
from ete4.smartview import TreeLayout, TextFace
import networkx as nx
from nltk.metrics.distance import edit_distance

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

    # Convert full tries to NetworkX graphs for path finding
    start_graph = trie_to_networkx(start_trie)
    end_graph = trie_to_networkx(end_trie)

    # print_all_networkx_nodes(start_graph)
    # print_all_networkx_nodes(end_graph)
    num_nodes = start_graph.number_of_nodes()
    print("[START] Initial number of nodes:", num_nodes)
    num_nodes = end_graph.number_of_nodes()
    print("[END] Initial number of nodes:", num_nodes)
    num_edges = start_graph.number_of_edges()
    print("[START] Initial number of edges:", num_edges)
    num_edges = end_graph.number_of_edges()
    print("[END] Initial number of edges:", num_edges)

    # Connect words that are one edit distance away in the graph
    connect_words_by_edit_distance(start_graph)
    connect_words_by_edit_distance(end_graph)

    # print_all_networkx_nodes(start_graph)
    # print_all_networkx_nodes(end_graph)
    num_nodes = start_graph.number_of_nodes()
    print("[START] Middle number of nodes:", num_nodes)
    num_nodes = end_graph.number_of_nodes()
    print("[END] Middle number of nodes:", num_nodes)
    num_edges = start_graph.number_of_edges()
    print("[START] Middle number of edges:", num_edges)
    num_edges = end_graph.number_of_edges()
    print("[END] Middle number of edges:", num_edges)

    # Remove nodes without words from the graph
    remove_nodes_without_words(start_graph)
    remove_nodes_without_words(end_graph)

    # print_all_networkx_nodes(start_graph)
    # print_all_networkx_nodes(end_graph)
    num_nodes = start_graph.number_of_nodes()
    print("[START] End number of nodes:", num_nodes)
    num_nodes = end_graph.number_of_nodes()
    print("[END] End number of nodes:", num_nodes)
    num_edges = start_graph.number_of_edges()
    print("[START] End number of edges:", num_edges)
    num_edges = end_graph.number_of_edges()
    print("[END] End number of edges:", num_edges)

    print_all_networkx_nodes(start_graph)
    print_all_networkx_nodes(end_graph)

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
        if len(str(selected_tree)) == 1:
            interactive_phonemic_trees[selected_tree].explore(include_props=['words', 'phoneme'],
                                                              show_leaf_name=False, keep_server=True, layouts=layouts)
        # Find the shortest path between two words
        else:
            words = selected_tree.split()
            word1, word2 = words
            print(f"Finding the shortest path between '{word1}' and '{word2}'.")
            print(find_shortest_path_between_words(start_graph, word1, word2))
            print(find_shortest_path_between_words(end_graph, word1, word2))

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
    print("Or enter any two words separated by a space (e.g. 'hello world').")

    while True:
        selection = input("Select a tree by entering its number or two words: ")
        words = selection.strip().split()

        # Check if the user entered a valid number
        if len(words) == 1:
            try:
                val = int(words[0])
                if 1 <= val <= 4:
                    return val - 1  # Return the index (0-based)
                else:
                    print("Invalid selection. Please select a number between 1 and 4.")
            except ValueError:
                print("Invalid input. Please enter a valid number or two words.")

        # Check if the user entered exactly two words
        elif len(words) == 2:
            return ' '.join(words)  # Return the two words as a single string

        # Handle other invalid inputs
        else:
            print("Invalid input. Please enter a number (1-4) or exactly two words.")


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


def trie_to_networkx(trie_node, graph=None, parent_name=None, global_id=0):
    # Convert a PhonemeTrie to a NetworkX Tree
    if graph is None:
        graph = nx.DiGraph()  # Directed graph for trie representation

    # Add the root of the trie
    node_name = f'"root_{global_id}"' if parent_name is None else parent_name
    if parent_name is None:
        graph.add_node(node_name, phoneme="root", words=[])

    # Recursively process and add the children
    for trie_val, trie_child in trie_node.children.items():
        global_id += 1
        safe_trie_val = str(trie_val).replace(':', '\\:')  # Escape problematic characters like ':'
        child_node_name = f'"{safe_trie_val}_{global_id}"'  # Generate a unique name for the NetworkX node
        safe_words = [w.replace(':', '\\:') for w in trie_child.words] if trie_child.words else []
        graph.add_node(child_node_name, phoneme=safe_trie_val, words=safe_words)  # Create node with phoneme & words
        graph.add_edge(node_name, child_node_name)  # Connect the parent and child nodes
        trie_to_networkx(trie_child, graph, child_node_name, global_id)

    return graph


def print_all_networkx_nodes(graph):
    # Print all nodes and their attributes in the NetworkX graph
    for node, attrs in graph.nodes(data=True):
        print(f"Node: {node}, Attributes: {attrs}")


def is_one_edit_away(word1, word2):
    # Check if two words are one edit distance away
    return edit_distance(word1, word2) == 1


def connect_words_by_edit_distance(graph):
    # Connect words that are one edit distance away in the graph
    word_to_nodes = {}  # Gather all words with their corresponding node names
    for node, data in graph.nodes(data=True):
        for word in data.get('words', []):
            if word not in word_to_nodes:
                word_to_nodes[word] = []
            word_to_nodes[word].append(node)

    # Check each unique pair of words
    checked_pairs = set()
    for word1, nodes1 in word_to_nodes.items():
        for word2, nodes2 in word_to_nodes.items():
            if word1 != word2 and (word2, word1) not in checked_pairs:
                if is_one_edit_away(word1, word2):
                    # Connect all corresponding nodes
                    for node1 in nodes1:
                        for node2 in nodes2:
                            graph.add_edge(node1, node2, type='edit_distance_1')
                checked_pairs.add((word1, word2))

    return graph


def remove_nodes_without_words(graph):
    # Remove nodes from the graph that do not have any words
    nodes_to_remove = [node for node, attrs in graph.nodes(data=True) if not attrs.get('words')]
    graph.remove_nodes_from(nodes_to_remove)
    return graph


def find_nodes_by_word(graph, word):
    # Find all nodes in the graph that contain a specific word
    return [node for node, data in graph.nodes(data=True) if word in data.get('words', [])]


def find_shortest_path_between_words(graph, word1, word2):
    # Find the shortest path between two words in the graph
    word1_nodes = find_nodes_by_word(graph, word1)
    word2_nodes = find_nodes_by_word(graph, word2)

    if not word1_nodes or not word2_nodes:
        return f"No nodes found for {'both words' if not word1_nodes and not word2_nodes else word1 if not word1_nodes else word2}."

    try:
        # Find the shortest path between any node from nodes_word1 and any node from nodes_word2
        shortest_paths = []
        for node1 in word1_nodes:
            for node2 in word2_nodes:
                # Use nx.shortest_path to find the shortest path between node1 and node2
                path = nx.shortest_path(graph, source=node1, target=node2)
                shortest_paths.append((path, len(path)))

        # Return the shortest of the found paths
        shortest_path = min(shortest_paths, key=lambda x: x[1])
        return shortest_path[0]
    except nx.NetworkXNoPath:
        return "No path exists between these words."


def phoneme_tree_style(tree_style):
    # Set the style for the phoneme trees
    text = TextFace("Phoneme", min_fsize=5, max_fsize=12, width=50, rotation=0)
    tree_style.aligned_panel_header.add_face(text, column=1)
    tree_style.add_legend(
        title="MyLegend",
        variable="discrete",
        colormap={"vowel": "red", "consonant": "blue"})


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
