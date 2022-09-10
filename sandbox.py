import json
import numpy as np

"""
def get_arcs_from_topojson(topojson: dict[str, Any]) -> npt.NDArray:
    arcs_array = list(chain.from_iterable(topojson["arcs"]))
    scale = topojson["transform"]["scale"]
    translate = topojson["transform"]["translate"]
    arcs_array = list(decode_topojson_arc(arcs_array, scale, translate))
    #st.write(arcs_array)
    arcs = np.array(arcs_array)
    arcs = normalize_minmax(arcs, 500, 10)
    return arcs

def decode_topojson_arc(arc: list[list[int]], scale: list[float], translate: list[float]) -> Iterable[list[int]]:
    x, y = 0, 0
    for p in arc:
        x += p[0]
        y += p[1]
        lon = x * scale[0] + translate[0]
        lat = y * scale[1] + translate[1]
        xx, yy = transformer.transform(lat, lon)
        #print(f"{lat=} {lon=} {xx=} {yy=}")
        yield [xx, yy]
"""