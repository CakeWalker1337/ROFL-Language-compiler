import copy
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
        elif node.childs[0].name == 'ID': 
            return node.childs[0].value, ('VARIABLE', None)
        else:
            return get_info(node.childs[0])
    elif node.name == 'CHAIN_CALL': return get_info(node.childs[0])
    else: raise KeyError('Please add '+node.name+' to function get_info')

default_types = {'int':[],
                'string':[],
                'float':[],
                'boolean':[],
                'null':[]}

    
def check_var_definition(node, types=default_types, variables={}):
    errors = []
    cur_scope_vars = []
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
            if type[1] in types or type[1] == 'void':
                if not name in variables:
                    variables[name] = type
                    func_scope_vars = {}
                    for arg in d.get('FUNC_ARGS')[0].childs:
                        arg_name, arg_type = get_info(arg)
                        func_scope_vars[arg_name] = arg_type
                    errors += check_var_definition(d.get('SCOPE')[0], types, func_scope_vars)
                else: errors.append(wrap_error('Variable "'+name+'" already defined as "'+variables[name]+'".', d.line))
            else: errors.append(wrap_error('Undefined type "'+type+'" used.', d.line))
        elif d.name == 'VARIABLE' or d.name == 'VARIABLE_ARRAY' or d.name == 'ASSIGN' and d.childs[0].name != 'ID' and d.childs[0].name != 'CHAIN_CALL':
            # just check if there is a type and name in definitions
            if type[1] in types:
                if not name in variables:
                    variables[name] = type
                    cur_scope_vars.append(name)
                else: errors.append(wrap_error('Variable "'+name+'" already defined as "'+str(variables[name])+'".', d.line))
            else: errors.append(wrap_error('Undefined type "'+type[1]+'" used.', d.line))
        elif d.name == 'ID' and (not d.parent or (d.parent and d.parent.name != 'CHAIN_CALL')) or d.name == 'ASSIGN' and d.childs[0].name != 'CHAIN_CALL':
            # check if name defined in scope
            if name in types:
                errors.append(wrap_error('Variable name expected.', d.line))
            elif not name in variables:
                errors.append(wrap_error('Usage of undefined variable "'+name+'"', d.line))
        elif d.name == 'CHAIN_CALL' or d.name == 'ASSIGN':
            prev_name, prev_type = get_info(d.childs[0])
            childs = d.childs if d.name == 'CHAIN_CALL' else d.childs[0].childs
            if prev_name in types:
                errors.append(wrap_error('Variable name expected.', d.line))
            elif not prev_name in variables:
                errors.append(wrap_error('Usage of undefined variable "'+prev_name+'"', d.line))
            elif variables[prev_name][0] != prev_type[0]:
                errors.append(wrap_error('Wrong call of '+variables[prev_name][0].lower()+' "'+prev_name+'"; treated as '+prev_type[0].lower()+'.', d.line))
            else: 
                for idx in range(1, len(childs)):
                    call = childs[idx]
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
    if node.name == 'SCOPE':
        for var in cur_scope_vars:
            del variables[var]
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


def is_node(elem):
    return type(elem).__name__ == 'Node'


def is_node_has_id(node):
    if is_node(node):
        tnames = ['VARIABLE', 'VARIABLE_ARRAY', 'STRUCT', 'FUNCTION']
        return node.name in tnames
    return False


def is_node_atom(node):
    if is_node(node):
        tnames = ['CHAIN_CALL', 'ID', 'FUNC_CALL', 'CONSTANT', 'VARIABLE_ARRAY',
                  'VARIABLE', 'ARRAY_ALLOC', 'ARRAY_ELEMENT']
        return node.name in tnames
    return False


# gets first defined function, struct or variable consider scopes
def find_element_by_id(id, scope):
    if scope is None:
        return None
    for elem in scope.childs:
        if elem.name == "ASSIGN":
            current = elem.childs[0]
        else:
            current = elem
        if is_node_has_id(current) and current.get("ID")[0].value == id:
            return current
    return find_element_by_id(id, get_nearest_scope(scope))


# can be used when is needed to get closest scope from node
# NOTE: if scope belongs to function, it's arguments are adding to the END of scope
# it means that this function is not for checking the order of definitions.
# Use it if you sure that the definitions are correct.
def get_nearest_scope(node):
    if node.parent is None:
        return None
    if node.parent.name == "SCOPE" or node.parent.name == "CONTENT":
        scope = node.parent
        modified_scope = scope
        if scope.parent.name == "FUNCTION":
            func_args = scope.parent.get("FUNC_ARGS")[0].childs
            modified_scope = copy.deepcopy(scope)
            modified_scope.add_childs(func_args)
        return modified_scope
    return get_nearest_scope(node.parent)


def get_atom_type(atom):
    if atom.name == "CONST" or atom.name == "VARIABLE" or atom.name == "ARRAY_ALLOC" or atom.name == "VARIABLE_ARRAY":
        return atom.get("TYPE").value
    if atom.name == "CHAIN_CALL":
        first = atom.childs[0]
        second = atom.childs[1]
        type = get_atom_type(first)
        fst_struct = find_element_by_id(type, get_nearest_scope(first))
        if fst_struct.name == "STRUCT":
            desired_id = None
            if second.name == "ID":
                desired_id = second.value
            else:
                desired_id = second.get("ID")[0].value
            return get_atom_type(find_element_by_id(desired_id, fst_struct.get("CONTENT")[0]))
        else:
            raise Exception("First element hasn\'t got return type of structure")
    looked_id = None
    if atom.name == "ARRAY_ELEMENT":
        looked_id = atom.childs[0].value
    if atom.name == "FUNC_CALL":
        looked_id = atom.get("ID")[0].value
    elif atom.name == "ID":
        looked_id = atom.value
    found_elem = find_element_by_id(looked_id, get_nearest_scope(atom))
    if found_elem is None:
        return None
    else:
        return found_elem.get("TYPE")[0].value


def get_expression_result_type(root):
    if is_expression(root):
        if len(root.childs) == 1:
            first = get_expression_result_type(root.childs[0])
            if first == "end":
                return "end"
            comp_res = compare_expr(first, None, root.name)
            if comp_res == "error":
                print("Expression error: operand has an unsuitable type (%s). Line: %s" % (
                    first, root.childs[0].line))
                return "end"
            return comp_res
        else:

            first = get_expression_result_type(root.childs[0])
            second = get_expression_result_type(root.childs[1])
            if first == "end" or second == "end":
                return "end"
            comp_res = compare_expr(first, second, root.name)
            if comp_res == "error":
                print(
                    "Expression error: operands have unsuitable types (%s, %s). line: %s" % (
                        first, second, root.childs[0].line))
                return "end"
            return comp_res
    if is_node_atom(root):
        return get_atom_type(root)


def check_expression_results(root, has_errors):
    if is_node(root):
        for part in root.childs:
            if is_node(part):
                if part.name == "ASSIGN":
                    expr1 = get_expression_result_type(part.childs[0])
                    expr2 = get_expression_result_type(part.childs[1])

                    if not (expr1 == "end" or expr2 == "end"):
                        is_correct = False
                        if is_type_arithmetic(expr1) and is_type_arithmetic(expr2):
                            is_correct = True
                        if expr1 == expr2:
                            is_correct = True
                        if not is_correct:
                            has_errors = True
                            print("Type cast exception: cannot cast type \"%s\" to \"%s\" at line: %s" % (
                                expr2, expr1, part.line))
                else:
                    result = get_expression_result_type(part)
                    if result == "end":
                        has_errors = True
                    next_node = None
                    if part.name == "STRUCT":
                        next_node = part.get("CONTENT")[0]
                    elif part.name == "FUNCTION":
                        next_node = part.get("SCOPE")[0]
                    else:
                        next_node = part
                    check_expression_results(next_node, has_errors)


def is_expression(node):
    if is_node(node):
        tnames = ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'IDIVIDE',
                  'LOR', 'BOR', 'LAND', 'BAND', 'LNOT',
                  'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
                  'INCREMENT', 'DECREMENT', 'CHAIN_CALL']
        return node.name in tnames
    return False


def is_primitive_type(typename):
    tnames = ['int', 'string', 'boolean', 'void', 'float']
    return typename in tnames


def is_operation_arithmetic(oper):
    tnames = ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'IDIVIDE']
    return oper in tnames


def is_operation_logic(oper):
    tnames = ['LOR', 'LAND', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE']
    return oper in tnames


def is_operation_bit(oper):
    tnames = ['BOR', 'BAND']
    return oper in tnames


def is_type_arithmetic(typename):
    if typename == "int" or typename == "float":
        return True
    return False


def compare_expr(one, two, operation_type):
    if one == "null" or two == "null":
        return "error"
    if one == "array" or two == "array":
        return "error"
    if one == "void" or two == "void":
        return "error"
    if one is None:
        if two == "boolean":
            return two
        return "error"
    if two is None:
        if one == "boolean":
            return one
        return "error"
    if is_operation_logic(operation_type):
        if one == two or (is_type_arithmetic(one) and is_type_arithmetic(two)):
            return "boolean"
        return "error"
    if is_operation_arithmetic(operation_type):
        if is_type_arithmetic(one) and is_type_arithmetic(two):
            return "float"
        if one == "string" and operation_type == "PLUS":
            return "string"
        return "error"
    if is_operation_bit(operation_type):
        if (one == "boolean" or one == "int") and one == two:
            return one
        return "error"
    return "error"
