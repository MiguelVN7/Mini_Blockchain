#!/usr/bin/env python3
"""
CLI simple para operaciones PGP básicas.
Interfaz de línea de comandos para generar claves, firmar, cifrar y verificar.
"""

import argparse
import os
import sys
from pgp_utils import (
    generate_rsa_keypair, load_key_from_asc, encrypt_bytes, decrypt_to_bytes,
    sign_bytes_detached, verify_bytes_detached, sha256_file,
    read_bytes, write_text, read_text
)


def cmd_gen_key(args):
    """Genera un par de claves PGP y las guarda en archivos."""
    print(f"Generando claves para {args.name} <{args.email}>...")
    
    try:
        # Crear directorio si no existe
        os.makedirs(args.outdir, exist_ok=True)
        
        # Generar claves
        private_asc, public_asc = generate_rsa_keypair(
            name=args.name,
            email=args.email,
            passphrase=args.passphrase
        )
        
        # Guardar claves
        private_path = os.path.join(args.outdir, "private.asc")
        public_path = os.path.join(args.outdir, "public.asc")
        
        write_text(private_path, private_asc)
        write_text(public_path, public_asc)
        
        print(f"✓ Clave privada guardada en: {private_path}")
        print(f"✓ Clave pública guardada en: {public_path}")
        
        if args.passphrase:
            print("⚠️  Recuerda la contraseña para usar la clave privada")
        
    except Exception as e:
        print(f"✗ Error generando claves: {e}")
        sys.exit(1)


def cmd_sign(args):
    """Firma un archivo creando una firma detached."""
    print(f"Firmando archivo {args.input}...")
    
    try:
        # Leer archivo y clave privada
        data = read_bytes(args.input)
        private_asc = read_text(args.key)
        private_key = load_key_from_asc(private_asc)
        
        # Firmar
        signature_asc = sign_bytes_detached(
            data=data,
            private_key=private_key,
            passphrase=args.passphrase
        )
        
        # Guardar firma
        write_text(args.out, signature_asc)
        
        print(f"✓ Firma guardada en: {args.out}")
        print(f"📄 Archivo original: {args.input}")
        print(f"🔐 Firma detached: {args.out}")
        
    except Exception as e:
        print(f"✗ Error firmando archivo: {e}")
        sys.exit(1)


def cmd_verify(args):
    """Verifica la firma detached de un archivo."""
    print(f"Verificando firma de {args.input}...")
    
    try:
        # Leer archivo, firma y clave pública
        data = read_bytes(args.input)
        signature_asc = read_text(args.sig)
        public_asc = read_text(args.pub)
        public_key = load_key_from_asc(public_asc)
        
        # Verificar
        is_valid = verify_bytes_detached(
            data=data,
            signature_asc=signature_asc,
            public_key=public_key
        )
        
        if is_valid:
            print("✓ FIRMA VÁLIDA - El archivo es auténtico")
            sys.exit(0)
        else:
            print("✗ FIRMA INVÁLIDA - El archivo ha sido modificado o la firma no coincide")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ Error verificando firma: {e}")
        sys.exit(1)


def cmd_encrypt(args):
    """Cifra un archivo para un destinatario."""
    print(f"Cifrando archivo {args.input}...")
    
    try:
        # Leer archivo y clave pública del destinatario
        data = read_bytes(args.input)
        public_asc = read_text(args.to)
        public_key = load_key_from_asc(public_asc)
        
        # Cifrar
        encrypted_asc = encrypt_bytes(data, [public_key])
        
        # Guardar
        write_text(args.out, encrypted_asc)
        
        print(f"✓ Archivo cifrado guardado en: {args.out}")
        print(f"🔒 Solo el propietario de la clave privada puede descifrarlo")
        
    except Exception as e:
        print(f"✗ Error cifrando archivo: {e}")
        sys.exit(1)


def cmd_decrypt(args):
    """Descifra un archivo usando una clave privada."""
    print(f"Descifrando archivo {args.input}...")
    
    try:
        # Leer archivo cifrado y clave privada
        cipher_asc = read_text(args.input)
        private_asc = read_text(args.key)
        private_key = load_key_from_asc(private_asc)
        
        # Descifrar
        decrypted_data = decrypt_to_bytes(
            cipher_asc=cipher_asc,
            private_key=private_key,
            passphrase=args.passphrase
        )
        
        # Guardar
        with open(args.out, 'wb') as f:
            f.write(decrypted_data)
        
        print(f"✓ Archivo descifrado guardado en: {args.out}")
        
    except Exception as e:
        print(f"✗ Error descifrando archivo: {e}")
        sys.exit(1)


def cmd_hash(args):
    """Calcula el hash SHA-256 de un archivo."""
    print(f"Calculando hash SHA-256 de {args.input}...")
    
    try:
        file_hash = sha256_file(args.input)
        print(f"SHA-256: {file_hash}")
        print(f"Archivo: {args.input}")
        
    except Exception as e:
        print(f"✗ Error calculando hash: {e}")
        sys.exit(1)


def main():
    """Función principal del CLI."""
    parser = argparse.ArgumentParser(
        description="CLI simple para operaciones PGP básicas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Generar claves
  %(prog)s gen-key --name "Alice" --email "alice@example.com" --outdir ./keys

  # Firmar archivo
  %(prog)s sign --in documento.pdf --key keys/private.asc --out documento.pdf.sig

  # Verificar firma
  %(prog)s verify --in documento.pdf --sig documento.pdf.sig --pub keys/public.asc

  # Cifrar archivo
  %(prog)s encrypt --in secreto.txt --to keys/public.asc --out secreto.txt.asc

  # Descifrar archivo
  %(prog)s decrypt --in secreto.txt.asc --key keys/private.asc --out secreto.txt.dec

  # Calcular hash
  %(prog)s hash --in archivo.bin
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando gen-key
    parser_genkey = subparsers.add_parser('gen-key', help='Generar par de claves PGP')
    parser_genkey.add_argument('--name', required=True, help='Nombre del propietario')
    parser_genkey.add_argument('--email', required=True, help='Email del propietario')
    parser_genkey.add_argument('--passphrase', help='Contraseña para proteger la clave privada')
    parser_genkey.add_argument('--outdir', required=True, help='Directorio donde guardar las claves')
    parser_genkey.set_defaults(func=cmd_gen_key)
    
    # Comando sign
    parser_sign = subparsers.add_parser('sign', help='Firmar archivo (firma detached)')
    parser_sign.add_argument('--in', dest='input', required=True, help='Archivo a firmar')
    parser_sign.add_argument('--key', required=True, help='Archivo de clave privada (.asc)')
    parser_sign.add_argument('--passphrase', help='Contraseña de la clave privada')
    parser_sign.add_argument('--out', required=True, help='Archivo de salida para la firma')
    parser_sign.set_defaults(func=cmd_sign)
    
    # Comando verify
    parser_verify = subparsers.add_parser('verify', help='Verificar firma detached')
    parser_verify.add_argument('--in', dest='input', required=True, help='Archivo original')
    parser_verify.add_argument('--sig', required=True, help='Archivo de firma (.sig)')
    parser_verify.add_argument('--pub', required=True, help='Archivo de clave pública (.asc)')
    parser_verify.set_defaults(func=cmd_verify)
    
    # Comando encrypt
    parser_encrypt = subparsers.add_parser('encrypt', help='Cifrar archivo')
    parser_encrypt.add_argument('--in', dest='input', required=True, help='Archivo a cifrar')
    parser_encrypt.add_argument('--to', required=True, help='Clave pública del destinatario (.asc)')
    parser_encrypt.add_argument('--out', required=True, help='Archivo cifrado de salida')
    parser_encrypt.set_defaults(func=cmd_encrypt)
    
    # Comando decrypt
    parser_decrypt = subparsers.add_parser('decrypt', help='Descifrar archivo')
    parser_decrypt.add_argument('--in', dest='input', required=True, help='Archivo cifrado')
    parser_decrypt.add_argument('--key', required=True, help='Archivo de clave privada (.asc)')
    parser_decrypt.add_argument('--passphrase', help='Contraseña de la clave privada')
    parser_decrypt.add_argument('--out', required=True, help='Archivo descifrado de salida')
    parser_decrypt.set_defaults(func=cmd_decrypt)
    
    # Comando hash
    parser_hash = subparsers.add_parser('hash', help='Calcular hash SHA-256 de archivo')
    parser_hash.add_argument('--in', dest='input', required=True, help='Archivo a hashear')
    parser_hash.set_defaults(func=cmd_hash)
    
    # Parsear argumentos
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Ejecutar comando
    args.func(args)


if __name__ == "__main__":
    main()
