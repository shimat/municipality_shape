from itertools import chain
from typing import Any, Iterable, NamedTuple

import numpy as np
import numpy.typing as npt
import cv2
import streamlit as st
from pyproj import Transformer

transformer = Transformer.from_proj(4326, 6680)


class Data(NamedTuple):
     name: str
     score: float
     img_contours: npt.NDArray
     defects: Any
     largest_contour: Any


@st.cache(persist=True)
def compute_score(name: str, contours: Any) -> Data:
    contours_points, img_contours = get_contours_points(contours)
    largest_contour, hull, defects = get_defects_hull(contours_points) 

    distances = [defects[i, 0] for i in range(defects.shape[0])]
    distances = sorted((d for s, e, f, d in distances), key=lambda d: d, reverse=True)
    score = np.average(distances[:5])
    return Data(name, score, img_contours, defects, largest_contour)


def get_minmax(contours: list[list[list[float]]]) -> tuple[float, float, float, float]:
    flat = list(chain.from_iterable(contours))
    array = np.array(flat)
    x, y = array.T
    xmin, xmax, _, _ = cv2.minMaxLoc(x)
    ymin, ymax, _, _ = cv2.minMaxLoc(y)
    return xmin, xmax, ymin, ymax


def normalize_minmax(
        coordinates: npt.NDArray,
        xmin: float, xmax: float, ymin: float, ymax: float,
        size: int,
        border_size: int,
        dtype: np.dtype=np.int32
) -> npt.NDArray:
    x, y = coordinates.T
    if (xmax - xmin) > (ymax - ymin):
        scale = (xmax - xmin)
    else:
        scale = (ymax - ymin)
    normx = ((x-xmin)/scale) * (size - border_size*2)
    normy = ((y-ymin)/scale) * (size - border_size*2)
    result = np.vstack([normx + border_size, size - normy - border_size]).T
    return result.astype(dtype)


@st.cache(persist=True)
def get_contours_from_geojson(geojson: dict[str, Any], size: int = 500) -> list[npt.NDArray[np.int32]]:
    all_coordinates = geojson["features"][0]["geometry"]["coordinates"]
    contours: list[list[list[float]]] = list(chain.from_iterable(all_coordinates))

    xmin, xmax, ymin, ymax = get_minmax(contours)

    contours = [
        [transformer.transform(c[1], c[0])[::-1] for c in contour if 120 < c[0] < 150 and 20 < c[1] < 50]  # 緯度経度0の異常データがたまに紛れている
        for contour in contours]
    xmin, xmax, ymin, ymax = get_minmax(contours)

    result = []
    for contour in contours:
        if not contour:
            continue
        normalized_contour = normalize_minmax(np.array(contour), xmin, xmax, ymin, ymax, size, 10)
        result.append(normalized_contour.astype(np.int32))

    return result


@st.cache(persist=True)
def get_contours_points(contours: Iterable[npt.NDArray], size: int = 500) -> tuple[Any, npt.NDArray]:
    img_contours = np.zeros((size, size, 1), np.uint8)
    cv2.polylines(img_contours, list(contours), isClosed=True, color=(255, 255, 255), thickness=2)
    contours_points, _ = cv2.findContours(img_contours, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours_points, img_contours


@st.cache(persist=True)
def get_defects_hull(contours: Any) -> tuple[Any, Any, Any]:
    largest_contour = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)[0]
    hull = cv2.convexHull(largest_contour, returnPoints=False)
    defects = cv2.convexityDefects(largest_contour, hull)
    return largest_contour, hull, defects


@st.cache(persist=True)
def draw_hull_image(defects, c0, img: npt.NDArray) -> npt.NDArray:
    img_hull = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    # cv2.drawContours(img_hull, [hull], -1, (255, 0, 0), 2)
    if defects is not None:
        elems = sorted((defects[i, 0] for i in range(defects.shape[0])), key=lambda x: x[3], reverse=True)

        for i, (s, e, f, d) in enumerate(elems):
            start = tuple(c0[s][0])
            end = tuple(c0[e][0])
            far = tuple(c0[f][0])
            cv2.line(img_hull, start, end, color=(0, 255, 0), thickness=2)
            color = (255, 0, 0) if i < 5 else (255, 160, 160)
            cv2.circle(img_hull, far, radius=7, color=color, thickness=-1)

    return img_hull
