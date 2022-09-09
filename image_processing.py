from itertools import chain
from typing import Any, NamedTuple

import numpy as np
import numpy.typing as npt
import cv2


class Size(NamedTuple):
    width: int
    height: int


def normalize_minmax(coordinates: npt.NDArray, size: Size, border_size: int, dtype: np.dtype=np.int32) -> npt.NDArray:
    x, y = coordinates.T
    xmin, xmax, _, _ = cv2.minMaxLoc(x)
    ymin, ymax, _, _ = cv2.minMaxLoc(y)
    normx = ((x-xmin)/(xmax-xmin)) * (size.width - border_size*2)
    normy = ((y-ymin)/(ymax-ymin)) * (size.height - border_size*2)
    result = np.vstack([normx + border_size, size.height - normy - border_size]).T
    return result.astype(dtype)


def get_arcs_from_geojson(geojson: dict[str, Any]) -> npt.NDArray:
    arcs_array = geojson["features"][0]["geometry"]["coordinates"]
    arcs_array = list(chain.from_iterable(chain.from_iterable(arcs_array)))
    print(arcs_array)
    arcs = np.array(arcs_array)
    #arcs = np.array(geojson["features"][0]["geometry"]["coordinates"][0][0])
    arcs = normalize_minmax(arcs, Size(500, 500), 10)
    return arcs


def draw_hull_image(arcs: npt.NDArray):
    img = np.zeros((500, 500, 1), np.uint8)
    cv2.polylines(img, [arcs], isClosed=True, color=(255, 255, 255), thickness=1)
    # img = cv2.copyMakeBorder(img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, None, value=0)

    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c0 = contours[0]
    hull = cv2.convexHull(c0, returnPoints=False)
    defects = cv2.convexityDefects(c0, hull)

    # img_contour = cv2.drawContours(img_bgr.copy(), contours, -1, (0,255,0), 1)
    img_hull = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    # cv2.drawContours(img_hull, [hull], -1, (255, 0, 0), 2)
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(c0[s][0])
        end = tuple(c0[e][0])
        far = tuple(c0[f][0])
        cv2.line(img_hull, start, end, color=(0, 255, 0), thickness=2)
        cv2.circle(img_hull, far, radius=7, color=(255, 0, 0), thickness=-1)

    return img_hull
