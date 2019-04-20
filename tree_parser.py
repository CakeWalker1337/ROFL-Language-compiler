from yacc import Node

identified = []
main_root = None


def init_semantic(root):
    global identified, main_root
    identified = get_nodes_with_id(root)
    main_root = root


def parse_chain_call_error(node):
    pass


def parse_var_error(node, variables):
    childs = []
    if is_node(node):
        if node.type == 'VARIABLE':
            if node.parts[1].parts[0] in variables:
                print('Redundant definition of "'+node.parts[1]+'" on line', node.line)
            else:
                variables[node.parts[1].parts[0]] = node.parts[0].parts[0]
        elif node.type == 'ID':
            if not node.parts[0] in variables:
                print('Undefined identificator "'+node.parts[0]+'" on line', node.line)
        elif node.type == 'STRUCT':
            name = node.parts[0].parts[0]
            if name in variables:
                print('Redundant definition of "'+name+'" on line', node.line)
            else:
                variables[name] = 'struct'
                childs = node.get_element_by_tag("CONTEXT").parts if node.get_element_by_tag("CONTEXT") else []
        elif node.type == 'FUNCTION':
            name = node.parts[0].parts[0]
            if name in variables:
                print('Redundant definition of "'+name+'" on line', node.line)
            else:
                variables[name] = 'function'
                childs = node.get_element_by_tag("SCOPE").parts
        else:
            childs = node.parts
        for child in childs:
            parse_var_error(child, variables)


def get_all_nodes_by_name(root, name, nodes):
    for elem in root.parts:
        if is_node(elem):
            if elem.type == name:
                nodes.append(elem)
            get_all_nodes_by_name(elem, name, nodes)


def is_type_arithmetic(typename):
    if typename == "int" or typename == "float":
        return True
    return False


def get_nodes_with_id(root):
    elements = []

    def recursive_find(root, elems):
        for elem in root.parts:
            if is_node(elem):
                if elem.type == "VARIABLE" or elem.type == "FUNCTION" or elem.type == "STRUCT":
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


def compare_expr(one, two, operation_type):
    if one == "null" or two == "null":
        return "error"
    if one == "array" or two == "array":
        return "error"
    if one == "void" or two == "void":
        return "error"
    if one is None:
        if (two == "boolean") | (
                is_type_arithmetic(two) and (operation_type == "INCREMENT" or operation_type == "DECREMENT")):
            return two
        return "error"
    if two is None:
        if (one == "boolean") | (
                is_type_arithmetic(one) and (operation_type == "INCREMENT" or operation_type == "DECREMENT")):
            return one
        return "error"
    if one == "string" and operation_type == "PLUS":
        return "string"
    if is_type_arithmetic(one) and is_type_arithmetic(two):
        return "float"
    if one == two:
        return one
    if operation_type == "CHAIN_CALL":
        return two
    return "error"


def is_expression(node):
    if is_node(node):
        tnames = ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'IDIVIDE',
                  'LOR', 'BOR', 'LAND', 'BAND', 'LNOT',
                  'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
                  'INCREMENT', 'DECREMENT']
        return node.type in tnames
    return False


def get_atom_type(atom):
    if atom.type == "CHAIN_CALL":
        return get_atom_type(atom.parts[len(atom.parts) - 1])
    if atom.type == "CONSTANT":
        return atom.get_element_by_tag("DATATYPE").parts[0]
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
        tnames = ['CHAIN_CALL', 'ID', 'FUNC_CALL', 'CONSTANT']
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
            comp_res = compare_expr(first, None, root)
            if comp_res == "error":
                print("Expression error: operand has an unsuitable type (%s)." % first)
                return "end"
            return comp_res
        else:
            first = get_expression_result_type(root.parts[0])
            second = get_expression_result_type(root.parts[1])
            if first == "end" or second == "end":
                return "end"
            comp_res = compare_expr(first, second, root)
            if comp_res == "error":
                print(
                    "Expression error: operands have unsuitable types (%s, %s). line: %s" % (first, second, root.parts[0].line))
                return "end"
            return comp_res
    if is_node_atom(root):
        return get_atom_type(root)
    print("its none")


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


def check_forbidden_definitions(tree):
    functions = []
    definitions = []
    get_all_nodes_by_name(tree, 'FUNCTION', functions)
    if (len(functions)):
        for func in functions:
            struct_definitions = []
            get_all_nodes_by_name(func, 'STRUCT', struct_definitions)
            func_definitions = []
            get_all_nodes_by_name(func, 'FUNCTION', func_definitions)
            definitions += func_definitions
            definitions += struct_definitions
    
    for d in definitions:
        print('Forbidden definition of', d.type, 'on line', d.line)

