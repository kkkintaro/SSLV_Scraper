# SS.LV Auto Sludinājumu Skrāpis

Profesionāls rīks automašīnu sludinājumu automatizētai iegūšanai no ss.lv vietnes. Šis skrāpis ir izstrādāts, lai efektīvi filtrētu un analizētu sludinājumus atbilstoši sekojošiem parametriem:

- Gads: 2016+
- Cena: līdz 20 000 EUR
- Transmisija: Automāts

## Tehniskās prasības

- Python 3.6 vai jaunāka versija
- Google Chrome pārlūkprogramma
- Nepieciešamās Python bibliotēkas (skatīt requirements.txt)

## Instalācija

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

Alternatīva palaišana:
```
python main.py
```

## Funkcionalitāte

Skrāpis balstās uz Selenium WebDriver tehnoloģiju un veic šādas funkcijas:

1. Automātiski atvēr ss.lv auto sadaļu
2. Konfigurē filtrus atbilstoši definētajiem parametriem (gads, cena, transmisija)
3. Iegūst detalizētus sludinājumu datus (virsraksts, saite, modelis, gads, tilpums, nobraukums, cena)
4. Strukturēti saglabā iegūtos datus teksta failā tālākai analīzei

## Problēmu novēršana

Ja rodas problēmas ar Chrome WebDriver:

1. Pārbaudiet Chrome pārlūkprogrammas instalāciju
2. Lietotājiem ar Mac M1/M2: Skripts veic automātisku konfigurāciju Apple Silicon procesoriem
3. Sarežģītāku problēmu gadījumā var būt nepieciešama manuāla ChromeDriver instalācija atbilstoši Jūsu Chrome versijai 
