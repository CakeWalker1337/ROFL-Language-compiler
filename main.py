import sys
import ply.lex as lex
from initialdata import *
from yacc import *
import pandas
import io
import utils as utils
import ply.yacc as yacc
from tree_parser import *


errordata = []


def findErrors(data):
    errordata = []

    # redundant repeating
    for i in range(len(data) - 1):
        if data[i][0] == "CONST_INTEGER" and (abs(int(data[i][1])) > (2**32)-1):
            errordata.append("Integer type overflow at line " + str(data[i][2]) + " pos " + str(data[i][3]))
            # addError("Integer type overflow", data[i])
    return errordata


if  __name__ == "__main__":
    filename = 'program.rofl'

    if (len(sys.argv) > 1):
        filename = sys.argv[1]

    lexer = lex.lex()

    with io.open(filename, "r", encoding="utf8") as f:
        text = f.read()
        # lexer.input(text)

        # data = []
        # symbolcounter = 0
        # for token in lexer:
        #     if (re.match(r'(NEWLINE)|(COMMENT)', token.type)):
        #         symbolcounter = token.lexpos
        #     data.append([token.type, token.value, token.lineno, token.lexpos - symbolcounter])

        # errors = findErrors(data)
        # for error in errors:
        #     print(error)

        # print(pandas.DataFrame([row for row in data], columns=["token_type", "token_value", "line_no", "pos"]))

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

        init_semantic(result)
        parse_chain_call_errors()
        
        check_var_definition(result)
        check_expression_results(result, False)
        check_forbidden_definitions(result)
        check_inner_commands(result)
        check_func_call(result)