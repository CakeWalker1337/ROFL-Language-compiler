
# Wraps the error message with error syntax
# returns tuple of error message and line number
def wrap_error(err_str, line_num):
    error_prefix = 'Semantic error at line '+ str(line_num) +': '
    return (error_prefix + err_str, line_num)


# returns (str ID, str TYPE) of node or just (str ID)
def get_info(node):
    if node.name == 'ID': return node.value, ('VARIABLE', None)
    elif node.name == 'FUNCTION': return node.childs[0].value, (node.name, node.childs[2].value)
    elif node.name == 'STRUCT': return node.childs[0].value, (node.name, None)
    elif node.name == 'VARIABLE': return node.childs[1].value, (node.name, node.childs[0].value)
    elif node.name == 'VARIABLE_ARRAY': return node.childs[1].value, (node.name, node.childs[0].value)
    elif node.name == 'FUNC_CALL': return node.childs[0].value, ('FUNCTION', None)
    elif node.name == 'ARRAY_ELEMENT': return node.childs[0].value, ('VARIABLE_ARRAY', None)
    elif node.name == 'ASSIGN': 
        if node.childs[0].name == 'VARIABLE' or node.childs[0].name == 'VARIABLE_ARRAY':
            return node.childs[0].childs[1].value, (node.childs[0].name, node.childs[0].childs[0].value)
        else: 
            return node.childs[0].value, ('VARIABLE', None)
    elif node.name == 'CHAIN_CALL': return None, None
    else: raise KeyError('Please add '+node.name+' to function get_info')

default_types = {'int':[],
                'string':[],
                'float':[],
                'boolean':[],
                'null':[]}

    
def check_var_definition(node, types=default_types, variables={}):
    errors = []
    def_names = ['FUNCTION', 'STRUCT', 'VARIABLE', 'VARIABLE_ARRAY', 'ID', 'CHAIN_CALL', 'ASSIGN']
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
                        if not str_var_name in new_dict:
                            str_var_type = str_var_type
                            new_dict[str_var_name] = str_var_type
                        else:
                            errors.append(wrap_error('Repeat definition of "'+str_var_name+'" in struct "'+name+'"'+'. It\'s already defined above.', d.line))
                    else: 
                        errors.append(wrap_error('Undefined type "'+type+'" used.', d.line))
                types[name] = new_dict
                types[name+'[]'] = new_dict
            else: errors.append(wrap_error('Variable "'+name+'" already defined as "'+variables[name]+'".', d.line))
        elif d.name == 'FUNCTION': 
            if type[1] in types:
                if not name in variables:
                    variables[name] = type
                    func_scope_vars = {}
                    for arg in d.get('FUNC_ARGS')[0].childs:
                        arg_name, arg_type = get_info(arg)
                        func_scope_vars[arg_name] = arg_type
                    errors += check_var_definition(d.get('SCOPE')[0], types, func_scope_vars)
                else: errors.append(wrap_error('Variable "'+name+'" already defined as "'+variables[name]+'".', d.line))
            else: errors.append(wrap_error('Undefined type "'+type+'" used.', d.line))
        elif d.name == 'VARIABLE' or d.name == 'VARIABLE_ARRAY' or d.name == 'ASSIGN' and d.childs[0].name != 'ID':
            # just check if there is a type and name in definitions
            if type[1] in types:
                if not name in variables:
                    variables[name] = type
                else: errors.append(wrap_error('Variable "'+name+'" already defined as "'+str(variables[name])+'".', d.line))
            else: errors.append(wrap_error('Undefined type of a variable.', d.line))
        elif d.name == 'ID' and (d.parent and d.parent.name != 'CHAIN_CALL') or d.name == 'ASSIGN' and d.childs[0].name == 'ID':
            # check if name defined in scope
            if name in types:
                errors.append(wrap_error('Variable name expected.', d.line))
            elif not name in variables:
                errors.append(wrap_error('Usage of undefined variable "'+name+'"', d.line))
        elif d.name == 'CHAIN_CALL':
            prev_name, prev_type = get_info(d.childs[0])
            if prev_name in types:
                errors.append(wrap_error('Variable name expected.', d.line))
            elif not prev_name in variables:
                errors.append(wrap_error('Usage of undefined variable "'+prev_name+'"', d.line))
            elif variables[prev_name][0] != prev_type[0]:
                errors.append(wrap_error('Wrong call of '+variables[prev_name][0].lower()+' "'+prev_name+'"; treated as '+prev_type[0].lower()+'.', d.line))
            else: 
                for idx in range(1, len(d.childs)):
                    call = d.childs[idx]
                    name, type = get_info(call)
                    if name in types[variables[prev_name][1]]:
                        real_type = types[variables[prev_name][1]][name][0]
                        if not type[0] == real_type and idx != len(d.childs) - 1:
                            errors.append(wrap_error('Wrong call of '+real_type.lower()+' "'+name+'"; treated as '+type[0].lower()+'.', call.line))
                    else: errors.append(wrap_error('Struct "'+variables[prev_name][1]+'" has no properties with name "'+name+'".', call.line))
                    prev_name = name
                    prev_type = type
            pass
    for child in node.childs:
        if not child.name in def_names:
            errors += check_var_definition(child, types, variables) 
    return errors

#     return 1

def check_funcs_have_returns(root):
    if root is not None:
        funcs = root.get("FUNCTION", nest=True)
        for func in funcs:
            ftype = func.get("TYPE")[0]
            scope = func.get("SCOPE")[0]
            rets = scope.get("RETURN")
            if len(rets) == 0:
                if ftype.value != "void":
                    print("Return error: expected return statement with type \'%s\'. Line: %s" % (ftype.value, func.line))
            else:
                for ret in rets:
                    if ret.value is None and len(ret.childs) == 0:
                        print("Return error: function with type \"%s\" must return a value. Line: %s" % (
                        ftype.value, ret.line))


def check_unexpected_keywords(root):

    def check_keywords_recursive(node, prev_anchor=None, is_in_func=False):
        if node.name == "FUNCTION" or node.name == "WHILE" or node.name == "DO_WHILE":
            prev_anchor = node.name
            if node.name == "FUNCTION":
                is_in_func = True
        elif node.name == "RETURN" and not is_in_func:
            print("Unexpected return keyword outside of function. Line %s" % node.line)
        elif (node.name == "BREAK" or node.name == "SKIP") and (prev_anchor != "WHILE" and prev_anchor != "DO_WHILE"):
            print("Unexpected \'%s\' keyword outside of function. Line %s" % (node.name.lower(), node.line))
        for child in node.childs:
            check_keywords_recursive(child, prev_anchor, is_in_func)

    if root is not None:
        check_keywords_recursive(root)


# gets first defined function, struct or variable consider scopes
def find_element_by_id(id, scope):
    pass


#can be used when is needed to get closest scope from node
def get_nearest_scope(node):
    if node.parent.name == "SCOPE" or node.parent.name == "CONTENT":
        return node.parent
    return get_nearest_scope(node.parent)


#gets type of atom
def get_atom_type(atom):
    if atom.name == "CONST" or atom.name == "VARIABLE" or atom.name == "ARRAY_ALLOC":
        return atom.get("TYPE").value
    if atom.name == "ARRAY_ELEMENT":
        id = atom.children[0].children[0]
        arr = find_element_by_id(id)
        # if not arr is None:
        #     if not is_primitive_type(arr.children[0].children[0]):
        #         return arr.get_element_by_tag("DATATYPE").children[0].replace("[]", "")
        #     else:
        #         print("Array call error. Element can't be called as array element. Line: %s" % atom.line)
        #         return arr.children[0].children[0]
    looked_id = None
    if atom.name == "FUNC_CALL":
        looked_id = atom.get_element_by_tag("ID").children[0]
    elif atom.name == "ID":
        looked_id = atom.children[0]
    found_elem = find_element_by_id(looked_id)
    if found_elem is None:
        return None
    else:
        return found_elem.get_element_by_tag("DATATYPE").children[0]

def check_chain_calls(root):

    def find_chain_calls(node):
        if node.name == "CHAIN_CALL":
            check_chain_recursive(node)
        else:
            for child in node.childs:
                find_chain_calls(child)

    def check_chain_recursive(node):
        if node.value is not None:
            pass
            #return get_atom_type(node)
        else:
            prev_type = check_chain_recursive(node.childs[0])
