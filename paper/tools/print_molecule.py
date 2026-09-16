"""Print the atoms and bonds of one graph from a chemical TUDataset."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(os.path.dirname(ROOT), "data", "TUDataset")

MAPS = {
    "MUTAG": ({0: "C", 1: "N", 2: "O", 3: "F", 4: "I", 5: "Cl", 6: "Br"},
              {0: "aromatic", 1: "single", 2: "double"}),
    "AIDS": (None, None),
    "Mutagenicity": (None, None),
}


def main(name, gid):
    raw = os.path.join(DATA, name, "raw")
    gi = [int(v) for v in open(os.path.join(raw, f"{name}_graph_indicator.txt")).read().split()]
    nl = [int(v) for v in open(os.path.join(raw, f"{name}_node_labels.txt")).read().split()]
    gl = [int(v) for v in open(os.path.join(raw, f"{name}_graph_labels.txt")).read().split()]
    edges = []
    for line in open(os.path.join(raw, f"{name}_A.txt")):
        line = line.strip()
        if line:
            a, b = line.split(",")
            edges.append((int(a), int(b)))
    epath = os.path.join(raw, f"{name}_edge_labels.txt")
    elabels = [int(v) for v in open(epath).read().split()] if os.path.exists(epath) else []

    node_map, bond_map = MAPS.get(name, (None, None))
    nodes = [i for i, g in enumerate(gi, start=1) if g == gid]
    nset = set(nodes)
    local = {n: k for k, n in enumerate(nodes)}

    print(f"{name} graph {gid}  (label={gl[gid-1]}, {len(nodes)} atoms)")
    print("  atoms:", [f"{local[n]}:{node_map[nl[n-1]] if node_map else nl[n-1]}" for n in nodes])
    print("  bonds:")
    for idx, (a, b) in enumerate(edges):
        if a in nset and b in nset:
            bt = bond_map[elabels[idx]] if bond_map and idx < len(elabels) else (
                elabels[idx] if idx < len(elabels) else "?")
            print(f"    {local[a]:2d}-{local[b]:2d}  {bt}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
