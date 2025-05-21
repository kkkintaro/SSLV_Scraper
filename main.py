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

def save_ads_to_file_overwrite(ads_data_list, filepath=DATA_FILE):
    """
    Saglabā visus iegūtos sludinājumus failā, katru reizi pārrakstot tā saturu.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    num_ads_found = len(ads_data_list)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"--- SKRAPĒŠANAS REZULTĀTI: {timestamp} --- ({num_ads_found} sludinājumi atrasti) ---\n")
            if not ads_data_list:
                f.write("(Netika atrasti sludinājumi ar norādītajiem fiksētajiem kritērijiem.)\n")
            for ad in ads_data_list:
                f.write(f"Virsraksts: {ad.get('title', 'N/A')}\n")
                f.write(f"Saite: {ad.get('link', 'N/A')}\n")
                f.write(f"Modelis: {ad.get('model', 'N/A')}\n")
                f.write(f"Gads: {ad.get('year', 'N/A')}\n")
                f.write(f"Tilpums: {ad.get('volume', 'N/A')}\n")
                f.write(f"Nobraukums: {ad.get('mileage', 'N/A')}\n")
                f.write(f"Cena: {ad.get('price', 'N/A')}\n")
                f.write("-" * 30 + "\n")
            f.write("\n")
        print(f"Saglabāti {num_ads_found} sludinājumi failā '{filepath}' (fails tika pārrakstīts).")
    except IOError as e:
        print(f"Kļūda, rakstot datu failā '{filepath}': {e}")

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

def set_filters(driver):
    """
    Iestatīt filtrus SS.LV meklēšanas formā.
    """
    # Iestatīt minimālo gadu
    year_min_selector = driver.find_element(By.NAME, "topt[18][min]")
    for option in year_min_selector.find_elements(By.TAG_NAME, "option"):
        if option.get_attribute("value") == MIN_YEAR:
            option.click()
            print(f"Iestatīts minimālais gads: {MIN_YEAR}")
            break
    
    # Iestatīt maksimālo cenu
    max_price_input = driver.find_element(By.NAME, "topt[8][max]")
    max_price_input.clear()
    max_price_input.send_keys(MAX_PRICE)
    print(f"Iestatīta maksimālā cena: {MAX_PRICE}")
    
    # Iestatīt automātisko transmisiju
    try:
        # Konkrēts elements pēc nosaukuma (zināms no iepriekšējās analīzes)
        transmission_select = driver.find_element(By.NAME, "opt[35]")
        # Izvēlamies opciju ar kodu 497 (automātiskā ātrumkārba)
        for option in transmission_select.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == "497":
                option.click()
                print(f"Iestatīta automātiskā ātrumkārba, kods: 497")
                return True
    except NoSuchElementException:
        print("Neizdevās atrast konkrēto ātrumkārbas filtru (opt[35]). Meklējam alternatīvu...")
        
        # Plašāka meklēšana
        try:
            # Atrodam visus select elementus un meklējam to, kas satur "automāts"
            all_selects = driver.find_elements(By.TAG_NAME, "select")
            for select in all_selects:
                select_id = select.get_attribute("id")
                select_name = select.get_attribute("name")
                print(f"Analizē select elementu: ID={select_id}, NAME={select_name}")
                
                # Pārbaudām visas opcijas
                options = select.find_elements(By.TAG_NAME, "option")
                for option in options:
                    option_text = option.text.lower()
                    option_value = option.get_attribute("value")
                    
                    if "automāt" in option_text or "автомат" in option_text:
                        print(f"Atrasts automātiskās ātrumkārbas variants: '{option_text}' ar vērtību '{option_value}'")
                        option.click()
                        print(f"Iestatīta automātiskā ātrumkārba")
                        return True
        except Exception as e:
            print(f"Neizdevās iestatīt ātrumkārbas filtru: {e}")
    
    return False

def click_search_button(driver, max_price_input):
    """
    Meklēt un nospiest meklēšanas pogu.
    """
    try:
        # Vispirms mēģinām atrast pēc tipa un vērtības
        search_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Meklēt']")
        print("Atrasta meklēšanas poga ar vērtību 'Meklēt'")
        # Pauze pirms nospiešanas
        time.sleep(1)
        search_button.click()
        print("Meklēšanas poga nospiesta")
        return True
    except NoSuchElementException:
        print("Nav atrasta poga ar tekstu 'Meklēt', meklējam jebkuru submit pogu...")
        
        try:
            # Meklējam visas submit pogas un izvadām tās atkļūdošanai
            submit_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
            print(f"Atrastas submit pogas: {len(submit_buttons)}")
            
            for idx, button in enumerate(submit_buttons):
                button_value = button.get_attribute("value")
                button_id = button.get_attribute("id")
                print(f"Poga #{idx+1}: value='{button_value}', id='{button_id}'")
            
            if submit_buttons:
                # Nospiežam pirmo atrasto submit pogu
                submit_buttons[0].click()
                print(f"Nospiesta pirmā atrastā submit poga ar value='{submit_buttons[0].get_attribute('value')}'")
                return True
            else:
                # Ja pogu nav, mēģinām iesniegt formu
                filter_form = driver.find_element(By.ID, "filter_frm")
                driver.execute_script("arguments[0].submit();", filter_form)
                print("Forma iesniegta ar JavaScript")
                return True
        except Exception as e:
            print(f"Kļūda, meklējot un spiežot pogu: {e}")
            try:
                # Pēdējais mēģinājums - nospiest Enter cenas laukā
                max_price_input.send_keys("\n")
                print("Nospiesta Enter taustiņš cenas laukā")
                return True
            except:
                print("Neizdevās iesniegt formu nekādā veidā")
                return False

def process_pagination(driver, all_collected_ads):
    """
    Apstrādāt pagināciju un iegūt datus no vairākām lapām.
    """
    # Apstrādājam rezultātus no pirmās lapas
    html_content_page1 = driver.page_source
    ads_on_page1 = parse_ads_from_page(html_content_page1)
    print(f"Lapā 1 atrasti {len(ads_on_page1)} sludinājumi.")
    all_collected_ads.extend(ads_on_page1)
    
    # Ja ir sludinājumi un atļauts skatīt vairāk lapu, mēģinām pārlūkot citas lapas
    if ads_on_page1 and PAGE_LIMIT > 1:
        current_page = 1
        while current_page < PAGE_LIMIT:
            try:
                # Meklējam saiti uz nākamo lapu
                next_page_links = driver.find_elements(By.CSS_SELECTOR, "a.navi[rel='next']")
                if not next_page_links:
                    print("Nav atrasta saite uz nākamo lapu. Pārtrauc pagināciju.")
                    break
                
                # Klikšķinām uz saites uz nākamo lapu
                next_page_links[0].click()
                current_page += 1
                print(f"Pārejam uz lapu {current_page}...")
                
                # Gaidām, līdz lapa ielādējas
                time.sleep(PAGE_LOAD_DELAY)
                
                # Iegūstam lapas HTML
                html_content_page_n = driver.page_source
                
                # Apstrādājam rezultātus
                ads_on_subsequent_page = parse_ads_from_page(html_content_page_n)
                print(f"Lapā {current_page} atrasti {len(ads_on_subsequent_page)} sludinājumi.")
                
                if not ads_on_subsequent_page:
                    print(f"Lapā {current_page} netika atrasti sludinājumi. Pieņem, ka sasniegtas rezultātu beigas.")
                    break
                
                all_collected_ads.extend(ads_on_subsequent_page)
            except Exception as e:
                print(f"Kļūda, apstrādājot lapu {current_page}: {e}")
                break
    
    return all_collected_ads

# --- Galvenā funkcija ---
def main():
    """
    Skripta galvenā izpildes funkcija - V4: Optimizēta gala versija
    """
    print("--- SS.LV Auto Skrāpja (Versija 4: Optimizēta gala versija) Palaišana ---")
    print(f"Filtri: Gads no={MIN_YEAR}, Cena līdz={MAX_PRICE}, Transmisija={TRANSMISSION}")
    print(f"Maksimālais lapu skaits: {PAGE_LIMIT}")
    print(f"Datu fails: {DATA_FILE} (tiks pārrakstīts)")
    
    all_collected_ads = []
    
    try:
        # Iestatīt Selenium pārlūkprogrammu
        driver = setup_driver()
        
        # Atvert SS.LV automašīnu lapu
        print(f"Atver SS.LV auto lapu: {CARS_URL}")
        driver.get(CARS_URL)
        
        # Gaidīt, līdz lapa ielādējas
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "filter_frm"))
        )
        
        print("Lapa ielādēta, iestatām filtrus...")
        
        # Iestatīt filtrus
        set_filters(driver)
        
        # Saglabājam HTML pirms pogas nospiešanas atkļūdošanai
        with open("debug_before_button_click.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        
        # Veidojam ekrānuzņēmumu atkļūdošanai
        driver.save_screenshot("before_search_click.png")
        
        print("Meklējam meklēšanas pogu...")
        
        # Iegūt atsauci uz cenas ievades lauku (nepieciešams klikšķināšanas funkcijai)
        max_price_input = driver.find_element(By.NAME, "topt[8][max]")
        
        # Meklēšanas pogas meklēšana un klikšķināšana
        if not click_search_button(driver, max_price_input):
            print("Neizdevās nospiesti meklēšanas pogu. Mēģinām turpināt...")
        
        # Veidojam ekrānuzņēmumu pēc nospiešanas
        time.sleep(2)
        driver.save_screenshot("after_search_click.png")
        
        # Gaidām, kamēr mainās URL (rezultātu lapas pazīme)
        try:
            WebDriverWait(driver, 10).until(
                lambda d: "filter" in d.current_url
            )
            print(f"Ielādēta rezultātu lapa: {driver.current_url}")
        except TimeoutException:
            print("Pārsniegts gaidīšanas laiks, mēģinām turpināt...")
        
        # Saglabājam rezultātu HTML atkļūdošanai
        with open("debug_initial_response.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        
        # Veidojam ekrānuzņēmumu rezultātu lapai
        driver.save_screenshot("search_results_page.png")
        
        # Apstrādājam rezultātus un pagināciju
        all_collected_ads = process_pagination(driver, all_collected_ads)
        
    except Exception as e:
        print(f"Galvenā kļūda: {e}")
    finally:
        # Aizvērt pārlūkprogrammu
        if 'driver' in locals():
            driver.quit()
            print("Pārlūkprogramma aizvērta.")
    
    print(f"\nKopā savākti {len(all_collected_ads)} sludinājumi.")
    
    # Saglabājam datus failā
    save_ads_to_file_overwrite(all_collected_ads)
    
    # Izdrukāt pirmos 3 sludinājumus kā paraugu
    if all_collected_ads:
        print(f"\n--- Pirmie 3 atrastie sludinājumi (paraugs): ---")
        for i, ad_item in enumerate(all_collected_ads[:3]):
            print(f"  #{i+1}: {ad_item.get('title', 'N/A')} | Cena: {ad_item.get('price', 'N/A')}")
    else:
        print("\nNetika atrasti sludinājumi ar dotajiem kritērijiem.")
    
    print("--- Skrāpis V4 pabeidzis darbu ---")

if __name__ == "__main__":
    main() 
