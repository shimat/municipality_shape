from itertools import chain
from typing import Any, NamedTuple, Iterable

import numpy as np
import numpy.typing as npt
import cv2
import streamlit as st
from pyproj import Transformer

transformer = Transformer.from_proj(4326, 6680)

class Size(NamedTuple):
    width: int
    height: int


def get_minmax(contours: list[list[list[int]]]) -> tuple[int, int, int, int]:
    flat = list(chain.from_iterable(contours))
    array = np.array(flat)
    x, y = array.T
    xmin, xmax, _, _ = cv2.minMaxLoc(x)
    ymin, ymax, _, _ = cv2.minMaxLoc(y)
    return xmin, xmax, ymin, ymax


def normalize_minmax(
        coordinates: npt.NDArray,
        xmin, xmax, ymin, ymax,
        size: int,
        border_size: int,
        dtype: np.dtype=np.int32
) -> npt.NDArray:
    x, y = coordinates.T
    #xmin, xmax, _, _ = cv2.minMaxLoc(x)
    #ymin, ymax, _, _ = cv2.minMaxLoc(y)
    #print(f"{xmin=} {xmax=} {ymin=} {ymax=}")
    #print(f"xdiff={xmax-xmin} ydiff={ymax-ymin}")
    if (xmax - xmin) > (ymax - ymin):
        scale = (xmax - xmin)
    else:
        scale = (ymax - ymin)
    normx = ((x-xmin)/scale) * (size - border_size*2)
    normy = ((y-ymin)/scale) * (size - border_size*2)
    result = np.vstack([normx + border_size, size - normy - border_size]).T
    return result.astype(dtype)


def get_contours_from_geojson(geojson: dict[str, Any]) -> Iterable[npt.NDArray]:
    all_coordinates = geojson["features"][0]["geometry"]["coordinates"]
    contours: list[list[list[int]]] = list(chain.from_iterable(all_coordinates))
    get_minmax(contours)
    contours = [
        [transformer.transform(c[1], c[0])[::-1] for c in contour]
        for contour in contours]

    xmin, ymin, xmax, ymax = get_minmax(contours)
    #st.write(contours)
    for contour in contours:
        normalized_contour = normalize_minmax(np.array(contour), xmin, xmax, ymin, ymax, 500, 10)
        #st.write(normalized_contour)
        yield normalized_contour

def draw_hull_image(contours: Iterable[npt.NDArray]):
    img = np.zeros((500, 500, 1), np.uint8)

    for c in list(contours)[:2]:
        cv2.polylines(img, [c], isClosed=False, color=(255, 255, 255), thickness=1)
    #cv2.polylines(img, list(contours), isClosed=True, color=(255, 255, 255), thickness=1)
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
        #cv2.line(img_hull, start, end, color=(0, 255, 0), thickness=2)
        #cv2.circle(img_hull, far, radius=7, color=(255, 0, 0), thickness=-1)

    return img_hull
