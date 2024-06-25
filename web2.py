from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import requests

options = Options()
options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()
driver.get("https://www.google.com")
campo = driver.find_element(By.NAME,"q")
time.sleep(4)
campo.send_keys("Wikipedia", Keys.ENTER)
time.sleep(4)

header=driver.find_element(By.CSS_SELECTOR,"h3")
time.sleep(4)
header.click()
time.sleep(4)

busqueda=driver.find_element(By.NAME,"search")
time.sleep(4)
busqueda.send_keys("ESCOM", Keys.ENTER)
time.sleep(4)

html_content = driver.page_source
driver.quit()

soup = BeautifulSoup(html_content, 'html.parser')
directores = soup.find('table', class_="wikitable")
if directores:
    rows = directores.find_all('tr')
    for row in rows:  # Iterar sobre cada fila de la tabla
        cells = row.find_all('td')  # Obtener todas las celdas de la fila (td)
        if not cells:  # Si no hay celdas td, intenta con celdas de encabezado th
            cells = row.find_all('th')
        cell_texts = [cell.text.strip() for cell in cells]  # Extraer el texto de cada celda
        print(" | ".join(cell_texts))  # Imprimir el texto de cada celda separado por '|'
else:
    print("Tabla no encontrada")


