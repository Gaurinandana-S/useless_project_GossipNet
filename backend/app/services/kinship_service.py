import networkx as nx

def get_parents(graph: nx.DiGraph, person_id: str):
    """Return list of parent node IDs for person_id in parent-directed graph (parent -> child)."""
    if not graph.has_node(person_id):
        return []
    return [p for p, c, d in graph.in_edges(person_id, data=True) if d.get("primitive_type") == "parent"]

def get_children(graph: nx.DiGraph, person_id: str):
    """Return list of child node IDs for person_id."""
    if not graph.has_node(person_id):
        return []
    return [c for p, c, d in graph.out_edges(person_id, data=True) if d.get("primitive_type") == "parent"]

def get_spouses(graph: nx.DiGraph, person_id: str):
    """Return list of spouse node IDs for person_id."""
    if not graph.has_node(person_id):
        return []
    spouses = []
    # Spouses can be directed in graph, check both in and out
    for u, v, d in graph.edges(person_id, data=True):
        if d.get("primitive_type") == "spouse":
            spouses.append(v)
    for u, v, d in graph.in_edges(person_id, data=True):
        if d.get("primitive_type") == "spouse":
            spouses.append(u)
    return list(set(spouses))

def get_siblings(graph: nx.DiGraph, person_id: str):
    """Return list of sibling node IDs (share at least one parent or explicit sibling edge)."""
    if not graph.has_node(person_id):
        return []
    parents = get_parents(graph, person_id)
    siblings = set()
    for p in parents:
        for c in get_children(graph, p):
            if c != person_id:
                siblings.add(c)
    # Check explicit sibling primitive edges
    for u, v, d in graph.edges(person_id, data=True):
        if d.get("primitive_type") == "sibling":
            siblings.add(v)
    for u, v, d in graph.in_edges(person_id, data=True):
        if d.get("primitive_type") == "sibling":
            siblings.add(u)
    return list(siblings)

def get_relationship(graph: nx.DiGraph, person_a_id: str, person_b_id: str) -> str:
    """
    Returns human-readable relationship of person_a TO person_b.
    Example: get_relationship(graph, Madhavan, Suresh) -> "father"
    (Madhavan is the father of Suresh)
    """
    if person_a_id == person_b_id:
        return "the same person"

    if not graph.has_node(person_a_id) or not graph.has_node(person_b_id):
        return "unrelated"

    node_a = graph.nodes[person_a_id]
    gender_a = node_a.get("gender", "M")

    # Direct Parent / Child
    parents_b = get_parents(graph, person_b_id)
    if person_a_id in parents_b:
        return "father" if gender_a == "M" else "mother"

    children_b = get_children(graph, person_b_id)
    if person_a_id in children_b:
        return "son" if gender_a == "M" else "daughter"

    # Spouse
    spouses_b = get_spouses(graph, person_b_id)
    if person_a_id in spouses_b:
        return "husband" if gender_a == "M" else "wife"

    # Sibling
    siblings_b = get_siblings(graph, person_b_id)
    if person_a_id in siblings_b:
        return "brother" if gender_a == "M" else "sister"

    # Grandparent / Grandchild
    for pb in parents_b:
        parents_pb = get_parents(graph, pb)
        if person_a_id in parents_pb:
            pb_node = graph.nodes[pb]
            side = "paternal" if pb_node.get("gender") == "M" else "maternal"
            rel = "grandfather" if gender_a == "M" else "grandmother"
            return f"{side} {rel}"

    for cb in children_b:
        children_cb = get_children(graph, cb)
        if person_a_id in children_cb:
            return "grandson" if gender_a == "M" else "granddaughter"

    # Uncle / Aunt (A is sibling or spouse of sibling of B's parent)
    for pb in parents_b:
        sibs_pb = get_siblings(graph, pb)
        if person_a_id in sibs_pb:
            pb_node = graph.nodes[pb]
            side = "paternal" if pb_node.get("gender") == "M" else "maternal"
            rel = "uncle" if gender_a == "M" else "aunt"
            return f"{side} {rel}"
        # Spouse of parent's sibling
        for sib in sibs_pb:
            if person_a_id in get_spouses(graph, sib):
                pb_node = graph.nodes[pb]
                side = "paternal" if pb_node.get("gender") == "M" else "maternal"
                rel = "uncle" if gender_a == "M" else "aunt"
                return f"{side} {rel} (by marriage)"

    # Nephew / Niece (A is child of B's sibling)
    for sb in siblings_b:
        if person_a_id in get_children(graph, sb):
            return "nephew" if gender_a == "M" else "niece"

    # Cousin (A shares a grandparent with B)
    grandparents_b = set()
    for pb in parents_b:
        for gpb in get_parents(graph, pb):
            grandparents_b.add(gpb)

    parents_a = get_parents(graph, person_a_id)
    grandparents_a = set()
    for pa in parents_a:
        for gpa in get_parents(graph, pa):
            grandparents_a.add(gpa)

    if grandparents_a.intersection(grandparents_b):
        return "cousin"

    # In-laws via spouse
    for sb in spouses_b:
        parents_sb = get_parents(graph, sb)
        if person_a_id in parents_sb:
            return "father-in-law" if gender_a == "M" else "mother-in-law"
        sibs_sb = get_siblings(graph, sb)
        if person_a_id in sibs_sb:
            return "brother-in-law" if gender_a == "M" else "sister-in-law"

    # In-laws via child's spouse
    for cb in children_b:
        for spouse_cb in get_spouses(graph, cb):
            if person_a_id == spouse_cb:
                return "son-in-law" if gender_a == "M" else "daughter-in-law"

    # Primitive Social Relationships (Neighbor, Friend, Colleague)
    for u, v, d in graph.edges(person_a_id, data=True):
        if v == person_b_id:
            p_type = d.get("primitive_type")
            if p_type in ["neighbor", "friend", "colleague"]:
                return p_type
    for u, v, d in graph.in_edges(person_a_id, data=True):
        if u == person_b_id:
            p_type = d.get("primitive_type")
            if p_type in ["neighbor", "friend", "colleague"]:
                return p_type

    # Household connection
    h_a = node_a.get("household_id")
    h_b = graph.nodes[person_b_id].get("household_id")
    if h_a and h_b and h_a == h_b:
        return "housemate"

    # Shortest path distance fallback
    try:
        undirected = graph.to_undirected()
        dist = nx.shortest_path_length(undirected, person_a_id, person_b_id)
        if dist <= 3:
            return f"distant relative ({dist} steps away)"
        else:
            return f"distant acquaintance ({dist} steps away)"
    except nx.NetworkXNoPath:
        return "unrelated"
