import json
import numpy as np


def load_from_topojson(file_name: str):
    with open(file_name, "r", encoding="utf-8-sig") as f:
        j = json.load(f)
    arcs = np.array(j["arcs"][0][1:])
    arcs = (normalize_minmax(arcs) * 500).astype(np.int32)
    return arcs
