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
            if isinstance(name, str) and elem.name == name:
                nodes.append(elem)
            elif isinstance(name, list) and elem.name in name:
                nodes.append(elem)
            nodes = nodes + (elem.get(name, nest) if nest else [])
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

def wrap_error(err_str, line_num):
    error_prefix = 'Syntax error at line '+ str(line_num) +': '
    return error_prefix + err_str

def err_node():
    return Node('ERROR')

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
    p[0] = Node('ID', p[1], line=p.lexer.lineno)

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

def p_array_idx_error(p):
    'array_idx : LBRACKET error RBRACKET'
    print(wrap_error('Error in calling an array element. Number of element expected.', p.lexer.lineno))
    p[0] = err_node()

def p_array_idx_unclosed(p):
    'array_idx : LBRACKET error SEMI'
    'array_idx : LBRACKET error STATEMENT'
    print(wrap_error('Unclosed brackets. "]" expected.', p.lexer.lineno))
    p[0] = err_node()

def p_array_element(p):
    '''array_element : id array_idx'''
    line = p.lexer.lineno
    p[0] = Node('ARRAY_ELEMENT', childs=[p[1], p[2]], line=line)

def p_variable(p):
    '''variable_decl : variable_decl_primitive
                    | variable_decl_struct
                    | variable_decl_array_primitive
                    | variable_decl_array_struct'''
    p[0] = p[1]

def p_primitive_variable(p):
    'variable_decl_primitive : primitive_type id'
    line = p.lexer.lineno
    p[0] = Node('VARIABLE', childs=[p[1], p[2]], line=line)

def p_array_variable(p):
    '''variable_decl_array_primitive : array_type_primitive id
        variable_decl_array_struct : array_type_struct id'''
    line = p.lexer.lineno
    p[0] = Node('VARIABLE_ARRAY', childs=[p[1], p[2]], line=line)

def p_struct_variable(p):
    'variable_decl_struct : ID id'
    line = p.lexer.lineno
    p[0] = Node('VARIABLE', childs=[Node('TYPE', p[1], line=line), p[2]], line=line)

def p_var_error(p):
    '''variable_decl_primitive : primitive_type error
        variable_decl_struct : ID error
        variable_decl_array_primitive : array_type_primitive error
        variable_decl_array_struct : array_type_struct error
    '''
    p[0] = err_node()
    print(wrap_error('Variable name expected.', p.lexer.lineno))

def p_array_alloc_size(p):
    'array_size : LPAREN CONST_INTEGER RPAREN'
    line = p.lexer.lineno
    p[0] = Node('CONST', childs=[Node('TYPE', 'int', line=line), Node('VALUE', p[2], line=line)], line=line)

def p_array_alloc_size_error(p):
    'array_size : LPAREN error RPAREN'
    print(wrap_error('Error in allocation of array. Const integer expected.', p.lexer.lineno))
    p[0] = err_node()

def p_array_alloc_size_unclosed(p):
    'array_size : LPAREN error SEMI'
    'array_size : LPAREN error STATEMENT'
    print(wrap_error('Unclosed parenthesis. ")" expected.', p.lexer.lineno))
    p[0] = err_node()

def p_array_alloc(p):
    '''array_alloc : array_alloc_primitive
                | array_alloc_struct'''
    p[0] = p[1]

def p_array_alloc_childs(p):
    '''array_alloc_primitive : array_type_primitive array_size
        array_alloc_struct : array_type_struct array_size'''
    line = p.lexer.lineno
    p[0] = Node("ARRAY_ALLOC", childs=[p[1], p[2]], line=line)

def p_array_alloc_error(p):
    'array_alloc : array_type error'
    p[0] = err_node()
    print(wrap_error('Array size expected.', p.lexer.lineno))

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
    '''array_type : array_type_primitive
            | array_type_struct
    '''
    line = p.lexer.lineno
    p[0] = Node("TYPE", value=p[1].value, line=line)

def p_array_type_primitive(p):
    '''array_type_primitive : primitive_type LBRACKET RBRACKET
        array_type_struct : id LBRACKET RBRACKET'''
    line = p.lexer.lineno
    p[0] = Node("TYPE", value=p[1].value, line=line)

def p_array_type_error(p):
    '''array_type_primitive : primitive_type LBRACKET error
        array_type_struct : id LBRACKET error
    '''
    p[0] = err_node()
    print(wrap_error('Unclosed brackets at array type. "]" expected', p.lineno(1)))

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

def p_delimeters_error(p):
    'expression : LPAREN error RPAREN'
    print(wrap_error('Not an expression.', p.lexer.lineno))
    p[0] = err_node()

def p_delimeters_unclosed(p):
    'expression : LPAREN error SEMI'
    'expression : LPAREN error STATEMENT'
    print(wrap_error('Unclosed parenthesis. ")" expected.', p.lexer.lineno))
    p[0] = err_node()

def p_struct_content(p):
    'braced_content : LBRACE content RBRACE'
    p[0] = p[2]

def p_struct_content_error(p):
    'braced_content : LBRACE error RBRACE'
    print(wrap_error('Error in struct content declaration. Only definitions of properties expected.', p.lexer.lineno))
    p[0] = err_node()

def p_struct_content_unclosed(p):
    'braced_content : LBRACE error SEMI'
    'braced_content : LBRACE error STATEMENT'
    print(wrap_error('Unclosed braces. "}" expected.', p.lexer.lineno))
    p[0] = err_node()

def p_struct(p):
    '''struct : STRUCT id braced_content'''
    line = p.lexer.lineno
    p[0] = Node('STRUCT', childs=[p[2], p[3]], line=line)

def p_struct_name_error(p):
    'struct : STRUCT error'
    p[0] = err_node()
    print(wrap_error('Struct name expected.', p.lineno(1)))

def p_struct_body_error(p):
    'struct : STRUCT id error'
    p[0] = err_node()
    print(wrap_error('Struct body expected.', p.lineno(3)))

def p_content(p):
    '''content : variable_decl_primitive SEMI
            | variable_decl_array_primitive SEMI
    '''
    line = p.lexer.lineno
    p[0] = Node('CONTENT', childs=[p[1]], line=line)

def p_content_semi_error(p):
    '''
    content : variable_decl_primitive error
            | variable_decl_array_primitive error
            | variable_decl_primitive ASSIGN expression error
            | content variable_decl_primitive error
            | content variable_decl_array_primitive error
            | content variable_decl_primitive ASSIGN expression error
    '''
    p[0] = Node('SCOPE', childs=[err_node()])
    print(wrap_error('There is a ";" expected after statement.', p.lexer.lineno))

def p_content_statement_error(p):
    '''
    content : statement
            | content statement
            | content func
            | func
            | struct
            | content struct
            | variable_decl_struct
            | content variable_decl_struct
    '''
    p[0] = Node('SCOPE', childs=[err_node()])
    print(wrap_error('Only primitive type definitions expected inside struct.', p.lexer.lineno))

def p_content_add(p):
    '''content : content variable_decl_primitive SEMI
            | content variable_decl_array_primitive SEMI
    '''
    p[1].add_childs([p[2]])
    p[0] = p[1]

def p_content_assign(p):
    '''content : variable_decl_primitive ASSIGN expression SEMI
            | variable_decl_array_primitive ASSIGN array_type_primitive array_size SEMI
    '''
    line = p.lexer.lineno
    if (len(p) == 5):
        p[0] = Node('CONTENT', childs=[Node('ASSIGN', childs=[p[1], p[3]], line=line)], line=line)
    else:
        p[0] = Node('CONTENT', childs=[
            Node('ASSIGN', childs=[p[1], 
                Node('ARRAY_ALLOC', childs=[p[3], p[4]])
        ], line=line)], line=line)

def p_content_assign_error(p):
    '''
    content : variable_decl_primitive ASSIGN error
            | content variable_decl_primitive ASSIGN error
    '''
    p[0] = Node('SCOPE', childs=[err_node()])
    print(wrap_error('Not an expression.', p.lexer.lineno))

def p_content_assign_array_error(p):
    '''
    content : variable_decl_array_primitive ASSIGN error
            | content variable_decl_array_primitive ASSIGN error
    '''
    p[0] = Node('SCOPE', childs=[err_node()])
    print(wrap_error('Array allocation expected.', p.lexer.lineno))

def p_content_assign_array_size_error(p):
    '''
    content : variable_decl_array_primitive ASSIGN array_type_primitive error
            | content variable_decl_array_primitive ASSIGN array_type_primitive error
    '''
    p[0] = Node('SCOPE', childs=[err_node()])
    print(wrap_error('Array size expected.', p.lexer.lineno))

def p_content_add_assign(p):
    '''content : content variable_decl_primitive ASSIGN expression SEMI
            | content variable_decl_array_primitive ASSIGN array_type_primitive array_size SEMI'''
    line = p.lexer.lineno
    if (len(p) == 6):
        p[1].add_childs([Node('ASSIGN', childs=[p[2], p[4]], line=line)])
        p[0] = p[1]
    else:
        p[1].add_childs([
            Node('ASSIGN', childs=[p[2], 
                Node('ARRAY_ALLOC', childs=[p[4], p[5]])
        ], line=line)])
        p[0] = p[1]

def p_empty_content_error(p):
    'content : empty'
    p[0] = err_node()
    print(wrap_error('Struct content can\'t be empty. Property definitions expected.', p.lexer.lineno))

def p_assignment(p):
    '''assignment : variable_decl ASSIGN expression
                | id ASSIGN expression
                | variable_decl ASSIGN array_alloc
                | id ASSIGN array_alloc
                | array_element ASSIGN expression
                | chain_call ASSIGN expression
    '''
    line = p.lexer.lineno
    p[0] = Node('ASSIGN', childs=[p[1], p[3]], line=line)

def p_empty(p):
    '''empty : '''
    pass

def p_func_args_paren(p):
    'func_arg_paren : LPAREN func_arg RPAREN'
    p[0] = p[2]

def p_func_args_unclosed(p):
    '''func_arg_paren : LPAREN error
                    | LPAREN func_arg error'''
    print(wrap_error('")" or argument declaration expected.', p.lexer.lineno))
    p[0] = err_node()

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
    p[0] = Node('FUNC_ARGS', childs=[p[1]] if p[1] and err_node().name != p[1].name else [], line=line)


def p_func_arg_add(p):
    '''func_arg : func_arg COMMA variable_decl'''
    p[1].add_childs([p[3]])
    p[0] = p[1]

def p_func_arg_add_error(p):
    '''func_arg : func_arg COMMA error
            | func_arg COMMA empty'''
    print(wrap_error('Argument declaration expected.', p.lexer.lineno))
    p[0] = err_node()

def p_func(p):
    ''' func : FUNCTION id func_arg_paren COLON func_type braced_scope'''
    line = p.lexer.lineno
    p[0] = Node('FUNCTION', childs=[p[2], p[3], p[5], p[6]], line=line)

def p_func_name_error(p):
    ' func : FUNCTION error'
    p[0] = err_node()
    print(wrap_error('Function name expected.', p.lexer.lineno))

def p_func_argparen_error(p):
    'func : FUNCTION id error'
    p[0] = err_node()
    print(wrap_error('Function arguments expected.', p.lexer.lineno))

def p_func_colon_error(p):
    'func : FUNCTION id func_arg_paren error'
    p[0] = err_node()
    print(wrap_error('":" and function type expected.', p.lexer.lineno))

def p_func_type_error(p):
    'func : FUNCTION id func_arg_paren COLON error'
    p[0] = err_node()
    print(wrap_error('Function type expected.', p.lexer.lineno))

def p_func_body_error(p):
    'func : FUNCTION id func_arg_paren COLON func_type error'
    p[0] = err_node()
    print(wrap_error('Function body expected.', p.lexer.lineno))

def p_scope(p):
    '''scope : scope statement
            | statement
    '''
    line = p.lexer.lineno
    if len(p) == 2:
        p[0] = Node('SCOPE', childs=[p[1]] if p[1] and err_node().name != p[1].name else [], line=line)
    else:
        p[1].add_childs([p[2]])
        p[0] = p[1]


def p_return(p):
    '''return : RETURN expression
              | RETURN
    '''
    line = p.lexer.lineno
    if len(p) == 3:
        p[0] = Node('RETURN', childs=[p[2]], line=line)
    else:
        p[0] = Node('RETURN', childs=[], line=line)

def p_loop_keywords(p):
    '''loop_keyword : SKIP
                      | BREAK
    '''
    p[0] = Node(p[1].upper(), line=p.lexer.lineno)


def p_single_statement(p):
    '''semi_needed_statement : assignment
            | expression
            | variable_decl
            | loop_keyword
            | goto
            | return
            | empty
    '''
    p[0] = p[1] if p[1] else Node('EMPTY_STATEMENT')

def p_single_statement_error(p):
    'statement : semi_needed_statement error'
    p[0] = err_node()
    print(wrap_error('There is a ";" expected after statement.', p.lexer.lineno))

def p_complex_statement(p):
    '''statement : func
            | struct
            | condition_full
            | loop
            | mark
            | semi_needed_statement SEMI
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

def p_binary_operators_error(p):
    '''expression : expression PLUS error
            | expression MINUS error
            | expression TIMES error
            | expression DIVIDE error
            | expression MODULO error
            | expression IDIVIDE error
            | expression BOR error
            | expression BAND error
            | error PLUS expression
            | error MINUS expression
            | error TIMES expression
            | error DIVIDE expression
            | error MODULO expression
            | error IDIVIDE expression
            | error BOR expression
            | error BAND expression
            | error LT expression
            | error GT expression
            | error GE expression
            | error LE expression
            | error EQ expression
            | error NE expression
            | error LOR expression
            | error LAND expression
            | LNOT error
            | expression LT error
            | expression GT error
            | expression GE error
            | expression LE error
            | expression EQ error
            | expression NE error
            | expression LOR error
            | expression LAND error
    '''
    p[0] = err_node()
    print(wrap_error('Expression expected.', p.lexer.lineno))

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
        | function_call
        | array_element'''
    p[0] = p[1]

def p_chain_call(p):
    '''chain_call : call
            | chain_call DOT call'''
    line = p.lexer.lineno
    if len(p) == 2:
        p[0] = Node("CHAIN_CALL", childs=[p[1]], line=line)
    elif len(p) == 4:
        p[1].add_childs([p[3]])
        p[0] = p[1]# p[0] = Node("CHAIN_CALL", childs=[p[1], p[3]], line=line)


# def p_chain_call_error(p):
#     '''chain_call : chain_call DOT error
#     '''
#     p[0] = err_node()
#     print(wrap_error('Property name expected.', p.lexer.lineno))

def p_full_condition(p):
    '''condition_full : condition_statement else_cond
            | condition_statement
    '''
    if len(p) == 3:
        p[1].add_childs([p[2]])
    p[0] = p[1]

def p_else_error(p):
    'condition_full : else_cond'
    p[0] = err_node()
    print(wrap_error('There must not be "else" without "if" before it.', p.lexer.lineno))

def p_elif_error(p):
    'condition_full : elif_cond'
    p[0] = err_node()
    print(wrap_error('There must not be "elif" without "if" or another "elif" before it.', p.lexer.lineno))

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
    'if_cond : IF expression_paren braced_scope'
    line = p.lexer.lineno
    p[0] = Node(
        'IF', childs=[Node('CONDITION', childs=[p[2]], line=line), p[3]], line=line)

def p_cond_error(p):
    '''if_cond : IF error
            | ELIF error '''
    p[0] = err_node()
    print(wrap_error('Expression in parentheses expected.', p.lexer.lineno))

def p_cond_body_error(p):
    '''if_cond : IF expression_paren error
            | ELIF expression_paren error
            | ELSE error'''
    p[0] = err_node()
    print(wrap_error('Condition body excepted.', p.lexer.lineno))

def p_elif_cond(p):
    '''elif_cond : ELIF expression_paren braced_scope'''
    line = p.lexer.lineno
    p[0] = Node(
        'ELIF', childs=[Node('CONDITION', childs=[p[2]], line=line), p[3]], line=line)

def p_else_cond(p):
    '''else_cond : ELSE braced_scope'''
    line = p.lexer.lineno
    p[0] = Node('ELSE', childs=[p[2]], line=line)

def p_loop(p):
    '''loop : while_loop
            | do_while_loop'''
    p[0] = p[1]

def p_do_while(p):
    'do_while_loop : DO braced_scope WHILE expression_paren SEMI'
    line = p.lexer.lineno
    p[0] = Node('DO_WHILE', childs=[p[2], Node('CONDITION', childs=[p[4]], line=line)], line=line)

def p_do_while_operator_error(p):
    'do_while_loop : DO braced_scope error'
    p[0] = err_node()
    print(wrap_error('Operator "while" expected.', p.lexer.lineno))

def p_while_body_error(p):
    '''do_while_loop : DO error 
        while_loop : WHILE expression_paren error
    '''
    p[0] = err_node()
    print(wrap_error('Loop body expected.', p.lexer.lineno))

def p_while_expression_error(p):
    '''
        while_loop : WHILE error
        do_while_loop : DO braced_scope WHILE error
    '''
    p[0] = err_node()
    print(wrap_error('Expression in parentheses expected.', p.lexer.lineno))

def p_while(p):
    'while_loop : WHILE expression_paren braced_scope'
    line = p.lexer.lineno
    p[0] = Node('WHILE', childs=[Node(
        'CONDITION', childs=[p[2]], line=line), p[3]], line=line)

def p_expression_paren(p):
    'expression_paren : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_paren_error(p):
    'expression_paren : LPAREN error RPAREN'
    print(wrap_error('Not an expression.', p.lexer.lineno))
    p[0] = err_node()

def p_expression_paren_unclosed(p):
    'expression_paren : LPAREN error '
    print(wrap_error('Unclosed parenthesis. ")" expected.', p.lexer.lineno))
    p[0] = err_node()


def p_braced_scope(p):
    'braced_scope : LBRACE scope RBRACE'
    p[0] = p[2]

def p_empty_braced_scope_error(p):
    'braced_scope : LBRACE empty RBRACE'
    p[0] = err_node()
    print(wrap_error('Scope can\'t be empty.', p.lexer.lineno))

def p_mark(p):
    'mark : id COLON'
    line = p.lexer.lineno
    p[0] = Node('MARK', childs=[p[1]], line=line)

def p_mark_id_error(p):
    '''mark : statement COLON
            | expression COLON'''
    p[0] = err_node()
    print(wrap_error('Mark name expected.', p.lexer.lineno))

def p_goto(p):
    'goto : GOTO id'
    p[0] = Node('GOTO', p[2].value)


def p_call_args(p):
    '''call_args : expression
        | empty'''
    line = p.lexer.lineno
    p[0] = Node('CALL_ARGS', childs=[p[1]] if p[1] and err_node().name != p[1].name else [], line=line)

def p_call_args_add(p):
    '''call_args : call_args COMMA expression'''
    p[0] = p[1].add_childs([p[3]])

def p_call_args_add_error(p):
    '''call_args : call_args COMMA error
                | call_args COMMA empty'''
    print(wrap_error('Argument expected.', p.lexer.lineno))
    p[0] = err_node()

def p_call_args_paren(p):
    'call_args_paren : LPAREN call_args RPAREN'
    p[0] = p[2]

def p_call_args_unclosed(p):
    '''call_args_paren : LPAREN error
                    | LPAREN call_args error'''
    print(wrap_error('")" or argument expected.', p.lexer.lineno))
    p[0] = err_node()

def p_func_call(p):
    'function_call : id call_args_paren'
    p[0] = Node('FUNC_CALL', childs=[p[1], p[2]], line=p[1].line)

def p_error(p):
    if p is not None:
        print('Illegal token "%s" at line %s' % (p.value, p.lexer.lineno))
        pass
    else:
        print('Unexpected end of input, probably some brace is lost')
