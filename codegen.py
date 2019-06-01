## генерация struct
## генерация function
## транслировать дефолтные типы переменных (int -> i32, ...) кроме string
## генерация объявления внутренних переменных (после типов)
## TODO: генерация dowhile, while
## TODO: генерация if, else, elif
## TODO: придумать что делать со string
## генерация инициализации масива
## TODO: транслировать булевы операции (<=,>=, ==, <, >, !, !=, |, &)
## TODO: транслировать математические операции 
## TODO: объявления функций и структур вне main
## TODO: все строки-константы обьявить в начале
from node_utils import *

type_dict = {'int': 'i32', 'float': 'double', 'boolean': 'i8'}

NL = '\n'
TAB = '    '
struct_types = []

arrays = []
variables = []
functions = []
structs = []
buffer_num = 1


def raiseError(x): raise Exception(x)


def skip(x, y):
    x.checked = True
    if not x is None and len(x.childs):
        for child in x.childs:
            child.checked = True
    return None, []


def TODO(x, y): return None, [f'TODO {x.name}']


# Все функции возвращают набор из 1 или более команд,
# последняя в листе команда является ключевой, остальные должны быть расположены выше неё


def llvm_load_value(register_ptr, register_type):
    res_register = register_ptr[:-4]
    global buffer_num
    result = [
        f"{res_register}.{buffer_num} = load {type_dict[register_type]}, {type_dict[register_type]}* {res_register}.ptr",
        f"{res_register}.{buffer_num}"]
    buffer_num += 1
    return register_type, result


def llvm_type(ast, context=None):
    ast.checked = True
    if ast.value == 'string':
        return ['string']  # TODO: придумать как поступать с этим кейсом
    else:
        return [type_dict[ast.value]]


def llvm_value(ast, context=None):
    ast.checked = True
    return [ast.value]


def llvm_variable(ast, context=None):
    ast.checked = True
    ast.childs[1].checked = True
    var_id = ast.get("ID")[0].value
    var_type = ast.get("TYPE")[0].value
    if var_type in struct_types:
        return var_type, [f'%{var_id}.ptr = alloca %struct.{var_type}',
                          f'%{var_id}.ptr']
    else:
        return var_type, [
            f'%{var_id}.ptr = alloca {type_dict[var_type]}',
            f'%{var_id}.ptr'
        ]


def llvm_array_alloc(ast, context=None):
    ast.checked = True
    var_id = ast.childs[0].get("ID")[0].value
    var_type = ast.childs[1].get("TYPE")[0].value
    var_size = ast.childs[1].get("VALUE", nest=True)[0].value

    return var_type, [
        f'%{var_id}.ptr = alloca [{var_size} x {var_type}]',
        f'%{var_id}.ptr'
    ]


def llvm_assign(ast, context=None):
    ast.checked = True
    left = ast.childs[0]
    left.checked = True
    right = ast.childs[1]

    left_type = None
    left_strs = None

    if left.name == 'VARIABLE_ARRAY' and right.name == "ARRAY_ALLOC":
        arr_type, arr_strs = llvm_array_alloc(ast)
        return arr_type, arr_strs
    if left.name == 'CHAIN_CALL':
        left_type, left_strs = llvm_chain_call(left)
    elif left.name == 'VARIABLE':
        left_type, left_strs = llvm_variable(left)
    elif left.name == 'ID':
        left_type, left_strs = llvm_id(left, "ptr")
    elif left.name == 'ARRAY_ELEMENT':
        left_type, left_strs = llvm_array_el(left)

    right_type, right_strs = llvm_expression(right)
    left_ptr = left_strs[-1]
    right_ptr = right_strs[-1]
    return left_type, \
           left_strs[:-1] + \
           right_strs[:-1] + \
           [f"store {type_dict[right_type]} {right_ptr}, {type_dict[left_type]}* {left_ptr}", left_ptr]


def llvm_expression(ast, context=None):
    def recursive_run(node):
        node.checked = True
        if is_node_atom(node):
            expr_type, strs = atom_funcs[node.name](node)
            return expr_type, strs
        elif is_expression(node):
            left_type, left_strs = recursive_run(node.childs[0])
            right_type, right_strs = recursive_run(node.childs[1])
            res_type, res_strs = binary_op_funcs[node.name](left_type, left_strs[-1], right_strs[-1])
            res_strs = left_strs[:-1] + right_strs[:-1] + res_strs
            return res_type, res_strs

    if is_expression(ast) or is_node_atom(ast):
        rtype, strs = recursive_run(ast)
        return rtype, strs
    else:
        raise Exception("llvm_expression cannot process non-expression node.")


def llvm_struct(node, context=None):
    if node.name != "STRUCT":
        raise Exception("This function can't process the node which hasn't got a type STRUCT")
    name = node.childs[0].value
    childs = node.childs[1].childs
    struct_types.append(name)
    node.checked = True
    for memb in node.childs:
        memb.checked = True
    struct_decl = f"%struct.{name} = type " + "{"
    for child in childs:
        child.checked = True
        if child.name == "VARIABLE":
            var_type = type_dict[child.get("TYPE")[0].value]
            struct_decl += f"{var_type}, "
        elif child.name == "ASSIGN":
            variable = child.childs[0]
            if variable.name != "VARIABLE_ARRAY":
                raise Exception("The variable is not VARIABLE_ARRAY")
            array_alloc = child.childs[1]
            array_type = array_alloc.get("TYPE")[0].value
            array_size = array_alloc.get("CONST")[0].get("VALUE")[0].value
            struct_decl += f"[{array_size} x {type_dict[array_type]}], "
        else:
            raise Exception("Unexpected value in structure translate function")
    if len(childs) != 0:
        struct_decl = struct_decl[:-2]
    struct_decl = struct_decl + "}"
    return None, [struct_decl, ""]


def spread_nodes(root):
    if is_node(root):
        if root.name == "FUNCTION":
            functions.append(root)
        elif root.name == "VARIABLE" or root.name == "VARIABLE_ARRAY":
            variables.append(root)
        elif root.name == "STRUCT":
            structs.append(root)
        elif root.name == "ASSIGN" and root.childs[1].name == "ARRAY_ALLOC":
            array_var = root.childs[0]
            array_alloc = root.childs[1]
            array_id = array_var.get("ID")[0].value
            array_type = array_alloc.get("TYPE")[0].value
            array_size = array_alloc.get("VALUE", nest=True)[0].value
            arrays.append({
                "id": array_id,
                "type": array_type,
                "size": array_size
            })
        for child in root.childs:
            spread_nodes(child)


def llvm_return(node, context):
    node.checked = True
    node.childs[0].checked = True
    name, type = get_info(node.childs[0])
    if node.childs[0] != 'CONST':
        type = context[name]
        name = '%' + name

    return type[0], [f'ret {type_dict[type[1]]} {name}', name]


def llvm_func_def(node, context=None):
    f_name, f_type = get_info(node)
    node.checked = True
    for child in node.childs:
        child.checked = True

    args = []
    for arg in node.childs[1].childs:
        name, type = get_info(arg)
        context[name] = type
        args += [f'{llvm_type(arg.childs[0])[0]} %{arg.childs[1].value}']

    commands = recursive_run(node.childs[3], [], context)

    return type_dict[f_type[1]], (
            [f'define {type_dict[f_type[1]]} @{f_name}({", ".join(args)}) {"{"}'] + commands + ['}', f'@{f_name}'])


def recursive_run(node, res, context={}):
    if is_definition(node):
        if node.name == 'ASSIGN':
            name, type = get_info(node.childs[0])
            context[name] = type
        else:
            name, type = get_info(node)
            context[name] = type

    res_type, res_strs = fdict[node.name](node, context)
    res = res + res_strs[:-1]

    for child in node.childs:
        if not child.checked:
            res = recursive_run(child, res, context)
    return res


def create_main_node():
    return Node('FUNCTION', childs=[
        Node('ID', value='main'),
        Node('FUNC_ARGS'),
        Node('TYPE', value='int'),
        Node('SCOPE')], line=0)


def start_codegen(ast):
    init = []
    body = []

    spread_nodes(ast)

    llvm_result = []
    for function in functions:
        llvm_result += recursive_run(function, [])

    for struct in structs:
        llvm_result += recursive_run(struct, [])

    main_func_node = create_main_node()
    ast.parent = main_func_node
    main_func_node.childs[3] = ast
    ast = main_func_node

    llvm_result += recursive_run(ast, [])

    return llvm_result


# ############## BINARY FUNCS ################# #


def llvm_add_func(expr_type, left, right):
    ll_type = type_dict[expr_type]
    operator = 'fadd' if ll_type == 'double' else 'add'
    global buffer_num
    result = [f'%buffer{buffer_num} = {operator} {ll_type} {left}, {right}',
              f'%buffer{buffer_num}']
    buffer_num += 1
    return expr_type, result


def llvm_sub_func(expr_type, left, right):
    ll_type = type_dict[expr_type]
    operator = 'fsub' if ll_type == 'double' else 'sub'
    global buffer_num
    result = [f'%buffer{buffer_num} = {operator} {ll_type} {left}, {right}',
              f'%buffer{buffer_num}']
    buffer_num += 1
    return expr_type, result


def llvm_mul_func(expr_type, left, right):
    ll_type = type_dict[expr_type]
    operator = 'fmul' if ll_type == 'double' else 'mul'
    global buffer_num
    result = [f'%buffer{buffer_num} = {operator} {ll_type} {left}, {right}',
              f'%buffer{buffer_num}']
    buffer_num += 1
    return expr_type, result


def llvm_div_func(expr_type, left, right):
    ll_type = type_dict[expr_type]
    operator = 'fdiv' if ll_type == 'double' else 'sdiv'
    global buffer_num
    result = [f'%buffer{buffer_num} = {operator} {ll_type} {left}, {right}',
              f'%buffer{buffer_num}']
    buffer_num += 1
    return expr_type, result


def llvm_mod_func(expr_type, left, right):
    ll_type = type_dict[expr_type]
    operator = 'frem' if ll_type == 'double' else 'srem'
    global buffer_num
    result = [f'%buffer{buffer_num} = {operator} {ll_type} {left}, {right}',
              f'%buffer{buffer_num}']
    buffer_num += 1
    return expr_type, result


# ########################  ATOM FUNCS ########################## #

# Atoms are the nodes with types: ID, CHAIN_CALL, FUNC_CALL, CONST, ARRAY_ELEMENT

def llvm_id(ast, context=None):
    # if context is None variable is needed to load (returns value, not ptr), else returns ptr of variable
    if is_node(ast) and ast.name == "ID":
        var = find_node_by_id(variables, ast.value)
        var_type = var.get("TYPE")[0].value
        if context is None:
            var_type, buffer_strs = llvm_load_value(f'%{ast.value}.ptr', var_type)
        else:
            buffer_strs = [f"%{ast.value}.ptr"]
        return var_type, buffer_strs
    else:
        raise Exception("llvm_id cannot process node with different type from ID.")


def llvm_const(ast, context=None):
    if is_node(ast) and ast.name == "CONST":
        return ast.get("TYPE")[0].value, [f"{ast.get('VALUE')[0].value}"]
    else:
        raise Exception("llvm_const cannot process node with different type from CONST.")


def llvm_chain_call(ast, context=None):
    var_id = ast.childs[0].value
    struct_member_name = ast.childs[1].value if (ast.childs[1].name == "ID") else ast.childs[1].get("ID")[0].value
    struct_var = find_node_by_id(variables + functions, var_id)
    struct_id = struct_var.get("TYPE")[0].value
    struct = find_node_by_id(structs, struct_id)
    struct_members = struct.childs[1].childs
    member_index = -1
    struct_member = None
    for ind, member in enumerate(struct_members):
        if member.get("ID", nest=True)[0].value == struct_member_name:
            member_index = ind
            struct_member = member
            break
    if member_index > -1:
        global buffer_num
        result = [f"%{var_id}.{struct_member_name}.{buffer_num}.ptr = getelementptr inbounds %struct.{struct_id}, " +
                  f"%struct.{struct_id}* %{var_id}.ptr, i32 0, i32 {member_index}"]
        if struct_member.name == "ASSIGN":
            array_register = f"%{var_id}.{struct_member_name}.{buffer_num}"
            array_alloc = struct_member.childs[1]
            array_size = array_alloc.get("VALUE")[0].value
            array_type = array_alloc.childs[0].value
            element_context = {"id": array_register,
                               "type": array_type,
                               "size": array_size}
            element_type, strs = llvm_array_el(struct_member, element_context)
            result = result + strs
            buffer_num += 1
            return element_type, result
        elif struct_member.name == "VARIABLE":
            result.append(f"%{var_id}.{struct_member_name}.{buffer_num}.ptr")
            buffer_num += 1
            return struct_member.get("TYPE")[0].value, result
        else:
            print(f"Incorrect member of struct {struct_id}")

    else:
        print(f"Member of struct {struct_id} with id {struct_member_name} not found")

    return None


def llvm_array_el(ast, context=None):
    # context != None means that the function has been called from chain call.
    # in this case context has a structure {"id": array_register, "type": array_type, "size": array_size}
    if context is None:
        var_id = ast.get("ID")[0].value
        array_var = find_array_by_id(arrays, var_id)
    else:
        array_var = context
        var_id = context["id"]
    ll_type = f"[{array_var['size']} x {type_dict[array_var['type']]}]"
    buff_type, strs = llvm_expression(ast.childs[1])
    if "%" in strs[-1]:
        loaded_type, loaded_strs = llvm_load_value(strs[-1], buff_type)
    else:
        loaded_strs = strs
    global buffer_num
    result = strs[:-1] + loaded_strs[:-1] + [
        f"%{var_id}.{buffer_num}.ptr = getelementptr inbounds {ll_type}, {ll_type}* %{var_id}.ptr, i32 0, i32 {loaded_strs[-1]}",
        f"%{var_id}.{buffer_num}.ptr"]
    buffer_num += 1
    return array_var["type"], result


def llvm_func_call(ast, context=None):
    func_id = ast.get("ID")[0].value
    func_decl = find_node_by_id(functions, func_id)
    func_type = func_decl.get("TYPE")[0].value
    call_args = ast.get("CALL_ARGS")[0].childs
    ll_call_args = ""
    result_strs = []
    for arg in call_args:
        arg_type, arg_strs = llvm_expression(arg)
        result_strs = result_strs + arg_strs[:-1]
        ll_call_args += f"{type_dict[arg_type]} {arg_strs[-1]}, "
    if len(call_args) != 0:
        ll_call_args = ll_call_args[:-2]
    call_result = [f"%{func_id}.{buffer_num} = call {type_dict[func_type]} @{func_id}({ll_call_args})"]
    result_strs = result_strs + call_result + [f"%{func_id}.{buffer_num}"]
    return func_type, result_strs


binary_op_funcs = {'PLUS': llvm_add_func,
                   'MINUS': llvm_sub_func,
                   'TIMES': llvm_mul_func,
                   'DIVIDE': llvm_div_func}

atom_funcs = {'ID': llvm_id,
              'CHAIN_CALL': llvm_chain_call,
              'FUNC_CALL': llvm_func_call,
              'CONST': llvm_const,
              'ARRAY_ELEMENT': llvm_array_el}

fdict = {
    'ERROR': lambda x, y: raiseError('error in ast'),
    'FUNCTION': llvm_func_def,
    'STRUCT': llvm_struct, 'CONTENT': TODO,  # ?
    'VALUE': skip,
    'TYPE': skip,
    'CONST': llvm_const,
    'ID': llvm_id,
    'ARRAY_ELEMENT': llvm_array_el,
    'VARIABLE': llvm_variable,
    'VARIABLE_ARRAY': skip,  # TODO: убратть возможность определения массива без аллокации
    'ARRAY_ALLOC': skip,
    'ASSIGN': llvm_assign,
    'SCOPE': TODO,
    'FUNC_ARGS': TODO,
    'RETURN': llvm_return,
    'EMPTY_STATEMENT': skip,
    'PLUS': llvm_expression,
    'MINUS': llvm_expression,
    'TIMES': llvm_expression,
    'DIVIDE': llvm_expression,
    'MODULO': llvm_expression,
    'IDIVIDE': llvm_expression,
    'BOR': TODO,
    'BAND': TODO,
    'LT': TODO,
    'GT': TODO,
    'GE': TODO,
    'LE': TODO,
    'NE': TODO,
    'EQ': TODO,
    'LOR': TODO,
    'LAND': TODO,
    'CHAIN_CALL': llvm_chain_call,
    'IF_CONDITION': TODO,
    'IF': TODO,
    'CONDITION': TODO,
    'ELIF': TODO,
    'ELSE': TODO,
    'DO_WHILE': TODO,
    'WHILE': TODO,
    'MARK': TODO,
    'GOTO': TODO,
    'CALL_ARGS': TODO,
    'FUNC_CALL': TODO
}
