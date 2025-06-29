class TileNode:
    def __init__(self, name, data=None):
        self.data = data
        self.name = name
        self.children = []
    def add_child(self, child_node):
        self.children.append(child_node)

def print_graph(node, level=0):
    print("  " * level  + f"- {node.name}")
    for child in node.children:
        print_graph(child, level + 1)

def iterate_dfs(node, level=0):
    print(f"Level {level}: {node.name}")
    for child in node.children:
        iterate_dfs(child, level + 1)