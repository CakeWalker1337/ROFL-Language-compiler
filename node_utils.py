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
