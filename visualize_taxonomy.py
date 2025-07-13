#!/usr/bin/env python3
"""
Taxonomy Hierarchy Visualizer for Presentations

Dependencies:
    pip install graphviz
    # Also install Graphviz system package (e.g., sudo apt install graphviz)

Usage:
    python visualize_taxonomy_slide.py

Reads 'taxonomy.json' in the current directory and outputs 'taxonomy_slide.png'.
The JSON labels for papers should include titles and authors for rendering.
"""
import json
from graphviz import Digraph

# A vibrant color palette suitable for presentations
TOP_LEVEL_COLORS = ['#ffbe0b', '#fb5607', '#ff006e', '#8338ec', '#3a86ff', '#43aa8b']
LEAF_SHAPE = 'ellipse'
LEAF_STYLE = 'italic'
LEAF_COLOR = "#01080f"
OUTPUT_FILENAME = 'taxonomy_slide.png'

def load_taxonomy(filename="taxonomy.json"):
    """Loads the taxonomy data from a JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

def add_nodes_edges(dot, node, parent=None, color=None):
    """Recursively adds nodes and edges to the graph."""
    name = node['name']
    node_id = str(id(node))
    is_leaf = 'children' not in node or not node['children']
    
    node_kwargs = {'label': name}
    if color:
        node_kwargs['color'] = color
        node_kwargs['style'] = 'filled'
        node_kwargs['fillcolor'] = color
    
    if is_leaf:
        node_kwargs['shape'] = LEAF_SHAPE
        node_kwargs['fontcolor'] = LEAF_COLOR
        node_kwargs['fontname'] = 'italic'
        node_kwargs['fillcolor'] = '#ffffff' # White fill for leaves
        node_kwargs['color'] = color or '#cccccc'

    dot.node(node_id, **node_kwargs)
    
    if parent:
        dot.edge(parent, node_id)
        
    if 'children' in node:
        for child in node['children']:
            add_nodes_edges(dot, child, node_id, color)

def main():
    """Main function to generate the taxonomy graph."""
    try:
        data = load_taxonomy()
    except FileNotFoundError:
        print(f"Error: 'taxonomy.json' not found. Please create this file.")
        return
        
    output_format = OUTPUT_FILENAME.split('.')[-1]
    dot = Digraph(format=output_format)
    dot.attr(rankdir='TB')  # Top-to-Bottom layout
    dot.attr('node', 
             shape='box', 
             style='rounded,filled', 
             fontname='Arial', 
             fontsize='10',  # Reduced font size
             margin='0.15') # Reduced node margin
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
            add_nodes_edges(dot, child, root_id, color)
            
    # Render the graph
    output_base = OUTPUT_FILENAME.split('.')[0]
    dot.render(output_base, view=False, cleanup=True)
    print(f"Taxonomy graph saved to {output_base}.{output_format}")

if __name__ == '__main__':
    main()