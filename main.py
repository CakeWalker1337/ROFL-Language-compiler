import ply.lex as lex
from initialdata import *
import pandas
import io
import utils as utils

def findErrors(data):
    errordata = []
    columns = ["error", "token", "line", "position"]

    exceptions = r"(NEWLINE)"
    bracketbeacon = {}
    # redundant repeating
    for i in range(len(data) - 1):
        if (data[i][0] == data[i + 1][0] and not re.match(exceptions, data[i][0])):
            errordata.append(["Redundant repeating",                                # error message
                              "<" + data[i + 1][0] + ", " + data[i + 1][1] + ">",   # token
                              data[i + 1][2],                                       # line
                              data[i + 1][3]                                        # position on line
                              ])
        
    # spare brackets check
    # for i in range(len(data) - 1):
    #     if (data[i][1] and re.match(r'[\(\{\[\"\']', data[i][1])):
    #         bracket = data[i][1]
    #         obj = {"line": data[i][2], "pos": data[i][3]}
    #         try: bracketbeacon[bracket].append(obj)
    #         except KeyError: bracketbeacon[bracket] = [obj]
    #     elif (data[i][1] and re.match(r'[\)\}\]]', data[i][1])):
    #         bracket = data[i][1]
    #         obj = {"line": data[i][2], "pos": data[i][3]}
    #         try: bracketbeacon[utils.getSecondBracket(bracket)].pop()
    #         except (KeyError, IndexError): errordata.append(["Spare bracket", "<" + bracket + ">", obj["line"], obj["pos"]])
    #
    # for bracket in bracketbeacon:
    #     if (len(bracketbeacon[bracket]) % 2 != 0 and re.match(r'[\'\"]', bracket) or
    #             len(bracketbeacon[bracket]) and not re.match(r'[\'\"]', bracket)):
    #         errordata.append(["Bracket is missing", "<" + bracket + ">", bracketbeacon[bracket][0]["line"], bracketbeacon[bracket][0]["pos"]])

    return errordata, columns

filename = "program.rofl"
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
    print(pandas.DataFrame([row[:3] for row in data], columns=["token_type", "token_value", "line_no"]))
    
    errors, columns = findErrors(data)
    if (len(errors)):
        print("ERRORS:")
        print(pandas.DataFrame(errors, columns=columns))
    

