import json

from requests_html import HTMLSession
from bs4 import BeautifulSoup
import requests

yardim = """Yardım
    0 - Çıkış
    1 - Oyun ara\n"""

headers = {"User-Agent": "Mozilla/5.0"}

def oyunlari_ara(isim: str):
    url = f'https://www.protondb.com/search?q={isim}'
    response = session.get(url)

    response.html.render(sleep=2)

    main_root = response.html.find('div.pre-app-start-root', first=True)
    main_div = main_root.find('div.App__Root-sc-h4g8tw-0.cJvNf.root', first=True)
    main = main_div.find('main.App__FullFrame-sc-h4g8tw-1.eascgF', first=True)
    mains_main_div = main.find('div.styled__Flex-sc-g24nyo-0.styled__Column-sc-g24nyo-1.styled__AlignedColumn-sc-g24nyo-2.App__ContentContainer-sc-h4g8tw-2.content', first=True)
    games_div = mains_main_div.find('div[type="cell"].styled__Flex-sc-g24nyo-0.styled__Row-sc-g24nyo-4', first=True)
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

    print(genel_bilgiler)
    print(rating_bilgi)

    if genel_bilgiler.status_code == 200 and rating_bilgi.status_code == 200:
        genel_bilgiler = json.loads(genel_bilgiler.text)
        rating_bilgi = json.loads(rating_bilgi.text)

        oyun_bilgi = f"""
        {genel_bilgiler[_id]["data"]["name"]}

        Derecelendirme
            Mevcut Derecelendirme: {rating_bilgi["tier"]} ({rating_bilgi_al(rating_bilgi["tier"])})
            En İyi Derecelendirmeli Rapor: {rating_bilgi["bestReportedTier"]} ({rating_bilgi_al(rating_bilgi["bestReportedTier"])})
            Trend Olan Derecelendirme: {rating_bilgi["trendingTier"]} ({rating_bilgi_al(rating_bilgi["trendingTier"])})

        Oyunun Genel Bilgileri
            Program Tipi: {genel_bilgiler[_id]["data"]["type"]}
            Steam ID: {genel_bilgiler[_id]["data"]["steam_appid"]}
            Yaş Sınırı: {genel_bilgiler[_id]["data"]["required_age"]}
            Bedavamı?: {genel_bilgiler[_id]["data"]["is_free"]}
            Desteklenen Diller: {BeautifulSoup(genel_bilgiler[_id]["data"]["supported_languages"], 'html.parser').get_text(separator=" ")}
            Minimum PC Gereksinimleri: {BeautifulSoup(genel_bilgiler[_id]["data"]["pc_requirements"]["minimum"], 'html.parser').get_text(separator=" ")}
            Önerilen PC Gereksinimleri: {BeautifulSoup(genel_bilgiler[_id]["data"]["pc_requirements"]["recommended"], 'html.parser').get_text(separator=" ")}
            Oyunun Kısa Bilgisi: {genel_bilgiler[_id]["data"]["short_description"]}
            
        {fiyat_bilgi_al(genel_bilgiler, _id)}
        """

        return oyun_bilgi

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
        return
    else:
        print(f"""
        Fiyatlandırma
            {json_body[_id]["data"]["price_overview"]["final_formatted"]}""")

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
                            from BadiCo, for everyone.""")

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
                    break
                else:
                    print("Oyun bilgileri alınırken bir hata oluştu.")
                    break
