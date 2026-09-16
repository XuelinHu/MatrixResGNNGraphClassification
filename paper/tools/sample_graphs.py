"""Reconstruct a few example graphs from the raw TUDataset files.

Used to ground figure-generation prompts in the real structure of each
dataset (atom composition, ring count, node/edge semantics) instead of
guessing from the dataset name.
"""
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(os.path.dirname(ROOT), "data", "TUDataset")

ATOM = {0: "C", 1: "N", 2: "O", 3: "F", 4: "I", 5: "Cl", 6: "Br"}
BOND = {0: "aromatic", 1: "single", 2: "double"}


def load(name):
    raw = os.path.join(DATA, name, "raw")
    with open(os.path.join(raw, f"{name}_graph_indicator.txt")) as fh:
        gi = [int(v) for v in fh.read().split()]
    with open(os.path.join(raw, f"{name}_graph_labels.txt")) as fh:
        gl = [int(v) for v in fh.read().split()]
    with open(os.path.join(raw, f"{name}_node_labels.txt")) as fh:
        nl = [int(v) for v in fh.read().split()]
    edges = []
    with open(os.path.join(raw, f"{name}_A.txt")) as fh:
        for line in fh:
            line = line.strip()
            if line:
                a, b = line.split(",")
                edges.append((int(a), int(b)))
    elabels = None
    epath = os.path.join(raw, f"{name}_edge_labels.txt")
    if os.path.exists(epath):
        with open(epath) as fh:
            elabels = [int(v) for v in fh.read().split()]
    return gi, gl, nl, edges, elabels


def describe(name, max_show=3):
    gi, gl, nl, edges, elabels = load(name)
    n_graphs = max(gi)
    per_graph_nodes = {}
    for node, g in enumerate(gi, start=1):
        per_graph_nodes.setdefault(g, []).append(node)

    print(f"\n{'=' * 72}\n{name}: {n_graphs} graphs, {len(gi)} nodes, {len(edges)} edges")
    print(f"  label distribution: {dict(sorted(Counter(gl).items()))}")

    shown = 0
    for g in sorted(per_graph_nodes, key=lambda k: len(per_graph_nodes[k])):
        nodes = per_graph_nodes[g]
        if not (8 <= len(nodes) <= 16):
            continue
        nset = set(nodes)
        sub = [(a, b) for a, b in edges if a in nset and b in nset]
        comp = Counter(nl[n - 1] for n in nodes)
        if name in ("MUTAG", "Mutagenicity", "AIDS"):
            atoms = Counter(ATOM.get(k, str(k)) for k in comp.elements())
            # a 6-carbon ring is a good, recognisable illustration subject
            ring6 = comp.get(0, 0) >= 6
            body = f"atoms={dict(atoms)}  nodes={len(nodes)} edges={len(sub)} ring6={ring6}"
        else:
            body = f"nodes={len(nodes)} edges={len(sub)}"
        print(f"  graph {g}: label={gl[g - 1]}  {body}")
        shown += 1
        if shown >= max_show:
            break


if __name__ == "__main__":
    for name in ["MUTAG", "Mutagenicity", "AIDS", "PROTEINS", "DD", "ENZYMES"]:
        describe(name)
