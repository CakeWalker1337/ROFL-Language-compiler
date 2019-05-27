## TODO: генерация struct
## генерация function
## транслировать дефолтные типы переменных (int -> i32, ...) кроме string
## TODO: генерация объявления внутренних переменных (после типов)
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

# Makes function
# name - function name
# type - function type
# args - function arguments (ex. ['i32 %a', 'double %b'])
# statements - function statements (ex. ['%0 = add'])
def llvm_func(name, type, args=[], statements=[]):
    return [f"define {type} @{name}({', '.join(args)}) {{{NL+TAB}{(NL+TAB).join(statements)}{NL}}}"]
#print(llvm_func('123', '124', statements=['123', '123']))

# Makes variable definition
# name - var name 
# type - var type
# val - default value
# valtype - default value type
def llvm_def(name, type, val=None, valtype=None):
    default = f'%{name} = alloca {type}'
    if not val is None:
        if valtype is None:
            raise AttributeError('type is not specified')
        else:
            return [default, f'store {valtype}, {valtype}* %{name}']
    else:
        return [default]
#print(llvm_def('name', type_dict['float'], 0, type_dict['int']))