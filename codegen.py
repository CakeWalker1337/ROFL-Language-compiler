## TODO: генерация struct
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

def raiseError(x): raise Exception(x)
def skip(x, y): return []
def TODO(x, y): return [f'TODO {x.name}']

# Все функции возвращают набор из 1 или более команд, 
# последняя в листе команда является ключевой, остальные должны быть расположены выше неё


def llvm_type(ast, context=None):
    ast.checked = True
    if ast.value == 'string': return ['string'] # TODO: придумать как поступать с этим кейсом
    else:
        return [f'{type_dict[ast.value]}']

def llvm_value(ast, context=None):
    ast.checked = True
    return [ast.value]

def llvm_const(ast, context=None):
    ast.checked = True
    if ast.parent.name == 'SCOPE': return []
    value = llvm_value(ast.childs[1])[0]
    type = llvm_type(ast.childs[0])[0]
    if type == 'string': return []
    elif type == 'i8': value = '1' if value == 'true' else '0'
    return [type + ' ' + value]

def llvm_id(ast, context=None):
    ast.checked = True
    if ast.parent.name == 'SCOPE': return []
    name = get_info(ast)[0]
    return [f'{type_dict[context[name][1]]} %{ast.value}']

def llvm_array_el(ast, context):
    ast.checked = True
    ast.childs[0].checked = True
    name = get_info(ast)[0]
    type = type_dict[context[name][1]]
    return [
        f'%arr.ptr = getelementptr inbounds {type}, {type}* %{name}, i32 0 {fdict[ast.childs[1].name](ast.childs[1])[0]}',
        f'%elem = load {type}, {type}* %arr.ptr',
        f'%elem'] # TODO: придумать именование для выбранного элемента массива

def llvm_variable(ast, context=None):
    ast.checked = True
    ast.childs[1].checked = True
    name = get_info(ast)[0]
    type = llvm_type(ast.childs[0])
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
    
    if (left.name == 'VARIABLE_ARRAY'):
        name = get_info(left)[0]
        return [f'%{name} = {llvm_array_alloc(right)[0]}']
    else:
        return [''] # TODO: доделать для остальных присваиваний


fdict = {
    'ERROR': lambda x,y: raiseError('error in ast'),
    'FUNCTION': skip,
    'STRUCT': skip, 'CONTENT': TODO, # ?
    'VALUE': skip,
    'TYPE': skip,
    'CONST': llvm_const,
    'ID': llvm_id,
    'ARRAY_ELEMENT': llvm_array_el,
    'VARIABLE': llvm_variable,
    'VARIABLE_ARRAY': skip, # TODO: убратть возможность определения массива без аллокации
    'ARRAY_ALLOC': skip,
    'ASSIGN': llvm_assign,
    'SCOPE': TODO,
    'FUNC_ARGS': TODO,
    'RETURN': TODO,
    'EMPTY_STATEMENT': TODO,
    'PLUS': TODO,
    'MINUS':TODO,
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
    'CHAIN_CALL': TODO,
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




def start_codegen(ast, context = {}):
    if ast is None: raise Exception('ast is None')
    result = fdict[ast.name](ast, context)

    if is_definition(ast):
        name, type = get_info(ast)
        context[name] = type

    for child in ast.childs:
        if not child.checked:
            result += start_codegen(child, context)
        else:
            start_codegen(child, context)
    return result