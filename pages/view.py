import streamlit as st
from const import MUNICIPALITY_TABLE
from data_loader import get_geojson
from image_processing import compute_score, draw_hull_image, get_contours_from_geojson


st.set_page_config(page_title="Convexity Defects")
st.title("各市町村の形状")

municipality = st.selectbox('市区町村を選択', MUNICIPALITY_TABLE.keys())

geojson = get_geojson(MUNICIPALITY_TABLE[municipality])
contours = get_contours_from_geojson(geojson)

data = compute_score(municipality, contours)
_, img_hull = draw_hull_image(contours, data.largest_contour, data.defects)
st.image(img_hull, caption=f"{municipality}のConvexity Defects (Score: {data.score})")


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