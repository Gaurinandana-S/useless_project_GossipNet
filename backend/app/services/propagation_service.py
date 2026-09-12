import random
import networkx as nx
from datetime import datetime, timedelta
from typing import Dict, Any, List, Set, Tuple
from app.services.kinship_service import get_relationship

# Configurable propagation weights by relationship type
RELATIONSHIP_PROPAGATION_WEIGHTS = {
    "spouse": 0.95,
    "parent": 0.85,
    "child": 0.85,
    "sibling": 0.80,
    "friend": 0.80,
    "cousin": 0.65,
    "neighbor": 0.60,
    "colleague": 0.55,
    "in-law": 0.50,
    "paternal uncle": 0.60,
    "maternal uncle": 0.60,
    "paternal aunt": 0.60,
    "maternal aunt": 0.60,
    "grandfather": 0.70,
    "grandmother": 0.70,
    "grandson": 0.70,
    "granddaughter": 0.70,
    "nephew": 0.55,
    "niece": 0.55,
    "distant": 0.35,
    "social": 0.40
}

def get_personality_multiplier(node_data: Dict[str, Any]) -> float:
    """Calculates propagation transmission multiplier based on node personality traits."""
    gossip = node_data.get("gossip_reputation", "MED")
    comm = node_data.get("communication_frequency", "MED")
    secret = node_data.get("secret_keeping", "MED")

    gossip_mult = 1.3 if gossip == "HIGH" else (1.0 if gossip == "MED" else 0.6)
    comm_mult = 1.3 if comm == "HIGH" else (1.0 if comm == "MED" else 0.7)
    
    # Secret-keeping strongly dampens or halts rumor transmission
    secret_mult = 0.3 if secret == "HIGH" else (1.0 if secret == "MED" else 1.4)
    
    return gossip_mult * comm_mult * secret_mult

def simulate_rumor_propagation(
    graph: nx.DiGraph,
    starter_id: str,
    random_seed: int = None,
    subject_id: str = None
) -> Dict[str, Any]:
    """
    Simulates graph-based temporal rumor propagation originating from starter_id.
    Returns:
      - final_person_id: The last node to receive the rumor.
      - propagation_tree: Ordered list of transmission events with simulated clock times.
      - reached_person_ids: List of all people who heard the rumor.
      - hearing_times: Dict mapping person_id -> formatted time string.
      - sources: Dict mapping person_id -> who told them.
    """
    rng = random.Random(random_seed) if random_seed is not None else random.Random()
    
    # Start at 10:00 AM
    current_time = datetime(2026, 9, 11, 10, 0, 0)
    
    reached: Set[str] = {starter_id}
    hearing_times: Dict[str, str] = {starter_id: current_time.strftime("%I:%M %p")}
    sources: Dict[str, str] = {starter_id: "SELF"}
    propagation_events: List[Dict[str, Any]] = []

    # Queue of nodes currently spreading: (node_id, time_received)
    queue = [(starter_id, current_time)]
    
    # Track order of successful receipts to determine the final person
    receipt_order: List[Tuple[str, datetime]] = [(starter_id, current_time)]

    while queue:
        sender_id, sender_time = queue.pop(0)
        sender_data = graph.nodes[sender_id]
        
        # Check if sender is a strict secret-keeper (stopping condition!)
        if sender_id != starter_id and sender_data.get("secret_keeping") == "HIGH" and rng.random() < 0.85:
            # Refuses to share! Branch terminates.
            continue

        sender_multiplier = get_personality_multiplier(sender_data)

        # Get all adjacent contacts (out-edges, in-edges, neighbors)
        neighbors = set(graph.neighbors(sender_id))
        for u, v in graph.in_edges(sender_id):
            neighbors.add(u)

        # Shuffle candidates
        candidate_list = list(neighbors)
        rng.shuffle(candidate_list)

        for target_id in candidate_list:
            if target_id in reached:
                continue

            target_data = graph.nodes[target_id]
            rel_type = get_relationship(graph, sender_id, target_id)
            
            # Base probability from relationship weight
            base_prob = 0.50
            for k, weight in RELATIONSHIP_PROPAGATION_WEIGHTS.items():
                if k in rel_type.lower():
                    base_prob = weight
                    break

            # Effective transmission probability
            effective_prob = min(0.95, max(0.10, base_prob * sender_multiplier))
            
            # Dice roll for transmission
            if rng.random() < effective_prob:
                # Transmission successful!
                advance_minutes = rng.randint(10, 35)
                target_time = sender_time + timedelta(minutes=advance_minutes)
                time_str = target_time.strftime("%I:%M %p")

                reached.add(target_id)
                hearing_times[target_id] = time_str
                sources[target_id] = sender_id
                receipt_order.append((target_id, target_time))

                event = {
                    "step": len(propagation_events) + 1,
                    "source_id": sender_id,
                    "source_name": sender_data.get("name", "Unknown"),
                    "target_id": target_id,
                    "target_name": target_data.get("name", "Unknown"),
                    "time_str": time_str,
                    "timestamp": target_time.isoformat(),
                    "relationship": rel_type
                }
                propagation_events.append(event)
                queue.append((target_id, target_time))

    # Sort receipt order by timestamp to find the final recipient
    receipt_order.sort(key=lambda x: x[1])
    final_person_id = receipt_order[-1][0] if receipt_order else starter_id

    return {
        "final_person_id": final_person_id,
        "final_person_name": graph.nodes[final_person_id].get("name", "Unknown"),
        "propagation_tree": propagation_events,
        "reached_person_ids": list(reached),
        "hearing_times": hearing_times,
        "sources": sources
    }
