# -----------------------------------------------------------------------------
# calc.py
#
# Nuestros nombres
# -----------------------------------------------------------------------------

import syntax_tree as st

# Palabras reservadas

reserved = {
   'if' : 'IF',
   'then' : 'THEN',
   'else' : 'ELSE',
   'while' : 'WHILE',
   'return' : 'RETURN',
   'plot' : 'PLOT',
   'for' : 'FOR',
   'function' : 'FUNCTION',
}

tokens = [
    'PP','NAME','NUMBER','COMA','LLAVEI','LLAVED',
    'PLUS','MINUS','TIMES','DIVIDE','EQUALS',
    'LPAREN','RPAREN','POWER',
    'GT','GE','LT','LE','NE','EQ',
    'AND','OR','NOT',
    ]+list(reserved.values())

# Ignorar comentarios multilinea

def t_comentario(t):
    r'(/\*(.|\n)*?\*/)'
    pass

# Tokens

t_PP      = r'\.\.'
t_COMA    = r'\,'
t_LLAVEI  = r'\{'
t_LLAVED  = r'\}'
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_POWER   = r'\^'
t_GT      = r'\>'
t_GE      = r'\>='
t_LT      = r'\<'
t_LE      = r'\<='
t_NE      = r'\!='
t_EQ      = r'\=='
t_AND     = r'\&\&'
t_OR      = r'\|\|'
t_NOT     = r'\!'

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'NAME')    # Check for reserved words
    return t

def t_NUMBER(t):
    r'\.\d+|\d+(\.\d+)?'
    try:
        t.value = float(t.value)
    except ValueError:
        print("Float value too large %f", t.value)
        t.value = 0
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
import lex as lex
lex.lex()

# Parsing rules

precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('left','POWER'),
    ('right','UMINUS'),
    ('left','OR'),
    ('left','AND'),
    ('right','NOT'),
    ('right','ELSE'),   # Sin esto daba conflicto shift-reduce, por no saber a que if se asocia el else
                        # p/ej: if true then if true then a=1 else a=2
    )

# dictionary of names
names = { }

def p_test_test_test(t):
    'test_test_test : lista_funciones expression'

    lista_funciones = t[1]
    expresion = t[2]

    contexto = st.Contexto()

    print '/* Programa */'
    for decl in lista_funciones:
        print decl.mostrar()
    print expresion.mostrar()

    print
    print '/* Resultado */'
    for decl in lista_funciones:
        decl.evaluar(contexto)
    print expresion.evaluar(contexto)

def p_programa(t):
    'programa : lista_funciones plot'

def p_plot(t):
    'plot : PLOT LPAREN expression COMA expression RPAREN FOR NAME EQUALS rango'

def p_rango(t):
    'rango : expression PP expression PP expression'

def p_lambda(p):
    'lambda :'
    pass

def p_lista_expresiones_vacia(t):
    'lista_expresiones : lambda'
    t[0] = []

def p_lista_expresiones_no_vacia(t):
    'lista_expresiones : expression lista_expresiones_aux'
    t[0] = [t[1]] + t[2]

def p_lista_expresiones_aux_vacia(t):
    'lista_expresiones_aux : lambda'
    t[0] = []

def p_lista_expresiones_aux_no_vacia(t):
    'lista_expresiones_aux : COMA expression lista_expresiones_aux'
    t[0] = [t[2]] + t[3]

def p_lista_nombres_vacia(t):
    'lista_nombres : lambda'
    t[0] = []

def p_lista_nombres_no_vacia(t):
    'lista_nombres : NAME lista_nombres_aux'
    t[0] = [t[1]] + t[2]

def p_lista_nombres_aux_vacia(t):
    'lista_nombres_aux : lambda'
    t[0] = []

def p_lista_nombres_aux_no_vacia(t):
    'lista_nombres_aux : COMA NAME lista_nombres_aux'
    t[0] = [t[2]] + t[3]

def p_lista_funciones(t):
    'lista_funciones : funcion' 
    t[0] = [t[1]]

def p_lista_funciones_recursiva(t):
    'lista_funciones : funcion lista_funciones' 
    t[0] = [t[1]] + t[2]

def p_funcion(t):
    'funcion : FUNCTION NAME LPAREN lista_nombres RPAREN bloque' 
    t[0] = st.DeclararFuncion(t[2], t[4], t[6])

def p_instruccion_return(t):
    'instruccion : RETURN expression'
    t[0] = st.Return(t[2])

def p_instruccion_asig(t):
    'instruccion : NAME EQUALS expression'
    t[0] = st.Asignacion(t[1], t[3])

def p_instruccion_while(t):
    'instruccion : WHILE COMP bloque'
    t[0] = st.While(t[2], t[3])

def p_instruccion_ifthen(t):
    'instruccion : IF COMP THEN bloque else'
    t[0] = st.If(t[2], t[4], t[5])

def p_else_no_vacio(t):
    'else : ELSE bloque'
    t[0] = t[2]

def p_else_vacio(t):
    'else : lambda'
    t[0] = None

def p_bloque_una(t):
    'bloque : instruccion'
    # Porque evaluar un bloque de una sola
    # instruccion es equivalente a evaluar
    # la instruccion, la alternativa es hacer
    # t[0] = st.Bloque([t[1]])
    t[0] = t[1]

def p_bloque_muchas(t):
    'bloque : LLAVEI lista_instrucciones LLAVED'
    t[0] = st.Bloque(t[2])

def p_lista_instrucciones_una(t):
    'lista_instrucciones : instruccion'
    # Devuelvo una lista de instrucciones
    # (cada una es a la vez un nodo
    # correspondiente al tipo de 
    # instruccion que sea)
    t[0] = [t[1]]

def p_lista_instrucciones_muchas(t):
    'lista_instrucciones : instruccion lista_instrucciones'
    t[0] = [t[1]] + t[2]

def p_expression_funcion(t):
    'expression : NAME LPAREN lista_expresiones RPAREN'
    t[0] = st.LlamarFuncion(t[1], t[3]) 

def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression POWER expression'''
    t[0] = st.OperadorBinario(t[2], t[1], t[3])

def p_comparison_binop(t):
    '''COMP : expression LE expression
            | expression LT expression
            | expression GE expression
            | expression GT expression
            | expression NE expression
            | expression EQ expression'''
    t[0] = st.OperadorBinario(t[2], t[1], t[3])

def p_and(t):
    'COMP : COMP AND COMP'
    t[0] = st.OperadorBinario('and', t[1], t[3])

def p_or(t):
    'COMP : COMP OR COMP'
    t[0] = st.OperadorBinario('or', t[1], t[3])

def p_cond_paren(t):
    'COMP : LPAREN COMP RPAREN'
    t[0] = t[2]

def p_cond_not(t):
    'COMP : NOT COMP'
    t[0] = st.Not(t[2])

def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = st.Neg(t[2])

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = t[2]

def p_expression_number(t):
    'expression : NUMBER'
    t[0] = st.Constante(t[1])

def p_expression_name(t):
    'expression : NAME'
    t[0] = st.Variable(t[1])

def p_error(t):
    print("Syntax error at '%s'" % t.value)

import sys
import yacc as yacc
yacc.yacc()

s = sys.stdin.read()

programa = yacc.parse(s) #,debug=1)

