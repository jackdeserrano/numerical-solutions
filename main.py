from write_to_tex import *

name = str(input("Enter what you would like to name the file. \n"))
    
expression = str(input("\nEnter the expression you want solved.\n"
        + "Use M for matrix.\nUse parentheses when performing "
        + "exponentiation in an exponent.\n"))
    
make_file(True, name, result(expression))

