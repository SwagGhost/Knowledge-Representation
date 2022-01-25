from sys import stdin
from copy import copy, deepcopy
import time
import argparse

def parseFileInput(in_file, cnf):
    cnf.append(list())
    for line in in_file:
        tokens = line.split()
        if len(tokens) > 0 and tokens[0] not in ("p", "c"):
            for token in tokens:
                lit = int(token)
                if lit == 0: cnf.append(list())
                else: cnf[-1].append(lit)
    cnf.pop()
    return cnf

def transformSudoku(in_file):
    line = in_file.readline()
    vars = list()
    row = 1
    col = 1
    for token in line:
        if token != '.': vars.append(int(str(row) + str(col) + str(token)))
        col += 1
        if col == 10:
            row += 1
            col = 1
            if row == 10: break
    return vars

def parse(files):
    file1 = open(files[0], "r")
    if len(files) == 1:
        line = file1.readline()
        if "p" in line:
            cnf = parseFileInput(file1, list())
            file1.close()
            return True, cnf
        file1 = open(files[0], "r")
        vars = transformSudoku(file1)
        createOutFile(files[0] + ".out.txt", vars)
        file1.close()
        return False, list()
    file2 = open(files[1], "r")
    cnf = parseFileInput(file1, parseFileInput(file2, list()))
    file1.close()
    file2.close()
    return True, cnf

def assignValue(cnf, lit, literals):
    for clause in copy(cnf):
        if lit in clause: cnf.remove(clause)
        if -lit in clause: clause.remove(-lit)
    if lit > 0: literals.append(lit)
    return cnf, literals

def unitPropagation(cnf, literals):
    unit_clause = False
    for clause in cnf:
        if len(clause) == 1:
            cnf, literals = assignValue(cnf, clause[0], literals)
            unit_clause = True
            break
    return cnf, literals, unit_clause

def pureLiteralElimination(cnf, literals):
    pure_rule = False
    for clause in cnf:
        if pure_rule == False:
            for lit in clause:
                pure = True
                for c in cnf:
                    if -lit in c:
                        pure = False
                        break
                if pure:
                    pure_rule = True
                    cnf, literals = assignValue(cnf, lit, literals)
                    break
    return cnf, literals, pure_rule

def printSudoku(literals):
    sudoku = [[0, 0, 0, 0, 0, 0, 0, 0, 0] for i in range(9)]
    for lit in literals:
        row, col, digit = int(str(lit)[:1]) - 1, int(str(lit)[1:2]) - 1, int(str(lit)[2:3])
        sudoku[row][col] = digit
    for i in range(9): print(sudoku[i])

def createOutFile(filename, literals):
    file = open(filename, "w")
    for lit in literals: file.write(str(lit) + ' 0\n')
    file.close

def chooseLit(cnf):
    if heuristic == 1: return cnf[0][0]
    if heuristic == 2: return MOM(cnf)
    if heuristic == 3: return JW(cnf)

def DP(cnf, literals):
    cnf, literals, unit_clause = unitPropagation(cnf, literals) # Satisfy unit clauses
    while unit_clause: cnf, literals, unit_clause = unitPropagation(cnf, literals)
    cnf, literals, pure_rule = pureLiteralElimination(cnf, literals) # Remove pure literals
    while pure_rule: cnf, literals, pure_rule = unitPropagation(cnf, literals)
    if len(cnf) == 0:
        createOutFile(files[0] + ".out.txt", literals)
#        printSudoku(literals)
        return True
    if [] in cnf: return False # Empty clause
    cnf = deepcopy(cnf)
    lit = chooseLit(cnf)
    cnf1, literals1 = assignValue(cnf, lit, literals)
    if DP(cnf1, literals1): return True
    cnf2, literals2 = assignValue(cnf, -lit, literals)
    return DP(cnf2, literals2)

def MOM(cnf):
    bestValue = 0
    minClause = min(len(clause) for clause in cnf)
    maxFunction = 0
    k = 1.8
    count = dict()
    for clause in cnf:
        if len(clause) == minClause:
            for lit in clause: count[lit] = count.get(lit, 0) + 1
    for val in count.keys():
        function = (count[val] * count.get(-val, 0)) * 2**k + count[val] * count.get(-val, 0)
        if function > maxFunction:
            maxFunction = function
            lit = val
    return lit

def JW(cnf):
    count = variables
    for clause in cnf:
        for lit in clause: count[abs(lit)] = count.get(abs(lit), 0) + 2**-len(clause)
    lit = max(variables, key = count.get)
    return lit

def main():
    start_time = time.time()
    sat = DP(cnf, list())
    print("--- %s seconds ---" % (time.time() - start_time))
    if sat == True: print("Satisfiable")
    elif sat == False:
        createOutFile(files[0] + ".out.txt", list())
        print("Unsatisfiable")

def parseArguments():
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser()
    parser.add_argument("-S", type = int)
    parser.add_argument("files", nargs = '+')
    args = parser.parse_args()
    return args.S, args.files

variables = dict()
heuristic, files = parseArguments()
execute, cnf = parse(files)
if execute:
    if heuristic == 3:
        for clause in cnf:
            for lit in clause: variables[abs(lit)] = variables.get(abs(lit), 0) + 2**-len(clause)
    main()
