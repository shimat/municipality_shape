import gc
import streamlit as st
from data_loader import get_geojson
from image_processing import Data, compute_score, get_contours_from_geojson, draw_hull_image
from const import MUNICIPALITY_TABLE, PREFECTURES
from sortedcontainers import SortedList

st.set_page_config(page_title="いびつな市町村ランキング", layout="wide")

st.title("いびつな市町村ランキング")

prefecture = st.selectbox("都道府県を選択", PREFECTURES)

url_table = MUNICIPALITY_TABLE
if prefecture != "全国":
    url_table = {name: url for name, url in url_table.items() if prefecture in name}


@st.cache(persist=True)
def get_data(name: str, url: str) -> Data:
    geojson = get_geojson(url)
    all_contours = list(get_contours_from_geojson(geojson))
    return compute_score(name, all_contours)


# ベストNを探す
MAX_COUNT = 10
top_n = SortedList(key=lambda x: -x.score)
for name, url in url_table.items():
    d = get_data(name, url)
    top_n.add(d)
    if len(top_n) > MAX_COUNT:
        top_n.pop()

#tabs = st.tabs(("いびつな形ベスト10", "きれいな形ベスト10 (微妙)"))
tabs = st.tabs(("いびつな形ベスト10", ))

for i, d in enumerate((top_n, )):
    header_cols = tabs[i].columns(3)
    header_cols[0].header("市区町村名")
    header_cols[1].header("形状")
    header_cols[2].header("スコア")
    for rank, (name, score, contours, largest_contour, defects) in enumerate(d):
        _, img_hull = draw_hull_image(contours, largest_contour, defects)
        cols = tabs[i].columns(3)
        cols[0].markdown(f"<p style='font-size: x-large;'>{rank+1}: {name}</p>", unsafe_allow_html=True)
        cols[1].image(img_hull)
        cols[2].markdown(f"<p style='font-size: x-large;'>{score}</p>", unsafe_allow_html=True)

gc.collect()

st.markdown("""
-----
<style>
div.small-font li{ font-size: small; }
</style>
<p>GitHub: <a href="https://github.com/shimat/municipality_shape">https://github.com/shimat/municipality_shape</a></p>
<p>出典</p>
<div class="small-font">
<ul>
<li>『国土数値情報「⾏政区域データ」 (N03)』（国土交通省）（<a href="https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-v2_4.html">https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-v2_4.html</a>）を加工して作成</li>
<li>『歴史的行政区域データセットβ版 (<a href="https://geoshape.ex.nii.ac.jp/city/">https://geoshape.ex.nii.ac.jp/city/</a>)』（CODH作成）を加工して作成</li>
</ul>
</div>
""", unsafe_allow_html=True)