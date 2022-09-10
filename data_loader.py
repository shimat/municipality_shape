from typing import Any
import requests
import streamlit as st


@st.cache(persist=True)
def get_geojson(url: str) -> dict[str, Any]:
    print(f"Cache miss: {url}")
    response = requests.get(url)
    return response.json()
