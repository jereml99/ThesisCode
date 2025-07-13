#!/usr/bin/env python3
"""
Taxonomy Hierarchy Visualizer

Dependencies:
    pip install graphviz
    # Also install Graphviz system package (e.g., sudo apt install graphviz)

Usage:
    python visualize_taxonomy.py [-o output.png|output.svg]

Reads 'taxonomy.json' in the current directory and outputs a hierarchy graph.
"""
import json
import argparse
from graphviz import Digraph

# Colors for top-level sections
TOP_LEVEL_COLORS = ['#8ecae6', '#ffb703', "#a9c9b4", '#f28482']
LEAF_SHAPE = 'ellipse'
LEAF_STYLE = 'italic'
LEAF_COLOR = "#01080f"


def load_taxonomy(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def add_nodes_edges(dot, node, parent=None, color=None, leaf_nodes=None):
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
        if leaf_nodes is not None:
            leaf_nodes.append(node_id)
    dot.node(node_id, **node_kwargs)
    if parent:
        dot.edge(parent, node_id)
    if 'children' in node:
        for child in node['children']:
            add_nodes_edges(dot, child, node_id, color, leaf_nodes)

def main():
    parser = argparse.ArgumentParser(description='Visualize taxonomy hierarchy from taxonomy.json')
    parser.add_argument('-o', '--output', default='taxonomy.png', help='Output filename (png or svg)')
    args = parser.parse_args()
    
    data = load_taxonomy('taxonomy.json')
    dot = Digraph(format=args.output.split('.')[-1])
    dot.attr(rankdir='TB')  # Top-down
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
    
    # Color top-level sections
    leaf_nodes = []
    root_id = str(id(data))
    dot.node(root_id, label=data['name'], shape='box', style='filled,bold', fillcolor='#219ebc', fontcolor='white')
    if 'children' in data:
        for idx, child in enumerate(data['children']):
            color = TOP_LEVEL_COLORS[idx % len(TOP_LEVEL_COLORS)]
            add_nodes_edges(dot, child, root_id, color, leaf_nodes)
    
    dot.render(args.output, view=False, cleanup=True)
    print(f"Taxonomy graph saved to {args.output}")

if __name__ == '__main__':
    main()
