from semantic_analysis import *

def check_func_and_struct_decl_place(root):
    errors = []
    elems = root.get(["FUNCTION", "STRUCT"], nest=True)
    for elem in elems:
        if get_nearest_scope(elem).parent is not None:
            errors.append("Syntax error at line " + str(elem.get("ID")[0].line) + ": Unexpected declaration of " +
                          elem.name.lower() + " \'" + str(elem.get("ID")[0].value) + "\' in this scope.")
    return errors