"""
Gestión del estado del protocolo de consenso.
Maneja el registro de nodos, tokens, turnos y votos.
"""

import json
import os
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
import socket
import struct


@dataclass
class Node:
    nodeId: str
    ip: str
    publicKey: str
    assignedOrder: int
    active: bool = True
    
    def ip_as_int(self) -> int:
        """Convierte IP string a entero de 32 bits para ordenamiento."""
        try:
            return struct.unpack("!I", socket.inet_aton(self.ip))[0]
        except socket.error:
            # Fallback: usar hash del IP si no es válida
            return hash(self.ip) & 0xFFFFFFFF


@dataclass
class TurnState:
    current_turn: int = 0  # 0-65535, luego rollover
    current_seed: Optional[int] = None
    seed_leader: Optional[str] = None
    
    def next_turn(self):
        """Avanza al siguiente turno con rollover."""
        self.current_turn = (self.current_turn + 1) % 65536
        self.current_seed = None
        self.seed_leader = None


@dataclass 
class Vote:
    nodeId: str
    encryptedVote: str  # Firma del voto
    selectedIndex: int  # Índice del nodo seleccionado
    

class NodeRegistry:
    """Registro de nodos activos en la red."""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self._next_order = 0
    
    def register_node(self, nodeId: str, ip: str, publicKey: str) -> int:
        """Registra un nuevo nodo y retorna su orden asignado."""
        if nodeId in self.nodes:
            return self.nodes[nodeId].assignedOrder
        
        node = Node(
            nodeId=nodeId,
            ip=ip,
            publicKey=publicKey,
            assignedOrder=self._next_order
        )
        
        self.nodes[nodeId] = node
        self._next_order += 1
        
        # Re-ordenar nodos por IP (mayor a menor)
        self._reorder_nodes()
        
        return node.assignedOrder
    
    def _reorder_nodes(self):
        """Reordena los nodos por IP de mayor a menor."""
        active_nodes = [n for n in self.nodes.values() if n.active]
        # Ordenar por IP como entero, mayor a menor
        active_nodes.sort(key=lambda n: n.ip_as_int(), reverse=True)
        
        # Reasignar órdenes
        for i, node in enumerate(active_nodes):
            node.assignedOrder = i
    
    def get_leader_for_turn(self, turn: int) -> Optional[str]:
        """Retorna el nodeId del líder para el turno dado."""
        active_nodes = [n for n in self.nodes.values() if n.active]
        if not active_nodes:
            return None
        
        # Ordenar por assignedOrder
        active_nodes.sort(key=lambda n: n.assignedOrder)
        leader_index = turn % len(active_nodes)
        return active_nodes[leader_index].nodeId
    
    def get_nodes_ordered(self) -> List[Node]:
        """Retorna lista de nodos activos ordenados por assignedOrder."""
        active_nodes = [n for n in self.nodes.values() if n.active]
        return sorted(active_nodes, key=lambda n: n.assignedOrder)
    
    def ban_node(self, nodeId: str):
        """Marca un nodo como inactivo (baneado)."""
        if nodeId in self.nodes:
            self.nodes[nodeId].active = False
            self._reorder_nodes()


class TokenLedger:
    """Gestión de tokens congelados por nodo."""
    
    def __init__(self):
        self.frozen_tokens: Dict[str, int] = {}
    
    def freeze_tokens(self, nodeId: str, tokens: int):
        """Congela tokens para un nodo."""
        self.frozen_tokens[nodeId] = tokens
    
    def get_tokens(self, nodeId: str) -> int:
        """Retorna los tokens congelados de un nodo."""
        return self.frozen_tokens.get(nodeId, 0)
    
    def get_all_tokens(self) -> Dict[str, int]:
        """Retorna todos los tokens congelados."""
        return self.frozen_tokens.copy()


class VotesStore:
    """Almacena y gestiona los votos del turno actual."""
    
    def __init__(self):
        self.votes: Dict[str, Vote] = {}  # nodeId -> Vote
        self.current_turn: int = 0
    
    def record_vote(self, nodeId: str, encryptedVote: str, selectedIndex: int):
        """Registra un voto de un nodo."""
        self.votes[nodeId] = Vote(
            nodeId=nodeId,
            encryptedVote=encryptedVote,
            selectedIndex=selectedIndex
        )
    
    def get_votes(self) -> List[Vote]:
        """Retorna todos los votos del turno actual."""
        return list(self.votes.values())
    
    def clear_votes(self):
        """Limpia los votos para el siguiente turno."""
        self.votes.clear()
    
    def count_votes_for_node(self, nodeId: str) -> int:
        """Cuenta cuántos votos recibió un nodo específico."""
        count = 0
        for vote in self.votes.values():
            # Aquí necesitamos mapear selectedIndex a nodeId
            # Esto se resuelve en engine.py con el orden de nodos
            pass
        return count


class AccusationsStore:
    """Gestiona las acusaciones contra líderes."""
    
    def __init__(self):
        self.accusations: Dict[str, List[str]] = {}  # leaderId -> [reporterIds]
    
    def add_accusation(self, leaderId: str, reporterId: str, evidence: dict):
        """Añade una acusación contra un líder."""
        if leaderId not in self.accusations:
            self.accusations[leaderId] = []
        
        if reporterId not in self.accusations[leaderId]:
            self.accusations[leaderId].append(reporterId)
    
    def get_accusation_count(self, leaderId: str) -> int:
        """Retorna el número de acusaciones contra un líder."""
        return len(self.accusations.get(leaderId, []))
    
    def clear_accusations(self, leaderId: str):
        """Limpia las acusaciones contra un líder."""
        if leaderId in self.accusations:
            del self.accusations[leaderId]


class ConsensusState:
    """Estado global del consenso."""
    
    def __init__(self, state_file: str = "consensus_state.json"):
        self.state_file = state_file
        self.registry = NodeRegistry()
        self.tokens = TokenLedger()
        self.votes = VotesStore()
        self.accusations = AccusationsStore()
        self.turn_state = TurnState()
        
        # Cargar estado si existe
        self.load_state()
    
    def save_state(self):
        """Guarda el estado en disco."""
        state_data = {
            "nodes": {nid: asdict(node) for nid, node in self.registry.nodes.items()},
            "frozen_tokens": self.tokens.frozen_tokens,
            "turn_state": asdict(self.turn_state),
            "next_order": self.registry._next_order
        }
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            print(f"Error guardando estado: {e}")
    
    def load_state(self):
        """Carga el estado desde disco."""
        if not os.path.exists(self.state_file):
            return
        
        try:
            with open(self.state_file, 'r') as f:
                state_data = json.load(f)
            
            # Cargar nodos
            for nid, node_data in state_data.get("nodes", {}).items():
                node = Node(**node_data)
                self.registry.nodes[nid] = node
            
            # Cargar tokens
            self.tokens.frozen_tokens = state_data.get("frozen_tokens", {})
            
            # Cargar estado del turno
            turn_data = state_data.get("turn_state", {})
            self.turn_state = TurnState(**turn_data)
            
            # Cargar next_order
            self.registry._next_order = state_data.get("next_order", 0)
            
        except Exception as e:
            print(f"Error cargando estado: {e}")


# Instancia global del estado
consensus_state = ConsensusState()
