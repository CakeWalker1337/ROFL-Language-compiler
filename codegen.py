from node_utils import *

type_dict = {'int': 'i32', 'float': 'double', 'boolean': 'i1', 'string': 'i8*', 'void': 'void'}
cmp_dict = {'LT': "slt", 'LE': "sle", 'GT': "sgt", 'GE': "sge", 'EQ': "eq", 'NE': "ne"}
NL = '\n'
TAB = '    '
struct_types = []
const_str_num = 1
strings = []
arrays = []
variables = []
functions = []
structs = []
buffer_num = 1
condition_counter = 0
LABEL = 'lab..'
arrays_from_func = []


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
    res_register = register_ptr
    if register_ptr[-4:] == ".ptr":
        res_register = register_ptr[:-4]
    global buffer_num
    ll_type = llvm_type_from_string(register_type)
    result = [
        f"{res_register}.{buffer_num} = load {ll_type}, {ll_type}* {res_register}.ptr",
        f"{res_register}.{buffer_num}"]
    buffer_num += 1
    return register_type, result


def llvm_type(ast, context=None):
    ast.checked = True
    if ast.value in struct_types:
        return [f'%struct.{ast.value}']
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
    if ast.name == "VARIABLE_ARRAY":
        var_type = var_type + "[]"
    ll_type = llvm_type_from_string(var_type)
    return var_type, [
        f'%{var_id}.ptr = alloca {ll_type}',
        f'%{var_id}.ptr'
    ]


def llvm_array_alloc(ast, context=None):
    ast.checked = True
    var_id = ast.childs[0].get("ID")[0].value
    var_type = ast.childs[1].get("TYPE")[0].value
    var_size = ast.childs[1].get("VALUE", nest=True)[0].value
    ll_type = llvm_type_from_string(var_type)
    return var_type, [
        f'%{var_id}.ptr = alloca [{var_size} x {ll_type}]',
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
        left_type, left_strs = llvm_chain_call(left, True)
    elif left.name == 'VARIABLE' or left.name == "VARIABLE_ARRAY":
        left_type, left_strs = llvm_variable(left)
    elif left.name == 'ID':
        left_type, left_strs = llvm_id(left, "ptr")
    elif left.name == 'ARRAY_ELEMENT':
        left_type, left_strs = llvm_array_el(left)

    right_type, right_strs = llvm_expression(right)
    left_ptr = left_strs[-1]
    right_ptr = right_strs[-1]
    left_ll_type = llvm_type_from_string(left_type)
    right_ll_type = llvm_type_from_string(right_type)
    return left_type, \
           left_strs[:-1] + \
           right_strs[:-1] + \
           [f"store {right_ll_type} {right_ptr}, {left_ll_type}* {left_ptr}", left_ptr]


def llvm_expression(ast, context=None):
    def recursive_run(node):
        node.checked = True
        if is_node_atom(node):
            expr_type, strs = atom_funcs[node.name](node, context)
            # for cases where
            if len(strs[-1]) >= 4 and strs[-1][-4:] == ".ptr" and "[]" not in expr_type:
                expr_type, load_strs = llvm_load_value(strs[-1], expr_type)
                strs = strs[:-1] + load_strs
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
            ll_array_type = f"[{array_size} x {type_dict[array_type]}]"
            struct_decl += f"{ll_array_type}, "
        else:
            raise Exception("Unexpected value in structure translate function")
    if len(childs) != 0:
        struct_decl = struct_decl[:-2]
    struct_decl = struct_decl + "}"
    return None, [struct_decl, ""]


def init_constants():
    result = ['declare i32 @printf(i8*, ...)']
    for s in strings:
        id = s["id"]
        size = s["size"]
        value = s["value"]
        result.append(f'{id} = private unnamed_addr constant [{size} x i8] c\"{value}\\00\", align 1')
    return result


def collect_local_nodes(root):
    if is_node(root):
        if root.name == "VARIABLE" or root.name == "VARIABLE_ARRAY":
            variables.append(root)
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
            collect_local_nodes(child)


def spread_nodes(root):
    if is_node(root):
        if root.name == "FUNCTION":
            functions.append(root)
        elif root.name == "VARIABLE" or root.name == "VARIABLE_ARRAY":
            variables.append(root)
        elif root.name == "STRUCT":
            structs.append(root)
            struct_types.append(root.get("ID")[0].value)
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
        elif root.name == "CONST" and root.get("TYPE")[0].value == "string":
            const_type = root.get("TYPE")[0].value
            const_value = root.get("VALUE")[0].value
            global const_str_num

            strings.append({
                "id": f"@.str.{const_str_num}",
                "value": const_value,
                "size": len(const_value) + 1,
            })
            const_str_num += 1
        for child in root.childs:
            spread_nodes(child)


def llvm_return(node, context):
    node.checked = True
    if len(node.childs) == 0 and node.value is None:
        return "void", ['ret void', "remove_it"]
    node.childs[0].checked = True
    expr_type, expr_strs = llvm_expression(node.childs[0])
    # if node.childs[0] != 'CONST':
    #     type = context[name]
    #     name = '%' + name
    ll_type = llvm_type_from_string(expr_type)
    return expr_type, expr_strs[:-1] + [f'ret {ll_type} {expr_strs[-1]}', expr_strs[-1]]


def llvm_type_from_string(str_type):
    if "[]" in str_type:
        str_type = str_type.replace("[]", '')
        if str_type in struct_types:
            return f"%struct.{str_type}*"
        else:
            return f"{type_dict[str_type]}*"
    else:
        if str_type in struct_types:
            return f"%struct.{str_type}"
        else:
            return f"{type_dict[str_type]}"


def llvm_func_def(node, context=None):
    f_name, f_type = get_info(node)
    node.checked = True
    for child in node.childs:
        child.checked = True

    args = []
    allocs, stores = [], []
    global arrays_from_func, arrays, variables
    arrays = []
    variables = []
    arrays_from_func = []
    collect_local_nodes(node)
    for arg in node.childs[1].childs:
        name, type = get_info(arg)
        context[name] = type
        additive_type = ""
        additive_name = ""
        if arg.name == "VARIABLE_ARRAY":
            additive_type = "*"
            additive_name = ".ptr"
            arrays_from_func.append({"id": name, "type": type[1]})
        else:
            allocs.append(f'%{name}.ptr = alloca {llvm_type(arg.childs[0])[0]}')
            stores.append(f'store {llvm_type(arg.childs[0])[0]} %{name}, {llvm_type(arg.childs[0])[0]}* %{name}.ptr')
        args += [f'{llvm_type(arg.childs[0])[0]}{additive_type} %{arg.childs[1].value}{additive_name}']

    commands = allocs + stores + recursive_run(node.childs[3], [], context)
    if f_name == "main":
        commands += ["ret i32 0"]
    else:
        f_name = f"func.{f_name}"
    ll_type = llvm_type_from_string(f_type[1])
    return f_type[1], (
            [f'define {ll_type} @{f_name}({", ".join(args)}) {"{"}'] + commands + ['}', f'@{f_name}'])


def set_checked(node):
    if not node is None:
        node.checked = True
        for child in node.childs:
            set_checked(child)


def llvm_condition(node, context={}):
    global condition_counter
    result = []

    type, cond_results = llvm_cond_if(node.childs[0], context)
    condition_counter += 3
    result += cond_results[:-1]
    cond_close_label = cond_results[-1]
    context['#cond.close'] = cond_close_label

    if len(node.childs) > 1:
        for i in range(1, len(node.childs)):
            child = node.childs[i]
            # вместо context был cond_close_label, возможна ошибка
            type, cond_results = fdict[child.name](child, context)
            condition_counter += 2
            result += cond_results[:-1]

    set_checked(node)

    return None, result + [f'br label %{cond_close_label}', f'{cond_close_label}:', None]


def llvm_cond_if(node, context={}):
    res_type, result = llvm_expression(node.childs[0].childs[0])
    expr_result = result[-1]
    inner_commands = recursive_run(node.childs[1], [], context)

    return 'label', result[:-1] + [
        f'br {type_dict[res_type]} {expr_result}, label %{LABEL}{condition_counter}, label %{LABEL}{condition_counter+1}',
        f'{LABEL}{condition_counter}:'
    ] + inner_commands + [
               f'br label %{LABEL}{condition_counter+2}',
               f'{LABEL}{condition_counter+1}:',
               f'{LABEL}{condition_counter+2}'
           ]


def llvm_cond_elif(node, context={}):
    # context is the dictionary with '#cond.close' name
    cond_close_label = context['#cond.close']
    res_type, result = llvm_expression(node.childs[0].childs[0])
    expr_result = result[-1]
    inner_commands = recursive_run(node.childs[1], [], context)

    return 'label', result[:-1] + [
        f'br {type_dict[res_type]} {expr_result}, label %{LABEL}{condition_counter}, label %{LABEL}{condition_counter+1}',
        f'{LABEL}{condition_counter}:'
    ] + inner_commands + [
               f'br label %{cond_close_label}',
               f'{LABEL}{condition_counter+1}:',
               None
           ]


def llvm_cond_else(node, context={}):
    # context is the dictionary with '#cond.close' name
    cond_close_label = context['#cond.close']
    inner_commands = recursive_run(node.childs[0], [], context)

    return 'label', [
        f'br label %{LABEL}{condition_counter}',
        f'{LABEL}{condition_counter}:'
    ] + inner_commands + [
               f'br label %{cond_close_label}',
               f'{LABEL}{condition_counter+1}:',
               None
           ]


def llvm_while(node, context):
    global condition_counter
    res_type, result = llvm_expression(node.childs[0].childs[0])
    expr_result = result[-1]
    condition_label_num, start_label_num, end_label_num = condition_counter, condition_counter + 1, condition_counter + 2
    condition_counter += 3
    context['#begin'] = f'{LABEL}{start_label_num}'
    context['#end'] = f'{LABEL}{end_label_num}'
    inner_commands = recursive_run(node.childs[1], [], context)
    set_checked(node)
    cycle_cond = f'br {type_dict[res_type]} {expr_result}, label %{LABEL}{start_label_num}, label %{LABEL}{end_label_num}'

    ret = 'label', [
        f'br label %{LABEL}{condition_label_num}',
        f'{LABEL}{condition_label_num}:'] + result[:-1] + [
              cycle_cond,
              f'{LABEL}{start_label_num}:'
          ] + inner_commands + [
              f'br label %{LABEL}{condition_label_num}',
              f'{LABEL}{end_label_num}:',
              None
          ]

    condition_counter += 2
    return ret


def llvm_do_while(node, context):
    global condition_counter
    res_type, result = llvm_expression(node.childs[1].childs[0])
    expr_result = result[-1]
    start_label_num, end_label_num = condition_counter, condition_counter + 1
    condition_counter += 2
    context['#begin'] = f'{LABEL}{start_label_num}'
    context['#end'] = f'{LABEL}{end_label_num}'
    inner_commands = recursive_run(node.childs[0], [], context)
    set_checked(node)
    cycle_cond = f'br {type_dict[res_type]} {expr_result}, label %{LABEL}{start_label_num}, label %{LABEL}{end_label_num}'

    ret = 'label', [
        f'br label %{LABEL}{start_label_num}',
        f'{LABEL}{start_label_num}:'
    ] + inner_commands + result[:-1] + [
              cycle_cond,
              f'{LABEL}{end_label_num}:',
              None
          ]

    return ret


def llvm_skip(node, context=None):
    # context = {'#begin': start_label, '#end': end_label}
    return None, [f'br label %{context["#begin"]}', None]


def llvm_break(node, context=None):
    # context = {'#begin': start_label, '#end': end_label}
    return None, [f'br label %{context["#end"]}', None]


def llvm_mark(node, context=None):
    set_checked(node)
    name = node.childs[0].value
    return 'label', [
        f'br label %{name}',
        f'{name}:',
        name
    ]


def llvm_goto(node, context=None):
    set_checked(node)
    name = node.value
    return None, [
        f'br label %{name}',
        None
    ]


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

    llvm_result += [""]

    for struct in structs:
        llvm_result += recursive_run(struct, [])

    llvm_result += [""]

    for function in functions:
        llvm_result += recursive_run(function, [])

    llvm_result += [""]

    main_func_node = create_main_node()
    ast.parent = main_func_node
    main_func_node.childs[3] = ast
    ast = main_func_node

    llvm_result += recursive_run(ast, [])

    return llvm_result + [""] + init_constants()


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


# ############### LOGIC OPERATIONS ################ #


def llvm_and_func(expr_type, left, right):
    ll_type = type_dict[expr_type]
    global buffer_num
    result = [f'%buffer{buffer_num} = and {ll_type} {left}, {right}',
              f'%buffer{buffer_num}']
    buffer_num += 1
    return 'boolean', result


def llvm_or_func(expr_type, left, right):
    ll_type = type_dict[expr_type]
    global buffer_num
    result = [f'%buffer{buffer_num} = or {ll_type} {left}, {right}',
              f'%buffer{buffer_num}']
    buffer_num += 1
    return 'boolean', result


def llvm_gt_func(expr_type, left, right):
    ll_type = type_dict[expr_type]
    operator = 'fcmp' if ll_type == 'double' else 'icmp'
    global buffer_num
    result = [f'%buffer{buffer_num} = {operator} sgt {ll_type} {left}, {right}',
              f'%buffer{buffer_num}']
    buffer_num += 1
    return 'boolean', result


def llvm_ge_func(expr_type, left, right):
    ll_type = type_dict[expr_type]
    operator = 'fcmp' if ll_type == 'double' else 'icmp'
    global buffer_num
    result = [f'%buffer{buffer_num} = {operator} sge {ll_type} {left}, {right}',
              f'%buffer{buffer_num}']
    buffer_num += 1
    return 'boolean', result


def llvm_lt_func(expr_type, left, right):
    ll_type = type_dict[expr_type]
    operator = 'fcmp' if ll_type == 'double' else 'icmp'
    global buffer_num
    result = [f'%buffer{buffer_num} = {operator} slt {ll_type} {left}, {right}',
              f'%buffer{buffer_num}']
    buffer_num += 1
    return 'boolean', result


def llvm_le_func(expr_type, left, right):
    ll_type = type_dict[expr_type]
    operator = 'fcmp' if ll_type == 'double' else 'icmp'
    global buffer_num
    result = [f'%buffer{buffer_num} = {operator} sle {ll_type} {left}, {right}',
              f'%buffer{buffer_num}']
    buffer_num += 1
    return 'boolean', result


def llvm_eq_func(expr_type, left, right):
    ll_type = type_dict[expr_type]
    operator = 'fcmp' if ll_type == 'double' else 'icmp'
    global buffer_num
    result = [f'%buffer{buffer_num} = {operator} eq {ll_type} {left}, {right}',
              f'%buffer{buffer_num}']
    buffer_num += 1
    return 'boolean', result


def llvm_ne_func(expr_type, left, right):
    ll_type = type_dict[expr_type]
    operator = 'fcmp' if ll_type == 'double' else 'icmp'
    global buffer_num
    result = [f'%buffer{buffer_num} = {operator} ne {ll_type} {left}, {right}',
              f'%buffer{buffer_num}']
    buffer_num += 1
    return 'boolean', result


# ########################  ATOM FUNCS ########################## #

# Atoms are the nodes with types: ID, CHAIN_CALL, FUNC_CALL, CONST, ARRAY_ELEMENT

def llvm_id(ast, context=None):
    # if context is None variable is needed to load (returns value, not ptr), else returns ptr of variable
    if is_node(ast) and ast.name == "ID":
        is_array = False

        var = find_array_by_id(arrays, ast.value)
        if var is not None:
            var_type = var['type']
            is_array = True
        else:
            var = find_node_by_id(variables, ast.value)
            var_type = var.get("TYPE")[0].value
            if var.name == "VARIABLE_ARRAY":
                is_array = True
                var_type = var_type + "[]"
        if context is None and not is_array:
            var_type, buffer_strs = llvm_load_value(f'%{ast.value}.ptr', var_type)
        else:
            if is_array:
                arr = find_array_by_id(arrays_from_func, ast.value)
                global buffer_num
                if arr is None:
                    lltype = llvm_type_from_string(var['type'])
                    var_type = var['type'] + "[]"
                    final_type = f"[{var['size']} x {lltype}]"
                    array_load = [
                        f"%{ast.value}.{buffer_num}.ptr = getelementptr inbounds {final_type}, {final_type}* %{ast.value}.ptr, i32 0, i32 0",
                        f"%{ast.value}.{buffer_num}.ptr"]
                    buffer_num += 1
                else:
                    ltype = llvm_type_from_string(arr['type'])
                    var_type = arr['type'] + "[]"
                    array_load = [
                        f"%{ast.value}.{buffer_num}.ptr = getelementptr inbounds {ltype}, {ltype}* %{ast.value}.ptr, i32 0",
                        f"%{ast.value}.{buffer_num}.ptr"]
                    buffer_num += 1
                    pass
                buffer_strs = array_load
            else:
                buffer_strs = [f"%{ast.value}.ptr"]
        return var_type, buffer_strs
    else:
        raise Exception("llvm_id cannot process node with different type from ID.")


def llvm_const(ast, context=None):
    if is_node(ast) and ast.name == "CONST":
        type = ast.get("TYPE")[0].value
        value = ast.get('VALUE')[0].value
        if type == "boolean":
            value = 1 if value == "true" else 0
        elif type == "string":
            str_info = find_string_by_value(strings, value)
            t_type = f"[{str_info['size']} x i8]"
            value = f"getelementptr inbounds ({t_type}, {t_type}* {str_info['id']}, i32 0, i32 0)"
        return type, [f"{value}"]
    else:
        raise Exception("llvm_const cannot process node with different type from CONST.")


def llvm_chain_call(ast, context=None):
    global buffer_num
    ast.checked = True
    for child in ast.childs:
        child.checked = True
    left = ast.childs[0]
    right = ast.childs[1]
    right_id = right.value if (right.name == "ID") else right.get("ID")[0].value
    left_type, left_strs = atom_funcs[left.name](left, True)

    struct = find_node_by_id(structs, left_type)
    struct_id = struct.get("ID")[0].value
    if left.name == "FUNC_CALL":
        lltype = llvm_type_from_string(left_type)
        left_strs = left_strs[:-1] + [f"%{left.get('ID')[0].value}.{buffer_num}.ptr = alloca %struct.{struct_id}",
                                      f"store {lltype} {left_strs[-1]}, {lltype}* %{left.get('ID')[0].value}.{buffer_num}.ptr",
                                      f"%{left.get('ID')[0].value}.{buffer_num}.ptr"]
        buffer_num += 1
    member_index = -1
    struct_member = None
    for ind, member in enumerate(struct.childs[1].childs):
        if member.get("ID", nest=True)[0].value == right_id:
            member_index = ind
            struct_member = member
            break
    if member_index > -1:
        result_reg = f"%struct.{struct_id}.{member_index}.{buffer_num}.ptr"
        result = left_strs[:-1] + [f"{result_reg} = getelementptr inbounds %struct.{struct_id}, " +
                                   f"%struct.{struct_id}* {left_strs[-1]}, i32 0, i32 {member_index}"]
        if struct_member.name == "ASSIGN":
            array_register = f"struct.{struct_id}.{member_index}.{buffer_num}"
            array_alloc = struct_member.childs[1]
            array_size = array_alloc.get("VALUE", nest=True)[0].value
            array_type = array_alloc.childs[0].value
            element_context = {"id": array_register,
                               "type": array_type,
                               "size": array_size}
            element_type, strs = llvm_array_el(right, element_context)
            result = result + strs
            buffer_num += 1
            return element_type, result
        elif struct_member.name == "VARIABLE":
            if context is None:
                load_type, load_strs = llvm_load_value(result_reg, struct_member.get("TYPE")[0].value)
                result = result + load_strs
            else:
                load_type = struct_member.get("TYPE")[0].value
                result.append(result_reg)
            buffer_num += 1
            return load_type, result
        else:
            print(f"Incorrect member of struct {struct_id}")

    else:
        print(f"Member of struct {struct_id} with id {struct_member_name} not found")


def llvm_array_el(ast, context=None):
    # context != None means that the function has been called from chain call.
    # in this case context has a structure {"id": array_register, "type": array_type, "size": array_size}
    ast.checked = True
    for child in ast.childs:
        child.checked = True
    if context is not None and type(context).__name__ == "dict" and "size" in context:
        array_var = context
        var_id = context["id"]
        pre_type = llvm_type_from_string(array_var['type'])
        ll_type = f"[{array_var['size']} x {pre_type}]"
    else:
        var_id = ast.get("ID")[0].value
        array_var = find_array_by_id(arrays, var_id)
        if array_var is None:
            array_var = find_array_by_id(arrays_from_func, var_id)
            if array_var is not None:
                pre_type = llvm_type_from_string(array_var['type'])
                ll_type = f"{pre_type}"
            else:
                raise Exception(f"Array {var_id} is not exist.")
        else:
            pre_type = llvm_type_from_string(array_var['type'])
            ll_type = f"[{array_var['size']} x {pre_type}]"

    buff_type, strs = llvm_expression(ast.childs[1])
    global buffer_num
    if ".ptr" in strs[-1]:
        loaded_type, loaded_strs = llvm_load_value(strs[-1], buff_type)
    else:
        loaded_strs = strs

    result = loaded_strs[:-1] + [
        f"%{var_id}.{buffer_num}.ptr = getelementptr inbounds {ll_type}, {ll_type}* %{var_id}.ptr, {'i32 0, ' if '[' in ll_type else ''}i32 {loaded_strs[-1]}",
        f"%{var_id}.{buffer_num}.ptr"]
    buffer_num += 1
    return array_var["type"], result


def llvm_func_call(ast, context=None):
    ast.checked = True
    for child in ast.childs:
        child.checked = True
    func_id = ast.get("ID")[0].value

    if (func_id == 'print'):
        return llvm_print(ast, context)

    func_decl = find_node_by_id(functions, func_id)
    func_type = func_decl.get("TYPE")[0].value
    call_args = ast.get("CALL_ARGS")[0].childs
    ll_call_args = ""
    result_strs = []
    for arg in call_args:
        arg_type, arg_strs = llvm_expression(arg)
        result_strs = result_strs + arg_strs[:-1]
        ll_type = llvm_type_from_string(arg_type)
        ll_call_args += f"{ll_type} {arg_strs[-1]}, "
    if len(call_args) != 0:
        ll_call_args = ll_call_args[:-2]
    ll_type = llvm_type_from_string(func_type)
    global buffer_num
    reg_buffer = ""
    if func_type != "void":
        reg_buffer = f'%{func_id}.{buffer_num} ='
    call_result = [f"{reg_buffer} call {ll_type} @func.{func_id}({ll_call_args})"]
    result_strs = result_strs + call_result + [f"{reg_buffer}"]
    buffer_num += 1
    return func_type, result_strs


def llvm_print(node, context):
    global buffer_num
    global const_str_num
    out_format = {'i32': '%d', 'double': '%lf', 'i8*': '%s', 'i1': '%d'}
    result_str = ''
    result = []
    args = node.get('CALL_ARGS')[0].childs
    var_queue = []

    for arg in args:
        if arg.name == 'CONST':
            val = arg.get('VALUE')[0].value
            result_str += val
        else:
            type, elem_results = fdict[arg.name](arg)
            if len(elem_results[-1]) >= 4 and elem_results[-1][-4:] == ".ptr":
                type, loaded_strs = llvm_load_value(elem_results[-1], type)
                elem_results = elem_results[:-1] + loaded_strs
            type = type_dict[type]
            name = elem_results[-1]
            result = result + elem_results[:-1]
            var_queue.append(f'{type} {name}')
            result_str += out_format[type]
            buffer_num += 1

    str_name = f'@.str.{const_str_num}'
    str_size = len(result_str) + 2
    strings.append({
        "id": str_name,
        "value": result_str + '\\0A',
        "size": str_size,
        'name': None
    })
    result.append(
        f'%buffer{buffer_num} = getelementptr inbounds [{str_size} x i8], [{str_size} x i8]* {str_name}, i32 0, i32 0 ')
    var_queue = [f'i8* %buffer{buffer_num}'] + var_queue
    buffer_num += 1
    const_str_num += 1
    result.append(f'call i32 (i8*, ...) @printf({", ".join(var_queue)})')

    return 'i32', result + ['1']


binary_op_funcs = {'PLUS': llvm_add_func,
                   'MINUS': llvm_sub_func,
                   'TIMES': llvm_mul_func,
                   'DIVIDE': llvm_div_func,
                   'MODULO': llvm_mod_func,
                   'BOR': llvm_or_func,
                   'BAND': llvm_and_func,
                   'LT': llvm_lt_func,
                   'GT': llvm_gt_func,
                   'GE': llvm_ge_func,
                   'LE': llvm_le_func,
                   'NE': llvm_ne_func,
                   'EQ': llvm_eq_func,
                   'LOR': llvm_or_func,
                   'LAND': llvm_and_func
                   }

atom_funcs = {'ID': llvm_id,
              'CHAIN_CALL': llvm_chain_call,
              'FUNC_CALL': llvm_func_call,
              'CONST': llvm_const,
              'ARRAY_ELEMENT': llvm_array_el}

fdict = {
    'ERROR': lambda x, y: raiseError('error in ast'),
    'FUNCTION': llvm_func_def,
    'STRUCT': llvm_struct, 'CONTENT': skip,  # ?
    'VALUE': skip,
    'TYPE': skip,
    'CONST': llvm_const,
    'ID': llvm_id,
    'ARRAY_ELEMENT': llvm_array_el,
    'VARIABLE': llvm_variable,
    'VARIABLE_ARRAY': skip,
    'ARRAY_ALLOC': skip,
    'ASSIGN': llvm_assign,
    'SCOPE': TODO,
    'FUNC_ARGS': skip,
    'RETURN': llvm_return,
    'EMPTY_STATEMENT': skip,
    'PLUS': llvm_expression,
    'MINUS': llvm_expression,
    'TIMES': llvm_expression,
    'DIVIDE': llvm_expression,
    'MODULO': llvm_expression,
    'IDIVIDE': llvm_expression,
    'BOR': llvm_expression,
    'BAND': llvm_expression,
    'LT': llvm_expression,
    'GT': llvm_expression,
    'GE': llvm_expression,
    'LE': llvm_expression,
    'NE': llvm_expression,
    'EQ': llvm_expression,
    'LOR': llvm_expression,
    'LAND': llvm_expression,
    'CHAIN_CALL': llvm_chain_call,
    'IF_CONDITION': llvm_condition,
    'IF': skip,
    'CONDITION': skip,
    'ELIF': llvm_cond_elif,
    'ELSE': llvm_cond_else,
    'DO_WHILE': llvm_do_while,
    'WHILE': llvm_while,
    'MARK': llvm_mark,
    'GOTO': llvm_goto,
    'CALL_ARGS': TODO,
    'FUNC_CALL': llvm_expression,
    'BREAK': llvm_break,
    'SKIP': llvm_skip
}
