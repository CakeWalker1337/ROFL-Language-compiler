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
    if ast.name in def_names: return True
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
                  'LOR', 'BOR', 'LAND', 'BAND', 'LNOT',
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
