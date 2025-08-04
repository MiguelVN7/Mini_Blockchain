import datetime
import hashlib
import time


def hacerMenu ():
    print('\n-----------------------------------')
    print('Simulación de Blockchain en Python')
    print('\n1. Crear la Cadena \n2. Adicionar un Bloque \n3. Verificar la Cadena \n4. Leer un Bloque \n5. Eliminar un Bloque \n6. Alterar un Bloque \n7. Simular Creación \n8. Salir')
    try:
        return int(input('\nElección: '))
    except ValueError:
        return None


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


    def ajustarDificultad (self, tiempoBloqueAnterior, cerosActuales): # Cambiar el paso a 2
        diferencia = self.tiempoObjetivo - tiempoBloqueAnterior
        paso = 1
        if tiempoBloqueAnterior < self.tiempoObjetivo:
            nuevo = cerosActuales + paso
        elif tiempoBloqueAnterior > self.tiempoObjetivo:
            nuevo = cerosActuales - paso
        else:
            nuevo = cerosActuales
        return max(self.minCeros, min(self.maxCeros, nuevo))
    

    def verificarCadena(self):
        resultados = []
        cadenaRota = False  # indica si ya se detectó una corrupción antes

        for i, bloque in enumerate(self.bloques):
            mensajes = []
            previoEsperado = b'\x00' * 32 if i == 0 else self.bloques[i - 1].hash

            # 1. Enlace
            if bloque.hashPrevio != previoEsperado:
                mensajes.append("prev_hash incorrecto")
                cadenaRota = True

            # 2. Hash recalculado
            recalculado = bloque.calcularHash(bloque.nonce)
            if recalculado != bloque.hash:
                messages = "Hash manipulado (contenido + nonce no coincide)"
                mensajes.append(messages)
                cadenaRota = True

            # 3. Dificultad
            if not bloque.hashValido(bloque.hash):
                mensajes.append(f"Dificultad no satisfecha (esperados {bloque.ceros} ceros)")
                cadenaRota = True

            # 4. Contaminación en cascada como advertencia, si no tiene fallo directo
            if cadenaRota and not mensajes:
                mensajes.append("Posiblemente comprometido por corrupción previa")

            if not mensajes:
                resultados.append(f"Bloque {i}: OK")
            else:
                resultados.append(f"Bloque {i}: {' y '.join(mensajes)}")

        return resultados



    def leerBloque (self):
        indice = int(input('\nIngrese el índice del bloque que quiere conocer (recuerde que el génesis tiene índice 0): '))
        if not (0 <= indice < len(self.bloques)):
            raise IndexError(f"Índice {indice} fuera de rango. La cadena tiene {len(self.bloques)} bloques.")
        print(f'Información del bloque con índice: {indice} \n')
        bloque = self.bloques[indice]
        bloque.darInfo()

    
    def borrarBloque (self):
        indice = int(input('\nIngrese el índice del bloque que quiere eliminar (recuerde que el génesis tiene índice 0): '))
        if not (0 <= indice < len(self.bloques)):
            raise IndexError(f"Índice {indice} fuera de rango. La cadena tiene {len(self.bloques)} bloques.")
        self.bloques = self.bloques[:indice]
        print('Bloque eliminado satisfactoriamente')


    def alterarBloque(self):
        indice = int(input('\nIngrese el índice del bloque que quiere alterar (recuerde que el génesis tiene índice 0): '))
        if not (0 <= indice < len(self.bloques)):
            raise IndexError(f"Índice {indice} fuera de rango. La cadena tiene {len(self.bloques)} bloques.")
        
        bloque = self.bloques[indice]
        bloque.nonce += 1
        bloque.tiempo = datetime.datetime.now()


    def romper_encadenamiento(self, indice: int):
        
        if not (0 <= indice < len(self.bloques) - 1):
            raise IndexError("Índice fuera de rango o no hay siguiente bloque.")
        siguiente = self.bloques[indice + 1]
        # Poner un prev_hash inválido (por ejemplo ceros distintos del real)
        siguiente.hashPrevio = b'\x01' + siguiente.hashPrevio[1:]
        


def main():
    cadena = None

    while True:
        respuesta = hacerMenu()
        if respuesta == 1:
            cadena = Cadena(dificultadInicial=20)

        elif respuesta == 2:
            if cadena is None:
                print("Primero crea la cadena (opción 1).")
            else:
                cadena.agregar_bloque()

        elif respuesta == 3:
            if cadena is None:
                print('Primero crea la cadena (opción 1)')
            else:
                errores = cadena.verificarCadena()
                for linea in errores:
                    print(linea)
    
        elif respuesta == 4:
            # Leer un bloque (deberías pedir índice)
            if cadena is None:
                print('Primero crea la cadena (opción 1)')
            else:
                cadena.leerBloque()

        elif respuesta == 5:
            # Eliminar un bloque
            if cadena is None:
                print('Primero crea la cadena (opción 1)')
            else:
                cadena.borrarBloque()

        elif respuesta == 6:
            # Alterar un bloque
            if cadena is None:
                print('Primero crea la cadena (opción 1)')
            else:
                cadena.alterarBloque()

        elif respuesta == 7:
            cantidad = int(input('¿Cuántos bloques deseas crear? '))
            if cadena is None:
                cadena = Cadena(dificultadInicial=20)
            
            for _ in range(cantidad):
                cadena.agregar_bloque()

        elif respuesta == 8:
            break

        else:
            print('Error, respuesta ingresada incorrecta, vuelva a intentarlo...')

    return 0

if __name__ == "__main__":
    main()
