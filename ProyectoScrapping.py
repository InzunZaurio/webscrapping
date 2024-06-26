from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import pandas as pd
import re



lugar=input("Ingresa la alcaldía: ")

# Configuración de las opciones del navegador
options = Options()
options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"

# Inicializar el driver de Chrome con las opciones configuradas
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()
driver.get("https://www.mudafy.com.mx/venta/departamentos")
time.sleep(4)

# Cerrar el mapa emergente si aparece
try:
    eliminarMapa = driver.find_element(By.CLASS_NAME, "close-button")
    time.sleep(4)
    eliminarMapa.click()
    time.sleep(4)
except:
    pass

alcaldia=driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Busca por alcaldía, colonia o estado"]')
alcaldia.send_keys(""+lugar)
time.sleep(5)
alcaldia.send_keys(Keys.ENTER)
time.sleep(5)

# Extraer información de los departamentos
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'html.parser')

departamentos = soup.find_all('div', class_='card--allow-favorites')

data = []

for depto in departamentos:
    try:
        quick_info = depto.find('div', class_='quick-info')
        info = quick_info.find_all('span', class_='quick-info-text')
        
        # Asumir que siempre existen los 4 elementos y acceder directamente
        superficie = re.sub(r'\D', '', info[0].text.strip())  # Eliminar cualquier carácter no numérico
        estacionamientos = re.sub(r'\D', '', info[1].text.strip())  # Eliminar cualquier carácter no numérico
        baños = re.sub(r'\D', '', info[2].text.strip())  # Eliminar cualquier carácter no numérico
        recamaras = re.sub(r'\D', '', info[3].text.strip())  # Eliminar cualquier carácter no numérico

        precio = re.sub(r'[^\d]', '', depto.find('div', class_='value').text.strip())  # Eliminar cualquier carácter no numérico

        data.append({
            'Superficie': superficie,
            'Recamaras': recamaras,
            'Baños': baños,
            'Estacionamientos': estacionamientos,
            'Precio': precio
        })
    except Exception as e:
        print(f"Error al procesar un departamento: {e}")
        continue

driver.quit()

# Guardar los datos en un DataFrame y exportar a CSV
df = pd.DataFrame(data)
df.to_csv('departamentos.csv', index=False)

print("Datos guardados en departamentos.csv")
