import random
import uuid
import networkx as nx
from typing import Dict, Any, List, Tuple

# Name repositories for realistic Kerala/Indian names
OLDER_MALE = ["Madhavan", "Krishnan", "Gopal", "Parameswaran", "Kuttan", "Vasudevan", "Unnikrishnan", "Damodaran", "Narayanan", "Raman"]
OLDER_FEMALE = ["Saraswathi", "Lakshmi", "Leela", "Bhavani", "Devaki", "Thankam", "Kalyani", "Janaki", "Sarojini", "Kamala"]

ADULT_MALE = ["Suresh", "Rajesh", "Pradeep", "Sunil", "Vinod", "Ramesh", "Mohan", "Biju", "Santhosh", "Sreekumar", "Girish", "Jayakumar", "Harikumar", "Venu"]
ADULT_FEMALE = ["Anitha", "Latha", "Bindu", "Sheela", "Manju", "Deepa", "Geetha", "Mini", "Sobhana", "Saritha", "Sindhu", "Beena", "Radhika", "Jayashree"]

YOUNG_MALE = ["Arjun", "Rahul", "Akhil", "Nikhil", "Kiran", "Adithya", "Siddharth", "Vishnu", "Harisankar", "Gautham", "Abhijith", "Aravind", "Nivin", "Gokul"]
YOUNG_FEMALE = ["Meera", "Priya", "Anjali", "Athira", "Neha", "Devika", "Kavya", "Reshma", "Aparna", "Archana", "Arya", "Gouri", "Malavika", "Sruthi"]

HOUSEHOLD_NAMES = [
    "Tharavadu House", "Ayodhya Villa", "Pookada Residency", "Kailasam",
    "Gokulam", "Surya Kiran", "Devi Nivas", "Sreevalsam", "Ananda Bhavan",
    "Lakshmi Nivas", "Krishna Kripa", "Green Gardens", "Hillview Cottage", "Maple House"
]

def get_target_node_count(difficulty_level: int) -> Tuple[int, int]:
    if difficulty_level == 1:
        return (20, 30)
    elif difficulty_level == 2:
        return (25, 35)
    elif difficulty_level == 3:
        return (30, 45)
    elif difficulty_level == 4:
        return (40, 55)
    else:
        return (50, 70)

def generate_family_graph(difficulty_level: int = 1, random_seed: int = None) -> Dict[str, Any]:
    """
    Procedurally generates a complex multi-generation, multi-household family/social graph
    enriched with persona attributes for non-obvious rumor deduction.
    """
    actual_seed = random_seed if random_seed is not None else random.randint(100000, 999999)
    rng = random.Random(actual_seed)

    min_people, max_people = get_target_node_count(difficulty_level)
    target_count = rng.randint(min_people, max_people)

    older_m = list(OLDER_MALE)
    older_f = list(OLDER_FEMALE)
    adult_m = list(ADULT_MALE)
    adult_f = list(ADULT_FEMALE)
    young_m = list(YOUNG_MALE)
    young_f = list(YOUNG_FEMALE)

    rng.shuffle(older_m)
    rng.shuffle(older_f)
    rng.shuffle(adult_m)
    rng.shuffle(adult_f)
    rng.shuffle(young_m)
    rng.shuffle(young_f)

    used_names = set()

    def get_unique_name(pool1, pool2, gender):
        for name in pool1 + pool2:
            if name not in used_names:
                used_names.add(name)
                return name
        suffix_idx = 1
        base = "Unni" if gender == "M" else "Ammu"
        while f"{base} {suffix_idx}" in used_names:
            suffix_idx += 1
        name = f"{base} {suffix_idx}"
        used_names.add(name)
        return name

    # 1. Create Households
    num_households = max(3, target_count // 7)
    household_pool = list(HOUSEHOLD_NAMES)
    rng.shuffle(household_pool)

    households = []
    for i in range(num_households):
        h_name = household_pool[i % len(household_pool)]
        if i >= len(household_pool):
            h_name = f"{h_name} {i + 1}"
        households.append({
            "id": f"hh_{i+1}",
            "name": h_name,
            "address_location": f"Sector {i+1}, Kerala Town"
        })

    graph = nx.DiGraph()
    people_list = []

    def add_person(name, gender, age, gen, household_id, tree_level=None, is_social=False):
        p_id = f"p_{len(people_list)+1}"
        lvl = tree_level if tree_level is not None else max(0, gen - 1)
        person = {
            "id": p_id,
            "name": name,
            "gender": gender,
            "age": age,
            "household_id": household_id,
            "generation": gen,
            "tree_level": lvl,
            "is_social": is_social,
            # Persona attributes for non-trivial deduction and Phase 2 propagation
            "gossip_reputation": rng.choice(["HIGH", "MED", "LOW"]),
            "previous_rumor_count": rng.randint(0, 8),
            "trustworthiness": rng.choice(["HIGH", "MED", "LOW"]),
            "drama_level": rng.choice(["HIGH", "MED", "LOW"]),
            "communication_frequency": rng.choice(["HIGH", "MED", "LOW"]),
            "secret_keeping": rng.choice(["HIGH", "MED", "LOW"]),
            "recent_contacts": [],
            "house_visitors": [],
            "perceived_suspects": []
        }
        people_list.append(person)
        graph.add_node(p_id, **person)
        return p_id

    # 2. Generation 1 (Grandparents / Level 0)
    gen1_couples = []
    num_gen1_couples = 3

    for i in range(num_gen1_couples):
        h_id = households[i % len(households)]["id"]
        gm_name = get_unique_name(older_m, adult_m, "M")
        gf_name = get_unique_name(older_f, adult_f, "F")

        gm_id = add_person(gm_name, "M", rng.randint(68, 82), 1, h_id, tree_level=0, is_social=False)
        gf_id = add_person(gf_name, "F", rng.randint(65, 78), 1, h_id, tree_level=0, is_social=False)

        graph.add_edge(gm_id, gf_id, primitive_type="spouse")
        graph.add_edge(gf_id, gm_id, primitive_type="spouse")
        gen1_couples.append((gm_id, gf_id))

    # 3. Generation 2 (Adults / Level 1)
    gen2_people = []
    gen2_couples = []

    for gm_id, gf_id in gen1_couples:
        num_children = rng.randint(2, 4)
        for _ in range(num_children):
            if len(people_list) >= target_count - 4:
                break
            g2_gender = rng.choice(["M", "F"])
            g2_name = get_unique_name(adult_m if g2_gender == "M" else adult_f, young_m if g2_gender == "M" else young_f, g2_gender)
            h_id = rng.choice(households)["id"]
            g2_id = add_person(g2_name, g2_gender, rng.randint(40, 58), 2, h_id, tree_level=1, is_social=False)

            graph.add_edge(gm_id, g2_id, primitive_type="parent")
            graph.add_edge(gf_id, g2_id, primitive_type="parent")
            gen2_people.append(g2_id)

            if rng.random() < 0.85:
                spouse_gender = "F" if g2_gender == "M" else "M"
                sp_name = get_unique_name(adult_f if spouse_gender == "F" else adult_m, young_f if spouse_gender == "F" else young_m, spouse_gender)
                sp_id = add_person(sp_name, spouse_gender, rng.randint(38, 56), 2, h_id, tree_level=1, is_social=False)
                graph.add_edge(g2_id, sp_id, primitive_type="spouse")
                graph.add_edge(sp_id, g2_id, primitive_type="spouse")
                gen2_couples.append((g2_id, sp_id))
            else:
                gen2_couples.append((g2_id, None))

    # 4. Generation 3 (Young Adults / Level 2)
    gen3_people = []
    for parent_a, parent_b in gen2_couples:
        num_children = rng.randint(1, 3)
        for _ in range(num_children):
            if len(people_list) >= target_count:
                break
            g3_gender = rng.choice(["M", "F"])
            g3_name = get_unique_name(young_m if g3_gender == "M" else young_f, adult_m if g3_gender == "M" else adult_f, g3_gender)

            p_node_a = graph.nodes[parent_a]
            h_id = p_node_a["household_id"]
            g3_id = add_person(g3_name, g3_gender, rng.randint(18, 32), 3, h_id, tree_level=2, is_social=False)

            graph.add_edge(parent_a, g3_id, primitive_type="parent")
            if parent_b:
                graph.add_edge(parent_b, g3_id, primitive_type="parent")
            gen3_people.append(g3_id)

    # 5. Fill remaining nodes (Generation 3 / 4, Level 2 / 3)
    while len(people_list) < target_count:
        gen = rng.choice([2, 3, 4])
        g_gender = rng.choice(["M", "F"])
        g_name = get_unique_name(young_m if g_gender == "M" else young_f, adult_m if g_gender == "M" else adult_f, g_gender)
        h_id = rng.choice(households)["id"]
        lvl = max(0, gen - 1)
        new_id = add_person(g_name, g_gender, rng.randint(10, 35), gen, h_id, tree_level=lvl, is_social=False)

        potential_parents = [p for p, d in graph.nodes(data=True) if d.get("generation", 1) == gen - 1 and not d.get("is_social", False)]
        if potential_parents:
            par = rng.choice(potential_parents)
            graph.add_edge(par, new_id, primitive_type="parent")

    # 6. Add Social Connections (Neighbors, Friends, Colleagues)
    all_p_ids = [p["id"] for p in people_list]
    for p_id in all_p_ids:
        num_social = rng.randint(1, 2)
        candidates = [c for c in all_p_ids if c != p_id and not graph.has_edge(p_id, c)]
        if candidates:
            for _ in range(min(num_social, len(candidates))):
                other_id = rng.choice(candidates)
                rel_type = rng.choice(["neighbor", "friend", "colleague"])
                graph.add_edge(p_id, other_id, primitive_type=rel_type)
                graph.add_edge(other_id, p_id, primitive_type=rel_type)

    # 7. Populate Persona Dynamic Links (Recent contacts, visitors, perceived suspects)
    for p_id in all_p_ids:
        nbrs = list(graph.neighbors(p_id))
        rng.shuffle(nbrs)
        # Recent contacts
        graph.nodes[p_id]["recent_contacts"] = nbrs[:min(3, len(nbrs))]
        # Visitors to house
        housemates = [other for other in all_p_ids if graph.nodes[other]["household_id"] == graph.nodes[p_id]["household_id"] and other != p_id]
        graph.nodes[p_id]["house_visitors"] = list(set(housemates + nbrs[:1]))

    # 8. Select Rumor Subject and Starter
    central_candidates = [p["id"] for p in people_list if graph.degree(p["id"]) >= 3]
    if not central_candidates:
        central_candidates = all_p_ids

    starter_id = rng.choice(central_candidates)
    
    # Ensure starter has plausible high/med gossip traits
    graph.nodes[starter_id]["gossip_reputation"] = rng.choice(["HIGH", "MED"])
    graph.nodes[starter_id]["previous_rumor_count"] = rng.randint(4, 8)

    subject_candidates = [p for p in all_p_ids if p != starter_id]
    subject_id = rng.choice(subject_candidates)

    # Make several other nodes plausible red herrings
    red_herrings = [p for p in all_p_ids if p not in (starter_id, subject_id)]
    rng.shuffle(red_herrings)
    for rh in red_herrings[:3]:
        graph.nodes[rh]["gossip_reputation"] = "HIGH"
        graph.nodes[rh]["previous_rumor_count"] = rng.randint(3, 7)

    # Set perceived suspects for nodes
    for p_id in all_p_ids:
        potential_suspects = [s for s in red_herrings + [starter_id] if s != p_id]
        if potential_suspects:
            graph.nodes[p_id]["perceived_suspects"] = [rng.choice(potential_suspects)]

    # 9. Initial Visible Nodes (Strictly Level 0 Elders)
    level_0_ids = [p["id"] for p in people_list if graph.nodes[p["id"]].get("tree_level", 0) == 0]
    visible_set = set(level_0_ids)
    
    # In the rare case starter was in level 0, pick another starter from level 1 or 2
    if starter_id in visible_set:
        other_candidates = [p for p in all_p_ids if p not in visible_set]
        if other_candidates:
            starter_id = rng.choice(other_candidates)

    # Convert updated node data back to list format
    updated_people_list = [graph.nodes[p_id] for p_id in all_p_ids]

    return {
        "seed": actual_seed,
        "difficulty": difficulty_level,
        "graph": graph,
        "households": households,
        "people": updated_people_list,
        "rumor_starter_id": starter_id,
        "rumor_subject_id": subject_id,
        "initial_visible_ids": list(visible_set)
    }
