from initialdata import tokens

class Node:
    def parts_str(self):
        st = []
        for part in self.parts:
            st.append( str( part ) )
        return "\n".join(st)

    def __repr__(self):
        return self.type + ":\n\t" + self.parts_str().replace("\n", "\n\t")

    def add_parts(self, parts):
        self.parts += parts
        return self

    def __init__(self, type, parts):
        self.type = type
        self.parts = parts


precedence = (
    ('left', 'ASSIGN'),
    ('left', 'LOR'),
    ('left', 'LAND'),
    ('right', 'LNOT'),
    ('nonassoc', 'LT', 'GT', 'GE', 'LE', 'EQ', 'NE'),  # Nonassociative operators
    ('left', 'BOR'),
    ('left', 'BAND'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO', 'IDIVIDE'),
    ('left', 'INCREMENT', 'DECREMENT')
)

def p_binary_operators(p):
    '''expression : expression PLUS expression
            | expression MINUS expression
            | expression TIMES expression
            | expression DIVIDE expression
            | expression MODULO expression
            | expression IDIVIDE expression
            | expression BOR expression
            | expression BAND expression
            | expression LT expression
            | expression GT expression
            | expression GE expression
            | expression LE expression
            | expression EQ expression
            | expression NE expression
            | LPAREN expression RPAREN
            | CONST_INTEGER
    '''
    print(p.parser)
    print(p.lexer)
    if len(p) == 4:
        if p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '*':
            p[0] = p[1] * p[3]
        elif p[2] == '/':
            p[0] = p[1] / p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '%':
            p[0] = p[1] % p[3]
        elif p[2] == '%%':
            p[0] = p[1] // p[3]

        elif p[2] == '|':
            p[0] = p[1] | p[3]
        elif p[2] == '&':
            p[0] = p[1] & p[3]

        elif p[2] == '>':
            p[0] = p[1] > p[3]
        elif p[2] == '<':
            p[0] = p[1] < p[3]
        elif p[2] == '>=':
            p[0] = p[1] >= p[3]
        elif p[2] == '<=':
            p[0] = p[1] <= p[3]
        elif p[2] == '!=':
            p[0] = p[1] != p[3]
        elif p[2] == '==':
            p[0] = p[1] == p[3]
    else:
        p[0] = p[1]

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")