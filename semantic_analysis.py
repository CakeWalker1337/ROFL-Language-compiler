import copy
from node_utils import *
# Wraps the error message with error syntax
# returns tuple of error message and line number
def wrap_error(err_str, line_num):
    error_prefix = 'Semantic error at line '+ str(line_num) +': '
    return (error_prefix + err_str, line_num)

default_types = {'int':[],
                'string':[],
                'float':[],
                'boolean':[]}

# checks if there is errors with repeat definitions, usage of undefined variables, incorrect calls of properties of struct
# returns array of wrap_error() objects
def check_var_definition(node, types=default_types, 
            variables={'print' : ('FUNCTION', 'void')}):
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
        elif d.name == 'FUNCTION': # add functions to variables dictionary
            if type[1] in types or type[1] == 'void':
                if not name in variables:
                    variables[name] = type
                    func_scope_vars = {}
                    # adding the function arguments into the scope 
                    for arg in d.get('FUNC_ARGS')[0].childs:
                        arg_name, arg_type = get_info(arg)
                        func_scope_vars[arg_name] = arg_type
                    # adding the declared functions to scope of the function
                    for name, type in variables.items():
                        if type[0] == 'FUNCTION':
                            func_scope_vars[name] = type
                    errors += check_var_definition(d.get('SCOPE')[0], types, func_scope_vars)
                else: errors.append(wrap_error('Variable "'+name+'" already defined as "'+variables[name]+'".', d.line))
            else: 
                if type[0] == 'FUNCTION':
                    errors.append(wrap_error('Function can\'t return function.', d.line))
                else:
                    errors.append(wrap_error('Undefined type "'+type[1]+'" used.', d.line))
        elif ((d.name == 'VARIABLE' or d.name == 'VARIABLE_ARRAY') and d.parent.name != 'ASSIGN') \
                 or d.name == 'ASSIGN' and d.childs[0].name != 'ID' and d.childs[0].name != 'ARRAY_ELEMENT' and d.childs[0].name != 'CHAIN_CALL':
            # just check if there is a type and name in definitions
            # and add it to the variable dictionary if it isn't defined already
            if type[1] in types:
                if not name in variables:
                    variables[name] = type
                    cur_scope_vars.append(name)
                else: errors.append(wrap_error('Variable "'+name+'" already defined as "'+str(variables[name])+'".', d.line))
            else: errors.append(wrap_error('Undefined type "'+type[1]+'" used.', d.line))
        elif (d.name == 'ID' and d.parent.name != 'ASSIGN') and (not d.parent or (d.parent and d.parent.name != 'CHAIN_CALL')) or d.name == 'ASSIGN' and d.childs[0].name != 'CHAIN_CALL':
            # check if name defined in scope
            # also check if there is a usage of struct name as a variable
            if name in types:
                errors.append(wrap_error('Variable name expected.', d.line))
            elif not name in variables:
                errors.append(wrap_error('Usage of undefined variable "'+name+'"', d.line))
            if d.parent.name == 'ARRAY_ELEMENT':
                if (variables[name][0] != 'VARIABLE_ARRAY'):
                    errors.append(wrap_error(f'Variable "{name}" is not an array.', d.line))
                print(d)
        elif (d.name == 'CHAIN_CALL' and d.parent.name != 'ASSIGN') or d.name == 'ASSIGN':
            # check if call of properties are ok
            # and name defined in scope
            # also check if there is a usage of struct name as a variable
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
    # start recursion for inner scopes
    for child in node.childs:
        if not child.name in def_names or child.name == 'ASSIGN':
            errors += check_var_definition(child, types, variables) 

    # clear current variables if we exit current scope
    if node.name == 'SCOPE':
        for var in cur_scope_vars:
            del variables[var]
    return errors


def check_funcs_returns(root):
    errors = []
    if root is not None:
        funcs = root.get("FUNCTION", nest=True)
        for func in funcs:
            ftype = func.get("TYPE")[0]
            scope = func.get("SCOPE")[0]
            rets = scope.get("RETURN")
            if len(rets) == 0:
                if ftype.value != "void":
                    errors.append(wrap_error("Expected return statement with type \'" + ftype.value + "\'", func.line))
            else:
                for ret in rets:
                    if ret.value is None and len(ret.childs) == 0:
                        if ftype.value != "void":
                            errors.append(
                                wrap_error("Function with type \"" + ftype.value + "\" must return a value.", ret.line))
                    else:
                        res_type = get_expression_result_type(ret.childs[0], errors, collect_errors=False)
                        if res_type != "end" and res_type != ftype.value:
                            errors.append(wrap_error(
                                "Incorrect return type \"" + res_type + "\". Function must return a value of type \"" + ftype.value + "\".",
                                ret.line))
    return errors


def check_arguments_of_func_calls(root) :
    errors = []
    exceptions = ['print']
    func_calls = root.get("FUNC_CALL", nest=True)
    for call in func_calls:
        if call.get("ID")[0].value in exceptions: continue
        func = find_element_by_id(call.get("ID")[0].value, get_nearest_scope(call))
        func_args = func.get("FUNC_ARGS")[0].childs
        call_args = call.get("CALL_ARGS")[0].childs
        if len(func_args) != len(call_args):
            errors.append(wrap_error("Incorrect number of arguments in the call of function '"+func.childs[0].value+"'.", call.line))
            continue
        call_arg_types = []
        for arg in call_args:
            call_arg_types.append(get_expression_result_type(arg, []))
        if "error" in call_arg_types:
            continue
        for i in range(0, len(func_args)):
            func_arg_type = get_atom_type(func_args[i])
            if func_arg_type != call_arg_types[i]:
                errors.append(wrap_error("Incorrect type of argument with type \'"+call_arg_types[i]+"\' (required \'" + func_arg_type + "\').", call.line))
    return errors


def check_unexpected_keywords(root):
    errors = []
    def check_keywords_recursive(node, errors, prev_anchor=None, is_in_func=False):
        if node.name == "FUNCTION" or node.name == "WHILE" or node.name == "DO_WHILE":
            prev_anchor = node.name
            if node.name == "FUNCTION":
                is_in_func = True
        elif node.name == "RETURN" and not is_in_func:
            errors.append(wrap_error("Unexpected return keyword outside of function.", node.line))
        elif (node.name == "BREAK" or node.name == "SKIP") and (prev_anchor != "WHILE" and prev_anchor != "DO_WHILE"):
            errors.append(wrap_error("Unexpected \'" + node.name.lower() + "\' keyword outside of function.", node.line))
        for child in node.childs:
            check_keywords_recursive(child, errors, prev_anchor, is_in_func)

    if root is not None:
        check_keywords_recursive(root, errors)
    return errors


# gets first defined function, struct or variable consider scopes
def find_element_by_id(id, scope):
    if scope is None:
        return None
    for elem in scope.childs:
        current = None
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
        if scope.parent is not None and scope.parent.name == "FUNCTION":
            func_args = scope.parent.get("FUNC_ARGS")[0].childs
            modified_scope = copy.deepcopy(scope)
            modified_scope.add_childs(func_args)
        return modified_scope
    return get_nearest_scope(node.parent)


def get_atom_type(atom):
    if atom.name == "CONST" or atom.name == "VARIABLE":
        return atom.get("TYPE")[0].value
    if atom.name == "VARIABLE_ARRAY" or atom.name == "ARRAY_ALLOC":
        return atom.get("TYPE")[0].value+"[]"
    if atom.name == "ARRAY_ELEMENT":
        elem_id = atom.childs[0].value
        arr = find_element_by_id(elem_id, get_nearest_scope(atom))
        if arr is not None:
            return arr.get("TYPE")[0].value
    if atom.name == "CHAIN_CALL":
        first = atom.childs[0]
        second = atom.childs[1]
        type = get_atom_type(first)
        type = type.replace("[]", '')
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
    if atom.name == "FUNC_CALL":
        looked_id = atom.get("ID")[0].value
    elif atom.name == "ID":
        looked_id = atom.value
    found_elem = find_element_by_id(looked_id, get_nearest_scope(atom))
    if found_elem is None:
        return None
    else:
        if is_node_atom(found_elem):
            return get_atom_type(found_elem)
        return found_elem.get("TYPE")[0].value


def get_expression_result_type(root, errors, collect_errors=True):
    if is_expression(root):
        if len(root.childs) == 1:
            first = get_expression_result_type(root.childs[0], errors)
            if first == "end":
                return "end"
            comp_res = compare_expr(first, None, root.name)
            if comp_res == "error":
                if collect_errors:
                    errors.append(
                        wrap_error("Expression error: operand has an unsuitable type (" + first + ")", root.line))
                return "end"
            return comp_res
        else:
            first = get_expression_result_type(root.childs[0], errors)
            second = get_expression_result_type(root.childs[1], errors)
            if first == "end" or second == "end":
                return "end"
            comp_res = compare_expr(first, second, root.name)
            if comp_res == "error":
                if collect_errors:
                    errors.append(wrap_error(
                        "Expression error: operands have unsuitable types (" + first + ", " + second + ")",
                        root.childs[0].line))
                return "end"
            return comp_res
    if is_node_atom(root):
        return get_atom_type(root)


def check_expression_results(root):
    if is_node(root):
        errors = []
        for part in root.childs:
            if is_node(part):

                if part.name == "ASSIGN":

                    expr1 = get_expression_result_type(part.childs[0], errors)
                    expr2 = get_expression_result_type(part.childs[1], errors)

                    if expr1 != "end" and expr2 != "end":
                        is_correct = False
                        if is_type_arithmetic(expr1) and is_type_arithmetic(expr2):
                            is_correct = True
                        if expr1 == expr2:
                            is_correct = True
                        if not is_correct:
                            errors.append(wrap_error(
                                "Type cast exception: cannot cast type \"" + expr2 + "\" to \"" + expr1 + "\"",
                                part.line))
                else:
                    get_expression_result_type(part, errors)
                    next_node = None
                    if part.name == "STRUCT":
                        next_node = part.get("CONTENT")[0]
                    elif part.name == "FUNCTION":
                        next_node = part.get("SCOPE")[0]
                    else:
                        next_node = part
                    if not is_node_atom(part):
                        errors.extend(check_expression_results(next_node))
        return errors


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
    if one.find("[]") != -1 or one.find("[]") != -1:
        return "error"
    if one == "void" or two == "void":
        return "error"
    if one == "string" or two == "string":
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
        if one == two:
            return "boolean"
        return "error"
    # if is_operation_arithmetic(operation_type):
    #     if is_type_arithmetic(one) and is_type_arithmetic(two):
    #         return "float"
    #     if one == "string" and operation_type == "PLUS":
    #         return "string"
    #     return "error"
    # if is_operation_bit(operation_type):
    #     if (one == "boolean" or one == "int") and one == two:
    #         return one
    if one == two:
        return one
    return "error"


# checks all the indexes in array_element callings for being 'int'
# also checks if there is array allocation with size = 0
def check_array_things(tree):
    arr_calls = tree.get('ARRAY_ELEMENT', True)
    errors = []
    for call in arr_calls:
        if get_expression_result_type(call.childs[1], errors) != 'int':
            errors.append(wrap_error('Array index can only be an integer.', call.line))
    arr_allocs = tree.get('ARRAY_ALLOC', True)
    for alloc in arr_allocs:
        if alloc.childs[1].childs[1].value == '0':
            errors.append(wrap_error('You can\'t create an array with zero size.', alloc.line))
    return errors


# check if there are not allocated array variables
def check_array_allocation(tree):
    arr_defs = tree.get('VARIABLE_ARRAY', True)
    errors = []

    for d in arr_defs:
        if d.parent.name != 'ASSIGN':
            errors.append(wrap_error('Array must be allocated.', d.line))
    
    return errors


def check_conditions(root):
    conds = root.get("CONDITION", nest=True)
    res_errors = []
    for cond in conds:
        node = cond.childs[0]
        errors = []
        ret_type = get_expression_result_type(node, errors)
        if len(errors) == 0:
            if ret_type != "boolean":
                res_errors.append(wrap_error('Condition must have only boolean type.', cond.line))

    return res_errors

#
# def check_array_element_types(root):
#     elems = root.get("ARRAY_ELEMENT", nest=True)
#     for elem in elems:
#         if elem.parent.name == "CHAIN_CALL":
#             structs = root.get("STRUCT")
#             for struct in structs:
#                 if struct.get("ID")[0].value == elem.parent.childs[0].get("ID")[0]
#         scope = get_nearest_scope(elem)


#TODO: Add comments and check func params while calling
