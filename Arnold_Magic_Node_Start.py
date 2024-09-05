# -*- coding: utf-8 -*-
import os
import sys
import importlib


Script_path = os.path.join(os.path.dirname(__file__))

def main():
    import DependenciesLibs
    importlib.reload(DependenciesLibs)
    DependenciesLibs.Main_program()

    # import LicenseValidator
    # importlib.reload(LicenseValidator)
    # LicenseValidator.Main_program()

    import Arnold_Magic_Node
    importlib.reload(Arnold_Magic_Node)
    Arnold_Magic_Node.Main_program()