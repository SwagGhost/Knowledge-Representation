from sys import stdin
from copy import copy, deepcopy
import time
import argparse
import numpy


def parseFileInput(in_file, cnf):  # Parse
    cnf.append(list())
    for line in in_file:
        tokens = line.split()
        if len(tokens) > 0 and tokens[0] not in ("p", "c"):
            for token in tokens:
                lit = int(token)
                if lit == 0:
                    cnf.append(list())
                else:
                    cnf[-1].append(lit)
    cnf.pop()
    return cnf


def transformSudoku(in_file):
    file = open("sudoku.txt", 'w')
    for line in in_file:
        row = 1
        col = 1
        if line != '.': file.write(str(row) + str(col) + str(line) + ' 0\n')
        col += 1
        if col == 10:
            row += 1
            col = 1
            if row == 10: break
    file.close()


def parse(files):
    file1 = open(files[0], "r")
    if len(files) == 1:
        line = file1.readline()
        if "p" in line:
            cnf = parseFileInput(file1, list())
            file1.close()
            return True, cnf
        transformSudoku(file1)
        file1.close()
        return False, list()
    file2 = open(files[1], "r")
    cnf = parseFileInput(file1, parseFileInput(file2, list()))
    file1.close()
    file2.close()
    return True, cnf


def assignValue(cnf, lit):
    for clause in copy(cnf):
        if lit in clause:
            cnf.remove(clause)
            variables[abs(lit)] = variables.get(abs(lit), 0) + 2 ** -len(clause)
        if -lit in clause:
            clause.remove(-lit)
            variables[abs(lit)] = variables.get(abs(lit), 0) + 2 ** -len(clause)
    if lit > 0: solution.append(lit)
    return cnf


def unitPropagation(cnf):
    unit_clause = False
    for clause in cnf:
        if len(clause) == 1:
            cnf = assignValue(cnf, clause[0])
            unit_clause = True
            break
    return cnf, unit_clause


def pureLiteralElimination(cnf):
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
                    cnf = assignValue(cnf, lit)
                    break
    return cnf, pure_rule


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
    globals()['splits'] += 1
    if heuristic == 1: return cnf[0][0]
    if heuristic == 2: return MOM(cnf)
    if heuristic == 3: return JW(cnf, solution)


def DP(cnf):
    cnf, unit_clause = unitPropagation(cnf)  # Satisfy unit clauses
    while unit_clause: cnf, unit_clause = unitPropagation(cnf)
    cnf, pure_rule = pureLiteralElimination(cnf)  # Remove pure literals
    while pure_rule: cnf, pure_rule = unitPropagation(cnf)
    if len(cnf) == 0:
        return True
    if [] in cnf: return False  # Empty clause
    cnf = deepcopy(cnf)
    lit = chooseLit(cnf)
    cnf1 = assignValue(cnf, lit)
    if DP(cnf1): return True
    cnf2 = assignValue(cnf, -lit)
    return DP(cnf2)


def MOM(cnf):
    bestValue = 0
    minClause = min(len(clause) for clause in cnf)
    maxFunction = 0
    # k = 1.8
    count = dict()
    for clause in cnf:
        if len(clause) == minClause:
            for lit in clause: count[lit] = count.get(lit, 0) + 1
    for val in count.keys():
        function = (count[val] * count.get(-val, 0)) * 2 ** k + count[val] * count.get(-val, 0)
        if function > maxFunction:
            maxFunction = function
            lit = val
    return lit


def JW(cnf, literals):
    count = variables
    for clause in cnf:
        for lit in clause: count[abs(lit)] = count.get(abs(lit), 0) + 2 ** -len(clause)
    lit = max(variables, key=count.get)
    return lit


def main():
    start_time = time.time()
    sat = DP(cnf)
    temp = time.time() - start_time
    # print("--- %s seconds ---" % (time.time() - start_time))
    ris.write(str(temp) + ' seconds ' + str(splits) + ' splits ' + str(k) + ' k value ' + '\n')
    # printSudoku(solution)
    # if sat == True: print("Satisfiable")
    # elif sat == False: print("Unsatisfiable")


def parseArguments():
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser()
    parser.add_argument("-S", type=int)
    parser.add_argument("files", nargs='+')
    args = parser.parse_args()
    return args.S, args.files


solution, variables = list(), dict()
heuristic = 2
ris = open("ResultsHard.txt", 'w')
k = 0
for i in range(1, 41):
    globals()['splits'] = 0
    print(i)
    files = ['sudoku-rules.txt', 'Hard%s.txt' % (i)]
    execute, cnf = parse(files)
    if execute:
        for i in numpy.arange(0, 4, 0.5):
            k = i
            main()
ris.close()
