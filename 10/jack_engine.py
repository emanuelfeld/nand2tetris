from jack_tokenizer import escape


class Engine:

    _OP = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    _UNARY_OP = ['-', '~']


    def __init__(self, tokens):
        self.tokens = tokens
        self.next_token = self.tokens[0]
        self.xml = []
        self.indent = 0


    def pop_token(self):
        """
        Dequeues token list
        """
        try:
            self.next_token = self.tokens[1]
        except IndexError:
            self.next_token = None

        return self.tokens.pop(0)


    def write(self, text):
        self.xml.append('  ' * self.indent + text)


    def write_open(self, tag):
        self.write(f'<{tag}>')
        self.indent += 1


    def write_close(self, tag):
        self.indent -= 1
        self.write(f'</{tag}>')


    def write_terminal(self, token, check_type=None, check_value=None):
        check_score = 0
        check_score += not check_type or (token.type in check_type)
        check_score += not check_value or (token.value in check_value)

        if check_score > 0:
            self.write(f'<{token.type}> {escape(token.value)} </{token.type}>')
        else:
            message = (f'Expected token in {check_value} or type in {check_type}.'
                       f'Got Token({token.value}, {token.type})')
            raise AssertionError(message)


    def compile_class(self):
        """
        'class' className '{' classVarDec* subroutineDec* '}'
        """
        self.write_open('class')
        self.write_terminal(self.pop_token(), check_type=['keyword'])
        self.write_terminal(self.pop_token(), check_type=['identifier'])
        self.write_terminal(self.pop_token(), check_value=['{'])
        while self.next_token.value in ['static', 'field']:
            self.compile_class_var_dec()
        while self.next_token.value != '}':
            self.compile_subroutine()
        self.write_terminal(self.pop_token())
        self.write_close('class')


    def compile_class_var_dec(self):
        """
        ('static' | 'field') type varName (',' varName)* ';'
        """
        self.write_open('classVarDec')
        self.write_terminal(self.pop_token(), check_value=['static', 'field'])
        self.compile_type_identifier_pair()
        while self.next_token.value != ';':
            self.write_terminal(self.pop_token(), check_value=[','])
            self.write_terminal(self.pop_token(), check_type=['identifier'])
        self.write_terminal(self.pop_token())
        self.write_close('classVarDec')


    def compile_subroutine(self):
        """
        ('constructor' | 'function' | 'method') ('void' | type)
        subroutineName '(' parameterList ')' subroutineBody
        """
        self.write_open('subroutineDec')
        self.write_terminal(self.pop_token(), check_value=['constructor', 'function', 'method'])
        self.write_terminal(self.pop_token(), check_value=['void'], check_type=['identifier'])
        self.write_terminal(self.pop_token(), check_type=['identifier'])
        self.write_terminal(self.pop_token(), check_value=['('])
        self.compile_parameter_list()
        self.write_terminal(self.pop_token(), check_value=[')'])
        self.compile_subroutine_body()
        self.write_close('subroutineDec')


    def compile_subroutine_body(self):
        """
        {' varDec* statements '}'
        """
        self.write_open('subroutineBody')
        self.write_terminal(self.pop_token(), check_value=['{'])
        while self.next_token.value == 'var':
            self.compile_var_dec()
        self.write_open('statements')
        while self.next_token.value in ['let', 'while', 'return', 'if', 'do']:
            self.compile_statement()
        self.write_close('statements')
        self.write_terminal(self.pop_token(), check_value=['}'])
        self.write_close('subroutineBody')


    def compile_type_identifier_pair(self):
        self.write_terminal(self.pop_token(), check_type=['keyword', 'identifier'])
        self.write_terminal(self.pop_token(), check_type=['identifier'])


    def compile_parameter_list(self):
        """
        ((type varName) (',' type varName)*)?
        """
        self.write_open('parameterList')
        if self.next_token.value != ')':
            self.compile_type_identifier_pair()
        while self.next_token.value != ')':
            self.write_terminal(self.pop_token(), check_value=[','])
            self.compile_type_identifier_pair()
        self.write_close('parameterList')


    def compile_var_dec(self):
        """
        'var' type varName (',' varName)* ';'
        """
        self.write_open('varDec')
        self.write_terminal(self.pop_token(), check_value=['var'])
        self.compile_type_identifier_pair()
        while self.next_token.value != ';':
            self.write_terminal(self.pop_token(), check_value=[','])
            self.write_terminal(self.pop_token(), check_type=['identifier'])
        self.write_terminal(self.pop_token(), check_value=[';'])
        self.write_close('varDec')


    def compile_statement(self):
        """
        letStatement | ifStatement | whileStatement | doStatement | returnStatement
        """
        if self.next_token.value == 'let':
            self.compile_let()
        elif self.next_token.value == 'while':
            self.compile_while()
        elif self.next_token.value == 'return':
            self.compile_return()
        elif self.next_token.value == 'if':
            self.compile_if()
        elif self.next_token.value == 'do':
            self.compile_do()
        else:
            raise Exception


    def compile_expression(self):
        """
        term (op term)*
        """
        self.write_open('expression')
        self.compile_term()
        while self.next_token.value in self._OP:
            self.write_terminal(self.pop_token(), check_type=['symbol'])
            self.compile_term()
        self.write_close('expression')


    def compile_expression_list(self):
        """
        (expression (',' expression)* )?
        """
        self.write_open('expressionList')
        if self.next_token.value != ')':
            self.compile_expression()
            while self.next_token.value == ',':
                self.write_terminal(self.pop_token())
                self.compile_expression()
        self.write_close('expressionList')


    def compile_subroutine_call(self):
        """
        subroutineName '(' expressionList ')' |
        (className | varName) '.' subroutineName '(' expressionList ')'
        """

        self.write_terminal(self.pop_token(), check_type=['identifier'])
        while self.next_token.value != '(':
            self.write_terminal(self.pop_token())
        self.write_terminal(self.pop_token())
        self.compile_expression_list()
        self.write_terminal(self.pop_token(), check_value=[')'])


    def compile_do(self):
        """
        'do' subroutineCall ';'
        """
        self.write_open('doStatement')
        self.write_terminal(self.pop_token(), check_value=['do'])
        self.compile_subroutine_call()
        self.write_terminal(self.pop_token(), check_value=[';'])
        self.write_close('doStatement')


    def compile_let(self):
        """
        'let' varName ('[' expression ']')? '=' expression ';'
        """
        self.write_open('letStatement')
        self.write_terminal(self.pop_token(), check_value=['let'])
        self.write_terminal(self.pop_token(), check_type=['identifier'])
        if self.next_token.value == '[':
            self.write_terminal(self.pop_token())
            self.compile_expression()
            self.write_terminal(self.pop_token(), check_value=[']'])
        self.write_terminal(self.pop_token(), check_value=['='])
        self.compile_expression()
        self.write_terminal(self.pop_token(), check_value=[';'])
        self.write_close('letStatement')


    def compile_while(self):
        """
        'while' '(' expression ')' '{' statements '}'
        """
        self.write_open('whileStatement')
        self.write_terminal(self.pop_token(), check_value=['while'])
        self.write_terminal(self.pop_token(), check_value=['('])
        self.compile_expression()
        self.write_terminal(self.pop_token(), check_value=[')'])
        self.write_terminal(self.pop_token(), check_value=['{'])
        self.write_open('statements')
        while self.next_token.value in ['let', 'while', 'return', 'if', 'do']:
            self.compile_statement()
        self.write_close('statements')
        self.write_terminal(self.pop_token(), check_value=['}'])
        self.write_close('whileStatement')


    def compile_return(self):
        """
        'return' expression? ';'
        """
        self.write_open('returnStatement')
        self.write_terminal(self.pop_token(), check_value=['return'])
        while self.next_token.value != ';':
            self.compile_expression()
        self.write_terminal(self.pop_token())
        self.write_close('returnStatement')


    def compile_if(self):
        """
        'if' '(' expression ')' '{' statements '}'
        ('else' '{' statements '}')?
        """
        self.write_open('ifStatement')
        self.write_terminal(self.pop_token(), check_value=['if'])
        self.write_terminal(self.pop_token(), check_value=['('])
        self.compile_expression()
        self.write_terminal(self.pop_token(), check_value=[')'])
        self.write_terminal(self.pop_token(), check_value=['{'])
        self.write_open('statements')
        while self.next_token.value in ['let', 'while', 'return', 'if', 'do']:
            self.compile_statement()
        self.write_close('statements')
        self.write_terminal(self.pop_token(), check_value=['}'])
        if self.next_token.value == 'else':
            self.write_terminal(self.pop_token(), check_value=['else'])
            self.write_terminal(self.pop_token(), check_value=['{'])
            self.write_open('statements')
            while self.next_token.value in ['let', 'while', 'return', 'if', 'do']:
                self.compile_statement()
            self.write_close('statements')
            self.write_terminal(self.pop_token(), check_value=['}'])
        self.write_close('ifStatement')


    def compile_term(self):
        """
        integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' |
        subroutineCall | '(' expression ')' | unaryOp term
        """
        self.write_open('term')
        if self.next_token.value == '(':
            self.write_terminal(self.pop_token())
            self.compile_expression()
            self.write_terminal(self.pop_token(), check_value=[')'])
        elif self.next_token.value in self._UNARY_OP:
            self.write_terminal(self.pop_token())
            self.compile_term()
        else:
            self.write_terminal(self.pop_token(), check_type=['integerConstant', 'stringConstant',
                                                              'keywordConstant', 'identifier',
                                                              'keyword'])
            if self.next_token.value == '[':
                self.write_terminal(self.pop_token())
                self.compile_expression()
                self.write_terminal(self.pop_token(), check_value=[']'])
            elif self.next_token.value == '.':
                self.write_terminal(self.pop_token())
                self.compile_subroutine_call()
        self.write_close('term')
