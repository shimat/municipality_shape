from typing import Any
import requests
import streamlit as st


@st.cache(persist=True)
def get_geojson(url: str) -> dict[str, Any]:
    response = requests.get(url)
    return response.json()
