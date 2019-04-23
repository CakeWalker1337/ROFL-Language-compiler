
# Wraps the error message with error syntax
# returns tuple of error message and line number
def wrap_error(err_str, line_num):
    error_prefix = 'Semantic error at line '+ str(line_num) +': '
    return (error_prefix + err_str, line_num)


# returns (str ID, str TYPE) of node or just (str ID)
def get_info(node):
    if node.name == 'ID': return node.value
    elif node.name == 'FUNCTION': return node.childs[0].value, node.childs[2].value
    elif node.name == 'STRUCT': return node.childs[0].value, 'struct'
    elif node.name == 'VARIABLE': return node.childs[1].value, node.childs[0].value
    elif node.name == 'FUNC_CALL': return node.childs[0].value
    else: raise KeyError('Please add node to function get_info')

# def check_var_definition(node, scope = None, variables = {}):
#     cur_scope_vars = []

#     defs = node.get(['FUNCTION', 'STRUCT', 'VARIABLE'])
#     a = list(map(get_info, defs))
    

#     return 1

def check_funcs_have_returns(root):
    if root is not None:
        funcs = root.get("FUNCTION", nest=True)
        for func in funcs:
            ftype = func.get("TYPE")[0]
            scope = func.get("SCOPE")[0]
            rets = scope.get("RETURN", nest=True)
            if len(rets) == 0:
                if ftype.value != "void":
                    print("Return error: expected return statement with type \'%s\'. Line: %s" % (ftype.value, func.line))
            else:
                for ret in rets:
                    if ret.value is None and len(ret.childs) == 0:
                        print("Return error: function with type \"%s\" must return a value. Line: %s" % (
                        ftype.value, ret.line))


def check_unexpected_keywords(root):

    def check_keywords_recursive(node, prev_anchor=None, is_in_func=False):
        if node.name == "FUNCTION" or node.name == "WHILE" or node.name == "DO_WHILE":
            prev_anchor = node.name
            if node.name == "FUNCTION":
                is_in_func = True
        elif node.name == "RETURN" and not is_in_func:
            print("Unexpected return keyword outside of function. Line %s" % node.line)
        elif (node.name == "BREAK" or node.name == "SKIP") and (prev_anchor != "WHILE" and prev_anchor != "DO_WHILE"):
            print("Unexpected \'%s\' keyword outside of function. Line %s" % (node.name.lower(), node.line))
        for child in node.childs:
            check_keywords_recursive(child, prev_anchor, is_in_func)

    if root is not None:
        check_keywords_recursive(root)


# gets first defined function, struct or variable consider scopes
def find_element_by_id(id, scope):
    pass


#can be used when is needed to get closest scope from node
def get_nearest_scope(node):
    if node.parent.name == "SCOPE" or node.parent.name == "CONTENT":
        return node.parent
    return get_nearest_scope(node.parent)


#gets type of atom
def get_atom_type(atom):
    if atom.name == "CONST" or atom.name == "VARIABLE" or atom.name == "ARRAY_ALLOC":
        return atom.get("TYPE").value
    if atom.name == "ARRAY_ELEMENT":
        id = atom.children[0].children[0]
        arr = find_element_by_id(id)
        # if not arr is None:
        #     if not is_primitive_type(arr.children[0].children[0]):
        #         return arr.get_element_by_tag("DATATYPE").children[0].replace("[]", "")
        #     else:
        #         print("Array call error. Element can't be called as array element. Line: %s" % atom.line)
        #         return arr.children[0].children[0]
    looked_id = None
    if atom.name == "FUNC_CALL":
        looked_id = atom.get_element_by_tag("ID").children[0]
    elif atom.name == "ID":
        looked_id = atom.children[0]
    found_elem = find_element_by_id(looked_id)
    if found_elem is None:
        return None
    else:
        return found_elem.get_element_by_tag("DATATYPE").children[0]

def check_chain_calls(root):

    def find_chain_calls(node):
        if node.name == "CHAIN_CALL":
            check_chain_recursive(node)
        else:
            for child in node.childs:
                find_chain_calls(child)

    def check_chain_recursive(node):
        if node.value is not None:
            pass
            #return get_atom_type(node)
        else:
            prev_type = check_chain_recursive(node.childs[0])
