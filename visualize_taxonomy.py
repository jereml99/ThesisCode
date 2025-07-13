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
    "LLM as Preprocessor": "#a9c9b4",
    "LLM as Modeler": "#f28482",
    "Personality": "#bde0fe",
    "LLM as planner": "#e9c46a"  # Added color for new category
}
OUTPUT_FILENAME = 'taxonomy_final.png'

# Maximum number of symbols for node and paper labels
MAX_NODE_LENGTH = 60  
MAX_PAPER_LENGTH = 60  

def load_taxonomy(filename="taxonomy.json"):
    """Loads the taxonomy data from a JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

def truncate_label(text, max_length):
    """
    Truncate text to max_length, adding '...' if needed.
    Always preserve author/date in parentheses at the end for papers.
    """
    if len(text) <= max_length:
        return text
    # For papers, preserve author/date in parentheses at the end
    if '(' in text and text.endswith(')'):
        idx = text.rfind('(')
        main = text[:idx].strip()
        suffix = text[idx:]
        allowed = max_length - len(suffix) - 3  # 3 for '...'
        if allowed < 1:
            # If suffix is too long, just show suffix
            return '...' + suffix
        return main[:allowed] + '...' + suffix
    # For other nodes, just truncate
    return text[:max_length-3] + '...'

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
        label = truncate_label(node_name, max_length=MAX_NODE_LENGTH)
        dot.node(node_id, label=label, fillcolor=color or "#ffffff")
        dot.edge(parent_id, node_id)
        
        # Create a new leaf node just for the papers
        papers_node_id = f"papers_{node_id}"
        paper_list = []
        for p in node['papers']:
            paper_label = truncate_label(p, max_length=MAX_PAPER_LENGTH)
            paper_label = f"• {paper_label}\\l"  # Add bullet point and line break
            paper_list.append(paper_label)
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
        label = truncate_label(node_name, max_length=MAX_NODE_LENGTH)
        # For the structural nodes ("Foundations & Heuristics", etc.), use a plain style
        style = {'fillcolor': color or '#ffffff', 'style': 'filled,dashed', 'fontstyle': 'italic'} if not COLOR_MAP.get(node_name) else {'fillcolor': color}
        dot.node(node_id, label=label, **style)
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
    dot.attr(rankdir='LR', splines='ortho', ranksep='0.05', nodesep='0.2', compound='true')
    dot.attr(strict='false')

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