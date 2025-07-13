#!/usr/bin/env python3
"""
Taxonomy Hierarchy Visualizer (Final Slide Version)

Dependencies:
    pip install graphviz
    # Also install Graphviz system package (e.g., sudo apt install graphviz)

Usage:
    python visualize_taxonomy_final.py
"""
import json
from graphviz import Digraph

# Colors are now mapped to specific categories for consistency
COLOR_MAP = {
    "Survey": "#8ecae6",
    "LLM as Heuristic": "#ffb703",
    "Foundational": "#adb5bd",
    "Task Decomposition": "#a9c9b4",
    "LLM as Modeler": "#f28482",
    "LLM-based Agents": "#bde0fe"
}
OUTPUT_FILENAME = 'taxonomy_final.png'

def load_taxonomy(filename="taxonomy.json"):
    """Loads the taxonomy data from a JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

def add_nodes_edges(dot, node, parent_id, parent_color=None):
    """
    Recursively adds nodes and edges to the graph.
    - Separates category nodes from leaf nodes containing paper lists.
    - Handles nested structures and applies consistent coloring.
    """
    node_id = str(id(node))
    node_name = node['name']
    # Use parent's color if available, otherwise get from COLOR_MAP
    color = COLOR_MAP.get(node_name) or parent_color

    # Case 1: Node is a category with papers.
    # Draw the category node, then a separate leaf node for the papers.
    if 'papers' in node:
        # Draw the category node
        dot.node(node_id, label=node_name, fillcolor=color or "#ffffff")
        dot.edge(parent_id, node_id)
        
        # Create a new leaf node just for the papers
        papers_node_id = f"papers_{node_id}"
        paper_list = [f"• {p}\\l" for p in node['papers']]
        papers_label = "".join(paper_list)
        
        dot.node(papers_node_id, 
                 label=papers_label, 
                 shape='note',
                 fillcolor="#f8f9fa",
                 fontname='Arial',
                 align='left')
        dot.edge(node_id, papers_node_id)

    # Case 2: Node is an intermediate category with children.
    # Draw it and recurse into its children.
    elif 'children' in node:
        # For the structural nodes ("Foundations & Heuristics", etc.), use a plain style
        style = {'fillcolor': color or '#ffffff', 'style': 'filled,dashed', 'fontstyle': 'italic'} if not COLOR_MAP.get(node_name) else {'fillcolor': color}
        dot.node(node_id, label=node_name, **style)
        dot.edge(parent_id, node_id)
        
        for child in node['children']:
            add_nodes_edges(dot, child, node_id, color)


def main():
    """Main function to generate the final taxonomy graph."""
    try:
        data = load_taxonomy()
    except FileNotFoundError:
        print(f"Error: 'taxonomy.json' not found. Please create this file.")
        return

    output_format = OUTPUT_FILENAME.split('.')[-1]
    dot = Digraph(format=output_format)
    dot.attr(rankdir='LR', splines='ortho', ranksep='0.05', nodesep='0.2')
    dot.attr('node', 
             shape='box', 
             style='rounded,filled', 
             fontname='Arial', 
             fontsize='10',
             margin='0.2')
    dot.attr(concentrate='true')

    dot.attr('edge', arrowhead='vee', arrowsize='0.7')

    # Draw the root node
    root_id = str(id(data))
    dot.node(root_id,
             label=data['name'],
             shape='box',
             style='filled,bold',
             fillcolor='#212529',
             fontcolor='white',
             fontsize='12')

    # Start the recursive drawing process from the root's children
    if 'children' in data:
        for child in data['children']:
            add_nodes_edges(dot, child, root_id, COLOR_MAP.get(data['name']))

    # Render the final graph
    output_base = OUTPUT_FILENAME.split('.')[0]
    dot.render(output_base, view=False, cleanup=True)
    print(f"Final taxonomy graph saved to {output_base}.{output_format}")

if __name__ == '__main__':
    main()