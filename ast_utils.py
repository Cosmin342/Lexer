TAB = '  '  # two whitespaces


class Node:
    def __init__(self, *args):
        self.height = int(args[0])  # the level of indentation required for current Node

    def __str__(self):
        return 'prog'

    @staticmethod
    def one_tab(line):
        """Formats the line of an argument from an expression."""
        return TAB + line + '\n'

    def final_print_str(self, print_str):
        """Adds height number of tabs at the beginning of every line that makes up the current Node."""
        return (self.height * TAB).join(print_str)


class InstructionList(Node):
    """begin <instruction_list> end"""

    def __init__(self, *args):  # args = height, [Nodes in instruction_list]
        super().__init__(args[0])
        self.list = args[1]

    def __str__(self):
        print_str = ['[\n']
        for expr in self.list:
            print_str.append(self.one_tab(expr.__str__()))
        print_str.append(']')

        return self.final_print_str(print_str)


class Expres(Node):
    """<expr> + <expr> | <expr> - <expr> | <expr> * <expr> | <expr> > <expr> | <expr> == <expr> | <variable> | <integer>"""

    def __init__(self, *args):  # args = height, '+' | '-' | '*' | '>' | '==' | 'v' | 'i', left_side, *right_side
        super().__init__(args[0])
        self.type = args[1]
        self.left = args[2]
        if len(args) > 3:
            self.right = args[3]
        else:
            # variable and integer have no right_side
            self.right = None

    def __str__(self):
        name = 'expr'
        if self.type == 'v':
            name = 'variable'
        elif self.type == 'i':
            name = 'integer'
        elif self.type == '+':
            name = 'plus'
        elif self.type == '-':
            name = 'minus'
        elif self.type == '*':
            name = 'multiply'
        elif self.type == '>':
            name = 'greaterthan'
        elif self.type == '==':
            name = 'equals'

        print_str = [name + ' [\n', self.one_tab(str(self.left))]
        if self.right:
            print_str.append(self.one_tab(str(self.right)))
        print_str.append(']')

        return self.final_print_str(print_str)


class While(Node):
    """while (<expr>) do <prog> od"""

    def __init__(self, *args):  # args = height, Node_expr, Node_prog
        super().__init__(args[0])
        self.expr = args[1]
        self.prog = args[2]

    def __str__(self):
        print_str = ['while [\n',
                     self.one_tab(self.expr.__str__()),
                     self.one_tab('do ' + self.prog.__str__()),
                     ']']
        return self.final_print_str(print_str)


class If(Node):
    """if (<expr>) then <prog> else <prog> fi"""

    def __init__(self, *args):  # args = height, Node_expr, Node_then, Node_else
        super().__init__(args[0])
        self.expr = args[1]
        self.then_branch = args[2]
        self.else_branch = args[3]

    def __str__(self):
        print_str = ['if [\n',
                     self.one_tab(self.expr.__str__()),
                     self.one_tab('then ' + self.then_branch.__str__()),
                     self.one_tab('else ' + self.else_branch.__str__()),
                     ']']
        return self.final_print_str(print_str)


class Assign(Node):
    """<variable> '=' <expr>"""

    def __init__(self, *args):  # args = height, Node_variable, Node_expr
        super().__init__(args[0])
        self.variable = args[1]
        self.expr = args[2]

    def __str__(self):
        print_str = ['assign [\n',
                     self.one_tab(self.variable.__str__()),
                     self.one_tab(self.expr.__str__()),
                     ']']
        return self.final_print_str(print_str)


# EXEMPLU DE INSTANTIERE:
#
# begin
# x = 7
# y = 0
# while (x < 15) do
#     x = x + 2
#     y = y + 3
# od
# if (x == y) then
#     x = x + y
# else
#     x = y
# fi
# end
#
# prog = InstructionList(0,
#                        [
#                            Assign(1,
#                                   Expr(2, 'v', 'x'),
#                                   Expr(2, 'i', '3')),
#                            While(1,
#                                  Expr(2,
#                                       '>',
#                                       Expr(3, 'v', 'x'),
#                                       Expr(3, 'i', '5')),
#                                  InstructionList(2,
#                                                  [
#                                                     Assign(3,
#                                                            Expr(4, 'v', 'x'),
#                                                            Expr(4,
#                                                                 '+',
#                                                                 Expr(5, 'v', 'x'),
#                                                                 Expr(5, 'i', '2')))
#                                                  ])
#                                 ),
#                            If(1,
#                               Expr(2,
#                                    '==',
#                                    Expr(3, 'v', 'x'),
#                                    Expr(3, 'v', 'y')),
#                               Assign(3,
#                                      Expr(4, 'v', 'x'),
#                                      Expr(4,
#                                           '+',
#                                           Expr(5, 'v', 'x'),
#                                           Expr(5, 'v', 'y'))),
#                               Assign(3,
#                                      Expr(4, 'v', 'x'),
#                                      Expr(4, 'v', 'y')))
#                        ])

# with open('prog.txt', 'w+') as f:
#     f.write(str(prog))

