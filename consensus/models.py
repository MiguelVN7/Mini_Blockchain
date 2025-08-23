"""
Modelos Pydantic para el protocolo de consenso.
Define las estructuras de datos para requests y responses de la API REST.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json


class RegisterReq(BaseModel):
    nodeId: str
    ip: str  # IPv4 como string, ej: "192.168.1.10"
    publicKey: str  # Clave pública en formato base64 o ASCII armored
    signature: str  # Firma del payload en base64


class RegisterRes(BaseModel):
    status: str
    assignedOrder: int


class FreezeReq(BaseModel):
    nodeId: str
    tokens: int
    signature: str


class FreezeRes(BaseModel):
    status: str
    frozenTokens: int


class SeedReq(BaseModel):
    leaderId: str
    encryptedSeed: str  # En realidad es "firma del seed" según aclaración
    turn: int
    signature: str


class SeedRes(BaseModel):
    status: str


class VoteReq(BaseModel):
    nodeId: str
    encryptedVote: str  # En realidad es "firma del voto" 
    signature: str


class VoteRes(BaseModel):
    status: str


class ConsensusResult(BaseModel):
    leader: str  # nodeId del líder seleccionado
    agreement: float  # Porcentaje de acuerdo (0.0 - 1.0)
    thresholdReached: bool  # Si se alcanzó 2/3 de consenso


class BlockData(BaseModel):
    index: int
    timestamp: str
    transactions: List[Dict[str, Any]]
    previousHash: str
    hash: Optional[str] = None  # Solo presente en submit


class BlockProposeReq(BaseModel):
    proposerId: str
    block: BlockData
    signature: str


class BlockProposeRes(BaseModel):
    status: str


class BlockSubmitReq(BaseModel):
    leaderId: str
    block: BlockData
    signature: str


class BlockSubmitRes(BaseModel):
    status: str


class Evidence(BaseModel):
    blockHash: str
    reason: str


class ReportReq(BaseModel):
    reporterId: str
    leaderId: str
    evidence: Evidence
    signature: str


class ReportRes(BaseModel):
    status: str


def canonical_json(model: BaseModel, exclude_signature: bool = True) -> bytes:
    """
    Genera el JSON canónico para firma digital.
    Excluye el campo signature del payload antes de firmar.
    """
    data = model.model_dump()
    
    if exclude_signature and 'signature' in data:
        del data['signature']
    
    # JSON canónico: ordenado, sin espacios
    json_str = json.dumps(data, separators=(',', ':'), sort_keys=True)
    return json_str.encode('utf-8')


def extract_seed_value(encrypted_seed_b64: str) -> int:
    """
    Extrae el valor del seed de la cadena base64.
    En una implementación real, esto descifraria/verificaría la firma.
    Para la demo, asumimos que los primeros 4 bytes son el seed en little-endian.
    """
    import base64
    try:
        # Decodificar base64 y tomar los primeros 4 bytes como seed
        decoded = base64.b64decode(encrypted_seed_b64)
        if len(decoded) >= 4:
            return int.from_bytes(decoded[:4], byteorder='little')
        else:
            # Si no hay suficientes bytes, generar seed desde el string
            return hash(encrypted_seed_b64) & 0xFFFFFFFF
    except Exception:
        # Fallback: usar hash del string
        return hash(encrypted_seed_b64) & 0xFFFFFFFF


def extract_vote_value(encrypted_vote_b64: str) -> int:
    """
    Extrae el índice del voto de la cadena base64.
    Similar a extract_seed_value, pero para votos.
    """
    import base64
    try:
        decoded = base64.b64decode(encrypted_vote_b64)
        if len(decoded) >= 4:
            return int.from_bytes(decoded[:4], byteorder='little')
        else:
            return hash(encrypted_vote_b64) & 0xFFFF  # Limitar a rango razonable
    except Exception:
        return hash(encrypted_vote_b64) & 0xFFFF
