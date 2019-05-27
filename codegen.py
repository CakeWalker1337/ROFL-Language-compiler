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

type_dict = {'int': 'i32', 'float': 'double', 'boolean': 'i8'}
NL = '\n'
TAB = '    '

def raiseError(x): raise Exception(x)
def skip(): pass

fdict = {
    'ERROR': lambda: raiseError('error in ast'),
    'FUNCTION': skip,
    'STRUCT': skip, 'CONTENT': '', # ?
    'CONST': '',
    'ID': '',
    'ARRAY_ELEMENT': '',
    'VARIABLE': '',
    'VARIABLE_ARRAY': '',
    'TYPE': '',
    'VALUE': '',
    'ARRAY_ALLOC': '',
    'SCOPE': '',
    'ASSIGN': '',
    'FUNC_ARGS': '',
    'FUNCTION': '',
    'RETURN': '',
    'EMPTY_STATEMENT': '',
    'PLUS': '',
    'MINUS':'',
    'TIMES': '',
    'DIVIDE': '',
    'MODULO': '',
    'IDIVIDE': '',
    'BOR': '',
    'BAND': '',
    'LT': '',
    'GT': '',
    'GE': '',
    'LE': '',
    'NE': '',
    'EQ': '',
    'LOR': '',
    'LAND': '',
    'LNOT': '',
    'CHAIN_CALL': '',
    'IF_CONDITION': '',
    'CONDITION': '',
    'ELIF': '',
    'ELSE': '',
    'DO_WHILE': '',
    'WHILE': '',
    'MARK': '',
    'GOTO': '',
    'CALL_ARGS': '',
    'FUNC_CALL': ''
}