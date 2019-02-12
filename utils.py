
def getSecondBracket(x):
    if (x == "("): return ")"
    elif (x == ")"): return "("
    elif (x == "{"): return "}"
    elif (x == "}"): return "{"
    elif (x == "["): return "]"
    elif (x == "]"): return "["
    elif (x == "\""): return "\""
    elif (x == "\'"): return "\'"
    else: return None