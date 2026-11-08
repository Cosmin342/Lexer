#!/usr/bin/env python3
import copy
import os
import subprocess
import sys
from subprocess import PIPE
import traceback

sys.path.append("checker")

POINTS_PER_TEST_DFA = 5
SRCFILE = "RegexConverter.py"
EXEC = "Main"
TESTDIR = "tests/T2"
TEST_TIMEOUT = 8  # seconds


class DFA(object):
    def __init__(self, alphabet, states, start_state, final_states, delta):
        assert start_state in states, "Start state not in states"
        assert final_states.issubset(states), \
            "Final states ({}) not subset of states ({})".format(final_states,
                                                                 states)
        for symbol in "()*|":
            assert symbol not in alphabet

        self.alphabet = alphabet
        self.states = states
        self.start_state = start_state
        self.final_states = final_states
        self.delta = delta
        self.sink_state = None

    def get_sink_state(self):
        if self.sink_state is not None:
            return self.sink_state

        for state in self.states:
            if state in self.final_states:
                continue

            is_sink = True
            for symbol in self.alphabet:
                if self.delta[(state, symbol)] != state:
                    is_sink = False

            if is_sink:
                self.sink_state = state
                return self.sink_state

        return None

    def accept(self, string):
        """Check if a string is in the DFA's language"""
        current_state = self.start_state
        sink_state = self.get_sink_state()
        for symbol in string:
            current_state = self.delta.get((current_state, symbol), sink_state)
            if current_state == sink_state:  # early bailout
                return False

        return current_state in self.final_states


def parse_dfa(text):
    """
    text must have the following format:

    <number of states>
    <final state 1> <final state 2> ... <final state n>
    <current state> <simbol> <next state>
    <current state> <simbol> <next state>
    ...
    <current state> <simbol> <next state>

    """

    def build_delta(transitions):
        delta = {}
        for transition in transitions:
            elems = transition.split(",")
            elems[1] = elems[1][1]
            delta[(int(elems[0]), elems[1])] = int(elems[2])

        return delta

    def normalize(states, final_states, delta):
        translate = {name: index for index, name in enumerate(states)}
        new_delta = {(translate[c], s): translate[n] for (c, s), n in
                     delta.items()}
        new_finals = {translate[s] for s in final_states}
        new_states = {translate[s] for s in states}

        return new_states, new_finals, new_delta

    try:
        lines = text.splitlines()
        alphabet = lines[0]
        states = set(int(s) for s in range(int(lines[1])))
        initial_state = int(lines[2])
        final_states = set(int(s) for s in lines[3].split())
        delta = build_delta(lines[4:])
        states, final_states, delta = normalize(states, final_states, delta)
        return DFA(alphabet, states, initial_state, final_states, delta)
    except Exception as e:
        return None

def epsilon_closure(nfa, state):
    """Get epsilon closure of a state"""

    def epsilon_closure_aux(nfa, state, closure):
        for next_state in nfa.delta.get((state, ""), set()):
            if next_state not in closure:
                closure |= {next_state}
                closure |= epsilon_closure_aux(nfa, next_state, closure)

        return closure

    return epsilon_closure_aux(nfa, state, {state})


def symmetric_difference(lhs, rhs):
    def new_state_name(ls, rs):
        return ls * len(rhs.states) + rs

    alphabet = lhs.alphabet
    states = set(range(len(lhs.states) * len(rhs.states)))

    final_states = set()
    for ls in lhs.states:
        for rs in rhs.states:
            ns = new_state_name(ls, rs)
            if (ls in lhs.final_states) and (rs not in rhs.final_states) or \
                    (ls not in lhs.final_states) and (rs in rhs.final_states):
                final_states.add(ns)

    start_state = new_state_name(lhs.start_state, rhs.start_state)

    delta = {}
    for ls in lhs.states:
        for rs in rhs.states:
            for ch in alphabet:
                ns = new_state_name(ls, rs)
                nns = new_state_name(lhs.delta[(ls, ch)], rhs.delta[(rs, ch)])
                delta[(ns, ch)] = nns

    return DFA(alphabet, states, start_state, final_states, delta)


def empty_language(a):
    visited = [False for state in a.states]

    def dfs_reach_final(state):
        visited[state] = True
        for ch in a.alphabet:
            nstate = a.delta[(state, ch)]
            if nstate in a.final_states:
                return True

            if not visited[nstate]:
                if dfs_reach_final(nstate):
                    return True

        return False

    return not dfs_reach_final(a.start_state)


def language_eq(lhs, rhs):
    da = symmetric_difference(lhs, rhs)
    return empty_language(da)


def equivalence(out_dfa, ref_dfa):
    return language_eq(out_dfa, ref_dfa)


def run_test_nfa(test, outfile, reffile, cp):
    try:
        with open(reffile, "r") as fin:
            ref_text_dfa = fin.read()
    except FileNotFoundError:
        print("No ref file for test {}".format(test), file=sys.stderr)
        return False

    try:
        with open(outfile, "r") as fin:
            out_text_dfa = fin.read()
    except FileNotFoundError:
        print("No out file for test {}".format(test), file=sys.stderr)
        print("Output of current run:", file=sys.stderr)
        print(cp.stdout.decode("utf-8"), file=sys.stderr)
        return False

    try:
        out_nfa = parse_dfa(out_text_dfa)
        ref_nfa = parse_dfa(ref_text_dfa)

        return equivalence(out_nfa, ref_nfa)
    except AssertionError as e:
        print("Assertion error:", file=sys.stderr)
        print(e, file=sys.stderr)
        return False
    except Exception as e:
        print("Exception raised while checking equivalence:", file=sys.stderr)
        traceback.print_exc(e)
        return False


def run_test_dfa(test, outfile, reffile, cp):
    try:
        with open(reffile, "r") as fin:
            ref_text_dfa = fin.read()
    except FileNotFoundError:
        print("No ref file for test {}".format(test), file=sys.stderr)
        return False

    try:
        with open(outfile, "r") as fin:
            out_text_dfa = fin.read()
    except FileNotFoundError:
        print("No out file for test {}".format(test), file=sys.stderr)
        print("Output of current run:", file=sys.stderr)
        print(cp.stdout.decode("utf-8"), file=sys.stderr)
        return False

    try:
        out_dfa = parse_dfa(out_text_dfa)
        ref_dfa = parse_dfa(ref_text_dfa)

        if out_dfa is None:
            return False

        return language_eq(out_dfa, ref_dfa)
    except AssertionError as e:
        print("Assertion error:", file=sys.stderr)
        print(e, file=sys.stderr)
        return False
    except Exception as e:
        print("Exception raised while checking equivalence:", file=sys.stderr)
        traceback.print_exc(e)
        return False


def run_test(test):
    # Ensure tests/out/ directory exists
    test_out = os.path.join(TESTDIR, "out")
    os.makedirs(test_out, exist_ok=True)

    infile = os.path.join(TESTDIR, "in", test)
    outfile = os.path.join(test_out, test[:-2] + "out")
    reffile = os.path.join(TESTDIR, "ref", test[:-2] + "ref")

    # print(infile, outfile, reffile)

    if os.path.isfile(outfile):
        os.remove(outfile)

    if lang == "haskell":
        cmd = "./{} {} {}".format(EXEC, infile, outfile)
    else:
        cmd = "python3 '{}' '{}' '{}'".format(SRCFILE, infile, outfile)
    # timeout_cmd = "timeout -k {0} {0} {1} 2>&1".format(TEST_TIMEOUT, cmd)
    cp = subprocess.run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    # if cp.returncode == 124:
    #     print("TIMEOUT on test {}".format(test), file=sys.stderr)
    #    return None

    return run_test_dfa(test, outfile, reffile, cp)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.stderr.write("Language (python3 or haskell) must be specified\n")
        sys.exit(1)

    if sys.argv[1] != "python3" and sys.argv[1] != "haskell":
        sys.stderr.write("Language must be either python3 or haskell\n")
        sys.exit(1)

    lang = sys.argv[1]

    if lang == "python3" and not (os.path.isfile(SRCFILE) and os.access(SRCFILE,os.R_OK)):
        sys.stderr.write("{} unavailable or unreadable!\n".format(SRCFILE))
        sys.exit(1)

    if lang == "haskell" and not (os.path.isfile(EXEC) and os.access(EXEC,os.X_OK)):
        sys.stderr.write("{} unavailable or unreadable!\n".format(EXEC))
        sys.exit(1)

    tests = os.listdir(os.path.join(TESTDIR, "in"))
    tests.sort(key = lambda s : int(s.split('.')[1]))
    nr_tests = len(tests)
    total = 0
    max_points = nr_tests * POINTS_PER_TEST_DFA

    print("TESTING Etapa 2 - ER -> DFA\n")
    header = " Running tests: "
    # This number is computed by summing the numbers in {} and the count of
    # characters outside of {} in...
    print("{:=^73}".format(header))
    print("{} {: <25} {: >20} {: >8} {: >8}\n".format("TEST #  ", "NAME", "",
                                                      "STATUS", "POINTS"))
    results = {
        'DFA': {}
    }
    for i, test in enumerate(tests):
        passed = run_test(test)
        results['DFA'][i] = (test, passed)

    for i in results['DFA'].keys():
        (test, passed1) = results['DFA'][i]
        crt_points = POINTS_PER_TEST_DFA if passed1 else 0
        total += crt_points
        str_status = "PASSED" if passed1 else "FAILED"
        str_points = "[{}/{}]".format(crt_points, POINTS_PER_TEST_DFA)
        # ... this print
        print("{: >6} - {: <25} {:.>20} {: >8} {: >8}".format(i + 1, test, "",
                                                              str_status,
                                                              str_points))

    print("\nTOTAL: {}/{}\n".format(total, max_points))

