import sys
import ply.lex as lex
from initialdata import *
from yacc import *
import pandas
import io
import utils as utils
import ply.yacc as yacc


errordata = []

def findErrors(data):
    errordata = []


    # redundant repeating
    for i in range(len(data) - 1):
        if data[i][0] == "CONST_INTEGER" and (abs(int(data[i][1])) > (2**32)-1):
            errordata.append("Integer type overflow at line " + str(data[i][2]) + " pos " + str(data[i][3]))
            # addError("Integer type overflow", data[i])
    return errordata

def parseVarError(node, variables={}, parent=None, scopevars=[]):
    
    try:
        if node.type == 'VARIABLE':
            # change it if you change a structure of the CONDITION node
            if node.parts[1] in variables:
                print('Redundant definition of "'+node.parts[1]+'" on line', node.line) # TODO: добавить номер строки
            else:
                variables[node.parts[1]] = node.parts[0].parts[0]
                scopevars.append(node.parts[1])
        elif node.type == 'ID':
            if not node.parts[0] in variables:
                print('Undefined variable "'+node.parts[0]+'" on line', node.line) #TODO: добавить номер строки
        else:
            for child in node.parts:
                parseVarError(child, variables, node, [] if child.type == 'SCOPE' else scopevars)
    except: pass
    
    if (node.type == 'SCOPE'):
        for name in scopevars:
            del variables[name]

if  __name__ == "__main__":
    filename = 'program.rofl'

    if (len(sys.argv) > 1):
        filename = sys.argv[1]

    lexer = lex.lex()

    with io.open(filename, "r", encoding="utf8") as f:
        text = f.read()
        lexer.input(text)

        data = []
        symbolcounter = 0
        for token in lexer:
            if (re.match(r'(NEWLINE)|(COMMENT)', token.type)):
                symbolcounter = token.lexpos
            data.append([token.type, token.value, token.lineno, token.lexpos - symbolcounter])

        errors = findErrors(data)
        for error in errors:
            print(error)

        print(pandas.DataFrame([row for row in data], columns=["token_type", "token_value", "line_no", "pos"]))

        # import logging

        # logging.basicConfig(
        #     level=logging.DEBUG,
        #     filename="parselog.txt",
        #     filemode="w",
        #     format="%(filename)10s:%(lineno)4d:%(message)s"
        # )
        # log = logging.getLogger()

        parser = yacc.yacc(debug=0)
        result = parser.parse(text)
        print(result)
        parseVarError(result)
