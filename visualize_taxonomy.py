#!/usr/bin/env python3
"""
Taxonomy Hierarchy Visualizer for Presentations (Grouped Papers)

Dependencies:
    pip install graphviz
    # Also install Graphviz system package (e.g., sudo apt install graphviz)

Usage:
    python visualize_taxonomy_grouped.py

Reads 'taxonomy.json' and groups papers under their final category into a single node.
"""
import json
from graphviz import Digraph

# A vibrant color palette suitable for presentations
TOP_LEVEL_COLORS = ['#ffbe0b', '#fb5607', '#ff006e', '#8338ec', '#3a86ff', '#43aa8b']
OUTPUT_FILENAME = 'taxonomy_grouped.png'

def load_taxonomy(filename="taxonomy.json"):
    """Loads the taxonomy data from a JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

def add_nodes_edges(dot, node, parent=None, color=None):
    """
    Recursively adds nodes and edges to the graph.
    If a node contains a 'papers' list, it's treated as a single, formatted leaf node.
    """
    node_id = str(id(node))
    
    # If the node is a final category with papers, create one grouped node
    if 'papers' in node:
        # Format the label with the category name and a bulleted list of papers.
        # The '\l' escape character creates left-justified newlines.
        paper_list = [f"• {p}\\l" for p in node['papers']]
        label = f"**{node['name']}**\\n\\n" + "".join(paper_list) # Use ** for bold in some renderers, or just for emphasis
        label = f"{node['name']}\\l\\l" + "".join(paper_list)


        node_kwargs = {
            'label': label,
            'shape': 'box',
            'style': 'filled,rounded',
            'fillcolor': color or '#f0f0f0',
            'fontname': 'Arial',
            'align': 'left' # Crucial for left-justified text
        }
        dot.node(node_id, **node_kwargs)

    # If it's a regular intermediate category, process it and its children
    else:
        node_kwargs = {
            'label': node['name'],
            'color': color or '#cccccc',
            'style': 'filled',
            'fillcolor': color or '#cccccc'
        }
        dot.node(node_id, **node_kwargs)
        if 'children' in node:
            for child in node['children']:
                # Pass the parent's color down to the children
                add_nodes_edges(dot, child, node_id, color)

    if parent:
        dot.edge(parent, node_id)


def main():
    """Main function to generate the taxonomy graph."""
    try:
        data = load_taxonomy()
    except FileNotFoundError:
        print(f"Error: 'taxonomy.json' not found. Please create this file.")
        return
        
    output_format = OUTPUT_FILENAME.split('.')[-1]
    dot = Digraph(format=output_format, graph_attr={'splines': 'ortho'})
    dot.attr(rankdir='TB')  # Top-to-Bottom layout
    dot.attr('node', 
             shape='box', 
             style='rounded,filled', 
             fontname='Arial', 
             fontsize='10',
             margin='0.25') # Increased margin for readability
    dot.attr('edge', arrowhead='vee', arrowsize='0.7')
    
    # Style for the root node
    root_id = str(id(data))
    dot.node(root_id, 
             label=data['name'], 
             shape='box', 
             style='filled,bold', 
             fillcolor='#003049', 
             fontcolor='white',
             fontsize='12')
             
    if 'children' in data:
        for idx, child in enumerate(data['children']):
            color = TOP_LEVEL_COLORS[idx % len(TOP_LEVEL_COLORS)]
            # The top-level nodes are intermediate, so they are drawn first
            top_level_id = str(id(child))
            dot.node(top_level_id, label=child['name'], fillcolor=color)
            dot.edge(root_id, top_level_id)
            # Process the children of the top-level nodes
            if 'children' in child:
                 for sub_child in child['children']:
                     add_nodes_edges(dot, sub_child, top_level_id, color)
            # If the top-level node has papers directly
            elif 'papers' in child:
                add_nodes_edges(dot, child, root_id)


            
    # Render the graph
    output_base = OUTPUT_FILENAME.split('.')[0]
    dot.render(output_base, view=False, cleanup=True)
    print(f"Grouped taxonomy graph saved to {output_base}.{output_format}")

if __name__ == '__main__':
    main()