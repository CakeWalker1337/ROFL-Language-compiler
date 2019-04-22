class Node:
    def __init__(self, name, value=None, parent=None, childs=[], line=0):
        self.name = name
        self.value = value
        self.childs = childs
        self.parent = parent
        for child in self.childs:
            child.parent = self
        self.line = line

    # returns all children of current node
    # name might be string or list of strings
    # if nest == True returns all nested elements
    def get(self, name, nest=False):
        nodes = []
        for elem in self.childs:
            if isinstance(name, str) and elem.type == name:
                nodes.append(elem)
            elif isinstance(name, list) and elem.type in name:
                nodes.append(elem)
            nodes = nodes + self.get(name) if nest else []
        return nodes

    # adds new list of childs to existed
    def add_childs(self, childs):
        self.childs += childs

    def __parts_str(self):
        st = []
        for part in self.childs:
            st.append(str(part))
        if len(self.childs) == 0:
            st.append(str(self.value))
        return "\n".join(st)

    def __repr__(self):
        if self.name == '':
            return self.__parts_str().replace("\n", "\n")
        else:
            return self.name + ":\n\t" + self.__parts_str().replace("\n", "\n\t")


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
    ('left', 'DOT'),
    ('nonassoc', 'LBRACKET', 'RBRACKET'),
    ('nonassoc', 'LPAREN', 'RPAREN'),
    ('nonassoc', 'LBRACE', 'RBRACE')
)

start = 'scope'


def p_id(p):
    '''id : ID'''
    p[0] = Node('ID', p[1])


def p_const_value_float(p):
    '''const_value : CONST_FLOAT'''
    line = p.lexer.lineno
    p[0] = Node('CONST', childs=[Node('TYPE', 'float', line=line), Node('VALUE', value=p[1], line=line)], line=line)


def p_const_value_string(p):
    '''const_value : CONST_STRING'''
    line = p.lexer.lineno
    p[0] = Node('CONST', childs=[Node('TYPE', 'string', line=line), Node('VALUE', value=p[1], line=line)], line=line)


def p_const_value_integer(p):
    'const_value : CONST_INTEGER'
    line = p.lexer.lineno
    p[0] = Node('CONST', childs=[Node('TYPE', 'int', line=line), Node('VALUE', value=p[1], line=line)], line=line)


def p_const_value_boolean(p):
    'const_value : CONST_BOOLEAN'
    line = p.lexer.lineno
    p[0] = Node('CONST', childs=[Node('TYPE', 'boolean', line=line), Node('VALUE', value=p[1], line=line)], line=line)


def p_const_value_null(p):
    'const_value : NULL'
    line = p.lexer.lineno
    p[0] = Node('CONST', childs=[Node('TYPE', 'null', line=line), Node('VALUE', value=p[1], line=line)], line=line)


def p_array_idx(p):
    'array_idx : LBRACKET expression RBRACKET'
    p[0] = p[2]


def p_array_element(p):
    '''array_element : id array_idx'''
    line = p.lexer.lineno
    p[0] = Node('ARRAY_ELEMENT', childs=[p[1], p[2]], line=line)


def p_primitive_variable(p):
    'variable_decl : datatype id'
    line = p.lexer.lineno
    p[0] = Node('VARIABLE', childs=[p[1], p[2]], line=line)


def p_struct_variable(p):
    'variable_decl : ID id'
    line = p.lexer.lineno
    p[0] = Node('VARIABLE', childs=[Node('TYPE', p[1], line=line), p[2]], line=line)


def p_array_alloc_size(p):
    'array_size : LPAREN CONST_INTEGER RPAREN'
    line = p.lexer.lineno
    p[0] = Node('CONST', childs=[Node('TYPE', 'int', line=line), Node('VALUE', p[2], line=line)], line=line)


def p_array_alloc(p):
    'array_alloc : array_type array_size'
    line = p.lexer.lineno
    p[0] = Node("ARRAY_ALLOC", childs=[p[1], p[2]], line=line)


def p_primitives(p):
    '''primitive_type : DECL_BOOLEAN
            | DECL_FLOAT
            | DECL_INTEGER
            | DECL_STRING
            | DECL_VOID
    '''
    line = p.lexer.lineno
    p[0] = Node('TYPE', value=p[1], line=line)


def p_array_type(p):
    '''array_type : primitive_type LBRACKET RBRACKET
            | id LBRACKET RBRACKET
    '''
    line = p.lexer.lineno
    p[0] = Node("TYPE", value=p[1].value + "[]", line=line)


def p_datatype(p):
    '''datatype : primitive_type
                | array_type
    '''
    p[0] = p[1]


def p_delimiters(p):
    '''expression : LPAREN expression RPAREN
            | LBRACE expression RBRACE
    '''
    p[0] = p[2]


def p_struct_content(p):
    'braced_content : LBRACE content RBRACE'
    p[0] = p[2]


def p_struct(p):
    '''struct : STRUCT id braced_content'''
    line = p.lexer.lineno
    p[0] = Node('STRUCT', childs=[p[2], p[3]], line=line)


def p_content(p):
    '''content : func
              | variable_decl SEMI
    '''
    line = p.lexer.lineno
    p[0] = Node('CONTENT', childs=[p[1]], line=line)


def p_content_add(p):
    '''content : content func
              | content variable_decl SEMI
    '''
    p[1].add_childs([p[2]])
    p[0] = p[1]


def p_content_assign(p):
    '''content : variable_decl ASSIGN expression SEMI'''
    line = p.lexer.lineno
    p[0] = Node('CONTENT', childs=[Node('ASSIGN', childs=[p[1], p[3]], line=line)], line=line)


def p_content_add_assign(p):
    '''content : content variable_decl ASSIGN expression SEMI'''
    line = p.lexer.lineno
    p[1].add_childs(Node('ASSIGN', childs=[p[2], p[4]], line=line))
    p[0] = p[1]


# TODO: create production with empty structure content

def p_assignment(p):
    '''assignment : variable_decl ASSIGN expression SEMI
                | id ASSIGN expression SEMI
                | variable_decl ASSIGN array_alloc SEMI
                | id ASSIGN array_alloc SEMI
                | array_element ASSIGN expression SEMI
    '''
    line = p.lexer.lineno
    p[0] = Node('ASSIGN', childs=[p[1], p[3]], line=line)


def p_empty(p):
    '''empty : '''
    pass


def p_func_args_paren(p):
    'func_arg_paren : LPAREN func_arg RPAREN'
    p[0] = p[2]


def p_func_type(p):
    '''func_type : datatype
            | id
    '''
    line = p.lexer.lineno
    p[0] = Node("TYPE", value=p[1].value, line=line)


def p_func_arg(p):
    '''func_arg : variable_decl
            | empty
    '''
    line = p.lexer.lineno
    p[0] = Node('FUNC_ARGS', childs=[p[1]] if p[1] else [], line=line)


def p_func_arg_add(p):
    '''func_arg : func_arg COMMA variable_decl'''
    p[1].add_childs([p[3]])
    p[0] = p[1]


def p_func(p):
    ''' func : FUNCTION id func_arg_paren COLON func_type scope_brace'''
    line = p.lexer.lineno
    p[0] = Node('FUNCTION', childs=[p[2], p[3], p[5], p[6]], line=line)


def p_scope(p):
    '''scope : scope statement
            | statement
            | empty
    '''
    line = p.lexer.lineno
    if len(p) == 2:
        p[0] = Node('SCOPE', childs=[p[1]] if p[1] else [], line=line)
    else:
        p[1].add_childs([p[2]])
        p[0] = p[1]


def p_return(p):
    '''return : RETURN expression SEMI
              | RETURN SEMI
    '''
    line = p.lexer.lineno
    if len(p) == 4:
        p[0] = Node('RETURN', childs=[p[2]], line=line)
    else:
        p[0] = Node('RETURN', childs=[], line=line)


def p_loop_keywords(p):
    '''loop_keyword : SKIP
                      | BREAK'''
    p[0] = Node(p[1].upper(), line=p.lexer.lineno)


def p_single_statement(p):
    '''statement : expression SEMI
              | variable_decl SEMI
              | loop_keyword SEMI
              | goto SEMI
    '''
    p[0] = p[1]


def p_complex_statement(p):
    '''statement : assignment
            | return
            | func
            | struct
            | condition_full
            | loop
            | comment
    '''
    p[0] = p[1]


def p_literal_expressions(p):
    '''expression : const_value
            | id
            | function_call
            | array_element
            | chain_call
    '''
    p[0] = p[1]


def p_unary_operators(p):
    '''expression : expression INCREMENT
            | expression DECREMENT
    '''
    line = p.lexer.lineno
    if p[2] == '++':
        p[0] = Node('PLUS', childs=[p[1], Node('CONST', childs=[Node('TYPE', value='int', line=line),
                                                             Node('VALUE', value="1", line=line)], line=line)], line=line)
    elif p[2] == '--':
        p[0] = Node('MINUS', childs=[p[1], Node('CONST', childs=[Node('TYPE', value='int', line=line),
                                                             Node('VALUE', value="1", line=line)], line=line)], line=line)


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
    line = p.lexer.lineno
    if len(p) == 4:
        if p[2] == '+':
            p[0] = Node('PLUS', childs=[p[1], p[3]], line=line)
        elif p[2] == '-':
            p[0] = Node('MINUS', childs=[p[1], p[3]], line=line)
        elif p[2] == '*':
            p[0] = Node('TIMES', childs=[p[1], p[3]], line=line)
        elif p[2] == '/':
            p[0] = Node('DIVIDE', childs=[p[1], p[3]], line=line)
        elif p[2] == '%':
            p[0] = Node('MODULO', childs=[p[1], p[3]], line=line)
        elif p[2] == '%%':
            p[0] = Node('IDIVIDE', childs=[p[1], p[3]], line=line)

        elif p[2] == '|':
            p[0] = Node('BOR', childs=[p[1], p[3]], line=line)
        elif p[2] == '&':
            p[0] = Node('BAND', childs=[p[1], p[3]], line=line)
    else:
        p[0] = p[1]


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
    line = p.lexer.lineno
    if len(p) == 4:
        if p[2] == '>':
            p[0] = Node('LT', childs=[p[1], p[3]], line=line)
        elif p[2] == '<':
            p[0] = Node('GT', childs=[p[1], p[3]], line=line)
        elif p[2] == '>=':
            p[0] = Node('GE', childs=[p[1], p[3]], line=line)
        elif p[2] == '<=':
            p[0] = Node('LE', childs=[p[1], p[3]], line=line)
        elif p[2] == '!=':
            p[0] = Node('NE', childs=[p[1], p[3]], line=line)
        elif p[2] == '==':
            p[0] = Node('EQ', childs=[p[1], p[3]], line=line)
        elif p[2] == '||':
            p[0] = Node('LOR', childs=[p[1], p[3]], line=line)
        elif p[2] == '&&':
            p[0] = Node('LAND', childs=[p[1], p[3]], line=line)
    else:
        p[0] = Node('LNOT', childs=[p[2]], line=line)


def p_call(p):
    '''call : id
        | function_call'''
    p[0] = p[1]


def p_chain_call(p):
    '''chain_call : id DOT call
            | array_element DOT call'''
    line = p.lexer.lineno
    p[0] = Node("CHAIN_CALL", childs=[p[1], p[3]], line=line)


def p_full_condition(p):
    '''condition_full : condition_statement else_cond
            | condition_statement
    '''
    if len(p) == 3:
        p[1].add_childs([p[2]])
    p[0] = p[1]


def p_conditions(p):
    '''condition_statement : if_cond
            | condition_statement elif_cond
    '''
    line = p.lexer.lineno
    if len(p) == 2:
        p[0] = Node('IF_CONDITION', childs=[p[1]], line=line)
    else:
        p[1].add_childs([p[2]])
        p[0] = p[1]


def p_if_cond(p):
    'if_cond : IF expression_paren scope_brace'
    line = p.lexer.lineno
    p[0] = Node(
        'IF', childs=[Node('CONDITION', childs=[p[2]], line=line), p[3]], line=line)


def p_elif_cond(p):
    '''elif_cond : ELIF expression_paren scope_brace'''
    line = p.lexer.lineno
    p[0] = Node(
        'ELIF', childs=[Node('CONDITION', childs=[p[2]], line=line), p[3]], line=line)


def p_else_cond(p):
    '''else_cond : ELSE scope_brace'''
    line = p.lexer.lineno
    p[0] = Node('ELSE', childs=[p[2]], line=line)


def p_loop(p):
    '''loop : while_loop
            | do_while_loop'''
    p[0] = p[1]


def p_do_while(p):
    'do_while_loop : DO scope_brace WHILE expression_paren SEMI'
    line = p.lexer.lineno
    p[0] = Node('DO_WHILE', childs=[p[2], Node('CONDITION', childs=[p[4]], line=line)], line=line)


def p_while(p):
    'while_loop : WHILE expression_paren scope_brace'
    line = p.lexer.lineno
    p[0] = Node('WHILE', childs=[Node(
        'CONDITION', childs=[p[2]], line=line), p[3]], line=line)


def p_expression_paren(p):
    'expression_paren : LPAREN expression RPAREN'
    p[0] = p[2]


def p_scope_brace(p):
    'scope_brace : LBRACE scope RBRACE'
    p[0] = p[2]


def p_mark(p):
    'mark : ID COLON'
    line = p.lexer.lineno
    p[0] = Node('MARK', childs=[p[1]], line=line)


def p_goto(p):
    'goto : GOTO mark'
    p[0] = p[2]


def p_comments(p):
    'comment : COMMENT'
    line = p.lexer.lineno
    p[0] = Node('COMMENT', childs=[p[1].replace('\n', '')], line=line)


def p_call_args_add(p):
    '''call_args : call_args COMMA expression'''
    p[0] = p[1].add_childs([p[3]])


def p_call_args(p):
    '''call_args : expression
        | empty'''
    line = p.lexer.lineno
    p[0] = Node('CALL_ARGS', childs=[p[1]] if p[1] else [], line=line)


def p_call_args_paren(p):
    'call_args_paren : LPAREN call_args RPAREN'
    p[0] = p[2]


def p_func_call(p):
    'function_call : id call_args_paren'
    p[0] = Node('FUNC_CALL', childs=[p[1], p[2]], line=p[1].line)


# Error rule for syntax errors
def p_error(p):
    if p is not None:
        print('Line %s, illegal token "%s"' % (p.lineno, p.value))
    else:
        print('Unexpected end of input')
