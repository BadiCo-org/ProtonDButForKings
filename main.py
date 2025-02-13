from requests_html import HTMLSession
from bs4 import BeautifulSoup
import requests

yardim = """Yardım
    0 - Çıkış
    1 - Oyun ara\n"""

headers = {"User-Agent": "Mozilla/5.0"}
translate_api_url = "https://google-translate113.p.rapidapi.com/api/v1/translator/text"

with open('api.json', 'r', encoding='utf-8') as api_infos:
    data = json.load(api_infos)
    x_rapidapi_key = data["x-rapidapi-key"]
    x_rapidapi_host = data["x-rapidapi-host"]
    exchange_rate_api_key = data["exchange_rate_api_key"]

def oyunlari_ara(isim: str):
    url = f'https://www.protondb.com/search?q={isim}'
    response = session.get(url)

    response.html.render(sleep=2)

    main_root = response.html.find('div.pre-app-start-root', first=True)
    main_div = main_root.find('div.App__Root-sc-h4g8tw-0.cJvNf.root', first=True)
    main = main_div.find('main.App__FullFrame-sc-h4g8tw-1.eascgF', first=True)
    mains_main_div = main.find('div.styled__Flex-sc-g24nyo-0.styled__Column-sc-g24nyo-1.styled__AlignedColumn-sc-g24nyo-2.App__ContentContainer-sc-h4g8tw-2.content', first=True)
    games_div = mains_main_div.find('div[type="cell"].styled__Flex-sc-g24nyo-0.styled__Row-sc-g24nyo-4', first=True)

    if games_div is None:
        print("Doğru bir oyun ismi giriniz!")
        return

    oyunlar = games_div.find('div.styled__Flex-sc-g24nyo-0.styled__Column-sc-g24nyo-1.GameCell__Container-sc-jkepq6-0.gMlTmq.nlzCs.hDldoz')

    oyun_bilgileri = []

    for oyun in oyunlar:
        oyun_main_child_div = oyun.find('div.styled__Flex-sc-g24nyo-0.styled__Row-sc-g24nyo-4.gMlTmq.dKXMgt', first=True)
        oyun_main_info_div = oyun_main_child_div.find('div.styled__Flex-sc-g24nyo-0.styled__Column-sc-g24nyo-1.styled__SpacedColumn-sc-g24nyo-3.GameSliceLegacy__Info-sc-1ka41zm-0', first=True)
        oyun_main_requested_info_child_div = oyun_main_info_div.find('div.styled__Flex-sc-g24nyo-0.styled__Row-sc-g24nyo-4.styled__SpacedRow-sc-g24nyo-9.gMlTmq.dKXMgt.hfOlYo', first=True)
        oyun_info_span = oyun_main_requested_info_child_div.find('span.GameSliceLegacy__Headline-sc-1ka41zm-1.ffhBSz', first=True)
        oyun_name_and_id = oyun_info_span.find('a', first=True)

        oyun_bilgileri.append((oyun_name_and_id.text,
                               oyun_name_and_id.attrs.get('href').replace('/app/', '')))

    return oyun_bilgileri

def oyun_detayli_bilgi(_id: int):
    url = f"https://www.protondb.com/app/{_id}"
    response = session.get(url)

    response.html.render(sleep=2)

    main_root = response.html.find('div.pre-app-start-root', first=True)
    main_info_div = main_root.find('div.App__Root-sc-h4g8tw-0.cJvNf.root', first=True)
    main = main_info_div.find('main.App__FullFrame-sc-h4g8tw-1.eascgF', first=True)
    mains_child_div = main.find('div.styled__Flex-sc-g24nyo-0.styled__Column-sc-g24nyo-1.styled__AlignedColumn-sc-g24nyo-2.App__ContentContainer-sc-h4g8tw-2.content', first=True)
    requested_infos_div = mains_child_div.find('div.styled__Flex-sc-g24nyo-0.styled__Column-sc-g24nyo-1.styled__AlignedColumn-sc-g24nyo-2.goqSt.nlzCs.inStNH', first=True)

    # Bilgileri alma

    genel_bilgiler = requests.get(f"https://www.protondb.com/proxy/steam/api/appdetails/?appids={_id}", headers=headers)
    rating_bilgi = requests.get(f"https://www.protondb.com/api/v1/reports/summaries/{_id}.json", headers=headers)

    if genel_bilgiler.status_code == 200 and rating_bilgi.status_code == 200:
        genel_bilgiler_json = json.loads(genel_bilgiler.text)
        rating_bilgi_json = json.loads(rating_bilgi.text)

        if genel_bilgiler_json[_id]["success"]:
            oyun_bilgi = f"""
                    {genel_bilgiler_json[_id]["data"]["name"]}

                    Derecelendirme
                        Mevcut Derecelendirme: {rating_bilgi_json["tier"]} ({rating_bilgi_al(rating_bilgi_json["tier"])})
                        En İyi Derecelendirmeli Rapor: {rating_bilgi_json["bestReportedTier"]} ({rating_bilgi_al(rating_bilgi_json["bestReportedTier"])})
                        Trend Olan Derecelendirme: {rating_bilgi_json["trendingTier"]} ({rating_bilgi_al(rating_bilgi_json["trendingTier"])})

                    Oyunun Genel Bilgileri
                        Program Tipi: {genel_bilgiler_json[_id]["data"]["type"]}
                        Steam ID: {genel_bilgiler_json[_id]["data"]["steam_appid"]}
                        Yaş Sınırı: {genel_bilgiler_json[_id]["data"]["required_age"]}
                        Bedavamı?: {genel_bilgiler_json[_id]["data"]["is_free"]}
                        Desteklenen Diller: {cevir(BeautifulSoup(genel_bilgiler_json[_id]["data"]["supported_languages"], 'html.parser').get_text(separator=" "))}
                        Minimum PC Gereksinimleri: {cevir(BeautifulSoup(genel_bilgiler_json[_id]["data"]["pc_requirements"]["minimum"], 'html.parser').get_text(separator=" ")).replace("Minimum: ", "")}
                        Önerilen PC Gereksinimleri: {cevir(BeautifulSoup(genel_bilgiler_json[_id]["data"]["pc_requirements"]["recommended"], 'html.parser').get_text(separator=" ")).replace("Önerilen: ", "")}
                        Oyunun Kısa Bilgisi: {cevir(genel_bilgiler_json[_id]["data"]["short_description"])}

                    {fiyat_bilgi_al(genel_bilgiler_json, _id)}
                    """

            return oyun_bilgi
        else:
            print("Oyun hala güncel bilgilere sahip değil veya bir hata oluştu.")
    else:
        print("ProtonDB sunucularına erişilemedi.")
        return

def rating_bilgi_al(rating: str):
    if rating == "platinum":
        return "Mevcut hali ile mükemmel şekilde çalışıyor."
    elif rating == "native":
        return "Linux'ta yerel olarak çalışabilir."
    elif rating == "gold":
        return "Bazı düzenlemeler ile kusursuz çalışır."
    elif rating == "silver":
        return "Küçük sorunlar olsana genel itibarıyla oynanabilir."
    elif rating == "bronze":
        return "Çalışsada sık sık çöküyor ve oyun deneyimini kötü etkileyen sorunlar var."
    elif rating == "borked":
        return "Açılmıyor veya oynanamaz halde."
    else:
        return None

def fiyat_bilgi_al(json_body: dict, _id: int):
    if not json_body[_id]["data"]["is_free"]:
        para_birimi = json_body[_id]["data"]["price_overview"]["currency"]
        fiyat = json_body[_id]["data"]["price_overview"]["final"] / 100
        return f"""
    Fiyatlandırma
        {fiyat} {para_birimi} = {fiyat_donustur(para_birimi, float(fiyat)):.2f} TL"""
    else:
        return

def cevir(text: str):
    json_payload = {
        "from": "auto",
        "to": "tr",
        "text": text
    }

    header_for_translation_api = {
        "x-rapidapi-key": x_rapidapi_key,
        "x-rapidapi-host": x_rapidapi_host,
        "Content-Type": "application/json"
    }

    response = requests.post(translate_api_url, json=json_payload, headers=header_for_translation_api)
    response_json = json.loads(response.text)

    return response_json["trans"]

def fiyat_donustur(para_birimi: str, miktar: float):
    response = requests.get(f"https://v6.exchangerate-api.com/v6/{exchange_rate_api_key}/latest/{para_birimi}")

    if response.status_code == 200:
        response_json = json.loads(response.text)

        try_donusturme = response_json["conversion_rates"]["TRY"] * miktar

        return try_donusturme
    else:
        print(f"Error {response.status_code}")
        return "Bulunamadı"

session = HTMLSession()

en_son_oyun_bilgileri = []

print("""
                                                        ,----,                     
,-.----.                                              ,/   .`|                ,--. 
\    /  \      ,---,        ,---,.                  ,`   .'  :   ,---,.   ,--/  /| 
|   :    \   .'  .' `\    ,'  .'  \         ,--,  ;    ;     / ,'  .' |,---,': / ' 
|   |  .\ :,---.'     \ ,---.' .' |       ,'_ /|.'___,/    ,',---.'   |:   : '/ /  
.   :  |: ||   |  .`\  ||   |  |: |  .--. |  | :|    :     | |   |   .'|   '   ,   
|   |   \ ::   : |  '  |:   :  :  /,'_ /| :  . |;    |.';  ; :   :  :  '   |  /    
|   : .   /|   ' '  ;  ::   |    ; |  ' | |  . .`----'  |  | :   |  |-,|   ;  ;    
;   | |`-' '   | ;  .  ||   :     \|  | ' |  | |    '   :  ; |   :  ;/|:   '   \   
|   | ;    |   | :  |  '|   |   . |:  | | :  ' ;    |   |  ' |   |   .'|   |    '  
:   ' |    '   : | /  ; '   :  '; ||  ; ' |  | '    '   :  | '   :  '  '   : |.  \ 
:   : :    |   | '` ,/  |   |  | ; :  | : ;  ; |    ;   |.'  |   |  |  |   | '_\.' 
|   | :    ;   :  .'    |   :   /  '  :  `--'   \   '---'    |   :  \  '   : |     
`---'.|    |   ,.'      |   | ,'   :  ,      .-./            |   | ,'  ;   |,'     
  `---`    '---'        `----'      `--`----'                `----'    '---'       
                            from BadiCo, for everyone.\n""")

while True:
    try:
        secenek = int(input("Bir seçenek giriniz (seçeneklere bakmak için 31 yazın. [komik demi]): "))
    except ValueError:
        print("Seçenek formatını doğru şekilde giriniz.")
        continue

    if 0 > secenek:
        print("Geçerli bir komut giriniz.")
        continue

    if secenek == 31:
        print(yardim)
    elif secenek == 0:
        print("Görüşürüz!")
        exit(0)
    elif secenek == 1:
        oyun_ismi = input("Aramak istediğiniz oyunun ismini giriniz: ")
        en_son_oyun_bilgileri = oyunlari_ara(oyun_ismi)

        print(f"| {oyun_ismi.capitalize()} için arama sonuçları: ")
        for oyun in en_son_oyun_bilgileri:
            print(f"| {en_son_oyun_bilgileri.index(oyun) + 1} - {oyun[0]} ID: {oyun[1]} |")
            print("----------------------------------------------------------------------")

        while True:
            try:
                info_secenek = int(
                    input("Belirli bir oyunun bilgilerini incelemek için oyunun sıra numarasını yazınız: "))
            except ValueError:
                print("Seçeneği geçerli bir formatta yazınız.")
                continue

            if info_secenek < 0:
                print("Geçerli bir seçenek giriniz.")
            elif info_secenek == 0:
                print("Detaylı bilgi giriş penceresine kapanıyor.")
                break
            elif info_secenek > len(en_son_oyun_bilgileri):
                print("Bu sıra numarasında bir oyun yok.")
            else:
                oyun_bilgi = oyun_detayli_bilgi(en_son_oyun_bilgileri[info_secenek - 1][1])
                if oyun_bilgi is not None:
                    print(oyun_bilgi)
                    with open('algoritma_duzenleyici.json', 'r+') as algoritma_file:
                        data: dict = json.loads(algoritma_file.read())

                        if oyun_ismi not in data["aranan-oyunlar"]:
                            data["aranan-oyunlar"][oyun_ismi] = 0

                        data["aranan-oyunlar"][oyun_ismi] = [data["aranan-oyunlar"].get(oyun_ismi) + 1, {
                            "secilen-oyunlar": {
                                en_son_oyun_bilgileri[info_secenek - 1][0]: data["aranan-oyunlar"][oyun_ismi][1].get(
                                    "secilen-oyunlar") + 1
                            }
                        }]
                        algoritma_file.write(json.dumps(data))
                    break
                else:
                    print("Oyun bilgileri alınırken bir hata oluştu.")
                    break
