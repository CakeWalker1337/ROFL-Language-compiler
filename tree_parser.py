def get_all_nodes_by_name(root, name, nodes):
    for elem in root.parts:
        if type(elem).__name__ == 'Node':
            if elem.type == name:
                nodes.append(elem)
            get_all_nodes_by_name(elem, name, nodes)




def check_keywords(root):
    def check_keywords_rec():
        print("EEe")

    for elem in root.parts:
        if type(elem).__name__ == 'Node':
            # if elem.type == name:
            #     nodes.append(elem)
            # check_keywords(elem)
            pass


def check_return_types(nodes):

    for node in nodes:
        scope = node.parts[3]
        return_value = node.parts[2].parts[0]
        returns = []
        get_all_nodes_by_name(scope, "RETURN", returns)
        if len(returns) == 0:
            if return_value != "void":
                print("Return token expected. Function must return a value of type \"%s\"!" % return_value)
        else:
            for val in returns:
                pass

