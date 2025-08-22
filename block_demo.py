#!/usr/bin/env python3
"""
Demostración de firma de bloques estilo blockchain usando PGP.
Script educativo que muestra cómo firmar el hash de un bloque.
"""

import json
import time
from pgp_utils import generate_rsa_keypair, load_key_from_asc, sign_bytes_detached, verify_bytes_detached, sha256_bytes


def main():
    """
    Demuestra el proceso de firma de un bloque tipo blockchain:
    1. Genera claves efímeras para Alice
    2. Crea un header de bloque
    3. Serializa a JSON canónico
    4. Calcula hash SHA-256
    5. Firma el hash con clave privada
    6. Verifica la firma con clave pública
    """
    print("=== Demostración de Firma de Bloques ===\n")
    
    # 1. Generar claves efímeras para Miguel
    print("1. Generando claves efímeras para Miguel...")
    try:
        private_asc, public_asc = generate_rsa_keypair(
            name="Miguel",
            email="miguevillegas1@gmail.com",
            passphrase="miguel2405"  # En un caso real, esto sería más seguro
        )
        print("   ✓ Claves generadas correctamente")
    except Exception as e:
        print(f"   ✗ Error generando claves: {e}")
        return
    
    # 2. Crear header del bloque
    print("\n2. Creando header del bloque...")
    header = {
        "index": 1,
        "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000",
        "merkle_root": "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b",
        "timestamp": int(time.time()),
        "nonce": 42
    }
    
    print(f"   Header creado:")
    for key, value in header.items():
        print(f"     {key}: {value}")
    
    # 3. Serializar a JSON canónico
    print("\n3. Serializando a JSON canónico...")
    json_bytes = json.dumps(header, sort_keys=True, separators=(',', ':')).encode('utf-8')
    json_str = json_bytes.decode('utf-8')
    print(f"   JSON canónico: {json_str}")
    print(f"   Tamaño: {len(json_bytes)} bytes")
    
    # 4. Calcular hash SHA-256
    print("\n4. Calculando hash SHA-256 del JSON...")
    block_hash = sha256_bytes(json_bytes)
    print(f"   Hash del bloque: {block_hash}")
    
    # 5. Firmar el hash con clave privada
    print("\n5. Firmando el hash del bloque...")
    try:
        private_key = load_key_from_asc(private_asc)
        hash_bytes = bytes.fromhex(block_hash)  # Convertir hash hex a bytes
        
        signature_asc = sign_bytes_detached(
            data=hash_bytes,
            private_key=private_key,
            passphrase="miguel2405",
            hash_name="SHA256"
        )
        
        print("   ✓ Firma creada correctamente")
        print(f"   Firma (primeros 120 chars): {signature_asc[:120]}...")
        
    except Exception as e:
        print(f"   ✗ Error firmando hash: {e}")
        return
    
    # 6. Verificar la firma con clave pública
    print("\n6. Verificando firma con clave pública...")
    try:
        public_key = load_key_from_asc(public_asc)
        
        is_valid = verify_bytes_detached(
            data=hash_bytes,
            signature_asc=signature_asc,
            public_key=public_key
        )
        
        if is_valid:
            print("   ✓ Firma VÁLIDA - El bloque fue firmado correctamente por Alice")
        else:
            print("   ✗ Firma INVÁLIDA - El bloque NO es auténtico")
            
    except Exception as e:
        print(f"   ✗ Error verificando firma: {e}")
        return
    
    # Resumen final
    print(f"\n=== RESUMEN ===")
    print(f"Bloque #{header['index']}")
    print(f"Hash: {block_hash}")
    print(f"Firmado por: Alice (alice@blockchain.local)")
    print(f"Firma válida: {'SÍ' if is_valid else 'NO'}")
    print(f"Algoritmo: RSA + SHA-256")
    
    print(f"\n💡 Nota educativa:")
    print(f"En blockchain reales se usan algoritmos como ECDSA o EdDSA,")
    print(f"pero PGP nos ayuda a entender los conceptos fundamentales:")
    print(f"- Hash del contenido")
    print(f"- Firma digital del hash")
    print(f"- Verificación con clave pública")


if __name__ == "__main__":
    main()
