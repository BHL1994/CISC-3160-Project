from sly import Lexer
from sly import Parser

class MyLexer(Lexer):
    #Create a set that stores the names of the tokens
    tokens = {LETTER, DIGIT, STRING}
    #A variable that lets us ignore whitespaces and tabs
    ignore = '\t '

    #Stores the literals
    literals = { '=', '+', '-', '/', '*', '(', ')', ',', ';' }

    #Define tokens
    LETTER = r'[a-zA-Z_][a-zA-Z0-9_]*'
    STRING = r'\".*?\"'

    #A function that defines a number that is
    #zero or a non digit number
    @_(r'0|[1-9][0-9]*')
    def DIGIT(self, x):
        x.value = int(x.value)
        return x


class MyParser(Parser):
    tokens = MyLexer.tokens

    # This will set the order of operations, so multiplication
    # and division will come before addition and subtraction
    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS'),
        )

    def __init__(self):
        self.env = { }

    #Grammar rules
    #An empty statement that will just do nothing
    @_('')
    def statement(self, x):
        pass

    @_('var_assign')
    def statement(self, x):
        return x.var_assign

    @_('LETTER "=" expr')
    def var_assign(self, x):
        return ('var_assign', x.LETTER, x.expr)

    @_('LETTER "=" STRING')
    def var_assign(self, x):
        return ('var_assign', x.LETTER, x.STRING)

    @_('expr')
    def statement(self, x):
        return (x.expr)

    @_('expr "+" expr')
    def expr(self, x):
        return ('add', x.expr0, x.expr1)

    @_('expr "-" expr')
    def expr(self, x):
        return ('sub', x.expr0, x.expr1)

    @_('expr "*" expr')
    def expr(self, x):
        return ('mul', x.expr0, x.expr1)

    @_('expr "/" expr')
    def expr(self, x):
        return ('div', x.expr0, x.expr1)

    @_('"-" expr %prec UMINUS')
    def expr(self, x):
        return x.expr

    @_('LETTER')
    def expr(self, x):
        return ('var', x.LETTER)

    @_('DIGIT')
    def expr(self, x):
        return ('num', x.DIGIT)


#The execution class that will create the syntax tree recursively
class Execute:

    def __init__(self, tree, env):
        self.env = env
        result = self.walkTree(tree)
        if result is not None and isinstance(result, int):
            print(result)
        if isinstance(result, str) and result[0] == '"':
            print(result)

    def walkTree(self, node):

        if isinstance(node, int):
            return node
        if isinstance(node, str):
            return node

        if node is None:
            return None

        if node[0] == 'program':
            if node[1] == None:
                self.walkTree(node[2])
            else:
                self.walkTree(node[1])
                self.walkTree(node[2])

        if node[0] == 'num':
            return node[1]

        if node[0] == 'str':
            return node[1]


        if node[0] == 'condition_eqeq':
            return self.walkTree(node[1]) == self.walkTree(node[2])


        if node[0] == 'add':
            return self.walkTree(node[1]) + self.walkTree(node[2])
        elif node[0] == 'sub':
            return self.walkTree(node[1]) - self.walkTree(node[2])
        elif node[0] == 'mul':
            return self.walkTree(node[1]) * self.walkTree(node[2])
        elif node[0] == 'div':
            return self.walkTree(node[1]) / self.walkTree(node[2])

        if node[0] == 'var_assign':
            self.env[node[1]] = self.walkTree(node[2])
            return node[1]

        if node[0] == 'var':
            try:
                return self.env[node[1]]
            except LookupError:
                print("Undefined variable '"+node[1]+"' found!")
                return 0


if __name__ == '__main__':
    lexer = MyLexer()
    parser = MyParser()
    env = {}
    while True:
        try:
            text = input('Please enter an expression: ')
        except EOFError:
            break
        if text:
            tree = parser.parse(lexer.tokenize(text))
            Execute(tree, env)