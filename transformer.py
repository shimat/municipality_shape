from pyproj import Transformer

WGS84 = 4326
PREF_TO_COORD_NUMBER = {
    "長崎県": 1,
    "福岡県": 2, "佐賀県": 2, "熊本県": 2, "大分県": 2, "宮崎県": 2,
    "山口県": 3, "島根県": 3, "広島県": 3,
    "香川県": 4, "愛媛県": 4, "徳島県": 4, "高知県": 4,
    "兵庫県": 5, "鳥取県": 5, "岡山県": 5,
    "京都府": 6, "大阪府": 6, "福井県": 6, "滋賀県": 6, "三重県": 6, "奈良県": 6, "和歌山県": 6,
    "石川県": 7, "富山県": 7, "岐阜県": 7, "愛知県": 7,
    "新潟県": 8, "長野県": 8, "山梨県": 8, "静岡県": 8,
    "福島県": 9, "栃木県": 9, "茨城県": 9, "埼玉県": 9, "千葉県": 9, "群馬県": 9, "神奈川県": 9,
    "青森県": 10, "秋田県": 10, "山形県": 10, "岩手県": 10, "宮城県": 10,
}
NUMBER_1_CITIES = {
    "十島村", "喜界町", "奄美市", "龍郷町", "大和村", "宇検村", "瀬戸内町",
    "天城町", "徳之島町", "伊仙町", "和泊町", "知名町", "与論町"
}
NUMBER_11_CITIES = {
    "小樽市", "函館市", "伊達市", "北斗市",
    "島牧村", "寿都町", "黒松内町", "蘭越町", "ニセコ町", "真狩村", "留寿都村", "喜茂別町", "京極町", "俱知安町", "共和町", "岩内町",
    "泊村", "神恵内村", "積丹町", "古平町", "仁木町", "余市町", "赤井川村",
    "豊浦町", "壮瞥町", "洞爺湖町",
    "松前町", "福島町", "知内町", "木古内町", "七飯町", "鹿部町", "森町", "八雲町", "長万部町",
    "江差町", "上ノ国町", "厚沢部町", "乙部町", "奥尻町", "今金町", "せたな町",
}
NUMBER_13_CITIES = {
    "北見市", "帯広市", "釧路市", "網走市", "根室市",
    "美幌町", "津別町", "斜里町", "清里町", "小清水町", "訓子府町", "置戸町", "佐呂間町", "大空町",
    "音更町", "士幌町", "上士幌町", "鹿追町", "新得町", "清水町", "芽室町", "中札内村", "更別村", "大樹町", "広尾町", "幕別町",
    "池田町", "豊頃町", "本別町", "足寄町", "陸別町", "浦幌町",
    "釧路町", "厚岸町", "浜中町", "標茶町", "弟子屈町", "鶴居村", "白糠町",
    "別海町", "中標津町", "標津町", "羅臼町",
    "色丹村", "泊村", "留夜別村", "留別村", "紗那村", "蘂取村",
}
NUMBER_14_CITIES = {
    "小笠原村"
}
NUMBER_16_CITIES = {
    "宮古島市", "多良間村", "石垣市", "竹富町", "与那国町",
}
NUMBER_17_CITIES = {
    "北大東村", "南大東村"
}


def get_transformer(pref: str, city: str) -> Transformer:
    """
    自治体名から、使うべきpyproj.Transformerを返す
    """
    number = get_coordinate_system_number(pref, city)
    epsg = get_epsg(number)
    return Transformer.from_proj(WGS84, epsg)


def get_epsg(coordinate_system_number: int) -> int:
    """
    平面直角座標系の番号 (I,II,III,...,XIX) から、EPSGコードを返す
    """
    # https://www.gsi.go.jp/LAW/heimencho.html
    # https://qiita.com/XPT60/items/9aa41cab07ce6369fb99#epsg
    return 6668 + coordinate_system_number


def get_coordinate_system_number(pref: str, city: str) -> int:
    """
    自治体名から、使うべき平面直角座標系コードを返す
    """
    if result := PREF_TO_COORD_NUMBER.get(pref):
        return result

    if pref == "鹿児島県":
        if city in NUMBER_1_CITIES:
            return 1
        return 2
    if pref == "東京都":
        if city in NUMBER_14_CITIES:
            return 14
        return 9
        # 沖ノ鳥島(18), 南鳥島(19)は小笠原村だが、父島で代表させるので該当なし
    if pref == "北海道":
        if city in NUMBER_11_CITIES:
            return 11
        if city in NUMBER_13_CITIES:
            return 13
        return 12
    if pref == "沖縄県":
        if city in NUMBER_16_CITIES:
            return 16
        if city in NUMBER_17_CITIES:
            return 17
        return 15

    raise f"Not expected municipality: {pref=}, {city=}"


if __name__ == "__main__":
    x = get_coordinate_system_number("福岡県", "福岡市")
    print(x)
