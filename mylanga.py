# -----------------------------------------------------------------------------
# mylanga.py
#
# TP Teoria de lenguajes - 1er C 2014 
#
# Autores (en orden alfabetico): Gabriela Croce - Elisa Orduna - Martin Rados
# -----------------------------------------------------------------------------

import syntax_tree as st
import math

# Palabras reservadas

reserved = {
   'pi' : 'PI',
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
    'PP','ID','NUMERO','COMA','LLAVEI','LLAVED',
    'MAS','MENOS','MULTIPLICACION','DIVISION','ASIGNACION',
    'PARENI','PAREND','POTENCIA',
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
t_MAS    = r'\+'
t_MENOS   = r'-'
t_MULTIPLICACION   = r'\*'
t_DIVISION  = r'/'
t_ASIGNACION  = r'='
t_PARENI  = r'\('
t_PAREND  = r'\)'
t_POTENCIA   = r'\^'
t_GT      = r'\>'
t_GE      = r'\>='
t_LT      = r'\<'
t_LE      = r'\<='
t_NE      = r'\!='
t_EQ      = r'\=='
t_AND     = r'\&\&'
t_OR      = r'\|\|'
t_NOT     = r'\!'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

def t_NUMERO(t):
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
    ('left','MAS','MENOS'),
    ('left','MULTIPLICACION','DIVISION'),
    ('left','POTENCIA'),
    ('right','UMENOS'),
    ('left','OR'),
    ('left','AND'),
    ('right','NOT'),
    ('right','ELSE'),   # Sin esto daba conflicto shift-reduce, por no saber a que if se asocia el else
                        # p/ej: if true then if true then a=1 else a=2
    )


# contexto de variables
contexto = st.Contexto()

# Simbolo distinguido
start='programa'

def p_programa(t):
    'programa : lista_funciones plot'

def p_plot(t):
    'plot : PLOT PARENI llamado_a_funcion COMA llamado_a_funcion PAREND FOR ID ASIGNACION rango'
    st.Plot(t[3],t[5],t[8],t[10]).evaluar(contexto)
    
def p_rango(t):
    'rango : expresion PP expresion PP expresion'
    t[0] = st.Rango(t[1],t[3],t[5])

def p_lambda(p):
    'lambda :'
    pass

def p_lista_expresiones_vacia(t):
    'lista_expresiones : lambda'
    t[0] = []

def p_lista_expresiones_no_vacia(t):
    'lista_expresiones : expresion lista_expresiones_aux'
    t[0] = [t[1]] + t[2]

def p_lista_expresiones_aux_vacia(t):
    'lista_expresiones_aux : lambda'
    t[0] = []

def p_lista_expresiones_aux_no_vacia(t):
    'lista_expresiones_aux : COMA expresion lista_expresiones_aux'
    t[0] = [t[2]] + t[3]

def p_lista_nombres_vacia(t):
    'lista_nombres : lambda'
    t[0] = []

def p_lista_nombres_no_vacia(t):
    'lista_nombres : ID lista_nombres_aux'
    t[0] = [t[1]] + t[2]

def p_lista_nombres_aux_vacia(t):
    'lista_nombres_aux : lambda'
    t[0] = []

def p_lista_nombres_aux_no_vacia(t):
    'lista_nombres_aux : COMA ID lista_nombres_aux'
    t[0] = [t[2]] + t[3]

def p_lista_funciones(t):
    'lista_funciones : funcion' 
    t[0] = [t[1]]

def p_lista_funciones_recursiva(t):
    'lista_funciones : funcion lista_funciones' 
    t[0] = [t[1]] + t[2]

def p_funcion(t):
    'funcion : FUNCTION ID PARENI lista_nombres PAREND bloque' 
    st.declarar_funcion(t[2], t[4], t[6])

def p_instruccion_return(t):
    'instruccion : RETURN expresion'
    t[0] = st.Return(t[2])

def p_instruccion_asig(t):
    'instruccion : ID ASIGNACION expresion'
    t[0] = st.Asignacion(t[1], t[3])

def p_instruccion_while(t):
    'instruccion : WHILE COND bloque'
    t[0] = st.While(t[2], t[3])

def p_instruccion_ifthen(t):
    'instruccion : IF COND THEN bloque else'
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

def p_llamado_a_funcion(t):
    'llamado_a_funcion : ID PARENI lista_expresiones PAREND'
    t[0] = st.LlamarFuncion(t[1], t[3]) 

def p_expresion_funcion(t):
    'expresion : llamado_a_funcion'
    t[0] = t[1]

def p_expresion_binop(t):
    '''expresion : expresion MAS expresion
                  | expresion MENOS expresion
                  | expresion MULTIPLICACION expresion
                  | expresion DIVISION expresion
                  | expresion POTENCIA expresion'''
    t[0] = st.OperadorBinario(t[2], t[1], t[3])

def p_comparison_binop(t):
    '''COND : expresion LE expresion
            | expresion LT expresion
            | expresion GE expresion
            | expresion GT expresion
            | expresion NE expresion
            | expresion EQ expresion'''
    t[0] = st.OperadorBinario(t[2], t[1], t[3])

def p_and(t):
    'COND : COND AND COND'
    t[0] = st.OperadorBinario('and', t[1], t[3])

def p_or(t):
    'COND : COND OR COND'
    t[0] = st.OperadorBinario('or', t[1], t[3])

def p_cond_paren(t):
    'COND : PARENI COND PAREND'
    t[0] = t[2]

def p_cond_not(t):
    'COND : NOT COND'
    t[0] = st.Not(t[2])

def p_expresion_uminus(t):
    'expresion : MENOS expresion %prec UMENOS'
    t[0] = st.Neg(t[2])

def p_expresion_group(t):
    'expresion : PARENI expresion PAREND'
    t[0] = t[2]

def p_expresion_pi(t):
    'pi : PI'
    t[0] = math.pi

def p_expresion_number(t):
    '''expresion : NUMERO
                 | pi'''
    t[0] = st.Constante(t[1])

def p_expresion_name(t):
    'expresion : ID'
    t[0] = st.Variable(t[1])

def p_error(t):
    print("Syntax error at '%s'" % t.value)

import sys
import yacc as yacc
yacc.yacc()

s = sys.stdin.read()

programa = yacc.parse(s) #,debug=1)

