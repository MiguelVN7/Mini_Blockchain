"""
API REST para el protocolo de consenso distribuido.
Implementa todos los endpoints especificados en el documento.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import base64
import json
from typing import Dict, Any

from .models import (
    RegisterReq, RegisterRes, FreezeReq, FreezeRes,
    SeedReq, SeedRes, VoteReq, VoteRes, ConsensusResult,
    BlockProposeReq, BlockProposeRes, BlockSubmitReq, BlockSubmitRes,
    ReportReq, ReportRes, canonical_json
)
from .engine import engine


app = FastAPI(
    title="Protocolo de Consenso Distribuido",
    description="API REST para consenso blockchain con rotación de liderazgo",
    version="1.0.0"
)

# Configurar CORS para permitir requests desde cualquier origen (desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
async def root():
    """Endpoint raíz con información del protocolo."""
    return {
        "protocol": "Consenso Distribuido Blockchain",
        "version": "1.0.0",
        "status": "active",
        "endpoints": [
            "/network/register",
            "/tokens/freeze", 
            "/leader/random-seed",
            "/consensus/vote",
            "/consensus/result",
            "/block/propose",
            "/block/submit",
            "/leader/report"
        ]
    }


@app.get("/status", tags=["General"])
async def status():
    """Retorna el estado actual del consenso."""
    return engine.get_current_state()


@app.post("/network/register", response_model=RegisterRes, tags=["Network"])
async def register_node(req: RegisterReq):
    """
    Registra un nuevo nodo en la red.
    
    El nodo debe proporcionar:
    - nodeId único
    - IP válida (usada para ordenamiento de liderazgo)
    - Clave pública para verificación de firmas
    - Firma del payload para autenticación
    """
    try:
        # Generar payload canónico para verificación
        payload = canonical_json(req, exclude_signature=True)
        signature = base64.b64decode(req.signature)
        
        # Registrar nodo (la verificación de firma se hace internamente si es necesario)
        assigned_order = engine.register_node(req.nodeId, req.ip, req.publicKey)
        
        return RegisterRes(
            status="registered",
            assignedOrder=assigned_order
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error de validación de firma: {str(e)}"
        )


@app.post("/tokens/freeze", response_model=FreezeRes, tags=["Tokens"])
async def freeze_tokens(req: FreezeReq):
    """
    Congela tokens de un nodo para participar en el consenso.
    
    Los tokens congelados determinan el peso del voto en la selección
    ponderada del líder. La firma debe verificarse con la clave pública
    del nodo registrado.
    """
    try:
        payload = canonical_json(req, exclude_signature=True)
        signature = base64.b64decode(req.signature)
        
        success = engine.freeze_tokens(req.nodeId, req.tokens, signature, payload)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Error congelando tokens: nodo no registrado o firma inválida"
            )
        
        return FreezeRes(
            status="ok",
            frozenTokens=req.tokens
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error decodificando signature: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )


@app.post("/leader/random-seed", response_model=SeedRes, tags=["Leadership"])
async def submit_random_seed(req: SeedReq):
    """
    El líder del turno envía el seed aleatorio.
    
    El seed se genera según especificación:
    - 2 bytes superiores: número del turno (0-65535 con rollover)
    - 2 bytes inferiores: aleatorio generado por el líder
    
    Solo el líder designado para el turno puede enviar el seed.
    """
    try:
        payload = canonical_json(req, exclude_signature=True)
        signature = base64.b64decode(req.signature)
        
        success = engine.set_seed(req.leaderId, req.encryptedSeed, req.turn, signature, payload)
        
        if not success:
            raise HTTPException(
                status_code=403,
                detail="No autorizado: no eres el líder del turno o firma inválida"
            )
        
        return SeedRes(status="received")
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error decodificando signature: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )


@app.post("/consensus/vote", response_model=VoteRes, tags=["Consensus"])
async def submit_vote(req: VoteReq):
    """
    Envía el voto de un nodo.
    
    El voto se calcula usando:
    1. El seed proporcionado por el líder
    2. Selección ponderada basada en tokens congelados
    3. Orden determinista de nodos (por IP)
    
    El resultado es el índice del nodo seleccionado.
    """
    try:
        payload = canonical_json(req, exclude_signature=True)
        signature = base64.b64decode(req.signature)
        
        success = engine.record_vote(req.nodeId, req.encryptedVote, signature, payload)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Error registrando voto: nodo no registrado, firma inválida, o no hay seed"
            )
        
        return VoteRes(status="recorded")
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error decodificando signature: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )


@app.get("/consensus/result", response_model=ConsensusResult, tags=["Consensus"])
async def get_consensus_result():
    """
    Obtiene el resultado del consenso actual.
    
    Retorna:
    - leader: nodeId del nodo más votado
    - agreement: porcentaje de votos que recibió el ganador (0.0-1.0)
    - thresholdReached: true si se alcanzó el umbral 2/3
    
    Solo cuando thresholdReached=true, el líder puede proceder a validar bloques.
    """
    try:
        leader, agreement, threshold_reached = engine.tally_votes()
        
        return ConsensusResult(
            leader=leader or "",
            agreement=agreement,
            thresholdReached=threshold_reached
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculando consenso: {str(e)}"
        )


@app.post("/block/propose", response_model=BlockProposeRes, tags=["Blockchain"])
async def propose_block(req: BlockProposeReq):
    """
    Propone un bloque para validación.
    
    Cualquier nodo puede proponer un bloque, pero solo el líder
    seleccionado por consenso podrá enviarlo posteriormente.
    """
    try:
        payload = canonical_json(req, exclude_signature=True)
        signature = base64.b64decode(req.signature)
        
        success = engine.propose_block(
            req.proposerId,
            req.block.model_dump(),
            signature,
            payload
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Error proponiendo bloque: nodo no registrado o firma inválida"
            )
        
        return BlockProposeRes(status="pending consensus")
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error decodificando signature: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )


@app.post("/block/submit", response_model=BlockSubmitRes, tags=["Blockchain"])
async def submit_block(req: BlockSubmitReq):
    """
    Envía un bloque validado por el líder.
    
    Solo el líder que ganó el consenso (2/3 de los votos) puede
    enviar bloques válidos. El bloque debe incluir el hash calculado
    y estar firmado por el líder.
    """
    try:
        payload = canonical_json(req, exclude_signature=True)
        signature = base64.b64decode(req.signature)
        
        success = engine.submit_block(
            req.leaderId,
            req.block.model_dump(),
            signature,
            payload
        )
        
        if not success:
            raise HTTPException(
                status_code=403,
                detail="No autorizado: no eres el líder seleccionado o no se alcanzó consenso"
            )
        
        return BlockSubmitRes(status="broadcasted")
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error decodificando signature: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )


@app.post("/leader/report", response_model=ReportRes, tags=["Leadership"])
async def report_leader(req: ReportReq):
    """
    Reporta a un líder por comportamiento fraudulento.
    
    Si 2/3 o más nodos reportan al mismo líder, será expulsado
    de la red (marcado como inactivo).
    
    Evidencias comunes:
    - invalid signature: firma de bloque inválida
    - wrong hash: hash de bloque incorrecto
    - malformed block: estructura de bloque inválida
    """
    try:
        payload = canonical_json(req, exclude_signature=True)
        signature = base64.b64decode(req.signature)
        
        success = engine.report_leader(
            req.reporterId,
            req.leaderId,
            req.evidence.model_dump(),
            signature,
            payload
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Error reportando líder: reporter no registrado o firma inválida"
            )
        
        return ReportRes(status="under review")
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error decodificando signature: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )


# Endpoint adicional para debugging (no en especificación)
@app.get("/debug/nodes", tags=["Debug"])
async def debug_nodes():
    """Lista todos los nodos registrados (solo para debugging)."""
    nodes_data = []
    for nodeId, node in engine.state.registry.nodes.items():
        nodes_data.append({
            "nodeId": nodeId,
            "ip": node.ip,
            "assignedOrder": node.assignedOrder,
            "active": node.active,
            "frozenTokens": engine.state.tokens.get_tokens(nodeId)
        })
    
    return {
        "nodes": nodes_data,
        "total": len(nodes_data),
        "active": len([n for n in nodes_data if n["active"]])
    }


@app.get("/debug/votes", tags=["Debug"])
async def debug_votes():
    """Lista todos los votos del turno actual (solo para debugging)."""
    votes = engine.state.votes.get_votes()
    votes_data = []
    
    for vote in votes:
        votes_data.append({
            "nodeId": vote.nodeId,
            "selectedIndex": vote.selectedIndex,
            "encryptedVote": vote.encryptedVote[:20] + "..." if len(vote.encryptedVote) > 20 else vote.encryptedVote
        })
    
    return {
        "votes": votes_data,
        "count": len(votes_data),
        "turn": engine.state.turn_state.current_turn,
        "seed": engine.state.turn_state.current_seed
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
