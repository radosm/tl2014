# -----------------------------------------------------------------------------
# calc.py
#
# Nuestros nombres
# -----------------------------------------------------------------------------
 
import math

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

def p_programa(t):
    'programa : lista_funciones plot'

def p_plot(t):
    'plot : PLOT LPAREN expression COMA expression RPAREN FOR NAME EQUALS rango'

def p_rango(t):
    'rango : expression PP expression PP expression'

def p_lambda(p):
    'lambda :'
    pass

def p_lista_expresiones(t):
    '''lista_expresiones : expression lista_expresiones_aux
                         | lambda'''

def p_lista_expresiones_aux(t):
    '''lista_expresiones_aux : COMA expression lista_expresiones_aux 
                             | lambda'''

def p_lista_nombres(t):
    '''lista_nombres : NAME lista_nombres_aux 
                     | lambda'''

def p_lista_nombres_aux(t):
    '''lista_nombres_aux : COMA NAME lista_nombres_aux 
                         | lambda'''

def p_lista_funciones(t):
    'lista_funciones : funcion' 

def p_lista_funciones_recursiva(t):
    'lista_funciones : funcion lista_funciones' 

def p_funcion(t):
    'funcion : FUNCTION NAME LPAREN lista_nombres RPAREN bloque' 

def p_instruccion_return(t):
    'instruccion : RETURN expression'

def p_instruccion_asig(t):
    'instruccion : NAME EQUALS expression'

def p_instruccion_while(t):
    'instruccion : WHILE COMP bloque'

def p_instruccion_ifthen(t):
    'instruccion : IF COMP THEN bloque else'

def p_else(t):
    '''else : ELSE bloque
            | lambda'''

def p_bloque(t):
    '''bloque : instruccion 
              | LLAVEI lista_instrucciones LLAVED'''

def p_lista_instrucciones(t):
    '''lista_instrucciones : instruccion
                           | instruccion lista_instrucciones'''

def p_expression_funcion(t):
    'expression : NAME LPAREN lista_expresiones RPAREN'

def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression POWER expression'''
    if t[2] == '+'  : pass
    elif t[2] == '-': pass
    elif t[2] == '*': pass
    elif t[2] == '/': pass
    elif t[2] == '^': pass

def p_comparison_binop(t):
    '''COMP : expression LE expression
            | expression LT expression
            | expression GE expression
            | expression GT expression
            | expression NE expression
            | expression EQ expression'''
    if t[2]   == '<' : pass
    elif t[2] == '<=': pass
    elif t[2] == '>' : pass
    elif t[2] == '>=': pass
    elif t[2] == '==': pass
    elif t[2] == '!=': pass

def p_and(t):
    'COMP : COMP AND COMP'

def p_or(t):
    'COMP : COMP OR COMP'

def p_cond_paren(t):
    'COMP : LPAREN COMP RPAREN'

def p_cond_not(t):
    'COMP : NOT COMP'

def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'

def p_expression_number(t):
    'expression : NUMBER'

def p_expression_name(t):
    'expression : NAME'

def p_error(t):
    print("Syntax error at '%s'" % t.value)

import sys
import yacc as yacc
yacc.yacc()

s = sys.stdin.read()
yacc.parse(s) #,debug=1)

