import datetime
import hashlib
import time

class Bloque:
    def __init__ (self, hashPrevio: bytes, ceros: int):
        self.hashPrevio = hashPrevio # Hash del bloque anterior en la cadena
        self.tiempo = datetime.datetime.now() # Tiempo para añadirle un time stamp al bloque 
        self.ceros = ceros # Número de ceros objetivo que se busca en el hash
        self.nonce = 0 # Nonce con el que se inicia en el bloque
        self.hash = None # Hash del bloque actual
        self.inicio = 0.0 # Inicio del minado 
        self.final  = 0.0 # Final del minado
        self.segundos = 0.0 # Tiempo en segundos que se demora el minado


    # Función para "unir" o concatenar toda la info que irá dentro del bloque para calcular el hash    
    def construirContenido (self, nonce:int) -> bytes:
        partes = (
            self.hashPrevio + str(self.tiempo.timestamp()).encode('utf-8') + str(nonce).encode('utf-8') # Objeto de Bytes donde se concatena el hash, timestamp y nonce
        )
        return partes
    

    # Función para, usando el contenido obtenido de la función anterior, calcular el hash y convertirlo a Bytes
    def calcularHash (self, nonce: int) -> bytes:
        contenido = self.construirContenido(nonce) # Se construye el contenido para el bloque específico a trabajar
        return hashlib.sha256(contenido).digest() # Se calcula el hash, usando la función sha256 metiéndole todo el contenido tenido y se convierte a Bytes
    

    # Función para validar si el hash en Bytes cumple con el requisito de ceros necesario
    def hashValido (self, hashBytes: bytes) -> bool:
        bitsParaRevisar = self.ceros # Dependiendo de los ceros objetivos, tendremos que revisar ese numero de bits
        limite = self.ceros // 8 # Acá calculamos cuántos bytes vamos a revisar o preocuparnos por (20 bits // 8 que da 2)
        reps = 0 # Cuantas repeticiones llevamos 
        
        # Mientras que las repeticiones sean menores al límite (0 < 2, por ejemplo) y el Byte en la posición reps del hash sea cero
        while reps < limite and hashBytes[reps] == 0:
            bitsParaRevisar -= 8 # Disminuimos los bits para revisar en 1 byte (8 bits), por ejemplo 20 - 8 = 12
            reps += 1 # Aumentamos las repeticiones que llevamos en 1; acá 0 + 1 = 1
        
        # Si las repeticiones que llevamos son menores al límite retornamos falso, pero la idea es que no lo sean (por eso las aumentamos en el while pasado)
        if reps < limite: 
            return False
        
        bitsSobrantes = self.ceros % 8 # Como el hash está en bytes y debemos revisar 20 bits (2 bytes y medio byte), p.ej., 20 / 8 = 2, con residuo = 4. 
        
        # Si los ceros objetivos no son multiplo de 8, por lo que hay bits sobrantes
        if bitsSobrantes > 0:
            mask = 0xff << (8-bitsSobrantes)  # Creamos máscara de bits para verificar solo la cantidad de los primeros bits sobrantes (4 en el ejemplo) del byte actual
                                              # El 0xff son ocho 1s y lo que hace el << (8-bitsSobrantes) es mover esos bits a la izquiera por esa cantidad de posiciones
                                              # En el ejemplo sobran 4, por lo que la mascara hace 0xff << (4) 11110000
            # Acá se aplica la operación AND (si ambos bits comparados son 1, la salida es 1, sino es 0) y buscamos que el resultado sea cero
            if hashBytes[reps] & mask != 0:
                return False # Si el resultado de comparar ambas cosas es distinto a cero, entonces no nos sirve
                             # Ejemplo: Si necesitamos 20 ceros, eso equivale a 2 bytes completos (16 bits) más 4 bits adicionales:
                                            # - Ya verificamos los 2 bytes completos en el bucle anterior.
                                            # - Ahora necesitamos verificar que los 4 primeros bits del tercer byte sean ceros.
                                            # - bitsSobrantes = 4
                                            # - mask = 0xff << (8-4) = 0xff << 4 = 11110000 en binario
                                            # - Si hashBytes[reps] es por ejemplo 00010111, entonces hashBytes[reps] & mask da 00010000.
                                            # - Como el resultado no es cero, el hash no cumple con el requisito y retornamos False.
                                                                                            
        return True # Si no hemos retornado False hasta el momento, entonces el hash es válido
    
    # Función para coger un bloque y minarlo para calcular el hash y ver si es válido y ya entonces determinar la info. del bloque
    def minar (self):
        self.inicio = time.time() # Se determina el tiempo en el que inicia la minería
        nonce = 0 # Nonce = 0 para empezar

        # Hasta que el hash del bloque sea válido
        while True:
            hash = self.calcularHash(nonce) # Se calcula el hash con el nonce actual y se asigna a la variable
            if self.hashValido(hash): # Si el hash calculado con el nonce actual es válido
                self.nonce = nonce # Se asigna el nonce usado para encontrar el hash válido al bloque
                self.hash = hash # Se asigna el hash válido encontrado al bloque
                self.final = time.time() # Se calcula el tiempo del final del minado
                self.segundos = self.final - self.inicio # Se resta final - inicio para encontrar el tiempo en segundos
                return # Se termina
            nonce += 1 # Si el hash no es válido entonces se sumenta el nonce en 1


    def hashEnHex (self) -> str:
        return self.hash.hex() if self.hash else ''
    

    def darInfo (self):
        print(f'Ceros Objetivo: {self.ceros}')
        print(f'Nonce Usado: {self.nonce}')
        print(f'Timestamp: {self.tiempo.isoformat()}')
        print(f'Hash en Hexa: {self.hashEnHex()}')
        print(f'Tiempo en Segundos para Minarlo: {self.segundos} segundos')
        print(f'Hash del Bloque Anterior: {self.hashPrevio.hex()}')


class Cadena:
    def __init__(self, tiempoObjetivo = 15.0, dificultadInicial=20):
        self.bloques = []
        self.tiempoObjetivo = tiempoObjetivo
        self.minCeros = 20
        self.maxCeros = 40
        self.ajuste = 20
        self.dificultadObjetivo = dificultadInicial
        self.crear_genesis()


    def crear_genesis (self):
        genesis = Bloque(b'\x00' * 32, self.dificultadObjetivo)
        genesis.minar()
        print("\nBloque génesis minado:")
        genesis.darInfo()
        self.bloques.append(genesis)


    def agregar_bloque (self):
        previo = self.bloques[-1]
        tiempoAnterior = previo.segundos
        nuevaDificultad = self.ajustarDificultad(tiempoAnterior, previo.ceros)
        bloque = Bloque(previo.hash, nuevaDificultad)
        bloque.minar()
        print("\nNuevo bloque minado:")
        bloque.darInfo()
        self.bloques.append(bloque)


    def ajustarDificultad (self, tiempoBloqueAnterior, cerosActuales):
        diferencia = self.tiempoObjetivo - tiempoBloqueAnterior
        if abs(diferencia) >= 2:
            paso = 2
        else:
            paso = 1
        if tiempoBloqueAnterior < self.tiempoObjetivo:
            nuevo = cerosActuales + paso
        elif tiempoBloqueAnterior > self.tiempoObjetivo:
            nuevo = cerosActuales - paso
        else:
            nuevo = cerosActuales
        return max(self.minCeros, min(self.maxCeros, nuevo))


def verificarCadena():
    return 0;

def leerBloque():
    return 0;

def modificarBloque():
    return 0;

def borrarBloque():
    return 0;


def main():
    # Génesis: prev_hash de ceros
    cadena = Cadena(dificultadInicial=20)
    cadena.agregar_bloque()
    

    return 0;

if __name__ == "__main__":
    main()
