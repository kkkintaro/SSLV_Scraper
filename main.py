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
    Skripta galvenā izpildes funkcija - V1: Pamata savienojums ar SS.LV
    """
    print("--- SS.LV Auto Skrāpja (Versija 1: Pamata savienojums) Palaišana ---")
    
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
        
        # Saglabāt lapu atkļūdošanai
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
        print("Lapas saturs saglabāts failā 'debug_page.html'")
        
    except Exception as e:
        print(f"Kļūda: {e}")
    finally:
        # Aizvērt pārlūkprogrammu
        if 'driver' in locals():
            driver.quit()
            print("Pārlūkprogramma aizvērta.")
    
    print("--- Skrāpis V1 pabeidzis darbu ---")

if __name__ == "__main__":
    main() 