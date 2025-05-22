# SS.LV Auto Sludinājumu Skrāpis

Vienkāršs rīks automašīnu sludinājumu iegūšanai no ss.lv vietnes. Skrāpis meklē automašīnas pēc šādiem parametriem:
- Gads: 2016+
- Cena: līdz 20 000 EUR
- Transmisija: Automāts

## Uzstādīšana

Nepieciešams Python 3.6+ un Google Chrome.

```
pip install -r requirements.txt
```

## Palaišana

Windows:
```
run.bat
```

Mac/Linux:
```
./run.sh
```

Vai manuāli:
```
python main.py
```

## Kā tas darbojas

Skrāpis izmanto Selenium, lai:
1. Atvērtu ss.lv auto sadaļu
2. Iestatītu filtrus (gads, cena, transmisija)
3. Savāktu sludinājumu datus (virsraksts, saite, modelis, gads, tilpums, nobraukums, cena)
4. Saglabātu rezultātus teksta failā

## Problēmu novēršana

Ja rodas problēmas ar Chrome draiveri:
1. Pārliecinieties, ka Chrome ir instalēts
2. Uz Mac M1/M2: Skripts automātiski konfigurē Chrome darbībai ar Apple Silicon
3. Ja problēmas turpinās, mēģiniet instalēt ChromeDriver manuāli 
