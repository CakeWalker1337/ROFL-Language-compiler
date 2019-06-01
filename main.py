import sys
import ply.lex as lex
from initialdata import *
from rofl_parser import *
import io
import ply.yacc as yacc
from semantic_analysis import *
from syntax_analysis import *
from codegen import start_codegen
import argparse 

import xml.etree.ElementTree as etree
from xml.dom import minidom

from os import listdir, path, getcwd
from os.path import isfile, join, abspath, dirname, splitext

def convert_to_xml(root):
    main_scope = etree.Element('SCOPE')

    def convert_node(node, prev):
        node_xml = etree.SubElement(prev, node.name)
        if len(node.childs) == 0:
            node_xml.text = node.value
        else:
            for child in node.childs:
                convert_node(child, node_xml)

    if len(root.childs) == 0:
        main_scope.text = root.value
    else:
        for elem in root.childs:
            convert_node(elem, main_scope)
    return main_scope


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = etree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")


def llvm_prettify(code):
    additive = ""
    for line in code:
        if "define" in line:
            print(additive + line)
            additive = additive + "    "
        elif ":" in line:
            additive = additive[:-4]
            print(additive + line)
            additive += "    "
        elif "}" in line:
            additive = additive[:-4]
            print(additive + line)
        else:
            print(additive + line)


default_file = 'test.rofl'

if __name__ == "__main__":

    # handling of arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--xml', action='store_true', help='An optional boolean argument for XML output')
    arg_parser.add_argument('--file', type=str, nargs='?',
                            help='An optional argument for filename')
    args = arg_parser.parse_args()

    # parameter to show output in xml
    show_tree_with_errors = not args.xml
    filename = args.file if args.file else default_file

    lexer = lex.lex()

    with io.open(filename, "r", encoding="utf8") as f:
        text = f.read()
        ply_parser = yacc.yacc(debug=0)
        result = ply_parser.parse(text)
        print_xml_to_file = True
        print_xml_to_console = True

        if not result is None and \
                (len(result.get('ERROR', nest=True)) == 0):
            s_errors = check_func_and_struct_decl_place(result)
            if len(s_errors) == 0:
                # please add errors to that list of tuples
                # type: [('message', lineno), ...]
                errors = check_var_definition(result)
                if len(errors) == 0:
                    errors = errors + check_expression_results(result)
                if len(errors) == 0:
                    errors = errors + check_arguments_of_func_calls(result) + check_funcs_returns(result) + \
                             check_unexpected_keywords(result) + check_array_things(result) + \
                             check_array_allocation(result) + check_conditions(result)
                for error in sorted(errors, key=lambda tup: tup[1]):
                    print(error[0])

                if len(errors) == 0 and not show_tree_with_errors:
                    xml_result = convert_to_xml(result)

                    if print_xml_to_console:
                        print(prettify(xml_result))
                    if print_xml_to_file:
                        xmlfile = open(join(getcwd(), "program.xml"), "w+")
                        xmlfile.write(prettify(xml_result))
                    llvm_prettify(start_codegen(result))
                elif len(errors) == 0 and show_tree_with_errors:
                    print(result)
                    print("\n")
                    llvm_prettify(start_codegen(result))



            else:
                for error in s_errors:
                    print(error)
                print("There are some syntax errors detected in source code.")

        else:
            print("There are some syntax errors detected in source code.")
        



