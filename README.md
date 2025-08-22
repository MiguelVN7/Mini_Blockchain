# Mini-Módulo PGP para Proyecto Universitario

Este es un proyecto educativo que implementa operaciones básicas de PGP usando la librería `pgpy`.

## Instalación

1. Crear entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Generar claves PGP
```bash
python cli.py gen-key --name "Alice" --email "alice@example.com" --passphrase "mi_password" --outdir ./keys
```

### Firmar archivo
```bash
python cli.py sign --in archivo.txt --key keys/private.asc --passphrase "mi_password" --out archivo.txt.sig
```

### Verificar firma
```bash
python cli.py verify --in archivo.txt --sig archivo.txt.sig --pub keys/public.asc
```

### Cifrar archivo
```bash
python cli.py encrypt --in secreto.txt --to keys/public.asc --out secreto.txt.asc
```

### Descifrar archivo
```bash
python cli.py decrypt --in secreto.txt.asc --key keys/private.asc --passphrase "mi_password" --out secreto.txt.dec
```

### Calcular hash SHA-256
```bash
python cli.py hash --in archivo.txt
```

### Demostración de firma de bloques
```bash
python block_demo.py
```

## Estructura del proyecto

- `requirements.txt`: Dependencias del proyecto
- `pgp_utils.py`: Funciones utilitarias para operaciones PGP
- `block_demo.py`: Demostración de firma de bloques tipo blockchain
- `cli.py`: Interfaz de línea de comandos
- `README.md`: Este archivo

## Nota Académica

Este proyecto usa PGP con fines educativos. En blockchain reales se usan esquemas de firma diferentes (ECDSA, EdDSA), pero PGP nos permite entender los conceptos básicos de criptografía asimétrica, firmas digitales y cifrado.

## Archivos generados

Al usar el CLI, se generarán archivos como:
- `keys/private.asc`: Clave privada en formato ASCII armor
- `keys/public.asc`: Clave pública en formato ASCII armor
- `*.sig`: Archivos de firma detached
- `*.asc`: Archivos cifrados
- `*.dec`: Archivos descifrados
