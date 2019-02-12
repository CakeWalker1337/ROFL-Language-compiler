import ply.lex as lex
from initialdata import *


lexer = lex.lex()
data = ''' 
a = 3 + (4 + 5) //123
    * 10 + -20 *2
    "компиляция"
    'компиляция'
    a | b; b = b + 1
    b & a
'''

lexer.input(data)

for token in lexer:
    print(token)
