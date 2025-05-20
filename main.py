import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import time
import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# --- Fiksētās konfigurācijas konstantes ---
BASE_URL = "https://www.ss.lv"
CARS_URL = "https://www.ss.lv/lv/transport/cars/"
DATA_FILE = "ss_lv_cars_data.txt"  # Fails tiks pārrakstīts katrā palaišanas reizē

# --- Filtru konstantes ---
MIN_YEAR = "2016"  # Minimālais gads
MAX_PRICE = "20000"  # Maksimālā cena
TRANSMISSION = "Automāts"  # Automātiskā transmisija

PAGE_LIMIT = 10  # Maksimālais skrapējamo lapu skaits
PAGE_LOAD_DELAY = 1.5  # Sekundes, aizkave starp lapu ielādēm

# --- Palīgfunkcijas ---
def parse_ads_from_page(html_content):
    """
    Apstrādā lapas HTML saturu, lai iegūtu sludinājumu datus.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    ads_list = []
    ad_rows = soup.find_all("tr", id=re.compile(r"^tr_\d+$"))

    if not ad_rows:
        # Saglabā HTML atkļūdošanai
        with open("debug_response.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Nevarēja atrast sludinājumu rindas. HTML saglabāts failā 'debug_response.html'")
        return ads_list

    for row in ad_rows:
        cols = row.find_all("td")
        if len(cols) < 8:
            continue
        try:
            ad_data = {}
            link_tag = cols[2].find('a', href=re.compile(r"/msg/"))
            if not link_tag or not link_tag.get('href'):
                continue 
            
            ad_data['title'] = link_tag.get_text(strip=True)
            ad_data['link'] = urljoin(BASE_URL, link_tag['href'])
            ad_data['model'] = cols[3].get_text(strip=True)
            ad_data['year'] = cols[4].get_text(strip=True)
            ad_data['volume'] = cols[5].get_text(strip=True)
            ad_data['mileage'] = cols[6].get_text(strip=True)
            price_text = cols[7].get_text(strip=True)
            ad_data['price'] = ' '.join(price_text.split())

            if ad_data.get('title') and ad_data.get('link'):
                ads_list.append(ad_data)
        except Exception as e:
            print(f"Kļūda apstrādājot rindu: {e}")
            continue
    return ads_list

# --- Draivera iestatīšana ---
def setup_driver():
    """
    Iestatīt Selenium pārlūkprogrammas draiveri.
    """
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Bez redzama loga - atkļūdošanai atstājam redzamu pārlūku
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        # Automātiski lejupielādē un uzstāda atbilstošo ChromeDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        print("Chrome draiveris veiksmīgi uzstādīts.")
        return driver
    except Exception as e:
        print(f"Kļūda, uzstādot Chrome draiveri: {e}")
        print("Mēģina izmantot noklusējuma atrašanās vietu...")
        try:
            # Mēģina izmantot noklusējuma Chrome draiveri
            driver = webdriver.Chrome(options=chrome_options)
            print("Chrome draiveris veiksmīgi uzstādīts ar noklusējuma atrašanās vietu.")
            return driver
        except Exception as e2:
            print(f"Kļūda, uzstādot Chrome draiveri ar noklusējuma atrašanās vietu: {e2}")
            print("Mēģina bez automātiskās uzstādīšanas...")
            try:
                # Mēģina bez ChromeDriverManager
                driver = webdriver.Chrome(options=chrome_options)
                return driver
            except Exception as e3:
                print(f"Nopietna kļūda: {e3}")
                print("Lūdzu, pārliecinieties, ka Chrome ir uzstādīts un ChromeDriver ir pieejams.")
                raise

# --- Galvenā funkcija ---
def main():
    """
    Skripta galvenā izpildes funkcija - V2: Sludinājumu datu iegūšana
    """
    print("--- SS.LV Auto Skrāpja (Versija 2: Sludinājumu datu iegūšana) Palaišana ---")
    
    all_collected_ads = []
    
    try:
        # Iestatīt Selenium pārlūkprogrammu
        driver = setup_driver()
        
        # Atvert SS.LV automašīnu lapu
        print(f"Atver SS.LV auto lapu: {CARS_URL}")
        driver.get(CARS_URL)
        
        # Pārbaudīt, vai lapa ielādējās
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "filter_frm"))
        )
        
        print("Lapa ielādēta veiksmīgi!")
        
        # Iegūt lapas HTML saturu
        html_content = driver.page_source
        
        # Saglabāt lapu atkļūdošanai
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("Lapas saturs saglabāts failā 'debug_page.html'")
        
        # Parsēt sludinājumus no lapas
        ads_found = parse_ads_from_page(html_content)
        all_collected_ads.extend(ads_found)
        
        print(f"Lapā atrasti {len(ads_found)} sludinājumi.")
        
        # Izdrukāt pirmos 3 sludinājumus kā paraugu
        if ads_found:
            print("\n--- Pirmie 3 atrastie sludinājumi (paraugs): ---")
            for i, ad_item in enumerate(ads_found[:3]):
                print(f"  #{i+1}: {ad_item.get('title', 'N/A')} | Cena: {ad_item.get('price', 'N/A')}")
        else:
            print("Netika atrasti sludinājumi.")
        
    except Exception as e:
        print(f"Kļūda: {e}")
    finally:
        # Aizvērt pārlūkprogrammu
        if 'driver' in locals():
            driver.quit()
            print("Pārlūkprogramma aizvērta.")
    
    print(f"\nKopā savākti {len(all_collected_ads)} sludinājumi.")
    print("--- Skrāpis V2 pabeidzis darbu ---")

if __name__ == "__main__":
    main() 