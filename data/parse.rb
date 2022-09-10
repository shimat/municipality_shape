# https://geoshape.ex.nii.ac.jp/city/code/
# のHTMLが入力
# TODO: 政令指定都市の区がちゃんと入らない

require 'csv'

text = open("data.html").read
trs = text.scan(/<tr.*?>(.+?)<\/tr>/m)

File.open('result.csv', 'w:UTF-8') do |f|
File.open('result_pythondict.txt', 'w:UTF-8') do |f2|
    f.write("\uFEFF")  # BOM
    f2.write("\uFEFF")  # BOM

    out_csv = CSV.new(
        f, force_quotes: true, write_headers: true, encoding: "UTF-8",
        headers: %w[pref city_kanji topo_href geo_href] )

    trs[1..].each do |tr|
        pref, city_kanji, city_yomi, date, link_str = tr[0].scan(
            /<td>(?<pref>\S{2,3}[都道府県])<\/td>\s*<td>.*?<\/td>\s*<td>.*?<\/td>\s*<td>(?<pref>[^<>]+[市区町村])<\/td>\s*<td>(?<yomi>\p{Hiragana}+?)<\/td>\s*<td>(?<date>.*?)<\/td>\s<td>(?<link>.*)<\/td>/m)[0]
        #p tr
        #p pref, city_kanji, city_yomi, date, link_str
        next unless link_str
        topo_href, geo_href = link_str.scan(/<a href="(?<topo>.+?)">\s*TopoJSON\s*<\/a><a href="(?<geo>.+?)">\s*GeoJSON\s*<\/a>/)[0]
        #p topo_href, geo_href
        out_csv << [pref, city_kanji, topo_href, geo_href]
        f2.puts("\"#{pref} #{city_kanji}\": \"#{geo_href}\",")
    end
end
end
