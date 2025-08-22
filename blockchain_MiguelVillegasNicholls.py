import datetime
import hashlib
import time
import os
import subprocess
import json

# Código con las adiciones para el parcial 2

# ========== FUNCIONES GPG ==========

def ejecutar_gpg(comando):
    """Ejecuta un comando GPG y retorna el resultado"""
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        return resultado.returncode, resultado.stdout, resultado.stderr
    except Exception as e:
        return -1, "", str(e)

def generar_claves_gpg():
    """Genera un par de claves GPG de forma interactiva"""
    print('\n=== GENERAR PAR DE CLAVES GPG ===')
    print('Se te pedirán algunos datos para generar las claves:')
    print('- Nombre completo')
    print('- Dirección de email') 
    print('- Comentario (opcional)')
    print('- Contraseña para proteger la clave privada')
    
    input('\nPresiona Enter para continuar...')
    
    # Comando para generar claves de forma interactiva
    comando = 'gpg --full-generate-key'
    codigo, salida, error = ejecutar_gpg(comando)
    
    if codigo == 0:
        print('\n✅ Claves generadas exitosamente!')
        listar_claves_gpg()
    else:
        print(f'\n❌ Error generando claves: {error}')

def listar_claves_gpg():
    """Lista las claves GPG disponibles"""
    print('\n=== CLAVES GPG DISPONIBLES ===')
    
    # Listar claves públicas
    print('\n--- Claves Públicas ---')
    comando = 'gpg --list-keys --keyid-format LONG'
    codigo, salida, error = ejecutar_gpg(comando)
    if salida:
        print(salida)
    else:
        print('No hay claves públicas.')
    
    # Listar claves privadas
    print('\n--- Claves Privadas ---')
    comando = 'gpg --list-secret-keys --keyid-format LONG'
    codigo, salida, error = ejecutar_gpg(comando)
    if salida:
        print(salida)
    else:
        print('No hay claves privadas.')

def exportar_clave_publica():
    """Exporta una clave pública en formato ASCII"""
    print('\n=== EXPORTAR CLAVE PÚBLICA ===')
    listar_claves_gpg()
    
    user_id = input('\nIngresa el email o ID de la clave a exportar: ').strip()
    if not user_id:
        print('❌ Debes proporcionar un email o ID.')
        return
    
    nombre_archivo = f'{user_id.replace("@", "_")}_publica.asc'
    comando = f'gpg --armor --export {user_id} > {nombre_archivo}'
    codigo, salida, error = ejecutar_gpg(comando)
    
    if codigo == 0:
        print(f'✅ Clave pública exportada a: {nombre_archivo}')
    else:
        print(f'❌ Error exportando clave: {error}')

def firmar_documento():
    """Firma un documento con GPG"""
    print('\n=== FIRMAR DOCUMENTO ===')
    
    archivo = input('Ingresa el nombre del archivo a firmar: ').strip()
    if not os.path.exists(archivo):
        print(f'❌ El archivo {archivo} no existe.')
        return
    
    listar_claves_gpg()
    user_id = input('\nIngresa tu email o ID para firmar: ').strip()
    
    # Crear firma detached
    comando = f'gpg --armor --detach-sign --local-user {user_id} {archivo}'
    codigo, salida, error = ejecutar_gpg(comando)
    
    if codigo == 0:
        print(f'✅ Archivo firmado! Firma guardada en: {archivo}.asc')
    else:
        print(f'❌ Error firmando archivo: {error}')

def verificar_firma():
    """Verifica la firma de un documento"""
    print('\n=== VERIFICAR FIRMA ===')
    
    archivo = input('Ingresa el nombre del archivo original: ').strip()
    if not os.path.exists(archivo):
        print(f'❌ El archivo {archivo} no existe.')
        return
    
    archivo_firma = f'{archivo}.asc'
    if not os.path.exists(archivo_firma):
        print(f'❌ El archivo de firma {archivo_firma} no existe.')
        return
    
    comando = f'gpg --verify {archivo_firma} {archivo}'
    codigo, salida, error = ejecutar_gpg(comando)
    
    print('\n--- Resultado de la verificación ---')
    if salida:
        print(salida)
    if error:
        print(error)
    
    if codigo == 0:
        print('✅ Firma VÁLIDA')
    else:
        print('❌ Firma INVÁLIDA o problemas en la verificación')

def cifrar_documento():
    """Cifra un documento para un destinatario"""
    print('\n=== CIFRAR DOCUMENTO ===')
    
    archivo = input('Ingresa el nombre del archivo a cifrar: ').strip()
    if not os.path.exists(archivo):
        print(f'❌ El archivo {archivo} no existe.')
        return
    
    listar_claves_gpg()
    destinatario = input('\nIngresa el email o ID del destinatario: ').strip()
    
    comando = f'gpg --armor --encrypt --recipient {destinatario} {archivo}'
    codigo, salida, error = ejecutar_gpg(comando)
    
    if codigo == 0:
        print(f'✅ Archivo cifrado! Guardado en: {archivo}.asc')
    else:
        print(f'❌ Error cifrando archivo: {error}')

def descifrar_documento():
    """Descifra un documento cifrado"""
    print('\n=== DESCIFRAR DOCUMENTO ===')
    
    archivo = input('Ingresa el nombre del archivo cifrado (.asc): ').strip()
    if not os.path.exists(archivo):
        print(f'❌ El archivo {archivo} no existe.')
        return
    
    comando = f'gpg --decrypt {archivo}'
    codigo, salida, error = ejecutar_gpg(comando)
    
    if codigo == 0:
        # Guardar el contenido descifrado
        nombre_descifrado = archivo.replace('.asc', '_descifrado')
        if archivo.endswith('.asc'):
            nombre_descifrado = archivo[:-4] + '_descifrado'
        
        with open(nombre_descifrado, 'w') as f:
            f.write(salida)
        print(f'✅ Archivo descifrado guardado en: {nombre_descifrado}')
    else:
        print(f'❌ Error descifrando archivo: {error}')

def firmar_hash_bloque():
    """Firma el hash de un bloque específico de la blockchain"""
    print('\n=== FIRMAR HASH DE BLOQUE ===')
    
    if 'cadena' not in globals() or globals()['cadena'] is None:
        print('❌ Primero debes crear la cadena (opción 1).')
        return
    
    try:
        indice = int(input(f'Ingresa el índice del bloque (0-{len(globals()["cadena"].bloques)-1}): '))
        if indice < 0 or indice >= len(globals()['cadena'].bloques):
            print('❌ Índice fuera de rango.')
            return
    except ValueError:
        print('❌ Debes ingresar un número válido.')
        return
    
    bloque = globals()['cadena'].bloques[indice]
    hash_hex = bloque.hash.hex()
    
    print(f'\n--- Información del Bloque {indice} ---')
    print(f'Hash: {hash_hex}')
    print(f'Nonce: {bloque.nonce}')
    print(f'Tiempo: {bloque.tiempo}')
    
    # Crear archivo temporal con el hash
    archivo_hash = f'bloque_{indice}_hash.txt'
    with open(archivo_hash, 'w') as f:
        f.write(hash_hex)
    
    # Firmar el archivo
    listar_claves_gpg()
    user_id = input('\nIngresa tu email o ID para firmar: ').strip()
    
    comando = f'gpg --armor --detach-sign --local-user {user_id} {archivo_hash}'
    codigo, salida, error = ejecutar_gpg(comando)
    
    if codigo == 0:
        print(f'✅ Hash del bloque {indice} firmado!')
        print(f'   Archivo hash: {archivo_hash}')
        print(f'   Firma: {archivo_hash}.asc')
    else:
        print(f'❌ Error firmando hash: {error}')

def menu_gpg():
    """Menú de operaciones GPG"""
    while True:
        print('\n=== MENÚ GPG ===')
        print('1. Generar par de claves')
        print('2. Listar claves')
        print('3. Exportar clave pública')
        print('4. Firmar documento')
        print('5. Verificar firma')
        print('6. Cifrar documento')
        print('7. Descifrar documento')
        print('8. Firmar hash de bloque')
        print('9. Volver al menú principal')
        
        try:
            opcion = int(input('\nElección: '))
        except ValueError:
            print('❌ Ingresa un número válido.')
            continue
        
        if opcion == 1:
            generar_claves_gpg()
        elif opcion == 2:
            listar_claves_gpg()
        elif opcion == 3:
            exportar_clave_publica()
        elif opcion == 4:
            firmar_documento()
        elif opcion == 5:
            verificar_firma()
        elif opcion == 6:
            cifrar_documento()
        elif opcion == 7:
            descifrar_documento()
        elif opcion == 8:
            firmar_hash_bloque()
        elif opcion == 9:
            break
        else:
            print('❌ Opción inválida.')

# ========== FIN FUNCIONES GPG ==========

# Función para limpiar la pantalla
def limpiar_pantalla():
    os.system('clear' if os.name == 'posix' else 'cls')

# Menú principal para el funcionamiento del programa...
def hacerMenu ():
    print('\n-----------------------------------')
    print('Simulación de Blockchain en Python')
    print('\n1. Crear la Cadena \n2. Adicionar un Bloque \n3. Verificar la Cadena \n4. Leer un Bloque \n5. Eliminar un Bloque \n6. Alterar un Bloque \n7. Simular Creación \n8. Ver Estadísticas \n9. Operaciones GPG \n10. Salir')
    try:
        return int(input('\nElección: '))
    except ValueError:
        return None


# Clase Bloque que contiene funciones muy importantes
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


    # Devuelve el hash convertido en Hexa para verlo
    def hashEnHex (self) -> str:
        return self.hash.hex() if self.hash else ''
    

    # Muestra los datos relevantes del bloque
    def darInfo (self):
        print(f'=== INFORMACIÓN DEL BLOQUE ===')
        print(f'Ceros Objetivo: {self.ceros}')
        print(f'Nonce Usado: {self.nonce:,}')
        print(f'Timestamp: {self.tiempo.isoformat()}')
        print(f'Hash en Hexa: {self.hashEnHex()}')
        print(f'Tiempo en Segundos para Minarlo: {self.segundos:.3f} segundos')
        print(f'Hash del Bloque Anterior: {self.hashPrevio.hex()}')
        print('=' * 35)


# Clase Cadena para todo lo relacionado con la formación de estas
class Cadena:
    def __init__(self, tiempoObjetivo = 15.0, dificultadInicial=20):
        self.bloques = []
        self.tiempoObjetivo = tiempoObjetivo
        self.minCeros = 20
        self.maxCeros = 40
        self.ajuste = 20
        self.dificultadObjetivo = dificultadInicial
        self.crear_genesis()


    # Crea el primer bloque de la cadena
    def crear_genesis (self):
        genesis = Bloque(b'\x00' * 32, self.dificultadObjetivo) # Es un bloque con un hash previo de puros ceros y objetivo de 20 ceros
        genesis.minar()
        print("\nBloque génesis minado:")
        genesis.darInfo()
        self.bloques.append(genesis)


    # Crea los siguientes bloques de la cadena distintos al de origen o génesis
    def agregar_bloque (self):
        previo = self.bloques[-1] # El último bloque de la lista de la cadena funciona como previo para el nuevo
        tiempoAnterior = previo.segundos # Se coge el tiempo del bloque anterior
        nuevaDificultad = self.ajustarDificultad(tiempoAnterior, previo.ceros) # Se ajustan los ceros objetivos

        bloque = Bloque(previo.hash, nuevaDificultad) # Se crea un nuevo bloque con los parámetros de arriba
        bloque.minar()
        print("\nNuevo bloque minado:")
        bloque.darInfo()
        self.bloques.append(bloque)


    # Se ajusta la cantidad de ceros que se necesitan en el hash
    def ajustarDificultad (self, tiempoBloqueAnterior, cerosActuales): 
        diferencia = self.tiempoObjetivo - tiempoBloqueAnterior
        paso = 1 # Se va a ir aumentando de a 1 cero o disminuyendo
        if tiempoBloqueAnterior < self.tiempoObjetivo: # Si el tiempo del bloque anterior fue menor a 15s
            nuevo = cerosActuales + paso
        elif tiempoBloqueAnterior > self.tiempoObjetivo: # Si el tiempo del bloque anterior fue mayor a 15s
            nuevo = cerosActuales - paso
        else:
            nuevo = cerosActuales
        return max(self.minCeros, min(self.maxCeros, nuevo)) # Sirve para asegurar que la dificultad no sea menor a la deseada ni mayor a la deseada


    # Función para obtener estadísticas de la cadena
    def obtenerEstadisticas(self):
        if not self.bloques:
            print("No hay bloques en la cadena.")
            return
            
        tiempos = [bloque.segundos for bloque in self.bloques]
        dificultades = [bloque.ceros for bloque in self.bloques]
        
        print(f"\n=== ESTADÍSTICAS DE LA CADENA ===")
        print(f"Número total de bloques: {len(self.bloques)}")
        print(f"Tiempo promedio de minado: {sum(tiempos)/len(tiempos):.2f} segundos")
        print(f"Tiempo más rápido: {min(tiempos):.2f} segundos")
        print(f"Tiempo más lento: {max(tiempos):.2f} segundos")
        print(f"Dificultad actual: {dificultades[-1]} ceros")
        print(f"Dificultad promedio: {sum(dificultades)/len(dificultades):.1f} ceros")
        print(f"Dificultad mínima alcanzada: {min(dificultades)} ceros")
        print(f"Dificultad máxima alcanzada: {max(dificultades)} ceros")
    

    # Revisa todos los bloques de la lista (cadena) y revisa que estén bien
    def verificarCadena(self):
        print(f"\n=== VERIFICANDO CADENA DE {len(self.bloques)} BLOQUES ===")
        resultados = []
        cadenaRota = False  # si ya se detectó una corrupción antes
        bloques_corruptos = 0

        for i, bloque in enumerate(self.bloques): # Itera todos los bloques y crea un contador del índice de cada uno
            mensajes = []
            
            # Verificar integridad del hash actual
            nonce = bloque.nonce
            hashViejo = bloque.hash
            hashNuevo = bloque.calcularHash(nonce)
            if hashNuevo != hashViejo:
                mensajes.append("Hash incorrecto")
                cadenaRota = True
                bloques_corruptos += 1
            
            # Verificar que el hash cumpla la dificultad
            if not bloque.hashValido(hashViejo):
                mensajes.append(f'No cumple el requisito de {bloque.ceros} ceros')
                cadenaRota = True
                if "Hash incorrecto" not in mensajes:
                    bloques_corruptos += 1

            # Verificar enlace con bloque previo
            if i > 0:
                hashPrevioEsperado = self.bloques[i-1].hash
                if bloque.hashPrevio != hashPrevioEsperado:
                    mensajes.append('Referencia al bloque previo incorrecta')
                    cadenaRota = True
                    if not any("Hash incorrecto" in m or "No cumple" in m for m in mensajes):
                        bloques_corruptos += 1
            elif bloque.hashPrevio != b'\x00' * 32:
                mensajes.append('Bloque génesis con hash previo incorrecto')
                cadenaRota = True
                if not any("Hash incorrecto" in m or "No cumple" in m for m in mensajes):
                    bloques_corruptos += 1

            # Contaminación en cascada si no tiene fallo directo
            if cadenaRota and not mensajes:
                mensajes.append("Posiblemente comprometido por corrupción previa")

            if not mensajes:
                resultados.append(f"Bloque {i}: ✅ OK")
            else:
                resultados.append(f"Bloque {i}: ❌ {' y '.join(mensajes)}")

        # Mostrar resumen
        if bloques_corruptos == 0:
            print("¡La cadena está íntegra!")
        else:
            print(f"Se encontraron {bloques_corruptos} bloque(s) con problemas")
        
        print(f"Bloques verificados: {len(self.bloques)}")
        print("Detalles:")
        return resultados


    # Simplemente da toda la información sobre un bloque en particular
    def leerBloque (self):
        try:
            indice = int(input('\nIngrese el índice del bloque que quiere conocer (recuerde que el génesis tiene índice 0): '))
            if not (0 <= indice < len(self.bloques)):
                print(f"Error: Índice {indice} fuera de rango. La cadena tiene {len(self.bloques)} bloques.")
                return
            print(f'Información del bloque con índice: {indice} \n')
            bloque = self.bloques[indice]
            bloque.darInfo()
        except ValueError:
            print("Error: Por favor ingrese un número válido.")


    # Sirve para borrar un bloque cualquiera (y los que le siguen) a partir de un índice
    def borrarBloque (self):
        try:
            indice = int(input('\nIngrese el índice del bloque que quiere eliminar (recuerde que el génesis tiene índice 0): '))
            if indice == 0:
                print("Error: No se puede eliminar el bloque génesis.")
                return
            if not (0 <= indice < len(self.bloques)):
                print(f"Error: Índice {indice} fuera de rango. La cadena tiene {len(self.bloques)} bloques.")
                return
            self.bloques = self.bloques[:indice]
            print(f'Bloque {indice} y todos los siguientes eliminados satisfactoriamente')
        except ValueError:
            print("Error: Por favor ingrese un número válido.")


    # Con esta se puede modificar un bloque, cambiando su nonce y timestamp para alterarlo
    def alterarBloque(self):
        try:
            indice = int(input('\nIngrese el índice del bloque que quiere alterar (recuerde que el génesis tiene índice 0): '))
            if not (0 <= indice < len(self.bloques)):
                print(f"Error: Índice {indice} fuera de rango. La cadena tiene {len(self.bloques)} bloques.")
                return
            
            bloque = self.bloques[indice]
            print(f"Bloque {indice} alterado. Hash anterior: {bloque.hashEnHex()[:16]}...")
            bloque.nonce += 1
            bloque.tiempo = datetime.datetime.now()
            print(f"Nuevo nonce: {bloque.nonce}, nuevo timestamp: {bloque.tiempo.isoformat()}")
        except ValueError:
            print("Error: Por favor ingrese un número válido.")


    # La puse para llamarla en alterar bloque, pero no es necesario
    def romper_encadenamiento(self, indice: int):
        if not (0 <= indice < len(self.bloques) - 1):
            raise IndexError("Índice fuera de rango o no hay siguiente bloque.")
        siguiente = self.bloques[indice + 1]
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
            # Leer un bloque
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
            try:
                cantidad = int(input('¿Cuántos bloques deseas crear? '))
                if cantidad <= 0:
                    print("Error: La cantidad debe ser un número positivo.")
                    continue
                if cadena is None:
                    cadena = Cadena(dificultadInicial=20)
                
                print(f"Creando {cantidad} bloques...")
                for i in range(cantidad):
                    print(f"Creando bloque {i+1}/{cantidad}")
                    cadena.agregar_bloque()
                    
            except ValueError:
                print("Error: Por favor ingrese un número válido.")

        elif respuesta == 8:
            # Ver estadísticas
            if cadena is None:
                print('Primero crea la cadena (opción 1)')
            else:
                cadena.obtenerEstadisticas()

        elif respuesta == 9:
            # Operaciones GPG
            menu_gpg()

        elif respuesta == 10:
            break

        else:
            print('Error, respuesta ingresada incorrecta, vuelva a intentarlo...')

    return 0

if __name__ == "__main__":
    main()
