import sys
from RegexConverter import Expr
from RegexConverter import Lexer
from ast_utils import InstructionList, Assign, Expres, If, While

#Functie ce va parsa toate caracterele dintr-o expresie regulata
def parse_all(word):
    stack = []
    #Cat timp expresia nu este vida, se vor parsa caractere
    while word != "":
        skip = parse_carac(word, stack)
        #Se vor ignora skip caractere parsate
        word = word[skip:]
    #Cum operatiile de CONCAT nu sunt definite de un operator specific,
    #dupa parsarea tuturor caracterelor se vor concatena formele prenex 
    #rezultate pe stiva pana cand va ramane doar o singura expresie,
    #reprezentand rezultatul
    while len(stack) > 1:
        elem2 = stack.pop()
        elem1 = stack.pop()
        stack.append("CONCAT " + elem1 + " " + elem2)
    return stack[-1]

#Functie ce parseaza unul sau mai multe caractere dintr-o expresie data
def parse_carac(word, stack):
    skip = 0
    special_carac = ["'('", "')'", "'*'", "'+'"]
    #In cazul in care primele 3 caractere din cuvant sunt acele caractere ASCII
    #care au si alte utilizari in expresii regulate, dar sunt intre ghilimele,
    #atunci vor fi puse pe stiva
    if word[0:3] in special_carac:
        stack.append(word[1:2])
        skip += 2
    #Daca actualul caracter este (, se va parsa tot ce este intre paranteze
    #utilizand o noua stiva, iar la final se va face concat intre expresiile
    #partiale de pe stiva
    elif word[0] == "(":
        new_stack = []
        ind = 0
        while 1:
            word = word[(ind + 1):]
            if word[0] == ")":
                skip += 1
                break
            ind = parse_carac(word, new_stack) - 1
            skip += ind + 1
        while len(new_stack) > 1:
            elem2 = new_stack.pop()
            elem1 = new_stack.pop()
            new_stack.append("CONCAT " + elem1 + " " + elem2)
        stack.append(new_stack.pop())
    #Daca actualul caracter este *, se va pune pe stiva STAR + actualul varf al
    #stivei
    elif word[0] == "*":
        stack.append("STAR " + stack.pop())
    #La fel si pentru +
    elif word[0] == "+":
        stack.append("PLUS " + stack.pop())
    #In cazul |, se va parsa si urmatorul argument, iar apoi se va pune pe
    #stiva UNION de cele doua argumente din varful stivei
    elif word[0] == "|":
        skip += parse_carac(word[1:], stack)
        elem2 = stack.pop()
        elem1 = stack.pop()
        stack.append("UNION " + elem1 + " " + elem2)
    #Daca se intalneste o paranteza patrata, vom avea un regex special pt
    #litere sau cifre si vom adauga pe stiva forma sa prenex
    elif word[0] == "[":
        if word[1:6] == "0-9]+":
            ind = 1
            stack.append("0")
            #La cifre, se va aduga PLUS de UNION de toate cifrele
            while ind != 10:
                stack.append("UNION " + stack.pop() + " " + str(ind))
                ind += 1
            stack.append("PLUS " + stack.pop())
            skip += 5
        elif word[1:6] == "a-z]+":
            #98 este codul ascii pt a
            ind = 98
            stack.append(chr(ind - 1))
            #Ca la cifre, se va face UNION de litera curenta si varful stivei
            #pana se ajunge la z
            while ind != 123:
                stack.append("UNION " + stack.pop() + " " + chr(ind))
                ind += 1
            stack.append("PLUS " + stack.pop())
            skip += 5
    #Daca actualul caracter este ', se vor parsa caractere pana cand se mai
    #intalneste o ghilimea, fiind un caracter ascii
    elif word[0] == "'":
        new_stack = []
        ind = 0
        while 1:
            word = word[(ind + 1):]
            if word[0] == "'":
                skip += 1
                break
            ind = parse_carac(word, new_stack) - 1
            skip += ind + 1
        #Dupa parsare, se concateneaza caracterele de pe stiva
        while len(new_stack) > 1:
            el2 = new_stack.pop()
            el1 = new_stack.pop()
            new_stack.append(el1 + el2)
        #Daca pe stiva avem spatiu, \n sau \t, acestea se vor adauga in stiva
        #principala intre ghilimele simple (datorita implementarii de la 
        #celelalte etape)
        if new_stack[-1] == " " or new_stack[-1] == "\\n" or new_stack[-1] == "\\t":
            stack.append("'" + new_stack.pop() + "'")
        else:    
            stack.append(new_stack.pop())
    #Altfel, se va pune pe stiva caracterul actual, verificandu-se daca dupa
    #el urmeaza * sau +
    else:
        if len(word) > 1:
            if word[1] == "*":
                stack.append("STAR " + word[0])
                skip += 1
            elif word[1] == "+":
                stack.append("PLUS " + word[0])
                skip += 1
            else:
                stack.append(word[0])
        else:
            stack.append(word[0])
    return skip + 1

#Functie ce verifica daca un sir poate fi convertit la int
def checkInt(nr):
    isInt = True
    try:
        int(nr)
    except ValueError:
        isInt = False
    return isInt

#Functie ce va rula lexer-ul pe un cuvant din fisierul in_data, utilizand
#specificatiile din in_lex pentru a-l separa in lexeme pe care le va scrie
#in out
def runcompletelexer(in_lex, in_data, out):
    #Se citeste specificatia si se face split dupa ; si \n pentru a obtine
    #expresiile regulate
    lexer_data = open(in_lex, "r").read().split(";\n")
    lexer_data.pop(len(lexer_data) - 1)
    dfas = []
    for regex in lexer_data:
        ind = regex.find(" ")
        #Se va imparti actualul regex in numele sau si in expresia efectiva
        comp = [regex[:ind], regex[(ind + 1):]]
        #Expresia se va converti in dfa utilizand codul de la etapele 1 si 2
        #din fisierul RegexConverter
        comp[1] = Expr(parse_all(comp[1])).get_nfa()
        comp[1].convert_to_dfa()
        dfas.append((comp[1], comp[0]))
    word = open(in_data, "r").read()
    #Se va rula lexer-ul pe cuvant, rezultand o lista de lexeme
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

#Functie ce parseaza un fisier scris in limbajul Imperative utilizand clasele
#din ast.py, runcompletelexer si specificatia din fisierul regexImperative.in
def runparser(inp, out):
    #Se imparte continutul fisierului in lexeme utilizand specificatia
    runcompletelexer("regexImperative.in", inp, "lex.out")
    data = open("lex.out", "r").read()
    #Se vor ignora lexemele ce cotin spatii
    data = data.replace("SPACE  \n", "")
    data_l = data.split("\n")
    stack = []
    #Se vor interpreta lexemele din lista pentru a fi create clase din ast
    #pentru reprezentare
    while len(data_l) > 0:
        convert_lex(data_l, stack, 0)
    file_output = open(out, "w")
    file_output.write(str(stack[-1]))

#Functie ce converteste un string intr-un obiect Expres
def convert_expres(elem, height):
    if not isinstance(elem, Expres):
        if checkInt(elem):
            elem = Expres(height + 2, 'i', elem)
        else:
            elem = Expres(height + 2, 'v', elem)
    return elem

#Functie ce va citii unul sau mai multe lexeme si le va interpreta
def convert_lex(data, stack, height):
    line = data[0]
    token = line.split()
    data.pop(0)
    #In cazul in care intalnim begin, vom avea un bloc de instructiuni care
    #se vor adauga intr-o lista care ulterior va fi folosita pentru a crea
    #un obiect InstructionList
    if token[0] == "INSTRLIST" and token[1] == "begin":
        data.pop(0)
        instr_list = []
        while 1:
            convert_lex(data, instr_list, height + 1)
            if len(instr_list) > 0:
                #Daca s-a intalnit end, se va elimina de pe stiva, impreuna cu
                #un eventual lexem pentru \n
                if instr_list[-1] == "end":
                    instr_list.pop()
                    if len(data) > 0:
                        data.pop(0)
                    break
        stack.append(InstructionList(height, instr_list))
    #Daca se intalneste if, se vor forma 3 expresii pentru clasa If: una ce
    #va contine conditia, una pentru ramura then si inca una pentru else
    elif token[0] == "IF" and token[1] == "if":
        data.pop(0)
        new_stack = []
        while 1:
            convert_lex(data, new_stack, height + 1)
            if new_stack[-1] == "then":
                new_stack.pop()
                new_stack.pop()
                data.pop(0)
                break
        #Se vor extrage pe rand, a doua parte a comparatiei, operatorul de
        #comparare, si prima parte a acesteia
        el2 = convert_expres(new_stack.pop(), height)
        comparator = new_stack.pop()
        el = convert_expres(new_stack.pop(), height)
        condition = Expres(height + 1, comparator, el, el2)
        new_stack = []
        #Se vor lua apoi cele doua blocuri then si else
        while 1:
            convert_lex(data, new_stack, height + 1)
            if len(new_stack) > 0:
                if new_stack[-1] == "else":
                    new_stack.pop()
                    data.pop(0)
                    break
        then = new_stack.pop()
        while 1:
            convert_lex(data, new_stack, height + 1)
            if len(new_stack) > 0:
                if new_stack[-1] == "fi":
                    new_stack.pop()
                    data.pop(0)
                    break
        el = new_stack.pop()
        #La final, se va crea un obiect de tip If
        stack.append(If(height, condition, then, el))
    #In cazul while-ului se procedeaza ca la If, doar ca vom avea un singur
    #bloc de instructiuni si o conditie
    elif token[0] == "WHILE" and token[1] == "while":
        data.pop(0)
        new_stack = []
        while 1:
            convert_lex(data, new_stack, height + 1)
            if new_stack[-1] == "do":
                new_stack.pop()
                new_stack.pop()
                data.pop(0)
                break
        el2 = convert_expres(new_stack.pop(), height)
        comparator = new_stack.pop()
        el = convert_expres(new_stack.pop(), height)
        condition = Expres(height + 1, comparator, el, el2)
        new_stack = []
        while 1:
            convert_lex(data, new_stack, height + 1)
            if len(new_stack) > 0:
                if new_stack[-1] == "od":
                    new_stack.pop()
                    data.pop(0)
                    break
        then = new_stack.pop()
        stack.append(While(height, condition, then))
    #In cazul assign, se va lua prima parte de pe stiva, iar cea de-a doua
    #se va forma in new_stack prin conversia lexemelor pana la intalnirea \n
    elif token[0] == "ASSIGN":
        el = convert_expres(stack.pop(), height)
        new_stack = []
        while 1:
            convert_lex(data, new_stack, height + 1)
            if new_stack[-1] == "\\n":
                new_stack.pop()
                break
        el2 = convert_expres(new_stack.pop(), height)
        stack.append(Assign(height, el, el2))
    #Cand intalnim un operator, vom crea o noua expresie utilizand cele doua
    #componente din stanga si din dreapta operatorului care se regasesc pe stiva
    elif token[0] == "OP":
        el = convert_expres(stack.pop(), height)
        new_stack = []
        convert_lex(data, new_stack, height + 1)
        el2 = convert_expres(new_stack.pop(), height)
        stack.append(Expres(height, token[1], el, el2))
    #Altfel, daca lexemul curent nu este de tip SPACE, se va adauga pe stiva
    elif token[0] != "SPACE":
        stack.append(token[1])