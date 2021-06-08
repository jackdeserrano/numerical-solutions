import numpy as np
from numpy.linalg import matrix_power, inv, pinv

np.set_printoptions(suppress=True)

steps = []
matrices = []
tex_matrices = []


def matrix_clear(dimension):
    """
    21 for Mac Terminal (change for some other IDE)
    """
    
    print("\n" * (21 - dimension))

def floating(a):
    try:
        float(a)
        return True
    
    except:
        return False

    
def integer(a):
    try:
        if float(a) == int(float(a)):
            return int(a)
        
        return float(a)
    
    except:
        return a

    
def matrix_to_tex(list):
    """
    Take in a list and detect instances of np.ndarray. 
    Return each instance of np.ndarray converted to TeX in a list. 
    """
    matrix_list = []
    
    for i in range(len(list)):

        if isinstance(list[i], np.ndarray):

            matrix_dimension = list[i].shape[0]
            matrix_string = "\\left[\\begin{array}{" + "c" * matrix_dimension + "}"
            column = 0
            row = 0
            
            for j in range(matrix_dimension ** 2):

                if column == matrix_dimension:

                    column = 0
                    row += 1
                    matrix_string = matrix_string[:-1] + "\\\\"
                    
                value = integer(list[i][row][column])
                matrix_string += " {" + str(value) + "} &"
                column += 1
                
            matrix_string = matrix_string[:-1] + "\\end{array}\\right]"
            matrix_list.append(matrix_string)
            
    return matrix_list

  
def tex_to_matrix(string):
    """
    Take in a TeX matrix as a string. 
    Return the matrix converted to np.ndarray.
    """
    
    matrix_dimension = string.count("c")
    string = string.replace("{array}", "")
    string = string.replace("{c", "")
    string = string.replace("c}", "")
    matrix = np.zeros((matrix_dimension, matrix_dimension))
    column = 0
    row = 0
    
    for i in range(len(string)):

        if string[i] == "{":
            
            if column == matrix_dimension:
                column = 0
                row += 1

            for j in range(i, len(string)):

                if string[j] == "}":
                    value = float(string[i+1:j])
                    break

            value = integer(value)
            matrix[row][column] = value
            column += 1
            
    return matrix


def separate_expression(expression):
    """
    Take in an expression. 
    Return each individual part of the expression separated in a list.
    """
    
    expression = expression.replace(" ", "")
    expression = expression.replace("**", "?") + " "
    counter = 0
    int_counter = 0
    separated_expression = []
    is_negative = False
    is_tex_matrix = False
    expression = expression.replace("--", "+").replace("+-", "-")
    
    # don't separate numbers or TeX matrices    
    for i in expression:

        if not is_tex_matrix:

            try:
                int(i)
                int_counter += 1
                
            except:
                if i == "\\":
                    is_tex_matrix = True
                    
                elif i == ".":
                    int_counter += 1

                elif i == "e":
                    int_counter += 1
                
                elif i == "-":
                    if expression[counter-1].isdigit() or expression[counter-1] == ")": 
                        separated_expression.append(expression[counter-int_counter:counter])
                        separated_expression.append(i)
                        int_counter = 0
                    
                    else:
                        int_counter += 1
                        
                elif int_counter == 0:
                    separated_expression.append(i)
                    
                else:
                    separated_expression.append(expression[counter-int_counter:counter])
                    separated_expression.append(i)
                    int_counter = 0
                    
        else:
            
            if i == "]":
                separated_expression.append(expression[counter-int_counter-1:counter+1])
                is_tex_matrix = False
                int_counter = 0
                
            else:
                int_counter += 1
                
        counter += 1
        
    try:
        separated_expression.append(expression[counter-int_counter:counter])
        
    except:
        pass
    
    # delete unnecessary elements
    for i in range(len(separated_expression)-1, -1, -1):
        
        if separated_expression[i] == " " or separated_expression[i] == "":
            del separated_expression[i]
            
    return separated_expression


def parenthetical_list(expression):
    """
    Take in an expression as a string. 
    Return the expression as a string if parentheses aren't in the expression. 
    If parentheses are in the expression, return a list with three elements. 
    The first is list of expressions only found in parentheses in order of nesting. 
    Format so future definitions can parse it. 
    The second is list of the same expressions in same order, only evaluated. 
    The third is list of tuples, [0] separate instance of parentheses and [1] its beginning and end index.
    """
    
    expression = expression.replace(" ", "")
    
    if "(" in expression:
        
        parentheses_instances = []
        balance = 0
        counter = 0
        count = False
        expression_len = len(expression)
        
        # detect new instances of parentheses
        for i in range(expression_len):
            
            if expression[i] == "(":
                count = True
                balance += 1
                
            elif expression[i] == ")":
                balance -= 1
                
                if balance == 0:
                    parentheses_instances.append((expression[i+1-counter:i], (i+2-counter, i+1)))
                    counter = 0
                    count = False
                    
            if count:
                counter += 1
                
        p_0 = 0
        p_1 = 0
        par_list = []
        counter = 0
        alpha_counter = 0
        
        for i in range(expression_len):
            
            if expression[i] == ")":
                
                for j in range(i, -2, -1):
                    
                    if expression[j] == "(":
                        par_list.append(expression[j:i+1])

                        if counter < 10:
                        # replace expression inside nested parentheses with its index * however many necessary to maintain length
                            expression = expression.replace(expression[j:i+1],
                                f"[{str(counter)*(len(expression[j:i+1])-2)}]"
                                )
                            counter += 1
                            
                        else:
                            expression = expression.replace(expression[j:i+1],
                                f"[{chr(alpha_counter+97)*(len(expression[j:i+1])-2)}]"
                                )
                            alpha_counter += 1
                            
                        break
                        
        par_list_len = len(par_list)
        lengths = [0] * par_list_len
        
        for i in range(par_list_len):
            
            alpha = par_list[i]
            length = len(alpha)
            lengths[i] = (length)
            bracket_count = alpha.count("]")
            maximum = 0
            is_replacement = False
            
            for j in range(length):
                
                if alpha[j] == "]":
                    is_replacement = True
                    maximum += 1
                    
                    if maximum == bracket_count:
                        break
                       
            # replace length maintainer with actual index
            if is_replacement:
                
                for j in range(par_list_len):
                    
                    if j < 10:
                        par_list[i] = par_list[i].replace(
                            f"[{str(j)*(lengths[j]-2)}]", f"[{str(j)}]")
                        
                    else:
                        par_list[i] = par_list[i].replace(
                            f"[{chr(j+87)*(lengths[j]-2)}]", f"[{str(j)}]")
                    
        original_par_list = par_list.copy()
        
        # convert TeX to np.ndarray
        for i in range(par_list_len):
            
            if "\\begin" in par_list[i]:
                array_list = separate_expression(par_list[i])
                
                for j in range(len(array_list)):
                    
                    if "\\begin" in array_list[j]:
                        matrix = str(tex_to_matrix(array_list[j])).replace("\n", ", ")
                        
                        for k in range(10):
                            matrix = matrix.replace(f"{str(k)}. ", f"{str(k)}.,")

                        array_list[j] = "np.array(" + matrix + "))"
                        
                original_par_list[i] = "".join(array_list)
                
            # evaluate par_list in new list
            for j in range(par_list_len):
                
                if f"[{j}]" in original_par_list[i]:
                    
                    try:
                        original_par_list[i] = original_par_list[i].replace(
                            f"[{j}]", str(integer(eval(original_par_list[j].replace("?", "**")))))
                        
                    except Exception as e:
                        return "exception " + str(e) 
                    
        return [par_list, original_par_list, parentheses_instances]

    else:
        return expression


def exp(expression):
    """
    Take in an expression as a string. 
    Return a simplified version of the expression as a string (without exponents) if every step can be calculated.
    Append each simplification to steps.
    If something cannot be done, return an error message.
    """
    
    after_parentheses = separate_expression(expression)
    exp_matrices = matrix_to_tex(after_parentheses)
    
    # convert np.ndarrray to TeX to add to steps
    if exp_matrices != []:
        counter = 0
        
        for i in range(len(after_parentheses)):
            
            if isinstance(after_parentheses[i], np.ndarray):  
                after_parentheses[i] = exp_matrices[counter]
                counter += 1
                
    expression = "".join(after_parentheses)
    steps.append(expression)
    
    while "?" in after_parentheses:
        
        exp_list = []
        
        # convert TeX to np.ndarray
        for i in range(len(after_parentheses)):
            
            if "\\begin" in after_parentheses[i]:
                after_parentheses[i] = tex_to_matrix(after_parentheses[i])
                
        # delete parentheses around np.ndarray instances  
        for i in range(len(after_parentheses)-1, -1, -1):
            
            try:
                if isinstance(after_parentheses[i], np.ndarray) and after_parentheses[i+1] == ")": 
                    del after_parentheses[i+1]
                    
                    if after_parentheses[i-1] == "(":
                        del after_parentheses[i-1]
                        
            except:
                continue
                
        # save all instances of exponentiation
        for i in range(len(after_parentheses)-1):
            
            if exp_list != [] and after_parentheses[i+1] != "(":
                
                if after_parentheses[i] == "?" and after_parentheses[i-1] != exp_list[-1][1]:
                    exp_list.append((after_parentheses[i-1], after_parentheses[i+1], i))
                    break
            else:
                
                if after_parentheses[i] == "?":
                    exp_list.append((after_parentheses[i-1], after_parentheses[i+1], i))
                    break
                    
        # evaluate exponentiations and retain remainder of expression in list
        for i in range(len(exp_list)):
            
            exp_0 = exp_list[i][0]
            exp_1 = exp_list[i][1]
            exp_2 = exp_list[i][2]
            
            if isinstance(exp_0, np.ndarray) and isinstance(exp_1, np.ndarray):
                return "exception cannot raise matrix to matrix power"
            
            # matrix exponentiation is not done elementwise
            elif isinstance(exp_0, np.ndarray):
                
                try:
                    after_parentheses[exp_2+1] = ""
                    after_parentheses[exp_2-1] = ""
                    after_parentheses[exp_2] = matrix_power(exp_0, integer(float(exp_1)))
                    
                except Exception as e:
                    return "exception " + str(e)
                
            elif isinstance(exp_1, np.ndarray):
                return "exception cannot raise scalar to matrix power"
            
            else:
                
                try:
                    after_parentheses[exp_2+1] = ""
                    after_parentheses[exp_2-1] = ""
                    after_parentheses[exp_2] = str(integer(float(exp_0) ** float(exp_1)))
                    
                except Exception as e:
                    return "exception " + str(e) 
                
        exp_matrices = matrix_to_tex(after_parentheses)
        
        # convert np.ndarrray to TeX to add to steps
        if exp_matrices != []:
            counter = 0
            
            for i in range(len(after_parentheses)):
                
                if isinstance(after_parentheses[i], np.ndarray):
                    after_parentheses[i] = exp_matrices[counter]
                    counter += 1
                    
        # append expression to steps after each step
        expression = "".join(after_parentheses)
        steps.append(expression)
        
    return "".join(after_parentheses)


def div(expression):
    """
    The same idea as exp, only with division and multiplication.
    """
    
    if "exception" in expression:
        return expression

    after_exponents = separate_expression(expression)
    div_matrices = matrix_to_tex(after_exponents)
    
    if div_matrices != []:
        counter = 0
        
        for i in range(len(after_exponents)):
            
            if isinstance(after_exponents[i], np.ndarray):  
                after_exponents[i] = div_matrices[counter]
                counter += 1
                
    expression = "".join(after_exponents)
    steps.append(expression)
    
    while "/" in after_exponents or "*" in after_exponents:
        
        div_list = []
        after_exponents = separate_expression(expression)
        after_exponents = list(filter(lambda x: x != "", after_exponents))
        after_exponents_len = len(after_exponents)
        
        for i in range(after_exponents_len):
            
            if "\\begin" in after_exponents[i]:
                after_exponents[i] = tex_to_matrix(after_exponents[i])
                
        # save divisions as multiplying by the inverse        
        for i in range(1, after_exponents_len):
            
            try:
                
                try:
                    a_0 = float(after_exponents[i-1].replace(")", "").replace("(", ""))
                    
                except:
                    a_0 = after_exponents[i-1]
                    
                try:
                    a_1 = float(after_exponents[i+1].replace(")", "").replace("(", ""))
                    
                except:
                    a_1 = after_exponents[i+1]
        
                if div_list != []:
                    
                    if isinstance(a_0, np.ndarray) or isinstance(a_1, np.ndarray):
                        
                        if after_exponents[i] == "/" or after_exponents[i] == "*":
                            
                            if a_0 != div_list[-1][1] and 1/a_0 != div_list[-1][1]:
                               div_list.append((a_0, a_1, i))
                               break
                            
                    elif after_exponents[i] == "/" and a_0 != div_list[-1][1] and 1/(a_0) != div_list[-1][1]:
                        div_list.append((float(a_0), 1/float(a_1), i))
                        break
                        
                    elif after_exponents[i] == "*" and a_0 != div_list[-1][1] and 1/(a_0) != div_list[-1][1]:
                        div_list.append((float(a_0), float(a_1), i))
                        break
                        
                else:
                    
                    if isinstance(a_0, np.ndarray) or isinstance(a_1, np.ndarray):
                        
                        if after_exponents[i] == "/" or after_exponents[i] == "*":
                            div_list.append((a_0, a_1, i))
                            break
                        
                    elif after_exponents[i] == "/":
                        div_list.append((float(a_0), 1/float(a_1), i))
                        break
                        
                    elif after_exponents[i] == "*":
                        div_list.append((float(a_0), float(a_1), i))
                        break
                        
            except ZeroDivisionError as e:
                return "exception " + str(e)
            
            except Exception:
                break
           
        for i in range(len(div_list)):
            
            div_0 = div_list[i][0]
            div_1 = div_list[i][1]
            div_2 = div_list[i][2]
            
            # matrix multiplication not done elementwise
            if isinstance(div_0, np.ndarray) and isinstance(div_1, np.ndarray):
                
                try:

                    if after_exponents[div_2] == "/":
                        after_exponents[div_2+1] = pinv(div_1)
                        after_exponents[div_2] = "*"
                        
                    else:
                        after_exponents[div_2+1] = ""
                        after_exponents[div_2-1] = ""
                        after_exponents[div_2] = np.matmul(div_0, div_1)
                        
                except Exception as e:
                    return "exception " + str(e)
                
            elif isinstance(div_0, np.ndarray):
                
                try:
                    
                    if after_exponents[div_2] == "/":
                        after_exponents[div_2+1] = ""
                        after_exponents[div_2-1] = ""
                        after_exponents[div_2] = div_0 / float(div_1)
                        
                    else:
                        after_exponents[div_2+1] = ""
                        after_exponents[div_2-1] = ""
                        after_exponents[div_2] = div_0 * float(div_1)
                        
                except Exception as e:
                    return "exception " + str(e)
                
            elif isinstance(div_1, np.ndarray):
                
                try:
                    
                    if after_exponents[div_2] == "/":
                        
                        # - will disappear if multiplier is negative
                        if after_exponents[div_2-1] >= 0:
                            after_exponents[div_2+1] = ""
                            after_exponents[div_2-1] = ""
                            
                        else:
                            after_exponents[div_2+1] = ""
                            after_exponents[div_2-1] = "+"
                            
                        after_exponents[div_2] = float(div_0) / div_1
                        
                    else:
            
                        if float(after_exponents[div_2-1]) >= 0:
                            after_exponents[div_2+1] = ""
                            after_exponents[div_2-1] = ""
                            
                        else:
                            after_exponents[div_2+1] = ""
                            after_exponents[div_2-1] = "+"
                            
                        after_exponents[div_2] = float(div_0) * div_1
                        
                except Exception as e:
                    return "exception " + str(e)
                
            else:
                
                try:

                    if float(after_exponents[div_2-1]) >= 0:
                        after_exponents[div_2+1] = ""
                        after_exponents[div_2-1] = ""
                    else:
                        after_exponents[div_2+1] = ""
                        after_exponents[div_2-1] = "+"
                        
                    after_exponents[div_2] = str(integer(div_0 * div_1))

                except Exception as e:
                    return "exception " + str(e)
                
        div_matrices = matrix_to_tex(after_exponents)
        
        if div_matrices != []:
            counter = 0
            
            for i in range(len(after_exponents)):
                
                if isinstance(after_exponents[i], np.ndarray):
                    after_exponents[i] = div_matrices[counter]
                    counter += 1
                    
        if len(list(filter(lambda x: x != "", after_exponents))) == 2:
            
            if after_exponents[0] == "+":
                after_exponents[0] = ""
                
        expression = "".join(after_exponents)
        steps.append(expression)
        
    return "".join(after_exponents)


def add(expression):
    """
    The same idea as exp and div, only with addition and subtraction.
    """
    
    if "exception" in expression:
        return expression
    
    after_division = separate_expression(expression)
    add_matrices = matrix_to_tex(after_division)
    
    if add_matrices != []: 
        counter = 0
        
        for i in range(after_division_len):
            
            if isinstance(after_division[i], np.ndarray):
                after_division[i] = add_matrices[counter]
                counter += 1
                
    expression = "".join(after_division).replace("(", "").replace(")", "")
    steps.append(expression)
    
    while "+" in after_division or "-" in after_division:
        
        add_list = []
        after_division = separate_expression(expression)
        after_division = list(filter(lambda x: x != "", after_division))
        after_division_len = len(after_division)
        
        for i in range(after_division_len):
            
            if "\\begin" in after_division[i]:
                after_division[i] = tex_to_matrix(after_division[i])
                
        # save subtractions as additions * -1
        for i in range(1, after_division_len):
            
            try:
                try:
                    a_0 = float(after_division[i-1].replace(")", "").replace("(", ""))

                except:
                    a_0 = after_division[i-1]
                    
                try:
                    a_1 = float(after_division[i+1].replace(")", "").replace("(", ""))

                except:
                    a_1 = after_division[i+1]
                    
                if add_list != []:

                    if isinstance(a_0, np.ndarray) or isinstance(a_1, np.ndarray):

                        if after_division[i] == "+" or after_division[i] == "-":

                            if a_0 != add_list[-1][1] and a_0 * -1 != add_list[-1][1]:
                                add_list.append((a_0, a_1, i))
                                break
                            
                    elif after_division[i] == "-" and a_0 != add_list[-1][1] and -1 * a_0 != add_list[-1][1]:
                        add_list.append((float(a_0), -1 * float(a_1), i))
                        break
                        
                    elif after_division[i] == "+" and a_0 != add_list[-1][1] and -1 * a_0 != add_list[-1][1]:
                        add_list.append((float(a_0), float(a_1), i))
                        break
                        
                else:

                    if isinstance(a_0, np.ndarray) or isinstance(a_1, np.ndarray):

                        if after_division[i] == "+" or after_division[i] == "-":
                            add_list.append((a_0, a_1, i))
                        
                    elif after_division[i] == "-":
                        add_list.append((float(a_0), -1 * float(a_1), i))
                        
                    elif after_division[i] == "+":
                        add_list.append((float(a_0), float(a_1), i))
                        
            except:   
                pass
            
        for i in range(len(add_list)):
            
            add_0 = add_list[i][0]
            add_1 = add_list[i][1]
            add_2 = add_list[i][2]
            
            try:
                
                if isinstance(add_0, np.ndarray) and isinstance(add_1, np.ndarray):

                    if after_division[add_2] == "+":
                        after_division[add_2-1] = ""
                        after_division[add_2+1] = ""
                        after_division[add_2] = add_0 + add_1
                        
                    else:
                        after_division[add_2-1] = ""
                        after_division[add_2+1] = ""
                        after_division[add_2] = add_0 - add_1
                        
                elif isinstance(add_0, np.ndarray):
                    return "exception cannot add matrix to scalar" 
                
                elif isinstance(add_1, np.ndarray):
                    return "exception cannot add scalar to matrix"
                
                else:
                    after_division[add_2-1] = ""
                    after_division[add_2+1] = ""
                    after_division[add_2] = str(integer(add_0 + add_1))

            except Exception as e:
                return "exception " + str(e)
            
        add_matrices = matrix_to_tex(after_division)
        
        if add_matrices != []:
            
            counter = 0
            
            for i in range(after_division_len):
                
                if isinstance(after_division[i], np.ndarray):
                    after_division[i] = add_matrices[counter]
                    counter += 1
                    
        expression = "".join(after_division).replace("(", "").replace(")", "")
        steps.append(expression)
        
    return 0


def result(expression):
    """
    Take in the original expression. 
    Use the above definitions and do some work to return TeX-compatible string.  
    """
    
    par_balance = []

    # check for incorrect placement of parentheses
    for i in range(len(expression)):

        if expression[i] == "(":
            par_balance.append(0)
        
        elif expression[i] == ")":
                
            if par_balance != []:
                del par_balance[0]
                    
            else:
                raise EOFError("check for unnmatched or misplaced parentheses")      

    if par_balance != []:
        raise EOFError("extra '('")
    
    balance = 0

    # detect wheter matrix found within parentheses
    for i in range(len(expression)):
        
        if expression[i] == "(":
            balance += 1
            
        elif expression[i] == ")":
            balance -= 1
            
        elif expression[i] == "M":

            if balance != 0:
                raise NotImplementedError("cannot handle matrix in parentheses")

        
    operations = ["+", "-", "*", "/", "?", "(", ")", "\\", "M"]

    expression = expression.replace("**", "?").replace("^", "?").replace(" ", "")

    unknown = []

    for i in expression:
        if not i.isdigit() and i not in operations and i != ".":
            unknown.append(i)

    if unknown != []:
        unknown = ", ".join(unknown)
        raise SyntaxError(f"uninterpretable values: {unknown}")
            
    exponent = False
    
    for i in list(expression):
        
        if i == "^":

            if exponent == True:
                raise NotImplementedError("cannot handle double, triple, etc. exponents. "
                                           + "try putting exponent in parentheses.")
            
            exponent = True

        elif i in operations and i != "M":
            exponent = False

    expression = separate_expression(expression)
                
    expression = "".join(expression)
    steps.append(expression)

    expression = expression.replace("^", "?")
    expression = expression.replace(" ", "")
    expression = expression.replace(")(", ")*(")
    expression = expression.replace("{", "")
    expression = expression.replace("}", "")
    
    matrix_present = False
    
    if "M" in expression:
        matrix_present = True
        
    new_expression = separate_expression(expression)
    
    if matrix_present:
        expression_for_printing = " ".join(new_expression).replace("?", "**")
        matrix_correct = True
        all_same = False
        
        for i in range(len(expression_for_printing)):
            
            if not matrix_correct:
                i -= 1
                
            if "M" == expression_for_printing[i]:
                is_identity = False
                
                if matrices == [] and expression_for_printing.count("M") != 1:
                    
                    if "n" in input("Will all matrices be the same? (y/n) \n"):
                        pass
                    
                    else: 
                        all_same = True
   
                        matrix_clear(1)
                        matrix_dimension = int(input("Dimension of all matrices: \n"))
                        
                        matrix = np.zeros((matrix_dimension, matrix_dimension))
                        column = 0
                        row = 0
                        j = 0
                        
                        while j < matrix_dimension ** 2:
                            
                            if column == matrix_dimension: 
                                column = 0
                                row += 1
                                
                            print(matrix)
                            matrix_clear(matrix_dimension)
                            value = input("Enter values starting from top left moving across (i for identity).\n")
                            
                            if value == "":
                                pass
                            
                            elif value.lower() == "i":
                                print(np.identity(matrix_dimension))
                                matrix_clear(matrix_dimension)
                                
                                if "n" in input("Do you mean the identity matrix? (y/n) \n").lower():
                                    pass
                                
                                else:
                                    is_identity = True
                                    matrix = np.identity(matrix_dimension)
                                    break
                                    
                            else:
                                matrix[row][column] = value
                                column += 1
                                j += 1
                                
                        if not is_identity:
                            print(matrix)
                            matrix_clear(matrix_dimension)
                            
                            if "n" in input("Correct? (y/n) \n").lower():
                                matrix_correct = False
                            
                        if matrix_correct:
                            matrices.append(matrix)
                        
                if not all_same:
                    # almost user-friendly prompt for taking in matrix information
                    print(str(expression_for_printing[:i] + "[" + expression_for_printing[i] + "]" + expression_for_printing[i+1:]))
                    matrix_clear(1)
                    matrix_dimension = int(input("Dimension of selected matrix: \n"))
                    
                    matrix = np.zeros((matrix_dimension, matrix_dimension))
                    column = 0
                    row = 0 
                    j = 0
                    
                    while j < matrix_dimension ** 2:
                        
                        if column == matrix_dimension:
                            column = 0
                            row += 1
                            
                        print(matrix)
                        matrix_clear(matrix_dimension)
                        value = input("Enter values starting from top left moving across (i for identity). \n")
                        
                        if value == "":
                            pass
                        
                        elif value.lower() == "i":
                            print(np.identity(matrix_dimension))
                            matrix_clear(matrix_dimension)

                            if "n" in input("Do you mean the identity matrix? (y/n) \n").lower():
                                pass
                            
                            else:
                                is_identity = True
                                matrix = np.identity(matrix_dimension)
                                break
                                
                        else:  
                            matrix[row][column] = value
                            column += 1
                            j += 1
 
                    if not is_identity:
                        print(matrix)
                        matrix_clear(matrix_dimension)
                        
                        if "n" in input("Correct? (y/n) \n").lower():
                            matrix_correct = False
                            
                    if matrix_correct:
                        matrices.append(matrix)
                        
                else:
                    matrices.append(matrices[0])
                    
        matrix_clear(0)
        
    new_expression = "".join(new_expression)

    for i in range(10):
        new_expression = new_expression.replace(f"{i}(", f"{i}*(")
        new_expression = new_expression.replace(f"{i}M", f"{i}*M")

    new_expression = separate_expression(new_expression)
                    
    matrix_counter = 0
    new_exp_len = len(new_expression)
    
    # convert np.ndarray to TeX
    for i in range(new_exp_len):
        
        if "M" == new_expression[i]:
            matrix_dimension = matrices[matrix_counter].shape[0]
            
            tex_matrix = "\\left[\\begin{array}{" + "c" * matrix_dimension + "}"
            
            column = 0
            row = 0
            
            for j in range(matrix_dimension ** 2):
                
                if column == matrix_dimension:
                    column = 0
                    row += 1
                    tex_matrix = tex_matrix[:-1] + "\n\\\\"
                    
                value = integer(matrices[matrix_counter][row][column])   
                tex_matrix += " {" + str(value) + "} &"
                column += 1
                
            tex_matrix = tex_matrix[:-1] + "\\end{array}\\right]"
            tex_matrices.append(tex_matrix)
            matrix_counter += 1
            
    counter = 0
    
    # replace each "M" in string with its respective TeX matrix
    for i in range(len(new_expression)):
        
        if "M" == new_expression[i]:
            new_expression[i] = tex_matrices[counter]
            counter += 1
            
    new_expression_string = "".join(new_expression)
    
    if new_expression_string != steps[0].replace("}", "").replace("{", "").replace(" ", "").replace("^", "?").replace("\\cdot", "*"):
        steps.append(new_expression_string.replace(" ", ""))
        
    parenthetical_list_tuple = parenthetical_list(new_expression_string)
    exception = False

    if "exception" in parenthetical_list_tuple:
        exception = True
    
    if parenthetical_list_tuple != new_expression_string.replace(" ", "") and not exception:
        parenthetica_list = parenthetical_list_tuple[0]
        evaluated_parenthetical_list = parenthetical_list_tuple[1]
        beginning_parentheses = parenthetical_list_tuple[2]
        
        for i in range(len(parenthetica_list)):
            gamma = evaluated_parenthetical_list[i]
            difference = gamma.count(")") - gamma.count("(")
            replacement = (eval("(" * difference + gamma.replace("?", "**")))
            new_expression_string = new_expression_string.replace(gamma, str(replacement))
            
            # append each parenthetical simplification to steps
            steps.append(new_expression_string.replace(" ", ""))
            
        # simplify and evaluate expression
        for i in range(len(beginning_parentheses)):
            delta = str(beginning_parentheses[i])
            
            if "\\begin" in delta:
                delta_list = separate_expression(delta)
                
                for j in range(len(delta_list)):
                    
                    if "\\begin" in delta_list[j]:
                        matrix = str(tex_to_matrix(delta_list[j])).replace("\n", ", ")

                        for k in range(10):
                            matrix = matrix.replace(f"{str(k)}. ", f"{str(k)}.,")

                        delta_list[j] = "np.array(" + matrix + "))"
                        
                delta = "".join(delta_list)
                
            new_expression_list = separate_expression(new_expression_string)
            
            for j in range(len(new_expression_list)):
                
                if "\\begin" in new_expression_list[j]: 
                    matrix = str(tex_to_matrix(new_expression_list[j])).replace("\n", ", ")
                    for k in range(10):

                        matrix = matrix.replace(f"{str(k)}. ", f"{str(k)}.,")

                    new_expression_list[j] = "np.array(" + matrix + ")"
                    
            new_expression_string = "".join(new_expression_list)
            delta_parentheses = delta.count(")") - delta.count("(")
            delta = delta.replace("?", "**").replace("\n", ", ")
            
            new_expression_string = new_expression_string.replace(
                delta, str(eval(delta))
                )
            
            if isinstance(eval(delta), np.ndarray):
                new_expression_string = new_expression_string.replace(
                    str(eval(delta)), str(matrix_to_tex([(eval(delta))])[0])
                    )
                
    new_expression_list = list(new_expression_string)
   
    # join each np.ndarray instance into one element in new_expression_list
    if "n" in new_expression_list and not exception:
        
        for i in range(len(new_expression_list)):
            
            try:
                if new_expression_list[i] == "n" and new_expression_list[i+1] == "p":

                    for j in range(i, len(new_expression_list)):
                        
                        try:
                            if new_expression_list[j] == "]" and new_expression_list[j+1] == "]" and new_expression_list[j+2] == ")":
                                new_expression_list[i:j+3] = ["".join(new_expression_list[i:j+3])]
                                break

                        except:
                            break

            except:
                break
            
    # convert each np.ndarray instance to TeX
    for i in range(len(new_expression_list)):
        
        if "np.array" in new_expression_list[i]:
            new_expression_list[i] = matrix_to_tex([eval(str(new_expression_list[i]))])[0]
            
    # carry out simplifications using above definitions
    new_expression_string = "".join(new_expression_list)
    new_expression_string = exp(new_expression_string)
    new_expression_string = div(new_expression_string)
    new_expression_string = add(new_expression_string)
    counter_list = []
    
    # universalize each step's TeX
    for i in range(len(steps)):
        steps[i] = steps[i].replace("{(", "(")
        steps[i] = steps[i].replace(")}", ")")

    # remove repeats
    filtered_steps = list(dict.fromkeys(steps))
    
    # epsilon = boxed answer if no errors
    if exception:
        epsilon = "&\\textrm{" + parenthetical_list_tuple[10:] + "}"
        
    # epsilon = error if it exists
    else:
        epsilon = "&\\textrm{" + str(new_expression_string)[10:] + "}"
        
    steps_string = ""

    # add each TeX-compatible step to a string to be returned
    for i in range(len(filtered_steps)):

        try:
            zeta = filtered_steps[i]
            zeta = zeta.replace("?", "^")
            zeta = zeta.replace("+-", "-")
            zeta = zeta.replace("--", "+")
            zeta = zeta.replace("(", "{(")
            zeta = zeta.replace(")", ")}")

            zeta_list = separate_expression(zeta)
            
            # change e- to 10^{-
            for j in range(len(zeta_list)):
                
                sep_zeta_list = list(zeta_list[j])

                for k in range(len(sep_zeta_list)):

                    try:
                        if sep_zeta_list[k] == "e" and sep_zeta_list[k+1] == "-":
                            sep_zeta_list.insert(k+4, "}")
                            sep_zeta_list[k]="{"
                            sep_zeta_list.insert(k,"^")
                            sep_zeta_list.insert(k,"10")
                            sep_zeta_list.insert(k,"*")
                            
                        
                            if sep_zeta_list[k+5] == "0":
                                sep_zeta_list[k+5] = ""

                            sep_zeta_list.insert(k+8, ")")

                            for l in range(k, 0, -1):

                                if sep_zeta_list[l] == ".":
                                    sep_zeta_list.insert(l-1, "(")

                        elif sep_zeta_list[k] == "e" and floating(sep_zeta_list[k+1]):
                            sep_zeta_list.insert(k+3, "}")
                            sep_zeta_list[k]="{"
                            sep_zeta_list.insert(k,"^")
                            sep_zeta_list.insert(k,"10")
                            sep_zeta_list.insert(k,"*")
                    except:
                        pass 

                zeta_list[j] = "".join(sep_zeta_list)
                    
            # correctly format exponents
            for j in range(len(zeta_list)):
                
                try:

                    if zeta_list[j] == "^":
                        
                        if floating(zeta_list[j+1]) or "\\begin{array}" in zeta_list[j+1]:

                            if "\\begin{array}" not in zeta_list[j+1]:
                                zeta_list[j+1] = "{" + zeta_list[j+1].replace("(", "").replace(")", "") + "}"
                                
                            else:
                                zeta_list[j+1] = "{" + zeta_list[j+1] + "}"

                except:
                    break

            zeta = "".join(zeta_list)
            
            # remove duplicates (unexplained bug)
            for j in ["^", "/", "+", "-"]:
                
                if j * 2 in zeta:
                    zeta = zeta.replace(j * 2, j)
            
            for j in range(len(zeta)):
                
                if zeta[j] == "-":
                    
                    if zeta[j-1] in operations:
                        
                        for k in range(j+1, len(zeta)-1):
                            
                            if zeta[k] in operations: 
                                zeta = zeta[:j] + "(" + zeta[j:k] + ")" + zeta[k:]
                                break
                            
                        break

        except:
            pass

                        
        steps_string += "".join(zeta)

        if i != len(filtered_steps)-1:
            steps_string += "\n\\\\="
        

    steps_string = "".join(steps_string)

    
    steps_string = steps_string.replace("inf", "\\infty")
    steps_string = steps_string.replace("(", "{\\left(")
    steps_string = steps_string.replace(")", "\\right)}")
    steps_string = steps_string.replace("*", "\\cdot ")
    steps_string = steps_string.replace(",", "\\,")
    steps_string = steps_string.replace("\\\\,", "\\,")
    steps_string = "&" + steps_string.replace("\\\\=", "\\\\=\\ &")

    steps_string = list(steps_string)
    
    for i in range(len(steps_string)-1, 0, -1):

        break_bool = False

        if steps_string[i] == "n":
            
            for j in range(i, 0, -1):
                
                if steps_string[j] == "&" and steps_string[j+1] != "{":
                    steps_string.insert(j+1, "\\boxed{")
                    break_bool = True
                    break
                
        if break_bool:
            break

        if steps_string[i] == "&":
            steps_string.insert(i+1, "\\boxed{")
            break

    steps_string = "".join(steps_string)

    if "{" in steps_string:

        steps_string += "}\\\\"
    
    if epsilon != "&\\textrm{}":
        steps_string+= epsilon
    
    if "\\\\boxed" in steps_string:
        steps_string = steps_string.replace("\\\\boxed", "\\boxed")
        
    if "\\boxed" not in steps_string:
        steps_string = steps_string.replace("boxed", "\\boxed")
    
    return steps_string