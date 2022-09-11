import json
import os
from time import sleep
from typing import Any
import requests
import streamlit as st


#@st.cache(persist=True)
def get_geojson(url: str) -> dict[str, Any]:
    file_name = os.path.basename(url)
    cache_path = os.path.join("geojson", file_name)

    if os.path.exists(cache_path):
        with open(cache_path, encoding="UTF-8-sig") as f:
            return json.load(f)
    else:
        raise f"Not found '{cache_path}'"
        # sleep(1)
        # return get_geojson_core(url)


@st.cache(persist=True)
def get_geojson_core(url: str) -> dict[str, Any]:
    print(f"Cache miss: {url}")
    response = requests.get(url)

    file_name = os.path.basename(url)
    cache_path = os.path.join("geojson", file_name)
    with open(cache_path, "w", encoding="UTF-8-sig") as f:
        f.write(json.dumps(response.json(), indent=4, ensure_ascii=False))

    return response.json()
