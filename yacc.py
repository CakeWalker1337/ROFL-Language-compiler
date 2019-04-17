from initialdata import tokens


class Node:
    def parts_str(self):
        st = []
        for part in self.parts:
            st.append( str( part ) )
        return "\n".join(st)

    def __repr__(self):
        if self.type == '':
            return self.parts_str().replace("\n", "\n")
        else:
            return self.type + ":\n\t" + self.parts_str().replace("\n", "\n\t")

    def add_parts(self, parts):
        self.parts += parts
        return self

    def __init__(self, type, parts, line):
        self.type = type
        self.parts = parts
        self.line = line


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


start = 'SCOPE'


def p_id(p):
    'id : ID'
    p[0] = Node('ID', [p[1]], p.lineno(1))


# 'ID', 'CONST_INTEGER', 'CONST_FLOAT', 'CONST_STRING', 'NULL', 'CONST_BOOLEAN',
def p_const_values(p):
    '''const_type : CONST_FLOAT
            | CONST_STRING
            | CONST_INTEGER
            | CONST_BOOLEAN
            | NULL
    '''
    p[0] = Node('CONST_VALUE', [p[1]], p.lineno(1))


def p_const_arr(p):
    '''const_type : LBRACKET call_args RBRACKET'''
    p[0] = Node('ARRAY', p[2].parts, p.lineno(1))


def p_array_element(p):
    '''array_element : id LBRACKET expression RBRACKET'''
    p[0] = Node('ARRAY_ELEMENT', [p[1], p[3]], p.lineno(1))


def p_variable(p):
    '''variable_decl : datatype ID'''
    p[0] = Node('VARIABLE', [p[1], p[2]], p.lineno(1))


def p_datatypes(p):
    '''datatype : DECL_BOOLEAN
            | DECL_FLOAT
            | DECL_INTEGER
            | DECL_STRING
            | DECL_ARRAY
            | DECL_VOID
    '''
    p[0] = Node('DATATYPE', [p[1]], p.lineno(1))


def p_delimiters(p):
    '''expression : LPAREN expression RPAREN
            | LBRACE expression RBRACE
            | LBRACKET expression RBRACKET
    '''
    p[0] = p[2]


def p_struct(p):
    '''struct : STRUCT id LBRACE content RBRACE'''
    p[0] = Node('STRUCT', [p[2], p[4]], p.lineno(1))


def p_content(p):
    '''content : content func
            | content variable_decl SEMI
            | content assignment
            | variable_decl SEMI
            | assignment
            | func
    '''
    if len(p) == 2:
        p[0] = Node('CONTENT', [p[1]], p.lineno(1))
    else:
        p[0] = p[1].add_parts([p[2]])


def p_assignment(p):
    '''assignment : variable_decl ASSIGN expression SEMI
                | id ASSIGN expression SEMI
                | array_element ASSIGN expression SEMI'''
    if len(p) == 5:
        p[0] = Node('ASSIGN', [p[1], p[3]], p.lineno(1))
    else:
        p[0] = Node('ASSIGN', [p[1], p[4]], p.lineno(1))


def p_empty(p):
    '''empty : '''
    pass


def p_func(p):
    ''' func : FUNCTION id LPAREN func_arg RPAREN COLON datatype LBRACE SCOPE RBRACE

        func_arg : variable_decl
                | empty
                | func_arg COMMA variable_decl

    '''
    if p[1] == 'function':
        p[0] = Node('FUNCTION', [p[2], p[4], p[7], p[9]], p.lineno(1))
    else:
        if len(p) == 2:
            p[0] = Node('FUNC_ARGS', [p[1]], p.lineno(1))
        else:
            p[0] = p[1].add_parts([p[3]])


def p_SCOPE(p):
    '''SCOPE : SCOPE statement
            | statement
    '''
    if len(p) == 2:
        p[0] = Node('SCOPE', [p[1]], p.lineno(1))
    else:
        p[0] = p[1].add_parts([p[2]])


def p_statement(p):
    '''statement : RETURN expression SEMI
            | expression SEMI
            | assignment
            | func
            | struct
            | variable_decl SEMI
            | condition_full
            | while_loop
            | SKIP SEMI
            | BREAK SEMI
            | GOTO mark SEMI
            | comment
    '''
    if len(p) == 3:
        p[0] = p[1]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Node('RETURN', [p[2]], p.lineno(1))


def p_literal_expressions(p):
    '''expression : const_type
            | id
            | function_call
            | array_element
    '''
    p[0] = p[1]


def p_unary_operators(p):
    '''expression : expression INCREMENT
            | expression DECREMENT
    '''
    if p[2] == '++':
        p[0] = Node('PLUS', [p[1], Node('CONST_VALUE', ['1'], p.lineno(1))], p.lineno(1))
    elif p[2] == '--':
        p[0] = Node('MINUS', [p[1], Node('CONST_VALUE', ['1'], p.lineno(1))], p.lineno(1))


def p_binary_operators(p):
    '''expression : expression PLUS expression
            | expression MINUS expression
            | expression TIMES expression
            | expression DIVIDE expression
            | expression MODULO expression
            | expression IDIVIDE expression
            | expression BOR expression
            | expression BAND expression
            | expression DOT expression
    '''
    if len(p) == 4:
        if p[2] == '+':
            p[0] = Node('PLUS', [p[1], p[3]], p.lineno(1))
        elif p[2] == '-':
            p[0] = Node('MINUS', [p[1], p[3]], p.lineno(1))
        elif p[2] == '*':
            p[0] = Node('TIMES', [p[1], p[3]], p.lineno(1))
        elif p[2] == '/':
            p[0] = Node('DIVIDE', [p[1], p[3]], p.lineno(1))
        elif p[2] == '%':
            p[0] = Node('MODULO', [p[1], p[3]], p.lineno(1))
        elif p[2] == '%%':
            p[0] = Node('IDIVIDE', [p[1], p[3]], p.lineno(1))

        elif p[2] == '|':
            p[0] = Node('BOR', [p[1], p[3]], p.lineno(1))
        elif p[2] == '&':
            p[0] = Node('BAND', [p[1], p[3]], p.lineno(1))
        elif p[2] == '.':
            p[0] = Node('CHAIN_CALL', [p[1], p[3]], p.lineno(1))
    else:
        p[0] = p[1]


# 1. Соответствие типов (константы, переменные, массивы)
# 2. Соответствие return и типа возвр функции
# 3. Return внутри функции, а break и skip внутри if/while
# 4. Объявлен ли id до его использования (также переобъявление).
# 5. Запрет объявления функции и структуры внутри функции.
#
#


def p_logic_expressions(p):
    '''expression : expression LT expression
                | expression GT expression
                | expression GE expression
                | expression LE expression
                | expression EQ expression
                | expression NE expression
                | expression LOR expression
                | expression LAND expression
                | LNOT expression
    '''
    if len(p) == 4:
        if p[2] == '>':
            p[0] = Node('LT', [p[1], p[3]], p.lineno(1))
        elif p[2] == '<':
            p[0] = Node('GT', [p[1], p[3]], p.lineno(1))
        elif p[2] == '>=':
            p[0] = Node('GE', [p[1], p[3]], p.lineno(1))
        elif p[2] == '<=':
            p[0] = Node('LE', [p[1], p[3]], p.lineno(1))
        elif p[2] == '!=':
            p[0] = Node('NE', [p[1], p[3]], p.lineno(1))
        elif p[2] == '==':
            p[0] = Node('EQ', [p[1], p[3]], p.lineno(1))
        elif p[2] == '||':
            p[0] = Node('LOR', [p[1], p[3]], p.lineno(1))
        elif p[2] == '&&':
            p[0] = Node('LAND', [p[1], p[3]], p.lineno(1))
    else:
        p[0] = Node('LNOT', [p[2]], p.lineno(1))


def p_full_condition(p):
    '''condition_full : condition_statement else_cond
            | condition_statement '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1].add_parts([p[2]])



def p_conditions(p):
    '''condition_statement : if_cond
            | condition_statement elif_cond
    '''
    #TODO: Отловить ошибку, когда больше одного else (правило, исключающее этот кейс, подобрать не смог)
    if len(p) == 2:
        p[0] = Node('CONDITION', [p[1]], p.lineno(1))
    else:
        p[0] = p[1].add_parts([p[2]])


def p_if_cond(p):
    'if_cond : IF LPAREN expression RPAREN LBRACE SCOPE RBRACE'
    p[0] = Node('IF', [Node('CONDITION', [p[3]], p.lineno(1)), p[6]], p.lineno(1))


def p_elif_cond(p):
    '''elif_cond : ELIF LPAREN expression RPAREN LBRACE SCOPE RBRACE'''
    p[0] = Node('ELIF', [Node('CONDITION', [p[3]], p.lineno(1)), p[6]], p.lineno(1))


def p_else_cond(p):
    '''else_cond : ELSE LBRACE SCOPE RBRACE'''
    p[0] = Node('ELSE', [p[3]], p.lineno(1))


def p_loop(p):
    'while_loop : DO LBRACE SCOPE RBRACE WHILE LPAREN expression RPAREN SEMI'
    p[0] = Node('WHILE', [p[3], Node('CONDITION', [p[7]], p.lineno(1))], p.lineno(1))


def p_mark(p):
    'mark : ID COLON'
    p[0] = Node('MARK', [p[1]], p.lineno(1))


def p_comments(p):
    'comment : COMMENT'
    p[0] = Node('COMMENT', [p[1].replace('\n', '')], p.lineno(1))


def p_call_args(p):
    '''call_args : expression
        | call_args COMMA expression
        | empty'''
    if len(p) == 4:
        p[0] = p[1].add_parts([p[3]])
    else:
        p[0] = Node('CALL_ARGS', [p[1]], p.lineno(1))


def p_call(p):
    'function_call : id LPAREN call_args RPAREN'
    p[0] = Node('FUNC_CALL', [p[1], p[3]], p.lineno(1))


# Error rule for syntax errors
def p_error(p):
    if p is not None and p.value == 'NEWLINE': 
        print('Semicolon is missing at line %s' % (p.lineno(1)))
    elif p is not None: 
        print('Line %s, illegal token "%s"' % (p.lineno(1), p.value))
    else:
        print('Unexpected end of input')
