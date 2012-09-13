#!/usr/bin/env python

from __future__ import print_function
import sys

from pycparser.c_parser import CParser
from pycparser.c_generator import CGenerator
from pycparser.c_ast import NodeVisitor
from pycparser import c_ast

class MethodVisitor(NodeVisitor):
    def __init__(self):
        self.current_parent = None
        self.test_functions = []

    def generic_visit(self, node):
        """ Called if no explicit visitor function exists for a
            node. Implements preorder visiting of the node.
        """

        def check_ensure_statement(func_node):
            return any([call for call
                             in func_node.body.block_items
                             if isinstance(call, c_ast.FuncCall) and
                                call.name.name == "ENSURE"])


        if isinstance(node, c_ast.FuncDef):
            check = check_ensure_statement(node)
            if check:
                self.test_functions.append(node.decl.name)

        oldparent = self.current_parent
        self.current_parent = node
        for c_name, child in node.children():
            self.visit(child)
        self.current_parent = oldparent

def build_main(function_names, file_name):
    """
        I'll build C code from an AST in near future :)
    """

    main_template = \
'''
%(include_text)s
#include <thc.h>
#include "%(file_name)s"

int main(int argc, char **argv) {
    ##TESTS##

    return thc_run(THC_VERBOSE);
}
''' % dict(file_name=file_name)

    test_call = "\n    thc_addtest(%(function_name)s);"

    tests = ""
    for function_name in function_names:
        tests += test_call % dict(function_name=function_name)

    main_template = main_template.replace("##TESTS##", tests)
    return main_template

def main(file_path):
    dir_and_name = file_path.split('/')
    tests_dir = dir_and_name[0]
    file_name = dir_and_name[1]
    file_content = open(file_path, "rt").read()

    parser = CParser()
    generator = CGenerator()

    ast = parser.parse(file_content, file_name, debuglevel=0)

    test_finder = MethodVisitor()
    test_finder.visit(ast)

    suite_code = build_main(test_finder.test_functions, file_name)

    suite_file = open("/".join([tests_dir, "suite.c"]), "wt")
    suite_file.write(suite_code)
    suite_file.close()

if __name__ == "__main__":
    """
        Usage:
        $ suite_generator tests/test_my_lib.c

        This will look for functions that contains calls to ENSURE and
        then generates the main function calling thc_addtest(func_name)
        and then thc_run()
    """
    main(sys.argv[1])
