
# Wraps the error message with error syntax
# returns tuple of error message and line number
def wrap_error(err_str, line_num):
    error_prefix = 'Semantic error at line '+ str(line_num) +': '
    return (error_prefix + err_str, line_num)

# returns (str ID, str TYPE) of node or just (str ID)
def get_info(node):
    if node.name == 'ID': return node.value, None
    elif node.name == 'FUNCTION': return node.childs[0].value, node.childs[2].value
    elif node.name == 'STRUCT': return node.childs[0].value, 'struct'
    elif node.name == 'VARIABLE': return node.childs[1].value, node.childs[0].value
    elif node.name == 'FUNC_CALL': return node.childs[0].value, None
    else: raise KeyError('Please add node to function get_info')

default_types = {'int':'int', 'int[]':'int[]',
                'string':'string', 'string[]':'string[]',
                'float':'float', 'float[]':'float[]',
                'boolean':'boolean', 'boolean[]':'boolean[]',
                'null':'null'}

    
def check_var_definition(node, types=default_types, variables={}):
    errors = []
    def_names = ['FUNCTION', 'STRUCT', 'VARIABLE', 'ID']
    defs = node.get(def_names)
    for d in defs:
        name, type = get_info(d)
        if d.name == 'STRUCT': # add struct to types dictionary 
            if not name in types:
                variables[name] = type
                new_dict = {}
                for str_var in d.get('CONTENT')[0].childs:
                    str_var_name, str_var_type = get_info(str_var)
                    if not str_var_name in types:
                        new_dict[str_var_name] = str_var_type
                    else: errors.append(wrap_error('Undefined type "'+type+'" used.', d.line))
                types[name] = new_dict
            else: errors.append(wrap_error('Variable "'+name+'" already defined as "'+variables[name]+'".', d.line))
        elif d.name == 'FUNCTION': 
            if type in types:
                if not name in variables:
                    variables[name] = {'function': type}
                    func_scope_vars = {}
                    for arg in d.get('FUNC_ARGS')[0].childs:
                        arg_name, arg_type = get_info(arg)
                        func_scope_vars[arg_name] = arg_type
                    errors += check_var_definition(d.get('SCOPE')[0], types, func_scope_vars)
                else: errors.append(wrap_error('Variable "'+name+'" already defined as "'+variables[name]+'".', d.line))
            else: errors.append(wrap_error('Undefined type "'+type+'" used.', d.line))
        elif d.name == 'VARIABLE':
            # just check if there is a type and name in definitions
            if type in types:
                if not name in variables:
                    variables[name] = type
                else: errors.append(wrap_error('Variable "'+name+'" already defined as "'+str(variables[name])+'".', d.line))
            else: errors.append(wrap_error('Undefined type of a variable.', d.line))
        elif d.name == 'ID':
            # check if name defined in scope
            if name in types:
                errors.append(wrap_error('Variable name expected.', d.line))
            elif not name in variables:
                errors.append(wrap_error('Usage of undefined variable "'+name+'"', d.line))
        elif d.name == 'CHAIN_CALL':
            pass
    
    for child in node.childs:
        if not child.name in def_names:
            errors += check_var_definition(child, types, variables) 
    return errors
