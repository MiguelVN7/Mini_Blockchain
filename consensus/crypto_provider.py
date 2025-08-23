"""
Proveedor de servicios criptográficos.
Abstracción para firmas digitales y verificación.
"""

import subprocess
import tempfile
import os
import base64
from abc import ABC, abstractmethod
from typing import Optional


class CryptoProvider(ABC):
    """Interfaz abstracta para proveedores criptográficos."""
    
    @abstractmethod
    def sign(self, nodeId: str, payload: bytes) -> bytes:
        """Firma un payload con la clave privada del nodo."""
        pass
    
    @abstractmethod
    def verify(self, public_key: str, payload: bytes, signature: bytes) -> bool:
        """Verifica una firma con la clave pública."""
        pass


class GPGCryptoProvider(CryptoProvider):
    """
    Proveedor criptográfico usando GPG.
    Reutiliza las funciones GPG del sistema.
    """
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="consensus_gpg_")
    
    def _run_gpg_command(self, command: str, input_data: Optional[bytes] = None) -> tuple[int, str, str]:
        """Ejecuta un comando GPG de forma segura."""
        try:
            process = subprocess.run(
                command,
                shell=True,
                input=input_data,
                capture_output=True,
                text=False if input_data else True,
                timeout=30
            )
            return process.returncode, process.stdout, process.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout ejecutando comando GPG"
        except Exception as e:
            return -1, "", str(e)
    
    def sign(self, nodeId: str, payload: bytes) -> bytes:
        """
        Firma un payload usando GPG.
        Asume que el nodeId corresponde al email en GPG.
        """
        # Crear archivo temporal con el payload
        temp_file = os.path.join(self.temp_dir, f"payload_{os.getpid()}.bin")
        
        try:
            with open(temp_file, 'wb') as f:
                f.write(payload)
            
            # Firmar con GPG (firma detached en ASCII armor)
            command = f'gpg --armor --detach-sign --local-user "{nodeId}" "{temp_file}"'
            code, stdout, stderr = self._run_gpg_command(command)
            
            if code == 0:
                # Leer el archivo de firma generado
                sig_file = temp_file + ".asc"
                if os.path.exists(sig_file):
                    with open(sig_file, 'r') as f:
                        signature_ascii = f.read()
                    
                    # Codificar en base64 para transporte
                    return base64.b64encode(signature_ascii.encode('utf-8'))
                else:
                    raise Exception("Archivo de firma no generado")
            else:
                raise Exception(f"Error firmando: {stderr}")
        
        finally:
            # Limpiar archivos temporales
            for ext in ['', '.asc']:
                temp_path = temp_file + ext
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
    
    def verify(self, public_key_or_nodeId: str, payload: bytes, signature: bytes) -> bool:
        """
        Verifica una firma usando GPG.
        public_key_or_nodeId puede ser el nodeId/email o la clave pública.
        """
        temp_payload = os.path.join(self.temp_dir, f"verify_payload_{os.getpid()}.bin")
        temp_sig = os.path.join(self.temp_dir, f"verify_sig_{os.getpid()}.asc")
        
        try:
            # Decodificar la firma base64
            signature_ascii = base64.b64decode(signature).decode('utf-8')
            
            # Escribir archivos temporales
            with open(temp_payload, 'wb') as f:
                f.write(payload)
            
            with open(temp_sig, 'w') as f:
                f.write(signature_ascii)
            
            # Verificar con GPG
            command = f'gpg --verify "{temp_sig}" "{temp_payload}"'
            code, stdout, stderr = self._run_gpg_command(command)
            
            # GPG retorna 0 si la verificación es exitosa
            return code == 0
        
        except Exception as e:
            print(f"Error verificando firma: {e}")
            return False
        
        finally:
            # Limpiar archivos temporales
            for temp_file in [temp_payload, temp_sig]:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    def __del__(self):
        """Limpia el directorio temporal al destruir el objeto."""
        try:
            import shutil
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass


class MockCryptoProvider(CryptoProvider):
    """
    Proveedor criptográfico mock para testing.
    NO usar en producción - solo para pruebas.
    """
    
    def sign(self, nodeId: str, payload: bytes) -> bytes:
        """Genera una firma mock determinística."""
        import hashlib
        
        # Crear firma mock usando hash del payload + nodeId
        signature_data = f"{nodeId}:{payload.hex()}"
        signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
        
        # Crear formato similar a GPG
        mock_signature = f"""-----BEGIN PGP SIGNATURE-----

{signature_hash[:64]}
{signature_hash[64:]}
-----END PGP SIGNATURE-----"""
        
        return base64.b64encode(mock_signature.encode('utf-8'))
    
    def verify(self, public_key_or_nodeId: str, payload: bytes, signature: bytes) -> bool:
        """Verifica una firma mock."""
        try:
            # Recrear la firma esperada
            expected_signature = self.sign(public_key_or_nodeId, payload)
            return signature == expected_signature
        except:
            return False


# Proveedor global - usar MockCryptoProvider por defecto para facilitar pruebas
crypto_provider = MockCryptoProvider()


def get_provider() -> CryptoProvider:
    """Retorna el proveedor criptográfico activo."""
    return crypto_provider


def set_mock_provider():
    """Cambia al proveedor mock para testing."""
    global crypto_provider
    crypto_provider = MockCryptoProvider()


def set_gpg_provider():
    """Cambia al proveedor GPG real."""
    global crypto_provider
    crypto_provider = GPGCryptoProvider()
