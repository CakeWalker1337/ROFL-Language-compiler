## генерация struct
## генерация function
## транслировать дефолтные типы переменных (int -> i32, ...) кроме string
## генерация объявления внутренних переменных (после типов)
## TODO: генерация dowhile, while
## TODO: генерация if, else, elif
## TODO: придумать что делать со string
## TODO: приведение типов (int-float, float-int, ... дописать)
## TODO: генерация инициализации масива
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


def skip(x, y): return []


def TODO(x, y): return [f'TODO {x.name}']


# Все функции возвращают набор из 1 или более команд,
# последняя в листе команда является ключевой, остальные должны быть расположены выше неё


def llvm_load_value(register_ptr, register_type):
    res_register = register_ptr[:-4]
    return [f"{res_register} = load {type_dict[register_type]}, {type_dict[register_type]}* {res_register}",
            f"{res_register}"]


def llvm_type(ast, context=None):
    ast.checked = True
    if ast.value == 'string':
        return ['string']  # TODO: придумать как поступать с этим кейсом
    elif ast.value in struct_types:
        return f"struct.{ast.value}"
    else:
        return [f'%{type_dict[ast.value]}']


def llvm_value(ast, context=None):
    ast.checked = True
    return [ast.value]


def llvm_const(ast, context=None):
    ast.checked = True
    if ast.parent.name == 'SCOPE': return []
    value = llvm_value(ast.childs[1])[0]
    type = llvm_type(ast.childs[0])[0]
    if type == 'string':
        return []
    elif type == 'i8':
        value = '1' if value == 'true' else '0'
    return [value]


def llvm_id(ast, context=None):
    ast.checked = True
    if ast.parent.name == 'SCOPE': return []
    name = get_info(ast)[0]
    return [f'%{ast.value}']


def llvm_array_el(ast, context):
    ast.checked = True
    ast.childs[0].checked = True
    name = get_info(ast)[0]
    type = type_dict[context[name][1]]
    return [
        f'%arr.ptr = getelementptr inbounds {type}, {type}* %{name}, i32 0 {llvm_type(ast.childs[1].childs[0])} {fdict[ast.childs[1].name](ast.childs[1])[0]}',
        f'%elem = load {type}, {type}* %arr.ptr',
        f'%elem']  # TODO: придумать именование для выбранного элемента массива


def llvm_variable(ast, context=None):
    ast.checked = True
    ast.childs[1].checked = True
    name = get_info(ast)[0]
    type = llvm_type(ast.childs[0])
    if "struct" in type:
        return [f'%{name}.ptr = alloca %{type}']
    else:
        return [
            f'%{name}.ptr = alloca {type}',
            f'%{name} = load {type}, {type}* %{name}.ptr'
        ]


def llvm_array_alloc(ast, context=None):
    ast.checked = True
    type = llvm_type(ast.childs[0])[0]
    size = llvm_value(ast.childs[1].childs[1])[0]
    return [
        f'alloca [{size} x {type}]'
    ]


def llvm_assign(ast, context=None):
    ast.checked = True
    left = ast.childs[0]
    left.checked = True
    right = ast.childs[1]

    if left.name == 'VARIABLE_ARRAY':
        name = get_info(left)[0]
        return [f'%{name} = {llvm_array_alloc(right)[0]}']
    elif left.name == 'VARIABLE':
        # TODO: скорее всего будет куча задроченных кейсов
        return []





# TODO: Доделать обработку выражений
def llvm_expression(ast, context=None):
    def recursive_run(node):
        if is_node_atom(node):
            expr_type, strs = atom_funcs[node.name](node)
            return expr_type, strs
        elif is_expression(node):
            left_type, left_strs = recursive_run(node.childs[0])
            right_type, right_strs = recursive_run(node.childs[1])
            res_type, res_strs = binary_op_funcs[node.name](left_type, left_strs[-1], right_strs[-1])
            res_strs = left_strs[:-1] + right_strs[:-1] + res_strs
            return res_type, res_strs

    if is_expression(ast):
        rtype, strs = recursive_run(ast)
        return rtype, strs
    else:
        raise Exception("llvm_expression cannot process non-expression node.")


def llvm_struct(node, context=None):
    if node.name != "STRUCT":
        raise Exception("This function can't process the node which hasn't got a type STRUCT")
    name = node.childs[0].value
    childs = node.childs[1].childs
    structs.append(node)
    struct_types.append(name)

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
    struct_decl = struct_decl[:-2] + "}"
    return [struct_decl]


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


def start_codegen(ast, context={}):
    if ast is None: raise Exception('ast is None')

    if is_definition(ast):
        name, type = get_info(ast)
        context[name] = type

    result = fdict[ast.name](ast, context)

    for child in ast.childs:
        if not child.checked:
            result += start_codegen(child, context)
        else:
            start_codegen(child, context)
    return result


# ############## BINARY FUNCS ################# #


def llvm_add_func(expr_type, left, right):
    ll_type = type_dict[expr_type]
    operator = 'fadd' if ll_type == 'double' else 'add'
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


# atom_funcs = {'ID': llvm_id,
#               'CHAIN_CALL': llvm_chain_call,
#               'FUNC_CALL': llvm_func_call,
#               'CONST': llvm_const,
#               'ARRAY_ELEMENT': llvm_array_el}


def llvm_id(ast):
    if is_node(ast) and ast.name == "ID":
        var = find_node_by_id(variables, ast.value)
        return var.get("TYPE")[0].value, [f'%{ast.name}.ptr']
    else:
        raise Exception("llvm_id cannot process node with different type from ID.")


def llvm_const(ast):
    if is_node(ast) and ast.name == "ID":
        return ast.get("TYPE")[0].value, [f"{ast.get('VALUE')[0].value}"]
    else:
        raise Exception("llvm_const cannot process node with different type from CONST.")


def llvm_chain_call(ast, context=None):
    struct_member_name = ast.childs[1].value if (ast.childs[1].name == "ID") else ast.childs[1].get("ID")[0].value
    struct_var = find_node_by_id(variables + functions, ast.childs[0].value)
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
        result = [f"%struct.{struct_id}.{struct_member_name}.ptr = getelementptr inbounds %struct.{struct_id}, " +
                  f"%struct.{struct_id}* %struct.{struct_id}.ptr, i32 0, i32 {member_index}"]
        if struct_member.name == "ASSIGN":
            array_register = f"%struct.{struct_id}.{struct_member_name}.ptr"
            array_alloc = struct_member.childs[1]
            array_size = array_alloc.get("VALUE")[0].value
            array_type = type_dict[array_alloc.childs[0].value]
            ll_type = f"[{array_size} x {array_type}]"
            ll_element_index = llvm_expression(ast.childs[1])

            global buffer_num

            result.append(
                f"%buffer{buffer_num}.ptr = getelementptr inbounds ll_type, ll_type* {array_register}, i64 0, i64 {ll_element_index}")
            result.append(f"%buffer{buffer_num}.ptr")
            buffer_num += 1
            return result
        elif struct_member.name == "VARIABLE":
            result.append(f"%struct.{struct_id}.{struct_member_name}.ptr")
            return result
        else:
            print(f"Incorrect member of struct {struct_id}")

    else:
        print(f"Member of struct {struct_id} with id {struct_member_name} not found")

    return None


def llvm_array_el(ast, context):
    if context is None:
        var_id = ast.get("ID")[0].value
        array_var = find_array_by_id(arrays, var_id)
        ll_type = f"[{array_var['size']} x {type_dict[array_var['type']]}]"
        buff_type, strs = llvm_expression(ast.childs[1])
        loaded = llvm_load_value(strs[-1], buff_type)
        result = strs[:-1] + loaded[:-1] + [
            f"%{var_id}.{buffer_num}.ptr = getelementptr inbounds {ll_type}, {ll_type}* %{var_id}.ptr, i32 0, i32 {loaded[-1]}",
            f"%{var_id}.{buffer_num}.ptr"]
        return array_var["type"], result
    else:
        # TODO: Доделать обработку элемента массива, если он из чейнкола
        pass


def llvm_func_call():
    pass


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
    'FUNCTION': skip,
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
    'RETURN': TODO,
    'EMPTY_STATEMENT': skip,
    'PLUS': TODO,
    'MINUS': TODO,
    'TIMES': TODO,
    'DIVIDE': TODO,
    'MODULO': TODO,
    'IDIVIDE': TODO,
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
    'LNOT': TODO,
    'CHAIN_CALL': llvm_chain_call,
    'IF_CONDITION': TODO,
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
