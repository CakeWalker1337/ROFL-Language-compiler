import ply.lex as lex
from initialdata import *
import pandas
import io


def findErrors(data):
    errordata = []
    columns = ["error", "token", "line", "position"]
    # redundant type repeating
    exceptions = r'(NEWLINE)'
    for i in range(len(data) - 1):
        if (data[i][0] == data[i + 1][0] and not re.match(exceptions, data[i][0])):
            errordata.append(["Redundant repeating",                                # error message
                              "<" + data[i + 1][0] + ", " + data[i + 1][1] + ">",   # token
                              data[i + 1][2],                                       # line
                              data[i + 1][3]                                        # position on line
                              ])

    return errordata, columns

filename = "program.rofl"
lexer = lex.lex()

with io.open(filename, 'r', encoding='utf8') as f:
    text = f.read()
    lexer.input(text)

    data = []
    symbolcounter = 0
    for token in lexer:
        if (token.type == "NEWLINE"):
            symbolcounter = token.lexpos
        data.append([token.type, token.value, token.lineno, token.lexpos - symbolcounter])
    print(pandas.DataFrame([row[0:3] for row in data], columns=["token_type", "token_value", "line_no"]))
    
    errors, columns = findErrors(data)
    if (len(errors)):
        print("ERRORS:")
        print(pandas.DataFrame(errors, columns=columns))
    

