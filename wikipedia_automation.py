from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re

def highlight_element(driver, element):
    """Выделяет элемент на странице"""
    # Выделяем сам элемент
    driver.execute_script(
        "arguments[0].style.backgroundColor = 'yellow';"
        "arguments[0].style.border = '3px solid red';"
        "arguments[0].style.padding = '2px';"
        "arguments[0].style.fontWeight = 'bold';",
        element
    )
    
    # Пытаемся выделить также родительскую строку таблицы, если это таблица
    try:
        row = element.find_element(By.XPATH, "./ancestor::tr")
        driver.execute_script(
            "arguments[0].style.backgroundColor = '#ffffcc';"
            "arguments[0].style.border = '2px solid orange';",
            row
        )
    except:
        pass

def main():
    # Настройка Chrome
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    
    # Инициализация драйвера
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Шаг 1: Открыть Wikipedia
        print("Открываю https://ru.wikipedia.org...")
        driver.get("https://ru.wikipedia.org")
        time.sleep(2)
        
        # Шаг 2: Найти поле поиска и ввести "Земля"
        print("Ищу поле поиска...")
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_box.clear()
        search_box.send_keys("Земля")
        time.sleep(1)
        
        # Шаг 3: Нажать Enter или кнопку поиска
        print("Выполняю поиск...")
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        
        # Шаг 4: Найти информацию о содержании кислорода в атмосфере
        print("Ищу информацию о содержании кислорода в атмосфере...")
        
        # Прокрутить страницу, чтобы найти информацию об атмосфере
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
        time.sleep(2)
        
        oxygen_found = False
        target_element = None
        
        # Сначала ищем в таблицах (информация часто находится в таблицах состава атмосферы)
        print("Ищу в таблицах...")
        try:
            tables = driver.find_elements(By.TAG_NAME, "table")
            for table in tables:
                table_text = table.text.lower()
                if 'кислород' in table_text or 'oxygen' in table_text or 'атмосфер' in table_text:
                    # Ищем ячейки таблицы с нужным значением
                    cells = table.find_elements(By.TAG_NAME, "td")
                    for cell in cells:
                        cell_text = cell.text
                        # Проверяем наличие 20,95 или 20.95
                        if ('20,95' in cell_text or '20.95' in cell_text) and ('%' in cell_text or 'процент' in cell_text.lower()):
                            # Проверяем контекст - должен быть про кислород
                            row_text = cell.find_element(By.XPATH, "./..").text.lower()
                            if 'кислород' in row_text or 'oxygen' in row_text:
                                target_element = cell
                                oxygen_found = True
                                print(f"Найдено в таблице: {cell_text}")
                                break
                    if oxygen_found:
                        break
        except Exception as e:
            print(f"Ошибка при поиске в таблицах: {e}")
        
        # Если не нашли в таблицах, ищем в тексте страницы
        if not oxygen_found:
            print("Ищу в тексте страницы...")
            # Ищем различные варианты написания
            search_patterns = ["20,95", "20.95"]
            
            for pattern in search_patterns:
                try:
                    # Ищем элементы, содержащие это значение
                    xpath = f"//*[contains(text(), '{pattern}')]"
                    elements = driver.find_elements(By.XPATH, xpath)
                    
                    for elem in elements:
                        try:
                            text = elem.text
                            # Проверяем, что это значение с процентами
                            if pattern in text and '%' in text:
                                # Проверяем контекст - ищем в родительских элементах
                                parent = elem.find_element(By.XPATH, "./..")
                                parent_text = parent.text.lower()
                                
                                # Также проверяем соседние элементы
                                try:
                                    row = elem.find_element(By.XPATH, "./ancestor::tr")
                                    row_text = row.text.lower()
                                except:
                                    row_text = ""
                                
                                # Проверяем, что это про кислород/атмосферу
                                if ('кислород' in parent_text or 'кислород' in row_text or 
                                    'oxygen' in parent_text or 'oxygen' in row_text or
                                    'атмосфер' in parent_text or 'атмосфер' in row_text):
                                    # Дополнительная проверка - значение должно быть около 20.95
                                    numbers = re.findall(r'20[.,]\d+', text)
                                    if numbers:
                                        num = float(numbers[0].replace(',', '.'))
                                        if 20.9 <= num <= 21.0:  # Допускаем небольшую погрешность
                                            target_element = elem
                                            oxygen_found = True
                                            print(f"Найдено в тексте: {text[:100]}...")
                                            break
                        except:
                            continue
                    if oxygen_found:
                        break
                except:
                    continue
        
        # Если все еще не нашли, ищем более широко
        if not oxygen_found:
            print("Выполняю расширенный поиск...")
            try:
                # Ищем все элементы с "20" и проверяем контекст
                all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '20')]")
                for elem in all_elements:
                    try:
                        text = elem.text
                        if ('20,95' in text or '20.95' in text) and '%' in text:
                            # Получаем больше контекста
                            try:
                                section = elem.find_element(By.XPATH, "./ancestor::div[contains(@class, 'mw-parser-output')]//*[contains(text(), 'кислород') or contains(text(), 'атмосфер')]")
                                target_element = elem
                                oxygen_found = True
                                print(f"Найдено (расширенный поиск): {text[:100]}...")
                                break
                            except:
                                # Проверяем, есть ли рядом текст про кислород
                                parent_text = elem.find_element(By.XPATH, "./ancestor::*[position()<=5]").text.lower()
                                if 'кислород' in parent_text or 'атмосфер' in parent_text:
                                    target_element = elem
                                    oxygen_found = True
                                    print(f"Найдено (расширенный поиск): {text[:100]}...")
                                    break
                    except:
                        continue
            except Exception as e:
                print(f"Ошибка при расширенном поиске: {e}")
        
        if oxygen_found and target_element:
            # Прокручиваем к элементу
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_element)
            time.sleep(1)
            
            # Выделяем элемент
            print("Выделяю найденную информацию...")
            highlight_element(driver, target_element)
            time.sleep(1)
            
            # Делаем скриншот
            print("Делаю скриншот...")
            driver.save_screenshot("wikipedia_earth_oxygen.png")
            print("Скриншот сохранен как 'wikipedia_earth_oxygen.png'")
            
            # Проверяем значение
            element_text = target_element.text
            if '20,95' in element_text or '20.95' in element_text:
                print(f"[OK] Подтверждено: найдено значение 20,95%")
                print(f"  Контекст: {element_text[:200]}...")
            else:
                print("⚠ Значение найдено, но требует проверки")
        else:
            print("⚠ Не удалось найти информацию о содержании кислорода 20,95%")
            print("Делаю скриншот всей страницы для проверки...")
            driver.save_screenshot("wikipedia_earth_full.png")
        
        # Ждем немного перед закрытием
        print("\nОжидание 5 секунд перед закрытием браузера...")
        time.sleep(5)
        
    except Exception as e:
        print(f"Ошибка: {e}")
        driver.save_screenshot("error_screenshot.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
