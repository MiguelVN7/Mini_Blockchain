"""
Motor del protocolo de consenso.
Implementa la lógica de rotación, generación de seeds, votación ponderada y validación.
"""

import random
import time
import math
from typing import Optional, Tuple, List, Dict
from .state import consensus_state, Node
from .models import extract_seed_value, extract_vote_value
from .crypto_provider import get_provider


class ConsensusEngine:
    """Motor principal del consenso distribuido."""
    
    def __init__(self):
        self.state = consensus_state
        self.crypto = get_provider()
    
    def register_node(self, nodeId: str, ip: str, publicKey: str) -> int:
        """
        Registra un nuevo nodo en la red.
        Retorna el orden asignado basado en IP.
        """
        order = self.state.registry.register_node(nodeId, ip, publicKey)
        self.state.save_state()
        return order
    
    def freeze_tokens(self, nodeId: str, tokens: int, signature: bytes, payload: bytes) -> bool:
        """
        Congela tokens para un nodo después de verificar la firma.
        """
        # Verificar que el nodo esté registrado
        if nodeId not in self.state.registry.nodes:
            return False
        
        node = self.state.registry.nodes[nodeId]
        
        # Verificar firma
        if not self.crypto.verify(node.publicKey, payload, signature):
            return False
        
        # Congelar tokens
        self.state.tokens.freeze_tokens(nodeId, tokens)
        self.state.save_state()
        return True
    
    def is_turn_leader(self, nodeId: str, turn: int) -> bool:
        """Verifica si un nodo es el líder del turno especificado."""
        expected_leader = self.state.registry.get_leader_for_turn(turn)
        return expected_leader == nodeId
    
    def set_seed(self, leaderId: str, encrypted_seed: str, turn: int, signature: bytes, payload: bytes) -> bool:
        """
        Establece el seed del líder para el turno actual.
        Verifica que sea el líder correcto y la firma sea válida.
        """
        # Verificar que es el líder del turno
        if not self.is_turn_leader(leaderId, turn):
            return False
        
        # Verificar que el nodo existe y obtener su clave pública
        if leaderId not in self.state.registry.nodes:
            return False
        
        node = self.state.registry.nodes[leaderId]
        
        # Verificar firma
        if not self.crypto.verify(node.publicKey, payload, signature):
            return False
        
        # Generar seed según especificación
        seed = self._generate_seed(turn, encrypted_seed)
        
        # Actualizar estado
        self.state.turn_state.current_turn = turn
        self.state.turn_state.current_seed = seed
        self.state.turn_state.seed_leader = leaderId
        
        self.state.save_state()
        return True
    
    def _generate_seed(self, turn: int, encrypted_seed: str) -> int:
        """
        Genera el seed según la especificación:
        - 2 bytes superiores: número del turno (con rollover en 65536)
        - 2 bytes inferiores: aleatorio del líder
        """
        # Los 2 bytes superiores son el turno (con rollover)
        turn_part = turn & 0xFFFF
        
        # Los 2 bytes inferiores vienen del encrypted_seed
        random_part = extract_seed_value(encrypted_seed) & 0xFFFF
        
        # Combinar: turn en bytes superiores, random en inferiores
        seed = (turn_part << 16) | random_part
        
        return seed
    
    def record_vote(self, nodeId: str, encrypted_vote: str, signature: bytes, payload: bytes) -> bool:
        """
        Registra el voto de un nodo después de verificar la firma.
        """
        # Verificar que el nodo existe
        if nodeId not in self.state.registry.nodes:
            return False
        
        node = self.state.registry.nodes[nodeId]
        
        # Verificar firma
        if not self.crypto.verify(node.publicKey, payload, signature):
            return False
        
        # Calcular el voto usando el seed actual
        if self.state.turn_state.current_seed is None:
            return False  # No hay seed todavía
        
        selected_index = self._calculate_weighted_vote(nodeId, self.state.turn_state.current_seed)
        
        # Registrar voto
        self.state.votes.record_vote(nodeId, encrypted_vote, selected_index)
        
        return True
    
    def _calculate_weighted_vote(self, voting_nodeId: str, seed: int) -> int:
        """
        Calcula el voto ponderado determinista usando el seed.
        Retorna el índice del nodo seleccionado.
        """
        # Obtener lista ordenada de nodos
        nodes = self.state.registry.get_nodes_ordered()
        if not nodes:
            return 0
        
        # Obtener pesos (tokens congelados)
        weights = []
        for node in nodes:
            tokens = self.state.tokens.get_tokens(node.nodeId)
            weights.append(max(tokens, 0))  # Peso mínimo 0
        
        # Si no hay tokens congelados, usar peso uniforme
        total_weight = sum(weights)
        if total_weight == 0:
            weights = [1] * len(nodes)
            total_weight = len(nodes)
        
        # Usar el seed para generar número determinista
        rng = random.Random(seed)
        
        # Selección ponderada por ruleta
        target = rng.randrange(total_weight)
        
        cumulative = 0
        for i, weight in enumerate(weights):
            cumulative += weight
            if target < cumulative:
                return i
        
        # Fallback (no debería llegar aquí)
        return len(nodes) - 1
    
    def tally_votes(self) -> Tuple[Optional[str], float, bool]:
        """
        Cuenta los votos y determina si se alcanzó el umbral 2/3.
        Retorna: (líder_seleccionado, porcentaje_acuerdo, umbral_alcanzado)
        """
        votes = self.state.votes.get_votes()
        if not votes:
            return None, 0.0, False
        
        # Obtener nodos ordenados para mapear índices a nodeIds
        nodes = self.state.registry.get_nodes_ordered()
        if not nodes:
            return None, 0.0, False
        
        # Contar votos por nodo seleccionado
        vote_counts: Dict[str, int] = {}
        
        for vote in votes:
            if 0 <= vote.selectedIndex < len(nodes):
                selected_nodeId = nodes[vote.selectedIndex].nodeId
                vote_counts[selected_nodeId] = vote_counts.get(selected_nodeId, 0) + 1
        
        if not vote_counts:
            return None, 0.0, False
        
        # Encontrar el nodo con más votos
        winner = max(vote_counts, key=vote_counts.get)
        max_votes = vote_counts[winner]
        
        # Calcular porcentaje de acuerdo
        total_votes = len(votes)
        agreement = max_votes / total_votes if total_votes > 0 else 0.0
        
        # Verificar umbral 2/3
        required_votes = math.ceil(2 * total_votes / 3)
        threshold_reached = max_votes >= required_votes
        
        return winner, agreement, threshold_reached
    
    def propose_block(self, proposerId: str, block_data: dict, signature: bytes, payload: bytes) -> bool:
        """
        Maneja la propuesta de un bloque.
        Verifica que el proposer tenga autorización.
        """
        # Verificar que el nodo existe
        if proposerId not in self.state.registry.nodes:
            return False
        
        node = self.state.registry.nodes[proposerId]
        
        # Verificar firma
        if not self.crypto.verify(node.publicKey, payload, signature):
            return False
        
        # Para la propuesta, simplemente verificamos que esté registrado
        # La autorización real se verifica en submit_block
        return True
    
    def submit_block(self, leaderId: str, block_data: dict, signature: bytes, payload: bytes) -> bool:
        """
        Maneja el envío de un bloque validado.
        Verifica que el líder sea el ganador del consenso.
        """
        # Verificar que el nodo existe
        if leaderId not in self.state.registry.nodes:
            return False
        
        node = self.state.registry.nodes[leaderId]
        
        # Verificar firma
        if not self.crypto.verify(node.publicKey, payload, signature):
            return False
        
        # Verificar que este líder ganó el consenso
        winner, _, threshold_reached = self.tally_votes()
        
        if not threshold_reached or winner != leaderId:
            return False
        
        # Aquí se integraría con tu blockchain actual
        # Por ahora, simplemente marcamos como exitoso
        
        # Avanzar al siguiente turno
        self._advance_turn()
        
        return True
    
    def report_leader(self, reporterId: str, leaderId: str, evidence: dict, signature: bytes, payload: bytes) -> bool:
        """
        Maneja el reporte de un líder fraudulento.
        """
        # Verificar que el reporter existe
        if reporterId not in self.state.registry.nodes:
            return False
        
        node = self.state.registry.nodes[reporterId]
        
        # Verificar firma
        if not self.crypto.verify(node.publicKey, payload, signature):
            return False
        
        # Registrar acusación
        self.state.accusations.add_accusation(leaderId, reporterId, evidence)
        
        # Verificar si se alcanzó el umbral para banear
        active_nodes = len([n for n in self.state.registry.nodes.values() if n.active])
        required_accusations = math.ceil(2 * active_nodes / 3)
        
        accusations_count = self.state.accusations.get_accusation_count(leaderId)
        
        if accusations_count >= required_accusations:
            # Banear el nodo
            self.state.registry.ban_node(leaderId)
            self.state.accusations.clear_accusations(leaderId)
            self.state.save_state()
            return True
        
        return True  # Acusación registrada, pero no baneado aún
    
    def _advance_turn(self):
        """Avanza al siguiente turno limpiando el estado."""
        self.state.turn_state.next_turn()
        self.state.votes.clear_votes()
        self.state.save_state()
    
    def get_current_state(self) -> dict:
        """Retorna el estado actual del consenso para debugging."""
        return {
            "current_turn": self.state.turn_state.current_turn,
            "current_seed": self.state.turn_state.current_seed,
            "seed_leader": self.state.turn_state.seed_leader,
            "nodes_count": len([n for n in self.state.registry.nodes.values() if n.active]),
            "votes_count": len(self.state.votes.get_votes()),
            "frozen_tokens": dict(self.state.tokens.frozen_tokens)
        }


# Instancia global del motor
engine = ConsensusEngine()
