import sys
import os
import errno
import subprocess
import argparse
from math import ceil
from subprocess import check_output
from Lexer import runlexer
from CompleteLexer import runcompletelexer, runparser

TESTER_DIR = "tests/"

stage = None

abs_total_1 = 107
abs_total_31 = 107
abs_total_32 = 8
max_grade_31 = 0.7
max_grade_32 = 0.3

def run_test(test_set, test):
    if stage == 1:
        lexer = TESTER_DIR + "T{}/".format(stage) + test_set + '/' + test_set + ".lex"
        finput = TESTER_DIR + "T{}/".format(stage) + test_set + "/input/" + test_set + '.' + test + ".in"
        foutput = TESTER_DIR + "T{}/".format(stage) + test_set + "/out/" + test_set + '.' + test + ".out"
        freference = TESTER_DIR + "T{}/".format(stage) + test_set + "/ref/" + test_set + '.' + test + ".ref"
    elif test_set != "T3.prog":
        lexer = TESTER_DIR + "T{}/".format(stage) + "regex/" + test_set + '/' + test_set + ".lex"
        finput = TESTER_DIR + "T{}/".format(stage) + "regex/" + test_set + "/input/" + test_set + '.' + test + ".in"
        foutput = TESTER_DIR + "T{}/".format(stage) + "regex/" + test_set + "/out/" + test_set + '.' + test + ".out"
        freference = TESTER_DIR + "T{}/".format(stage) + "regex/" + test_set + "/ref/" + test_set + '.' + test + ".ref"
    else:
        finput = TESTER_DIR + "T{}/".format(stage) + "prog/input/" + test + ".in"
        foutput = TESTER_DIR + "T{}/".format(stage) + "prog/out/" + test + ".out"
        freference = TESTER_DIR + "T{}/".format(stage) + "prog/ref/" + test + ".ref"

    if os.path.isfile(foutput):
        os.remove(foutput)

    if not os.path.exists(os.path.dirname(foutput)):
        try:
            os.makedirs(os.path.dirname(foutput))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    if stage == 1:
        runlexer(lexer, finput, foutput)
    elif test_set == "T3.prog":
        runparser(finput, foutput)
    else:
        runcompletelexer(lexer, finput, foutput)
    val = subprocess.call(["diff","--ignore-all-space", foutput, freference])

    if test_set == "T3.prog":
        no_dots = 20
    else:
        no_dots = 20
        set_no = int(test_set.split('.')[1])
        if set_no > 9:
            no_dots -= 1
        if int(test) > 9:
            no_dots -= 1
    dots = '.' * no_dots

    if val == 1:
        points = 0
        print(test_set + "." + test + dots + "failed [0p]")
    elif val == 0:
        if test_set != "T3.prog":
            if set_no == 1:
                points = 2.5
            else:
                points = 1
        else:
            points = 1
        print(test_set + "." + test + dots + "passed [{}p]".format(points))

    return points

def run_test_set(test_set):
    if stage == 1:
        input_dir = TESTER_DIR + "T{}/".format(stage) + test_set + "/input/"
    elif substage == "regex" or substage == "":
        input_dir = TESTER_DIR + "T{}/".format(stage) + "regex/" + test_set + "/input/"

    inputs = list(map(lambda f : int(f.split('.')[-2]), os.listdir(input_dir)))
    inputs = filter(lambda i : i <= 10, inputs)
    inputs = list(set(inputs))
    inputs.sort()
    inputs = map(lambda i : str(i), inputs)

    print("Testset", test_set)
    set_total = 0
    for i in inputs:
        set_total += run_test(test_set, i)
    set_total = ceil(set_total)
    print("Set total" + '.' * 17 + "[{}p]".format(set_total))

    return set_total

def run_all():
    print("Stage {}\n".format(stage))
    if stage == 1:
        test_sets = os.listdir(TESTER_DIR + "T1")
        test_sets.sort(key=lambda t : int(t[3:]))
        total = 0
        for test_set in test_sets:
            total += run_test_set(test_set)
            if test_set != test_sets[-1]:
                print()
        print("\nTotal" + '.' * 21 + "[{}p]".format(total))
        print("Final grade" + '.' * 15 + "{}p".format(total / abs_total_1))
    else:
        if substage == "":
            print("3.1. Complete lexer\n")
            regex_test_sets = os.listdir(TESTER_DIR + "T3/regex")
            regex_test_sets = list(filter(lambda t : not('-' in t), regex_test_sets))
            regex_test_sets.sort(key=lambda t : int(t[3:]))
            total_31 = 0
            for test_set in regex_test_sets:
                total_31 += run_test_set(test_set)
                if test_set != regex_test_sets[-1]:
                    print()
            grade_31 = (total_31 / abs_total_31) * max_grade_31
            print("\nTotal for 3.1" + '.' * 13 + "[{}p]".format(total_31))
            print("Grade for 3.1" + '.' * 13 + "{:.2f}p".format(grade_31))

            print("\n3.2. Imperative programs parsing\n")
            prog_tests = os.listdir(TESTER_DIR + "T3/prog/input")
            prog_tests.sort()
            total_32 = 0
            for test in prog_tests:
                total_32 += run_test("T3.prog", test[0])
            grade_32 = (total_32 / abs_total_32) * max_grade_32
            print("\nTotal for 3.2" + '.' * 13 + "[{}p]".format(total_32))
            print("Grade for 3.2" + '.' * 13 + "{:.2f}p".format(grade_32))

            print("\nTotal" + '.' * 20 + "[{}p]".format(total_31 + total_32))
            print("Final grade" + '.' * 14 + "{:.2f}p".format(grade_31 + grade_32))

        elif substage == 'regex':
            print("3.1. Complete lexer\n")
            regex_test_sets = os.listdir(TESTER_DIR + "T3/regex")
            regex_test_sets = list(filter(lambda t : not('-' in t), regex_test_sets))
            regex_test_sets.sort(key=lambda t : int(t[3:]))
            total = 0
            for test_set in regex_test_sets:
                total += run_test_set(test_set)
                if test_set != regex_test_sets[-1]:
                    print()
            print("\nTotal for 3.1" + '.' * 13 + "[{}p]".format(total))
            print("Grade for 3.1" + '.' * 13 + "{:.2f}p".format((total / abs_total_31) * max_grade_31))

        else: # substage == "prog"
            print("3.2. Imperative programs parsing\n")
            prog_tests = os.listdir(TESTER_DIR + "T3/prog/input")
            prog_tests.sort()
            total = 0
            for test in prog_tests:
                total += run_test("T3.prog", test[0])
            print("\nTotal for 3.2" + '.' * 13 + "[{}p]".format(total))
            print("Grade for 3.2" + '.' * 13 + "{:.2f}p".format((total / abs_total_32) * max_grade_32))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='FLA project checker')
    parser.add_argument('--stage', default='1',
                        help='Project stage; for stage 3, use either 3, 3-regex or 3-prog')
    parser.add_argument('--set',
                        help='Test set')
    parser.add_argument('--test',
                        help='Test index')
    args = parser.parse_args()

    if args.stage == '2':
        sys.exit("Stage 2 has its own separate checker")

    if not args.stage in ['1', '3', '3-regex', '3-prog']:
        sys.exit("Project stage argument can either be 1, 3, 3-regex or 3-prog")

    if args.stage == '3-prog' and args.set:
        sys.exit("3-prog substage has only tests, no test sets")

    if args.stage != '3-prog' and args.test and not args.set:
        sys.exit("Test set must be specified if you want to run a specific test")

    # if args.stage == '3-prog' or args.stage == '3':
    # if args.stage == '3':
    #     sys.exit("Update for stage 3 program parsing coming soon")

    stage = int(args.stage[0])
    substage = args.stage[2:]

    if args.set:
        if args.test:
            if not args.test.isnumeric():
                sys.exit("Test index must be a number")
            run_test(args.set, args.test)
        else:
            run_test_set(args.set)
    elif args.test:
        run_test("T3.prog", args.test)
    else:
        run_all()

