def get_all_nodes_by_name(root, name, nodes):
    for elem in root.parts:
        if type(elem).__name__ == 'Node':
            if elem.type == name:
                nodes.append(elem)
            get_all_nodes_by_name(elem, name, nodes)