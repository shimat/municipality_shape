import streamlit as st
from data_loader import get_geojson
from image_processing import get_contours_from_geojson, draw_hull_image

MUNICIPALITY_TABLE = {
"函館市": "https://geoshape.ex.nii.ac.jp/city/geojson/latest/01202.geojson",
"小樽市": "https://geoshape.ex.nii.ac.jp/city/geojson/latest/01203.geojson",
"旭川市": "https://geoshape.ex.nii.ac.jp/city/geojson/latest/01204.geojson",
"室蘭市": "https://geoshape.ex.nii.ac.jp/city/geojson/latest/01205.geojson",
"釧路市": "https://geoshape.ex.nii.ac.jp/city/geojson/latest/01206.geojson",
"帯広市": "https://geoshape.ex.nii.ac.jp/city/geojson/latest/01207.geojson",
"北見市": "https://geoshape.ex.nii.ac.jp/city/geojson/latest/01208.geojson",
"夕張市": "https://geoshape.ex.nii.ac.jp/city/geojson/latest/01209.geojson",
"幕別町": "https://geoshape.ex.nii.ac.jp/city/geojson/latest/01643.geojson",
}
"""
     "札幌市": "https://geoshape.ex.nii.ac.jp/city/topojson/latest/01100.topojson",
     "函館市": "https://geoshape.ex.nii.ac.jp/city/topojson/latest/01202.topojson",
     "小樽市": "https://geoshape.ex.nii.ac.jp/city/topojson/latest/01203.topojson",
     "旭川市": "https://geoshape.ex.nii.ac.jp/city/topojson/latest/01204.topojson",
     "室蘭市": "https://geoshape.ex.nii.ac.jp/city/topojson/latest/01205.topojson",
     "釧路市": "https://geoshape.ex.nii.ac.jp/city/topojson/latest/01206.topojson",
     "帯広市": "https://geoshape.ex.nii.ac.jp/city/topojson/latest/01207.topojson",
     "北見市": "https://geoshape.ex.nii.ac.jp/city/topojson/latest/01208.topojson",
     "夕張市": "https://geoshape.ex.nii.ac.jp/city/topojson/latest/01209.topojson",
     "幕別町": "https://geoshape.ex.nii.ac.jp/city/topojson/latest/01643.topojson",

"""

st.title("Convexity Defects")

municipality = st.selectbox('市区町村を選択', MUNICIPALITY_TABLE.keys())

geojson = get_geojson(MUNICIPALITY_TABLE[municipality])
contours = get_contours_from_geojson(geojson)
#arcs = get_arcs_from_topojson(geojson)
img_hull = draw_hull_image(contours)
st.image(img_hull, caption=f"{municipality}のConvexity Defects")


st.markdown("""
-----
<p>GitHub: <a href="https://github.com/shimat/municipality_shape">https://github.com/shimat/municipality_shape</a></p>
<p>出典</p>
<div class="xx-small-font">
<ul>
<li>『国土数値情報「⾏政区域データ」 (N03)』（国土交通省）（<a href="https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-v2_4.html">https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-v2_4.html</a>）を加工して作成</li>
<li>『歴史的行政区域データセットβ版 (<a href="https://geoshape.ex.nii.ac.jp/city/">https://geoshape.ex.nii.ac.jp/city/</a>)』（CODH作成）を加工して作成</li>
</ul>
</div>
""", unsafe_allow_html=True)