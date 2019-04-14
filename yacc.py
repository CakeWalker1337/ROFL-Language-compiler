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
    ('left', 'INCREMENT', 'DECREMENT'),
    ('nonassoc', 'LPAREN', 'RPAREN'),
    ('nonassoc', 'LBRACKET', 'RBRACKET'),
    ('nonassoc', 'LBRACE', 'RBRACE')
)


# 'ID', 'CONST_INTEGER', 'CONST_FLOAT', 'CONST_STRING', 'NULL', 'CONST_BOOLEAN',
def p_const_types(p):
    '''expression : CONST_FLOAT
            | CONST_STRING
            | CONST_INTEGER
            | CONST_BOOLEAN
            | NULL
            | ID
    '''
    p[0] = p[2]


def p_datatype(p):
    '''datatype : DECL_BOOLEAN
            | DECL_FLOAT
            | DECL_INTEGER
            | DECL_STRING
            | DECL_ARRAY
    '''
    p[0] = Node('DATATYPE', [p[1]])


def p_delimiters(p):
    '''expression : LPAREN expression RPAREN
            | LBRACE expression RBRACE
            | LBRACKET expression RBRACKET
    '''
    p[0] = p[2]


def p_struct(p):
    '''struct: STRUCT id LBRACE statement_group RBRACE'''
    p[0] = Node('STRUCT', [p[2], p[4]])


#TODO: Добавить (а нужно ли?) правило для переменной (variable : datatype ID) чтобы использовать в assignment и func_arg

def p_assignment(p):
    '''assignment : ID ASSIGN expression SEMI
                | datatype ID ASSIGN expression SEMI'''
    if len(p) == 5:
        p[0] = Node('ASSIGN', [p[1], p[3]])
    else:
        p[0] = Node('ASSIGN', [p[2], p[4]])


def p_empty(p):
    'empty :'
    pass


def p_func(p):
    ''' func : FUNCTION ID LPAREN func_arg RPAREN COLON datatype LBRACE statement_group RBRACE

        func_arg : datatype ID
                | empty
                | func_arg SEMI datatype ID

    '''
    p[0] = Node('FUNCTION', [p[2], p[4], p[7], p[9]])


def p_statement_group(p):
    '''statement_group: statement_group statement
            | statement
    '''
    if len(p) == 2:
        p[0] = Node('', [p[1]])
    else:
        p[0] = p[1].add_parts([p[2]])


def p_statements(p):
    '''statement : expression SEMI
            | RETURN expression SEMI
            | assignment
            | func
            | datatype ID SEMI
    '''


def p_binary_operators(p):
    '''expression : expression PLUS expression
            | expression MINUS expression
            | expression TIMES expression
            | expression DIVIDE expression
            | expression MODULO expression
            | expression IDIVIDE expression
            | expression BOR expression
            | expression BAND expression
    '''
    print(p.parser)
    print(p.lexer)
    if len(p) == 4:
        if p[2] == '+':
            p[0] = Node('PLUS', [p[1], p[3]])
        elif p[2] == '-':
            p[0] = Node('MINUS', [p[1], p[3]])
        elif p[2] == '*':
            p[0] = Node('TIMES', [p[1], p[3]])
        elif p[2] == '/':
            p[0] = Node('DIVIDE', [p[1], p[3]])
        elif p[2] == '%':
            p[0] = Node('MODULO', [p[1], p[3]])
        elif p[2] == '%%':
            p[0] = Node('IDIVIDE', [p[1], p[3]])

        elif p[2] == '|':
            p[0] = Node('BOR', [p[1], p[3]])
        elif p[2] == '&':
            p[0] = Node('BAND', [p[1], p[3]])
    else:
        p[0] = p[1]


def p_logic_expressions(p):
    '''expression : expression LT expression
                | expression GT expression
                | expression GE expression
                | expression LE expression
                | expression EQ expression
                | expression NE expression
    '''

    if p[2] == '>':
        p[0] = Node('LT', [p[1], p[3]])
    elif p[2] == '<':
        p[0] = Node('GT', [p[1], p[3]])
    elif p[2] == '>=':
        p[0] = Node('GE', [p[1], p[3]])
    elif p[2] == '<=':
        p[0] = Node('LE', [p[1], p[3]])
    elif p[2] == '!=':
        p[0] = Node('NE', [p[1], p[3]])
    elif p[2] == '==':
        p[0] = Node('EQ', [p[1], p[3]])


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")