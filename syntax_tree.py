
# Clase para guardar
# - declaraciones de funciones
# - valores de las variables locales
# - pila con las variables locales de todas las llamadas
class Contexto(object):

    def __init__(self):
        self.funciones = {}
        self.valores = {}

    # Variables locales

    def asignar(self, nombre, valor):
        self.valores[nombre] = valor

    def obtener(self, nombre):
        if nombre not in self.valores:
            raise Exception('Variable no inicializada: "' + nombre + '"')
        return self.valores[nombre]

    # Funciones

    def declarar_funcion(self, nombre, parametros, bloque):
        if nombre in self.funciones:
            raise Exception('Declaraciones multiples para la funcion: "' + nombre + '"')
        self.funciones[nombre] = (parametros, bloque)

    def buscar_funcion(self, nombre):
        if nombre not in self.funciones:
            raise Exception('Funcion no declarada: "' + nombre + '"')
        return self.funciones[nombre]

    # Copia el contexto para hacer llamados a funciones,
    # con diccionario de variables vacio.
    def copia(self):
        c = Contexto()
        c.funciones = self.funciones
        return c

# Clases para representar arboles de sintaxis
# (expresiones, instrucciones, programas, etc.)

class Variable(object):

    def __init__(self, name):
        self.name = name

    def mostrar(self):
        return self.name

    def evaluar(self, contexto):
        return contexto.obtener(self.name)

class Constante(object):

    def __init__(self, number):
        self.number = number

    def mostrar(self):
        return '%s' % (self.number,)

    def evaluar(self, contexto):
        return self.number

class Neg(object):
    # cambiar el signo

    def __init__(self, expresion):
        self.expresion = expresion

    def mostrar(self):
        return '-%s' % (self.expresion.mostrar(),)

    def evaluar(self, contexto):
        return -self.expresion.evaluar(contexto)

class Not(object):
    # negacion booleana

    def __init__(self, expresion):
        self.expresion = expresion

    def mostrar(self):
        return '!%s' % (self.expresion.mostrar(),)

    def evaluar(self, contexto):
        return not self.expresion.evaluar(contexto)

class OperadorBinario(object):

    def __init__(self, op, expresion1, expresion2):
        self.op = op
        self.expresion1 = expresion1
        self.expresion2 = expresion2

    def mostrar(self):
        return '(%s %s %s)' % (self.expresion1.mostrar(),
                               self.op,
                               self.expresion2.mostrar())

    def evaluar(self, contexto):
        v1 = self.expresion1.evaluar(contexto) 
        v2 = self.expresion2.evaluar(contexto) 
        
        if self.op == 'and':
          return v1 and v2
        elif self.op == 'or':
          return v1 or v2
        elif self.op == '<':
          return v1 < v2
        elif self.op == '<=':
          return v1 <= v2
        elif self.op == '>':
          return v1 > v2
        elif self.op == '>=':
          return v1 >= v2
        elif self.op == '==':
          return v1 == v2
        elif self.op == '!=':
          return v1 != v2
        elif self.op == '+':
          return v1 + v2
        elif self.op == '-':
          return v1 - v2
        elif self.op == '*':
          return v1 * v2
        elif self.op == '/':
          return v1 / v2
        elif self.op == '^':
          return v1 ** v2

class LlamarFuncion(object):
    
    def __init__(self, name, parametros):
        self.name = name
        self.parametros = parametros

    def mostrar(self):
        return '%s(%s)' % (self.name,
                           ', '.join([p.mostrar() for p in self.parametros]))

    def evaluar(self, contexto):
        (nombres_parametros, bloque) = contexto.buscar_funcion(self.name)

        if len(nombres_parametros) != len(self.parametros):
            raise Exception('No coincide la aridad para la funcion "' + self.name + '"')

        contexto2 = contexto.copia()
        for n, p in zip(nombres_parametros, self.parametros):
            contexto2.asignar(n, p.evaluar(contexto))

        try:
            bloque.evaluar(contexto2)
        except ReturnCondition as ret:
            return ret.valor

        # si llego aca es que la funcion no tenia return
        raise Exception('La funcion "' + self.name + '" no tiene return')

def identar(string):
    return '\n'.join(['    ' + linea for linea in string.split('\n')])

class Bloque(object):
    # instrucciones es lista de instrucciones
    def __init__(self, instrucciones):
        self.instrucciones = instrucciones

    def mostrar(self):
        return ('{\n' +
                 '\n'.join([identar(instr.mostrar()) for instr in self.instrucciones]) +
                 '\n}')

    def evaluar(self, contexto):
        for instr in self.instrucciones:
            instr.evaluar(contexto)

class Asignacion(object):
    
    def __init__(self, name, expresion):
        self.name = name
        self.expresion = expresion

    def mostrar(self):
        return '%s = %s' % (self.name, self.expresion.mostrar())

    def evaluar(self, contexto):
        contexto.asignar(self.name, self.expresion.evaluar(contexto))

class If(object):
    
    def __init__(self, cond, bloqueThen, bloqueElse):
        self.cond = cond
        self.bloqueThen = bloqueThen
        self.bloqueElse = bloqueElse
   
    def mostrar(self):
        if self.bloqueElse is None:
            else_mostrar = ''
        else:
            else_mostrar = ' else %s' % (self.bloqueElse.mostrar(),)
        return ('if %s then %s' % (self.cond.mostrar(), self.bloqueThen.mostrar()) +
                else_mostrar)

    def evaluar(self, contexto):
        if self.cond.evaluar(contexto):
            self.bloqueThen.evaluar(contexto)
        elif self.bloqueElse is not None:
            self.bloqueElse.evaluar(contexto)

class While(object):
    
    def __init__(self, cond, bloque):
        self.cond = cond
        self.bloque = bloque

    def mostrar(self):
        return 'while %s %s' % (self.cond.mostrar(), self.bloque.mostrar())

    def evaluar(self, contexto):
        while self.cond.evaluar(contexto):
            self.bloque.evaluar(contexto)

class Plot(object):
    
    def __init__(self, llamado_f1, llamado_f2, id, rango):
        self.llamado_f1 = llamado_f1
        self.llamado_f2 = llamado_f2
        self.id = id
        self.rango = rango

    def evaluar(self, contexto):
        ##f1=self.llamado_f1.name
        ##f2=self.llamado_f2.name
        d=self.rango.d.evaluar(contexto)
        h=self.rango.h.evaluar(contexto)
        s=self.rango.salto.evaluar(contexto)
        i=d

        
        #if len(nombres_parametros) != len(self.parametros):
        #    raise Exception('No coincide la aridad para la funcion "' + self.name + '"')

        #contexto2 = contexto.copia()
        
        #try:
        #    bloque.evaluar(contexto2)
        #except ReturnCondition as ret:
        #    return ret.valor

        # si llego aca es que la funcion no tenia return
        #raise Exception('La funcion "' + self.name + '" no tiene return')
        (nombres_parametros_f1, bloque_f1) = contexto.buscar_funcion(self.llamado_f1.name)
        (nombres_parametros_f2, bloque_f2) = contexto.buscar_funcion(self.llamado_f2.name)

        while(i<=h):
            contexto2=contexto.copia()
	    contexto2.asignar(self.id,i)
            for n, p in zip(nombres_parametros, self.parametros):
                contexto2.asignar(n, p.evaluar(contexto))

            x=f1.evaluar(contexto2)
            y=f2.evaluar(contexto2)
            print(x + " ,  " + y)
            i=i+s

class Rango(object):
    
    def __init__(self, d, salto, h):
        self.d = d
        self.salto = salto
        self.h = h

class DeclararFuncion(object):

    def __init__(self, name, parametros, bloque):
        self.name = name
        self.parametros = parametros
        self.bloque = bloque

    def mostrar(self):
        return 'function %s(%s) %s' % (
                    self.name,
                    ', '.join(self.parametros),
                    self.bloque.mostrar())

    def evaluar(self, contexto):
        contexto.declarar_funcion(self.name, self.parametros, self.bloque)

# Excepcion para indicar que se llego al return de
# una funcion.
class ReturnCondition(Exception):

    def __init__(self, valor):
        self.valor = valor

class Return(object):

    def __init__(self, expresion):
        self.expresion = expresion

    def mostrar(self):
        return 'return %s' % (self.expresion.mostrar(),)

    def evaluar(self, contexto):
        raise ReturnCondition(self.expresion.evaluar(contexto))

class Programa(object):

    def __init__(self, lista_funciones, plot):
	

t[0] = st.Programa(t[1], t[2])
