
# Wraps the error message with error syntax
# returns tuple of error message and line number
def wrap_error(err_str, line_num):
    error_prefix = 'Semantic error at line '+ str(line_num) +': '
    return (error_prefix + err_str, line_num)


# returns (str ID, str TYPE) of node or just (str ID)
def get_info(node):
    if node.name == 'ID': return node.value
    elif node.name == 'FUNCTION': return node.childs[0].value, node.childs[2].value
    elif node.name == 'STRUCT': return node.childs[0].value, 'struct'
    elif node.name == 'VARIABLE': return node.childs[1].value, node.childs[0].value
    elif node.name == 'FUNC_CALL': return node.childs[0].value
    else: raise KeyError('Please add node to function get_info')

# def check_var_definition(node, scope = None, variables = {}):
#     cur_scope_vars = []

#     defs = node.get(['FUNCTION', 'STRUCT', 'VARIABLE'])
#     a = list(map(get_info, defs))
    

#     return 1
