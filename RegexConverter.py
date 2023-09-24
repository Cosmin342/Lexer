class Automaton:
    #Constructor pentru un automat ce va primi codificarea lui (fara token) si
    #numarul de linii
    def __init__(self, code, nr_lines):
        ind = 0
        #Se initializeaza componentele
        self.alphabet = set()
        self.finals = []
        self.delta = {}
        self.states = set()
        for line in code.split('\n'):
            #Pe prima linie se vor regasii simbolurile din alfabet
            if ind == 0:
                if line == "'\\n'":
                    self.alphabet.add("\n")
                    ind += 1
                    continue
                if line == "'\\t'":
                    self.alphabet.add("\t")
                    ind += 1
                    continue
                for carac in line:
                    self.alphabet.add(carac)
                ind += 1
                continue
            #Pe a doua linie se gaseste starea initiala
            if ind == 1:
                self.ini = int(line)
                ind += 1
                continue
            #Pe urmatoarele linii (cu exceptia ultimei) se vor regasii tranzitii
            #Astfel, se face split dupa virgula
            components = [x for x in line.split(',')]
            #Pe ultima linie se regasesc starile finale
            if ind == nr_lines - 1:
                components = [x for x in line.split(' ')]
                for i in components:
                    if i == "":
                        continue
                    self.finals.append(int(i))
                continue
            #Se adauga starile din tranzitii
            self.states.add(int(components[0]))
            self.states.add(int(components[2]))
            #Daca se detecteaza \\n, se va adauga o tranzitie pe \n
            if components[1] == "'\\n'":
                self.delta[(int(components[0]), "\n")] = int(components[2])
                ind += 1
                continue
            if components[1] == "'\\t'":
                self.delta[(int(components[0]), "\t")] = int(components[2])
                ind += 1
                continue
            self.delta[(int(components[0]), components[1][1])] = int(components[2])
            ind += 1
    
    #Metoda ce executa urmatorul pas pentru o configuratie data
    def next(self, config):
        if config[1] == "" and config[0] in self.finals:
            return "Configuratie finala"
        #Se intoarce un mesaj de eroare daca actualul cuvant este consumat
        #si nu s-a ajuns intr-o stare finala
        else:
            if config[1] == "":
                return "Eroare"
        state = (config[0], config[1][0])
        #Daca tranzitia de efectuat nu se regaseste in delta, dfa-ul nu trece
        #mai departe
        if state not in self.delta:
            return "Pasul urmator nu se poate realiza"
        return(self.delta[state], config[1][1:])

    #Metoda ce verifica daca un cuvant este acceptat sau respins
    def accepted(self, word):
        config = (self.ini, word)
        #Se vor efectua pasi pana automatul intoarce eroare, sau ajunge
        #la o configuratie finala
        while 1:
            config = self.next(config)
            if config == "Configuratie finala":
                return "Acceptat"
            if config == "Eroare":
                return "Respins"

    #Metoda ce intoarce sink state-urile
    def findSinkState(self):
        #Se inverseaza delta (se vor pastra tranzitiile in set pentru a nu se
        #pierde anumite tranzitii)
        revDelta = set((self.delta[(key, lit)], lit, key) for (key, lit) in self.delta)
        visited = set()
        q = []
        #Se vor parcurge starile, pornind din cele finale si utilizand
        #tranzitiile din revDelta
        for state in self.finals:
            visited.add(state)
            q.append(state)
        while q:
            el = q.pop()
            for tran in revDelta:
                if tran[0] == el and tran[2] not in visited:
                    visited.add(tran[2])
                    q.append(tran[2])
        #print(self.states)
        #print(visited)
        return self.states - visited
    
    #Metoda ce intoarce indexul pana la cel mai lung prefix acceptat
    def longest_accepted_prefix(self, word):
        ind = 0
        long_ind = -1
        config = (self.ini, word)
        sink_states = self.findSinkState()
        while 1:
            ind += 1
            #Se va realiza cate un pas si se va analiza rezultatul
            config = self.next(config)
            if config[0] in self.finals:
                long_ind = ind
            if config == "Configuratie finala" or config[0] in sink_states or \
                config == "Eroare" or config == "Pasul urmator nu se poate realiza":
                break
        #Daca long_ind e -1, inseamna ca automatul nu a acceptat vreun prefix
        #si se va intoarce o pereche ce contine, pe langa long_ind, prefixul
        #pana la care automatul s-a blocat
        if long_ind == -1:
            return (long_ind, ind)
        return long_ind

    #Metoda pentru conversia unui automat la nfa
    def transform_star(self, ind):
        #Se retin vechea stare initiala si cea finala
        old_ini = self.ini
        old_finals = self.finals[0]

        #Se creeaza doua noi stari date de indicele ind
        self.ini = ind
        self.finals = [ind + 1]

        #Se adauga starile nou create in multimea starilor si tranzitiile pe
        #epsilon corespunzatoare
        self.states.add(ind)
        self.states.add(ind + 1)
        self.delta[(old_finals, "eps")] = [old_ini, ind + 1]
        self.delta[(ind, "eps")] = [old_ini, ind + 1]

    #Analog se realizeaza si celelalte transformari, tranzitiile adaugandu-se
    #in functie de algoritmul lui Thomson
    def transform_plus(self, ind):
        old_ini = self.ini
        old_finals = self.finals[0]
        self.ini = ind
        self.finals = [ind + 1]
        self.states.add(ind)
        self.states.add(ind + 1)
        self.delta[(old_finals, "eps")] = [old_ini, ind + 1]
        self.delta[(ind, "eps")] = old_ini
    
    def transform_union(self, ind, nfa):
        old_ini = self.ini
        old_finals = self.finals[0]
        self.delta.update(nfa.delta)
        self.states = set.union(self.states, nfa.states)
        self.states.add(ind)
        self.states.add(ind + 1)
        self.ini = ind
        self.finals = [ind + 1]
        self.delta[(ind, "eps")] = [old_ini, nfa.ini]
        self.delta[(old_finals, "eps")] = ind + 1
        self.delta[(nfa.finals[0], "eps")] = ind + 1
        self.alphabet = set.union(self.alphabet, nfa.alphabet)
    
    def transform_concat(self, nfa):
        old_finals = self.finals[0]
        self.delta.update(nfa.delta)
        self.states = set.union(self.states, nfa.states)
        self.finals = [nfa.finals[0]]
        self.delta[(old_finals, "eps")] = nfa.ini
        self.alphabet = set.union(self.alphabet, nfa.alphabet)

    #Metoda ce determina inchiderile epsilon pentru fiecare tranzitie
    def get_eps_enclosure(self):
        enclosures = []
        for state in self.states:
            enclosure = [state]
            q = [state]
            checked = [state]
            #Vom verifica daca exista tranzitii pe epsilon atat din starea
            #curenta, cat si din alte stari accesibile, utilizand o coada
            while len(q) > 0:
                elem_q = q.pop(0)
                if (elem_q, 'eps') in self.delta:
                    if isinstance(self.delta[(elem_q, 'eps')], list):
                        for elem in self.delta[(elem_q, 'eps')]:
                            enclosure.append(elem)
                            #Daca o stare a fost deja adaugata in inchidere,
                            #va fi ignorata
                            if elem not in checked:
                                q.append(elem)
                                checked.append(elem)
                    else:
                        enclosure.append(self.delta[(elem_q, 'eps')])
                        if self.delta[(elem_q, 'eps')] not in checked:
                            q.append(self.delta[(elem_q, 'eps')])
                            checked.append(self.delta[(elem_q, 'eps')])
            enclosures.append(enclosure)
        return enclosures

    #Metoda pentru convertirea la dfa
    def convert_to_dfa(self):
        #Se obtin inchiderile epsilon
        enclosures = self.get_eps_enclosure()
        #States_map va mapa un tuplu din transformarea nfa-dfa la un numar
        states_map = {}
        new_delta = {}
        initial_state = enclosures[self.ini]
        states_map[tuple(initial_state)] = 0
        state_new = [tuple(initial_state)]
        next_states_l = [initial_state]
        new_finals = set()
        #ind e folosit pentru o stare noua din dfa
        ind = 1
        #Daca starea initiala a dfa-ului contine o stare finala a nfa-ului,
        #atunci va fi si stare finala
        for st in initial_state:
            if st in self.finals:
                new_finals.add(0)
        while len(next_states_l) > 0:
            intermed_state = next_states_l.pop()
            #Pentru actuala stare a dfa-ului se vor lua starile nfa-ului din
            #aceasta si se vor verifica tranzitiile pe fiecare simbol din
            #alfabet si se vor adauga inchiderile epsilon din care fac parte
            #starile in care se va ajunge pe un anumit simbol
            for lit in self.alphabet:
                state = set()
                for i in intermed_state:
                    if (i, lit) in self.delta:
                        state.update(enclosures[self.delta[(i, lit)]])
                if state != set():
                    #Se verifica daca actuala stare a mai fost vizitata
                    if state in state_new:
                        #Se adauga tranzitia in noul delta si se verifica daca si aceasta
                        #stare este finala
                        new_delta[(states_map[tuple(intermed_state)], lit)] = states_map[tuple(state)]
                        for st in state:
                            if st in self.finals:
                                new_finals.add(states_map[tuple(state)])
                        continue
                    #Daca nu a mai fost vizitata, se adauga in coada pentru vizitare
                    next_states_l.append(state)
                    state_new.append(state)
                    states_map[tuple(state)] = ind
                    new_delta[(states_map[tuple(intermed_state)], lit)] = ind
                    for st in state:
                        if st in self.finals:
                            new_finals.add(ind)
                    ind += 1
        #Se completeaza delta prin adaugarea de tranzitii catre sink state
        for i in range(0, ind):
            for lit in self.alphabet:
                if (i, lit) not in new_delta:
                    new_delta[(i, lit)] = ind
        for lit in self.alphabet:
            new_delta[(ind, lit)] = ind
        new_st = set()
        for st in state_new:
            new_st.add(states_map[tuple(st)])
        new_st.add(ind)
        #Se inlocuiesc datele actualului automat
        self.delta = new_delta
        self.finals = list(new_finals)
        self.states = new_st
        self.ini = states_map[tuple(initial_state)]
        return self

class Lexer:
    def __init__(self, lex):
        self.lex = lex

    #Metoda ce va intoarce o lista de lexeme
    def lexical_analysis(self, word):
        l_words = []
        len_lex = len(self.lex)
        init_word = word
        max_ind = -1
        length_accepted = 0
        while 1:
            #Daca s-a terminat cuvantul, se va termina si analiza
            if word == "":
                break
            long_ind = -1
            part = ""
            autom_nr = 0
            max_ind = -1
            #Fiecare automat va primi cuvantul sau partea din cuvant neanalizata
            for autom in self.lex:
                ind = 0
                ind = autom[0].longest_accepted_prefix(word)
                #Daca in loc de indice s-a primit un tuplu, inseamna ca
                #automatul nu a reusit sa accepte vreo parte din cuvant
                if isinstance(ind, tuple):
                    x, y = ind
                    #Se va actualiza max_ind si se va incrementa numarul de
                    #automate ce au respins
                    max_ind = max(y, max_ind)
                    autom_nr += 1
                    continue
                #Daca insa
                if ind > long_ind:
                    long_ind = ind
                    part = autom[1]
            #Daca toate automatele nu pot accepta o portiune din cuvant,
            #analiza se termina si se returneaza un mesaj corespunzator
            if autom_nr == len_lex:
                if length_accepted + max_ind - 1 == len(init_word):
                    return "No viable alternative at character EOF, line " + str(init_word.count('\n'))
                return "No viable alternative at character " + str(length_accepted + max_ind - 1) \
                    + ", line " + str(init_word[0:length_accepted + max_ind - 1].count('\n'))
            #Altfel, se va adauga lexemul obtinut la lista de lexeme
            l_words.append((part, word[:long_ind]))
            word = word[long_ind:]
            length_accepted += long_ind
        return l_words

class Expr:
    def __init__(self, exp):
        stack = []
        #print(" " + exp[0])
        l_exp = exp.split(" ")
        #print(l_exp)
        #print(len(l_exp))
        new_l = []
        for i in range(len(l_exp)):
            if i + 1 <= len(l_exp) - 1:
                if l_exp[i] == "'" and l_exp[i + 1] == "'":
                    new_l.append(' ')
                elif l_exp[i] == "'":
                    continue
                else:
                    new_l.append(l_exp[i])
            else:
                if l_exp[i] == "'":
                    continue
                new_l.append(l_exp[i])
        #print(l_exp)
        #print(new_l)
        l_exp = new_l
        ind = 0
        for el in l_exp:
            if el == "CONCAT" or el == "STAR" or el == "UNION" or el == "PLUS":
                stack.append(el)
            else:
                #Se va creea un nfa daca avem un cuvant
                nfa = Word(el, ind).get_nfa()
                ind += 2
                #Se verifica daca se pot face simplificari daca se intalnesc
                #PLUS sau STAR
                if len(stack) > 1:
                    if stack[-1] == "STAR":
                        stack.pop()
                        stack.append(Star(nfa, ind).get_nfa())
                        ind += 2
                    elif stack[-1] == "PLUS":
                        stack.pop()
                        stack.append(Plus(nfa, ind).get_nfa())
                        ind += 2
                    elif stack[-1] == "CONCAT" or stack[-1] == "UNION":
                        stack.append(nfa)
                    else:
                        stack.append(nfa)
                else:
                    stack.append(nfa)
        #La final, se vor verifica daca se mai pot face simplificari pentru
        #UNION, STAR etc. utilizand o stiva intermediara
        while len(stack) > 1:
            new_stack = []
            el = stack.pop()
            while not isinstance(el, str):
                new_stack.append(el)
                el = stack.pop()
            while len(new_stack) > 0:
                if el == "UNION":
                    new_stack.append(Union(new_stack.pop(), new_stack.pop(), ind).get_nfa())
                    ind += 2
                    if len(stack) == 0:
                        break
                    el = stack.pop()
                elif el == "CONCAT":
                    new_stack.append(Concat(new_stack.pop(), new_stack.pop()).get_nfa())
                    if len(stack) == 0:
                        break
                    el = stack.pop()
                elif el == "STAR":
                    new_stack.append(Star(new_stack.pop(), ind).get_nfa())
                    ind += 2
                    if len(stack) == 0:
                        break
                    el = stack.pop()
                elif el == "PLUS":
                    new_stack.append(Plus(new_stack.pop(),ind).get_nfa())
                    ind += 2
                    if len(stack) == 0:
                        break
                    el = stack.pop()
                elif isinstance(el, Automaton):
                    stack.append(el)
                    while len(new_stack) > 0:
                        stack.append(new_stack.pop())
            while len(new_stack) > 0:
                stack.append(new_stack.pop())
        #Automatul rezultat va fi in varful stivei
        self.exp = stack[-1]

    def get_nfa(self):
        return self.exp

#Clasele urmatoare vor contine un nfa corespunzator creeand unul sau convertind
#unul sau mai multe plecand de la altele primite ca input
class Word(Expr):
    def __init__(self, word, ind):
        code_nfa = ""
        code_nfa += word + "\n" + str(ind) + "\n"
        if word == "'\\n'" or word == "'\\t'":
            code_nfa += str(ind) + "," + word + "," + str(ind + 1) + "\n"
        else:
            code_nfa += str(ind) + ",'" + word + "'," + str(ind + 1) + "\n"
        code_nfa += str(ind + 1)
        #print(code_nfa)
        nfa = Automaton(code_nfa, code_nfa.count('\n') + 1)
        self.word = nfa

    def get_nfa(self):
        return self.word
        

class Star(Expr):
    def __init__(self, nfa, ind):
        nfa.transform_star(ind)
        self.exp = nfa

    def get_nfa(self):
        return self.exp


class Plus(Expr):
    def __init__(self, nfa, ind):
        nfa.transform_plus(ind)
        self.exp = nfa

    def get_nfa(self):
        return self.exp

class Concat(Expr):
    def __init__(self, nfa1, nfa2):
        nfa1.transform_concat(nfa2)
        self.exp = nfa1

    def get_nfa(self):
        return self.exp


class Union(Expr):
    def __init__(self, nfa1, nfa2, ind):
        nfa1.transform_union(ind, nfa2)
        self.exp = nfa1

    def get_nfa(self):
        return self.exp

import sys

def main():
    ind = 0
    inp_reg = None
    out_file = None
    #Se extrag din linia de comanda numele fisierului de intrare si al celui
    #de iesire
    for files in sys.argv:
        if ind == 0:
            ind += 1
            continue
        if ind == 1:
            inp_reg = open(files, "r").read()
        if ind == 2:
            out_file = open(files, "w")
        ind += 1
    #Se creeaza nfa-ul pornind de la forma prenex din fisier
    nfa = Expr(inp_reg).get_nfa()
    #Se converteste la dfa
    nfa.convert_to_dfa()
    for lit in nfa.alphabet:
        out_file.write(lit)
    #Se va realiza scrierea in fisier conform cerintei
    out_file.write("\n")
    out_file.write(str(len(nfa.states)) + "\n")
    out_file.write(str(nfa.ini) + "\n")
    ind = 0
    for fin in nfa.finals:
        if ind == len(nfa.finals) - 1:
            out_file.write(str(fin))
            break
        out_file.write(str(fin) + " ")
        ind += 1
    out_file.write("\n")
    ind = 0
    for config in nfa.delta:
        if ind == len(nfa.delta) - 1:
            out_file.write(str(config[0]) + ",'" + config[1] + "'," + str(nfa.delta[config]))
            break
        out_file.write(str(config[0]) + ",'" + config[1] + "'," + str(nfa.delta[config]) + "\n")
        ind += 1

if __name__ == "__main__":
    main()