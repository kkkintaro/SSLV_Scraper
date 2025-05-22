from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import time
import datetime
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# konstantes
BASE_URL = "https://www.ss.lv"
CARS_URL = "https://www.ss.lv/lv/transport/cars/"
DATA_FILE = "ss_lv_cars_data.txt"  # Fails tiks pārrakstīts katrā palaišanas reizē

# filtru konstantes
MIN_YEAR = "2016"  # minimālais gads
MAX_PRICE = "20000"  # maksimālā cena
TRANSMISSION = "Automāts"  # automātiskā transmisija

PAGE_LIMIT = 10
PAGE_LOAD_DELAY = 2

# driver init
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")
    
    # macOS support
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        chrome_options.add_argument("--disable-features=Metal")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("chrome driver init")
        return driver
    except Exception as e:
        print(f"error while chrome driver init: {e}")
        
        try:
            # macOS support
            if platform.system() == "Darwin":
                driver = webdriver.Chrome(options=chrome_options)
                print("chrome init (macOS)")
                return driver
        except Exception as e2:
            print(f"error: {e2}")
            print("chrome is not installed")
            raise

def set_filters_manually(driver):
    try:
        print("applying filters")
        # Atver pamatlapu
        driver.get(CARS_URL)
        print("SS.LV auto lapa atverta")
        time.sleep(2)
        
        # Gada filtrs
        try:
            year_min_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "topt[18][min]"))
            )
            year_min_field.clear()
            year_min_field.send_keys(MIN_YEAR)
            print("Gada filtrs iestatīts")
        except Exception as e:
            print(f"Kļūda ar gada filtru: {e}")
        
        # Cenas filtrs
        try:
            price_max_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "topt[8][max]"))
            )
            price_max_field.clear()
            price_max_field.send_keys(MAX_PRICE)
            print("Cenas filtrs iestatīts")
        except Exception as e:
            print(f"Kļūda ar cenas filtru: {e}")
        
        # Transmisijas filtrs
        try:
            driver.execute_script("""
                var options = document.getElementsByName('opt[34]');
                for (var i = 0; i < options.length; i++) {
                    if (options[i].value == '1') {
                        options[i].click();
                        break;
                    }
                }
            """)
            print("Transmisijas filtrs iestatīts")
        except Exception as e:
            print(f"error: {e}")
        
        # find search button
        try:
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "sbtn"))
            )
            search_button.click()
            print("Meklēšanas poga nospiesta")
        except Exception as e:
            print(f"error: {e}")
            try:
                driver.execute_script("document.getElementById('sbtn').click();")
                print("Meklēšanas poga nospiesta]")
            except Exception as e2:
                print(f"error: {e2}")
        
        time.sleep(3)
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "filter_frm"))
            )
            print("page scrapped")
            
            filtered_url = driver.current_url
            print(f"Filtrētais URL: {filtered_url}")
            
            return True
        except Exception as e:
            print(f"error: {e}")
            return False
            
    except Exception as e:
        print(f"error: {e}")
        return False

def parse_ads_from_page(driver, apply_filters=True):
    """
    Izgūt sludinājumu datus no pašreizējās lapas.
    """
    ads_data = []
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Atrast sludinājumu tabulu
        table = soup.find('form', {'id': 'filter_frm'})
        if not table:
            print("Nevarēja atrast sludinājumu tabulu")
            return ads_data
        
        # Atrast visas sludinājumu rindas
        ad_rows = table.select('tr[id^="tr_"]')
        
        for row in ad_rows:
            try:
                columns = row.find_all('td')
                
                if len(columns) < 6:  # if all columns are not present, skip
                    continue
                
                # get saiti un virsrakstu
                link_element = columns[2].find('a')
                if not link_element:
                    continue
                    
                link = urljoin(BASE_URL, link_element.get('href'))
                title = link_element.text.strip()
                
                year_text = columns[3].text.strip()
                volume = columns[4].text.strip()
                mileage = columns[5].text.strip()
                
                # Cena var būt 6. vai 7. kolonnā, atkarībā no lapas struktūras
                price = ""
                for i in range(6, min(9, len(columns))):
                    if columns[i].text.strip() and "€" in columns[i].text:
                        price = columns[i].text.strip()
                        break
                
                year = 0
                try:
                    # Gads var būt "2016" vai "2016."
                    year = int(re.sub(r'[^0-9]', '', year_text))
                except:
                    year = 0
                
                # Pārbaudīt cenu
                price_value = 0
                try:
                    # Cena var būt "20 000 €" vai "20.000 €"
                    price_clean = re.sub(r'[^0-9]', '', price)
                    price_value = int(price_clean) if price_clean else 0
                except:
                    price_value = 0
                
                has_auto_transmission = False
                if "automāt" in title.lower() or "autom" in title.lower() or "aut." in title.lower():
                    has_auto_transmission = True
                
                # filtri
                if apply_filters:
                    
                    if year < int(MIN_YEAR) and year > 0:
                        continue
                    if price_value > int(MAX_PRICE) and price_value > 0:
                        continue
                
                ad_data = {
                    'title': title,
                    'link': link,
                    'year': year_text,
                    'year_value': year,
                    'volume': volume,
                    'mileage': mileage,
                    'price': price,
                    'price_value': price_value,
                    'has_auto_transmission': has_auto_transmission
                }
                
                ads_data.append(ad_data)
                
            except Exception as e:
                print(f"error: {e}")
                continue
        
        print(f"Veiksmīgi izgūti {len(ads_data)} sludinājumi.")
        
    except Exception as e:
        print(f"error: {e}")
    
    return ads_data


def go_to_next_page(driver):
    try:
        next_page_elements = driver.find_elements(By.CSS_SELECTOR, "a.navi[rel='next']")
        
        if not next_page_elements:
            print("Nav nākamās lapas.")
            return False
        
        current_url = driver.current_url
        
        next_page_elements[0].click()
        
        time.sleep(PAGE_LOAD_DELAY)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "filter_frm"))
        )
        new_url = driver.current_url
        if new_url == current_url:
            print("Nākamā lapa netika ielādēta (URL nav mainījies).")
            return False
        
        print(f"Veiksmīgi pāriets uz nākamo lapu: {new_url}")
        return True
        
    except Exception as e:
        print(f"error: {e}")
        return False

# Rezultātu saglabāšana
def save_ads_to_file(ads_data):

    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as file:

            file.write(f"SS.LV Auto sludinājumi - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"Filtri: gads >= {MIN_YEAR}, cena <= {MAX_PRICE} EUR, transmisija: {TRANSMISSION}\n")
            file.write("=" * 80 + "\n\n")
            
            for i, ad in enumerate(ads_data, 1):
                file.write(f"{i}. {ad['title']}\n")
                file.write(f"   Saite: {ad['link']}\n")
                file.write(f"   Gads: {ad['year']}, Tilpums: {ad['volume']}, Nobraukums: {ad['mileage']}\n")
                file.write(f"   Cena: {ad['price']}\n")
                file.write(f"   Automātiskā ātrumkārba: {'Jā' if ad['has_auto_transmission'] else 'Nav zināms'}\n")
                file.write("-" * 80 + "\n")
            
            file.write(f"\nKopā atrasti {len(ads_data)} sludinājumi, kas atbilst filtriem.\n")
        
        print(f"Dati veiksmīgi saglabāti failā: {DATA_FILE}")
        return True
        
    except Exception as e:
        print(f"error writing file {e}")
        return False

# Galvenā funkcija
def main():
    """
    Skripta galvenā izpildes funkcija.
    """
    print("--- SS.LV Auto Skrāpja Palaišana ---")
    print(f"Operētājsistēma: {platform.system()} {platform.release()} ({platform.machine()})")
    
    all_ads = []
    current_page = 1
    
    try:
        driver = setup_driver()
        
        if set_filters_manually(driver):

            while current_page <= PAGE_LIMIT:
                print(f"Apstrādā lapu #{current_page}")
                
                page_ads = parse_ads_from_page(driver, apply_filters=True)
                
                if page_ads:
                    all_ads.extend(page_ads)
                    print(f"Pievienoti {len(page_ads)} filtrēti sludinājumi no lapas #{current_page}")
                else:
                    print(f"Nav atrasti sludinājumi lapā #{current_page}")
                
                if not go_to_next_page(driver) or not page_ads:
                    print("Vairs nav lapu vai sludinājumu. Beidz skrāpēšanu.")
                    break
                
                current_page += 1
        
        if all_ads:
            save_ads_to_file(all_ads)
            print(f"Kopā savākti {len(all_ads)} sludinājumi, kas atbilst filtriem.")
        else:
            print("error no ads found by filters")
        
    except Exception as e:
        print(f"Kļūda: {e}")
    finally:
        # Aizvērt pārlūkprogrammu
        if 'driver' in locals():
            driver.quit()
            print("Pārlūkprogramma aizvērta.")
    
    print("--- Skrāpis pabeidzis darbu ---")

if __name__ == "__main__":
    main() 
