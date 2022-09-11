from itertools import chain
from typing import Any, Iterable, NamedTuple, Final

import numpy as np
import numpy.typing as npt
import cv2
import streamlit as st
from pyproj import Transformer

DEFAULT_IMAGE_SIZE: Final[int] = 500

transformer = Transformer.from_proj(4326, 6680)


class Data(NamedTuple):
     name: str
     score: float
     #img_contours: npt.NDArray
     contours: list[npt.NDArray[np.int32]]
     largest_contour: npt.NDArray[np.int32]
     defects: npt.NDArray[npt.NDArray[npt.NDArray[np.int32]]]


@st.cache(persist=True)
def compute_score(name: str, contours: list[npt.NDArray[np.int32]]) -> Data:
    #contours_points, img_contours = get_contours_points(contours)
    largest_contour, hull, defects = get_defects_hull(contours)

    distances = (defects[i, 0] for i in range(defects.shape[0]))
    distances = sorted((d for s, e, f, d in distances), key=lambda d: d, reverse=True)
    score = np.average(distances[:5])
    return Data(name, score, contours, largest_contour, defects)


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
        dtype: np.dtype = np.int32
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


#@st.cache(persist=True)
def get_contours_from_geojson(
        geojson: dict[str, Any], size: int = DEFAULT_IMAGE_SIZE
) -> list[npt.NDArray[np.int32]]:
    all_coordinates = geojson["features"][0]["geometry"]["coordinates"]
    contours: list[list[list[float]]] = list(chain.from_iterable(all_coordinates))

    cartesian_contours = [
        [transformer.transform(c[1], c[0])[::-1] for c in contour if 120 < c[0] < 150 and 20 < c[1] < 50]  # 緯度経度0の異常データがたまに紛れている
        for contour in contours]
    xmin, xmax, ymin, ymax = get_minmax(cartesian_contours)

    result = []
    for contour in cartesian_contours:
        if not contour:
            continue
        normalized_contour = normalize_minmax(np.array(contour), xmin, xmax, ymin, ymax, size, 10)
        result.append(normalized_contour)

    return result


#@st.cache(persist=True)
#def get_contours_points(
#        contours: Iterable[npt.NDArray], size: int = DEFAULT_IMAGE_SIZE
#) -> tuple[Any, npt.NDArray]:
#    img_contours = np.zeros((size, size, 1), np.uint8)
#    cv2.polylines(img_contours, list(contours), isClosed=True, color=(255, 255, 255), thickness=2)
#    contours_points, _ = cv2.findContours(img_contours, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#    return contours_points, img_contours


#@st.cache(persist=True)
def get_defects_hull(
        contours: list[npt.NDArray[np.int32]]
) -> tuple[npt.NDArray[np.int32], npt.NDArray[np.int32], npt.NDArray[npt.NDArray[npt.NDArray[np.int32]]]]:
    largest_contour: npt.NDArray[np.int32] = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)[0]
    hull: npt.NDArray[np.int32] = cv2.convexHull(largest_contour, returnPoints=False)

    # The convex hull indices are not monotonous, which can be in the case when the input contour contains
    # self-intersections in function 'cv::convexityDefects'
    # https://github.com/opencv/opencv/issues/4539#issuecomment-766798290
    hull[::-1].sort(axis=0)

    defects: npt.NDArray[npt.NDArray[npt.NDArray[np.int32]]] = cv2.convexityDefects(largest_contour, hull)
    return largest_contour, hull, defects


#@st.cache(persist=True)
def draw_hull_image(
        contours: list[npt.NDArray[np.int32]],
        largest_contour: npt.NDArray[np.int32],
        defects: npt.NDArray[npt.NDArray[npt.NDArray[np.int32]]],
        size: int = DEFAULT_IMAGE_SIZE
) -> tuple[npt.NDArray, npt.NDArray]:
    img_contours = np.zeros((size, size, 1), np.uint8)
    cv2.polylines(img_contours, list(contours), isClosed=True, color=(255, 255, 255), thickness=2)

    img_hull = cv2.cvtColor(img_contours, cv2.COLOR_GRAY2BGR)

    if defects is not None:
        sorted_defects = sorted((defects[i, 0] for i in range(defects.shape[0])), key=lambda x: x[3], reverse=True)

        for i, (s, e, f, d) in enumerate(sorted_defects):
            start = largest_contour[s]
            end = largest_contour[e]
            far = largest_contour[f]
            cv2.line(img_hull, start, end, color=(0, 255, 0), thickness=2)
            color = (255, 0, 0) if i < 5 else (255, 160, 160)
            cv2.circle(img_hull, far, radius=7, color=color, thickness=-1)

    return img_contours, img_hull
