# returns (str ID, str TYPE) of node or just (str ID)
def get_info(node):
    if node.name == 'ID': return node.value, ('VARIABLE', None)
    elif node.name == 'FUNCTION': return node.childs[0].value, (node.name, node.childs[2].value)
    elif node.name == 'CONST': return node.childs[1].value, (node.name, node.childs[0].value)
    elif node.name == 'STRUCT': return node.childs[0].value, (node.name, None)
    elif node.name == 'VARIABLE': return node.childs[1].value, (node.name, node.childs[0].value)
    elif node.name == 'VARIABLE_ARRAY': return node.childs[1].value, (node.name, node.childs[0].value)
    elif node.name == 'FUNC_CALL': return node.childs[0].value, ('FUNCTION', None)
    elif node.name == 'ARRAY_ELEMENT': return node.childs[0].value, ('VARIABLE_ARRAY', None)
    elif node.name == 'ASSIGN':
        if node.childs[0].name == 'VARIABLE' or node.childs[0].name == 'VARIABLE_ARRAY':
            return node.childs[0].childs[1].value, (node.childs[0].name, node.childs[0].childs[0].value)
        elif node.childs[0].name == 'ID': 
            return node.childs[0].value, ('VARIABLE', None)
        else:
            return get_info(node.childs[0])
    elif node.name == 'CHAIN_CALL': return get_info(node.childs[0])
    else: raise KeyError('Please add '+node.name+' to function get_info')


def is_definition(ast):
    def_names = ['VARIABLE', 'VARIABLE_ARRAY', 'FUNCTION']
    if ast.name in def_names: 
        return True
    elif ast.name == 'ASSIGN' and is_definition(ast.childs[0]):
        return True
    else: return False


def is_node(elem):
    return type(elem).__name__ == 'Node'


def is_node_has_id(node):
    if is_node(node):
        tnames = ['VARIABLE', 'VARIABLE_ARRAY', 'STRUCT', 'FUNCTION']
        return node.name in tnames
    return False


def is_node_atom(node):
    if is_node(node):
        tnames = ['CHAIN_CALL', 'ID', 'FUNC_CALL', 'CONST', 'VARIABLE_ARRAY',
                  'VARIABLE', 'ARRAY_ALLOC', 'ARRAY_ELEMENT']
        return node.name in tnames
    return False


def is_expression(node):
    if is_node(node):
        tnames = ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'IDIVIDE',
                  'LOR', 'BOR', 'LAND', 'BAND',
                  'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
                  'INCREMENT', 'DECREMENT']
        return node.name in tnames
    return False


def find_node_by_id(nodes, id):
    for node in nodes:
        if is_node_has_id(node) and node.get("ID")[0].value == id:
            return node
    return None


def find_array_by_id(list, id):
    for dict in list:
        if dict["id"] == id:
            return dict
    return None


def find_string_by_value(list, value):
    for l in list:
        if l["value"] == value:
            return l
    return None


class Node:
    def __init__(self, name, value=None, parent=None, childs=[], line=0):
        self.name = name
        self.value = value
        self.childs = childs
        self.parent = parent
        for child in self.childs:
            child.parent = self
        self.line = line
        self.checked = False

    # returns all children of current node
    # name might be string or list of strings
    # if nest == True returns all nested elements
    def get(self, name, nest=False):
        nodes = []
        for elem in self.childs:
            if isinstance(name, str) and elem.name == name:
                nodes.append(elem)
            elif isinstance(name, list) and elem.name in name:
                nodes.append(elem)
            nodes = nodes + (elem.get(name, nest) if nest else [])
        return nodes

    # adds new list of childs to existed
    def add_childs(self, childs):
        for child in childs:
            child.parent = self
        self.childs += childs

    def __parts_str(self):
        st = []
        for part in self.childs:
            st.append(str(part))
        if len(self.childs) == 0:
            st.append(str(self.value))
        return "\n".join(st)

    def __repr__(self):
        if self.name == '':
            return self.__parts_str().replace("\n", "\n")
        else:
            return self.name + ":\n\t" + self.__parts_str().replace("\n", "\n\t")
