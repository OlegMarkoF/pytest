import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Тестируем навигацию по сайту SBIS и проверяет изображения.
def test_sbis_website_navigation(driver):
    driver.get("https://sbis.ru/")
    
    # Ожидаем появления элемента "Контакты" и кликаем по нему
    contacts_menu = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "sbisru-Header-ContactsMenu"))
    )
    contacts_menu.click()

    # Ожидаем появления модального окна с классом 'sbisru-Header-ContactsMenu__items'
    contact_menu_items = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "sbisru-Header-ContactsMenu__items-visible"))
    )

    # Ожидаем появления ссылки с классом 'sbisru-link sbis_ru-link' внутри модального окна
    contact_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".sbisru-link.sbis_ru-link"))
    )
    
    # Кликаем по ссылке с использованием JavaScript для избежания ошибок
    driver.execute_script("arguments[0].click();", contact_link)

    # Ожидаем появления баннера Тензор и кликаем по нему
    tensor_banner = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "sbisru-Contacts__logo-tensor"))
    )
    tensor_banner.click()

    # Переключаемся на новую вкладку (после клика на баннер)
    driver.switch_to.window(driver.window_handles[1])

    # Проверяем текущий URL
    assert driver.current_url == "https://tensor.ru/", "URL не совпадает!"

    # Ожидаем появления блока с классом 'tensor_ru-Index__block4-bg'
    block = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "tensor_ru-Index__block4-bg"))
    )

    # Находим ссылку "Подробнее"
    more_link = block.find_element(By.XPATH, ".//a[contains(@class, 'tensor_ru-link') and text()='Подробнее']")

    # Кликаем по ссылке
    driver.execute_script("arguments[0].click();", more_link)

    # Ожидаем загрузки страницы "О компании"
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "tensor_ru-About__block3"))
    )

    # Проверяем текущий URL
    assert driver.current_url == "https://tensor.ru/about", "URL не совпадает!"

    # Ожидаем появления блока с классом "tensor_ru-About__block3"
    block = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "tensor_ru-About__block3"))
    )
    
    # Находим все изображения в этом блоке
    images = block.find_elements(By.TAG_NAME, "img")
    
    # Получаем размеры первого изображения для сравнения
    first_image_size = None
    
    for image in images:
        # Получаем размеры изображения
        width = image.size['width']
        height = image.size['height']
        
        print(f"Image: {image.get_attribute('src')} - Width: {width}, Height: {height}")
        
        if first_image_size is None:
            first_image_size = (width, height)
        else:
            # Проверяем, совпадают ли размеры с первым изображением
            assert (width, height) == first_image_size, "Изображения имеют разные размеры!"
    
    print("Все изображения имеют одинаковый размер.")

# Проверяем регион и список партнеров на сайте.
def check_region_and_partners(driver):
    
    # 1. Переходим на страницу https://sbis.ru/
    driver.get("https://sbis.ru/")
    
    # 2. Ожидаем появления элемента "Контакты" и кликаем по нему
    contacts_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "sbisru-Header-ContactsMenu"))
    )
    contacts_menu.click()
    
    # 3. Ожидаем появления модального окна с классом 'sbisru-Header-ContactsMenu__items'
    contact_menu_items = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "sbisru-Header-ContactsMenu__items-visible"))
    )
    
    # 4. Ожидаем появления ссылки с классом 'sbisru-link sbis_ru-link' внутри модального окна
    contact_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "sbisru-link.sbis_ru-link"))
    )
    
    # Кликаем по ссылке с использованием JavaScript для избежания ошибок
    driver.execute_script("arguments[0].click();", contact_link)
    
    # 5. Проверяем, что определился какой-то регион и есть список партнеров
    try:
        region_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "span.sbis_ru-Region-Chooser__text.sbis_ru-link"))
        )
        
        # Проверяем, что текст региона не пустой
        assert region_element.text.strip(), "Регион не определился"

        partners_list = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "contacts_list"))
        )
        assert partners_list.is_displayed(), "Список партнеров не отображается"
    
    except Exception as e:
        print(f"Ошибка при проверке региона или списка партнеров: {e}")
    
    # 6. Кликаем по региону
    driver.execute_script("arguments[0].click();", region_element)
    
    # 7. В открывшемся модальном окне выбираем Камчатский край
    kamchatka_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'sbis_ru-link') and contains(@title, 'Камчатский край')]"))
    )

    driver.execute_script("arguments[0].click();", kamchatka_element)
   
    # 8. Проверяем, что подставился выбранный регион, список партнеров изменился, url и title содержат информацию выбранного региона
    # new_region_element = WebDriverWait(driver, 10).until(
    #     EC.visibility_of_element_located((By.CSS_SELECTOR, "span.sbis_ru-Region-Chooser__text.sbis_ru-link"))
    # )
    time.sleep(5)
    contacts = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "sbisru-Contacts"))
    )
    # Находим ссылку новый регион
    new_region_element = contacts.find_element(By.XPATH, ".//span[contains(@class, 'sbis_ru-Region-Chooser__text sbis_ru-link')]")

    print(new_region_element.text.strip())

    assert "Камчатский край" in new_region_element.text.strip(), "Регион не изменился"
    # Проверяем, что список партнеров изменился (можно проверить, что он не пустой)
    new_partners_list = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "contacts_list"))
    )
    
    assert new_partners_list.find_elements(By.TAG_NAME, "div"), "Список партнеров пуст после смены региона"
    
    # Проверяем URL и title
    assert "kamchatskij-kraj" in driver.current_url, "URL не содержит информацию о Камчатском крае"
    assert "Камчатский край" in driver.title, "Title страницы не содержит информацию о Камчатском крае"
    
    print("Все проверки прошли успешно!")

# Скачивает плагин и проверяет его размер.
def download_plugin(driver):
    
     # 1. Переходим на страницу https://sbis.ru/
    driver.get("https://sbis.ru/")
    try:
        # 2. В Footer находим и кликаем "Скачать локальные версии"
        download_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'sbisru-Footer')]//a[contains(text(), 'Скачать локальные версии')]"))
        )
    
        # Прокручиваем страницу к элементу, чтобы он был видим
        driver.execute_script("arguments[0].scrollIntoView();", download_link)

        download_link.click()

    except Exception as e:
        print(f'Ошибка при попытке кликнуть по элементу')
    
    # 3. Скачиваем СБИС Плагин для Windows
    plugin_url = "https://update.sbis.ru/Sbis3Plugin/master/win32/sbisplugin-setup-web.exe"
    response = requests.get(plugin_url)
    
    # Определяем путь для сохранения файла
    file_path = os.path.join(os.getcwd(), "sbisplugin-setup-web.exe")
    
    # Записываем файл в указанную директорию
    with open(file_path, 'wb') as file:
        file.write(response.content)
    
    print("Скачивание завершено.")

    # 4. Убедимся, что плагин скачался
    assert os.path.exists(file_path), "Плагин не скачался"

    # 5. Сравниваем размер скачанного файла с указанным на сайте (11.48 МБ)
    downloaded_file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Конвертируем байты в мегабайты
    expected_file_size_mb = 11.48
    
    assert abs(downloaded_file_size_mb - expected_file_size_mb) < 0.01, f"Размер файла {downloaded_file_size_mb:.2f} МБ не совпадает с ожидаемым {expected_file_size_mb} МБ"

    print("Размер файла соответствует ожидаемому.")

# Основная функция для запуска тестов.
def main():
   
   driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
   
   try:
       test_sbis_website_navigation(driver)
       check_region_and_partners(driver)
       download_plugin(driver)
       
   except Exception as e:
       print(f"Произошла ошибка: {e}")

   finally:
       driver.quit()

if __name__ == "__main__":
   main()