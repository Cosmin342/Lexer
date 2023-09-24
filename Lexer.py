
class Dfa:
    #Constructor pentru dfa ce va primi codificarea lui (fara token) si numarul
    #de linii
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
                if line == "\\n":
                    self.alphabet.add("\n")
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

#Functie care primeste un fisier cu datele lexer-ului, cuvantul de analizat
#si fisierul unde se vor scrie lexemele obtinute
def runlexer(in_lex, in_data, out):
    dfas = []

    lexer_dfas_data = open(in_lex, "r").read().splitlines()

    dfa_code = ""
    lines_nr = 0
    ind = 0
    token_name = ""
    
    #Se va parcurge fisierul cu datele lexer-ului linie cu linie
    for elem in lexer_dfas_data:
        ind += 1
        #Daca se intalneste o linie goala, s-a terminat un dfa si acesta se
        #adauga in lista
        if elem == "":
            #Se elimina un \n de la final
            dfa_code = dfa_code[:-1]
            automata = Dfa(dfa_code, lines_nr)
            dfas.append((automata, token_name))

            dfa_code = ""
            ind = 0
            lines_nr = 0
            continue
        #Pe a doua linie a unui dfa se va afla numele token-ului acceptat de
        #acesta
        if ind == 2:
            token_name = elem
            continue
        lines_nr += 1
        dfa_code += elem + "\n"
    #Se adauga si ultimul automat
    dfa_code = dfa_code[:-1]
    automata = Dfa(dfa_code, lines_nr)
    dfas.append((automata, token_name))

    #Se citeste cuvantul de analizat si se va analiza utilizand automatele
    word = open(in_data, "r").read()
    lexemes = Lexer(dfas).lexical_analysis(word)

    file_output = open(out, "w")

    #Daca se primeste un string, se va scrie acesta in fisier
    if isinstance(lexemes, str):
        file_output.write(lexemes)
        return
    lexemes_nr = len(lexemes)
    ind = 0
    #Altfel, se vor scrie lexemele obtinute in forma ceruta
    for lexem in lexemes:
        x, y = lexem
        if y == "\n":
            file_output.write(x + " \\n")
        else:    
            file_output.write(x + " " + y)
        if (ind != lexemes_nr - 1):
            file_output.write("\n")
        ind += 1