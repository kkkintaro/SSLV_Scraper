# SS.LV Auto Sludinājumu Skrāpis

Šis projekts ir web skrāperis, kas paredzēts automašīnu sludinājumu iegūšanai no ss.lv tīmekļa vietnes. Skrāperis koncentrējas uz automašīnu sadaļu un ļauj iegūt sludinājumus, izmantojot konkrētus filtrus.

## Projekta uzdevuma apraksts

Skrāperis ir izstrādāts, lai automātiski izvāktu datus no ss.lv automašīnu sludinājumu sadaļas, izmantojot šādus fiksētus filtrus:
- Gads: 2016 un jaunākas automašīnas
- Cena: līdz 20 000 EUR
- Transmisija: Automātiskā 

Iegūtie dati tiek saglabāti teksta failā, kas satur informāciju par katru sludinājumu:
- Sludinājuma virsraksts
- Saite uz sludinājumu
- Automašīnas modelis
- Izlaides gads
- Dzinēja tilpums
- Nobraukums
- Cena

## Izmantotās Python bibliotēkas

Projekta izstrādē izmantotas šādas bibliotēkas:
- **requests**: HTTP pieprasījumu veikšanai
- **beautifulsoup4**: HTML parsēšanai un datu izgūšanai
- **selenium**: Tīmekļa pārlūkprogrammas automatizācijai
- **webdriver-manager**: Selenium draiveru automātiskai pārvaldībai

## Projekta datu struktūras

Galvenās datu struktūras, kas izmantotas projektā:
1. **Dictionary (Vārdnīca)**: Katrs sludinājums tiek glabāts kā Python vārdnīca (dict) ar atslēgām:
   - 'title': Sludinājuma virsraksts
   - 'link': Pilna saite uz sludinājumu
   - 'model': Automašīnas modelis
   - 'year': Izlaides gads
   - 'volume': Dzinēja tilpums
   - 'mileage': Nobraukums
   - 'price': Cena

2. **List (Saraksts)**: Visi sludinājumi tiek glabāti Python sarakstā (list), kas satur vārdnīcas.

## Programmēšanas metodes

Projektā izmantotas šādas programmēšanas metodes:
1. **Funkciju definēšana**: Kods sadalīts atsevišķās funkcijās, katrai ar konkrētu nolūku:
   - `setup_driver()`: Selenium draivera iestatīšana
   - `parse_ads_from_page()`: HTML satura apstrāde un sludinājumu izgūšana
   - `save_ads_to_file_overwrite()`: Sludinājumu saglabāšana teksta failā
   - `set_filters()`: Filtru iestatīšana meklēšanas formā
   - `click_search_button()`: Meklēšanas pogas atrašana un nospiešana
   - `process_pagination()`: Paginācijas apstrāde vairākām rezultātu lapām

2. **Kļūdu apstrāde**: Izmantota try-except struktūra, lai apstrādātu iespējamās kļūdas un nodrošinātu programmas darbību arī problēmsituācijās.

3. **Web skrāpēšanas tehnikas**:
   - Selenium izmantošana interaktīvai mijiedarbībai ar tīmekļa vietni
   - BeautifulSoup bibliotēkas izmantošana HTML parsēšanai
   - Regulāro izteiksmju izmantošana datu atlasīšanai

4. **Datu saglabāšana**: Iegūtie dati tiek strukturēti un saglabāti teksta failā formātētā veidā.

## Projekta versijas

Projekts izstrādāts pakāpeniski, sākot no vienkāršas versijas līdz pilnvērtīgam risinājumam:

1. **V1 (scraper_v1_basic_fetch.py)**: Pamata savienojums ar SS.LV vietni un lapas ielāde.
2. **V2 (scraper_v2_parse_ads.py)**: Sludinājumu datu izgūšana no lapas.
3. **V3 (scraper_v3_pagination_filters.py)**: Filtru iestatīšana un paginācijas apstrāde.
4. **V4 (scraper_v4_save_data.py)**: Datu saglabāšana teksta failā.
5. **V5 (scraper_v5_final.py)**: Optimizēta gala versija ar uzlabotu kļūdu apstrādi.

Gala risinājums ir **ss_lv_minimal_scraper.py**, kas apvieno labākās iezīmes no visām iepriekšējām versijām.

## Palaišanas instrukcijas

1. Instalējiet nepieciešamās Python bibliotēkas:
```
pip install -r requirements.txt
```

2. Pārliecinieties, ka jums ir instalēts Google Chrome.

3. Palaidiet skriptu:
```
python ss_lv_minimal_scraper.py
```

vai izmantojot pievienoto .bat failu (Windows):
```
run.bat 