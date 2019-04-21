from yacc import Node

identified = []
main_root = None


def init_semantic(root):
    global identified, main_root
    identified = get_nodes_with_id(root)
    main_root = root


def parse_chain_call_errors():
    global main_root
    calls = get_all_nodes_by_name(main_root, "CHAIN_CALL")
    for call in calls:
        prim = call.parts[0]
        second = call.parts[1]
        if prim.type == "ID":
            elem = find_element_by_id(prim.parts[0])
            if elem.type == "VARIABLE":
                type = elem.parts[0].parts[0]
                if not (is_primitive_type(type) or is_primitive_type(type.replace("[]", ''))):
                    decl = find_element_by_id(type)
                    if decl.type == "STRUCT":
                        scope = decl.get_element_by_tag("CONTENT")
                        is_found = False

                        variables = get_all_nodes_by_name(scope, "VARIABLE")
                        funcs = get_all_nodes_by_name(scope, "FUNCTION")

                        funcs.extend(variables)
                        desired_id = None
                        if second.type == "ID":
                            desired_id = second.parts[0]
                        else:
                            desired_id = second.get_element_by_tag(
                                "ID").parts[0]
                        for content_part in funcs:
                            if content_part.get_element_by_tag("ID").parts[0] == desired_id:
                                is_found = True
                                break
                        if not is_found:
                            print("Undefined member \"%s\" of struct \"%s\" on line: %s" % (
                                desired_id,
                                decl.get_element_by_tag("ID").parts[0],
                                call.line))
                    else:
                        raise Exception(
                            "Incorrect type %s detected. Maybe you didnt check var errors." % decl.type)
                else:
                    print(
                        "Incorrect call exception. Primitive types and arrays haven\'t got members. Line: %s" % call.line)
            else:
                print("Incorrect call \"%s\" on line: %s" %
                      (second.get_element_by_tag("ID").parts[0], call.line))
        elif prim.type == "ARRAY_ELEMENT":
            elem = find_element_by_id(prim.parts[0].parts[0])
            if not elem is None:
                type = elem.parts[0].parts[0][:-2]
                if not is_primitive_type(type):
                    decl = find_element_by_id(type)
                    if decl.type == "STRUCT":
                        scope = decl.get_element_by_tag("CONTENT")
                        is_found = False

                        variables = get_all_nodes_by_name(scope, "VARIABLE")
                        funcs = get_all_nodes_by_name(scope, "FUNCTION")

                        funcs.extend(variables)
                        desired_id = None
                        if second.type == "ID":
                            desired_id = second.parts[0]
                        else:
                            desired_id = second.get_element_by_tag(
                                "ID").parts[0]
                        for content_part in funcs:
                            if content_part.get_element_by_tag("ID").parts[0] == desired_id:
                                is_found = True
                                break
                        if not is_found:
                            print("Undefined member \"%s\" of struct \"%s\" on line: %s" % (
                                second.get_element_by_tag("ID").parts[0],
                                decl.get_element_by_tag("ID").parts[0],
                                call.line))
                    else:
                        raise Exception(
                            "Incorrect type %s detected. Maybe you didnt check var errors." % decl.type)
                else:
                    print(
                        "Incorrect call exception. Primitive types and arrays haven\'t got members. Line: %s" % call.line)
            else:
                raise Exception("Can't find element with id %s" %
                                prim.parts[0].parts[0])
        else:
            raise Exception("Bad chain call. Check yacc rules.")


# Prints errors with undefined variables or errors with multiple definitions
def check_var_definition(node):

    def get_name(x):
        if x.type == 'VARIABLE':
            return x.parts[1].parts[0], x.type
        elif x.type == 'FUNCTION':
            return x.parts[0].parts[0], x.type
        elif x.type == 'STRUCT':
            return x.parts[0].parts[0], x.type
        elif x.type == 'ID':
            return x.parts[0], x.type
        else:
            raise Exception('Wrong type in check_var_definition function, please debug it')

    ids = get_all_nodes_by_name(node, ['VARIABLE', 'FUNCTION', 'STRUCT', 'ID'])

    funcs = get_all_nodes_by_name(node, 'FUNCTION')

    # removing func arguments from definitions to avoid conflicts
    for func in funcs:
        defs = get_all_nodes_by_name(func.parts[1], 'VARIABLE')
        for d in defs:
            if d in ids:
                ids.remove(d)
                ids.remove(d.parts[1])

    names = {}
    for i in ids:
        name, id_type = get_name(i)
        if not name in names and id_type == 'ID':
            print('Usage of undefined variable "'+name+'", line', i.line)
        elif name in names and id_type != 'ID':
            print('Redundant definition of "'+name+'", line', i.line)
        else: names[name] = id_type


# root - node object
# name - string name or list of names
def get_all_nodes_by_name(root, name):
    nodes = []
    for elem in root.parts:
        if is_node(elem):
            if isinstance(name, str) and elem.type == name:
                nodes.append(elem)
            elif isinstance(name, list) and elem.type in name:
                nodes.append(elem)
            nodes = nodes + get_all_nodes_by_name(elem, name)
    return nodes


def is_type_arithmetic(typename):
    if typename == "int" or typename == "float":
        return True
    return False


def get_nodes_with_id(root):
    elements = []

    def recursive_find(root, elems):
        for elem in root.parts:
            if is_node(elem):
                if elem.type == "VARIABLE" or elem.type == "FUNCTION" or elem.type == "STRUCT" or elem.type == "MARK":
                    elems.append(elem)
                recursive_find(elem, elems)

    recursive_find(root, elements)
    return elements


def find_element_by_id(looked_id):
    global identified
    for el in identified:
        if el.get_element_by_tag("ID").parts[0] == looked_id:
            return el
    return None


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
    if operation_type == "CHAIN_CALL":
        return two
    return "error"


def is_expression(node):
    if is_node(node):
        tnames = ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'IDIVIDE',
                  'LOR', 'BOR', 'LAND', 'BAND', 'LNOT',
                  'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
                  'INCREMENT', 'DECREMENT', 'CHAIN_CALL']
        return node.type in tnames
    return False


def get_atom_type(atom):
    if atom.type == "CONSTANT" or atom.type == "VARIABLE" or atom.type == "ARRAY_ALLOC":
        return atom.get_element_by_tag("DATATYPE").parts[0]
    if atom.type == "ARRAY_ELEMENT":
        id = atom.parts[0].parts[0]
        arr = find_element_by_id(id)
        if not arr is None:
            return arr.get_element_by_tag("DATATYPE").parts[0].replace("[]", "")
    looked_id = None
    if atom.type == "FUNC_CALL":
        looked_id = atom.get_element_by_tag("ID").parts[0]
    elif atom.type == "ID":
        looked_id = atom.parts[0]
    found_elem = find_element_by_id(looked_id)
    if found_elem is None:
        return None
    else:
        return found_elem.get_element_by_tag("DATATYPE").parts[0]


def is_node_atom(node):
    if is_node(node):
        tnames = ['CHAIN_CALL', 'ID', 'FUNC_CALL', 'CONSTANT',
                  'VARIABLE', 'ARRAY_ALLOC', 'ARRAY_ELEMENT']
        return node.type in tnames
    return False


def is_node(elem):
    return type(elem).__name__ == 'Node'


def get_expression_result_type(root):
    if is_expression(root):
        if len(root.parts) == 1:
            first = get_expression_result_type(root.parts[0])
            if first == "end":
                return "end"
            comp_res = compare_expr(first, None, root.type)
            if comp_res == "error":
                print("Expression error: operand has an unsuitable type (%s). Line: %s" % (
                    first, root.parts[0].line))
                return "end"
            return comp_res
        else:

            first = get_expression_result_type(root.parts[0])
            second = get_expression_result_type(root.parts[1])
            if first == "end" or second == "end":
                return "end"
            comp_res = compare_expr(first, second, root.type)
            if comp_res == "error":
                print(
                    "Expression error: operands have unsuitable types (%s, %s). line: %s" % (
                        first, second, root.parts[0].line))
                return "end"
            return comp_res
    if is_node_atom(root):
        return get_atom_type(root)


def check_expression_results(root, has_errors):
    if is_node(root):
        for part in root.parts:
            if is_node(part):
                if part.type == "ASSIGN":
                    expr1 = get_expression_result_type(part.parts[0])
                    expr2 = get_expression_result_type(part.parts[1])
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
                    if part.type == "STRUCT":
                        next_node = part.get_element_by_tag("CONTENT")
                    elif part.type == "FUNCTION":
                        next_node = part.get_element_by_tag("SCOPE")
                    else:
                        next_node = part
                    check_expression_results(next_node, has_errors)


def check_return_types(nodes):
    for node in nodes:
        scope = node.parts[3]
        return_value = node.parts[2].parts[0]
        returns = get_all_nodes_by_name(scope, "RETURN")

        if len(returns) == 0:
            if return_value != "void":
                print(
                    "Return token expected. Function must return a value of type \"%s\"!" % return_value)
        else:
            for val in returns:
                pass


def check_forbidden_definitions(tree):
    functions = get_all_nodes_by_name(tree, 'FUNCTION')
    definitions = []

    if len(functions):
        for func in functions:
            struct_definitions = get_all_nodes_by_name(func, 'STRUCT')

            func_definitions = get_all_nodes_by_name(func, 'FUNCTION')

            definitions += func_definitions
            definitions += struct_definitions

    for d in definitions:
        print('Forbidden definition of', d.type, 'on line', d.line)


def check_inner_commands(tree):
    def check_return(tree, inside_func=False, func_datatype=None):
        if is_node(tree):
            for child in tree.parts:
                if is_node(child) and child.type == 'RETURN':
                    if inside_func:
                        if len(child.parts):
                            if func_datatype == 'void':
                                print(
                                    'You can\'t return value from void function, line', child.line)
                                return
                            return_type = get_expression_result_type(
                                child.parts[0])
                            if return_type != func_datatype:
                                print('You can\'t return', return_type, 'from', func_datatype, 'function, line',
                                      child.line)
                    else:
                        print(
                            'You can\'t use operator "RETURN" outside of a function, line', child.line)
                elif is_node(child):
                    is_func = child.type == 'FUNCTION'
                    datatype = None
                    if func_datatype:
                        datatype = func_datatype
                    elif is_func:
                        datatype = child.parts[2].parts[0]
                    check_return(child, is_func or inside_func, datatype)

    def check_skip_break(tree, inside_cycle):
        if is_node(tree):
            for child in tree.parts:
                if (is_node(child) and (child.type == 'SKIP' or child.type == 'BREAK')) and not inside_cycle:
                    print('You can\'t use operator "' + child.type +
                          '" outside of a cycle, line', child.line)
                elif is_node(child):
                    check_skip_break(child, child.type ==
                                     'WHILE' or inside_cycle)

    check_return(tree, False)
    check_skip_break(tree, False)


def check_func_call(tree):

    calls = get_all_nodes_by_name(tree, 'FUNC_CALL')
    functions = get_all_nodes_by_name(tree, 'FUNCTION')

    for call in calls:
        fun_id = call.parts[0].parts[0]
        fun_def = None
        for fun in functions:
            if fun.parts[0].parts[0] == fun_id:
                fun_def = fun
                break

        if (fun_def):
            types = []
            for arg in fun_def.parts[1].parts:
                types.append(arg.parts[0].parts[0])

            call_args = call.parts[1].parts

            if (len(call_args) != len(types)):
                print('Wrong number of arguments in the call of function "' +
                      fun_id+'", line', call.line)

            for i in range(len(call_args)):
                if get_expression_result_type(call_args[i]) != types[i]:
                    print('Wrong type of an argument "'+call_args[i].parts[0].parts[0] +
                          '" in the call of function "'+fun.parts[0].parts[0]+'", line', call_args[i].line)


def check_funcs_have_returns():
    global main_root
    if main_root is not None:
        funcs = get_all_nodes_by_name(main_root, "FUNCTION")
        for func in funcs:
            ftype = func.get_element_by_tag("DATATYPE")
            scope = func.get_element_by_tag("SCOPE")
            ret = scope.get_element_by_tag("RETURN")
            if ret is None and ftype.parts[0] != "void":
                print("Return error: function with type \"%s\" must return a value. Line: %s" % (ftype.parts[0], func.line))
