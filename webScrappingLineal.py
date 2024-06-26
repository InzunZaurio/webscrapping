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
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

def scrape_data():
    lugar = input("Ingresa la alcaldía: ")

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

    # Buscar alcaldía
    alcaldia = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Busca por alcaldía, colonia o estado"]')
    alcaldia.send_keys(lugar)
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

def train_and_predict():
    # Crear una sesión de Spark
    spark = SparkSession.builder.getOrCreate()

    # Cargar el archivo CSV generado
    direccion = "departamentos.csv"  # Asegúrate de que la ruta al archivo sea correcta
    sparkArchivo = spark.read.option("header", "true")\
                             .option("delimiter", ",")\
                             .option("inferSchema", "true")\
                             .csv(direccion)

    # Seleccionar las columnas relevantes
    columns = sparkArchivo.select("Precio", "Superficie", "Recamaras", "Baños", "Estacionamientos")
    columns.show()

    # Ensamblar las características
    assembler = VectorAssembler(inputCols=['Superficie', 'Recamaras', 'Baños', 'Estacionamientos'], 
                                outputCol='Caracteristicas')

    data = assembler.transform(columns)
    data = data.select('Caracteristicas', 'Precio')

    # Dividir los datos en conjuntos de entrenamiento y prueba
    train_data, test_data = data.randomSplit([0.8, 0.2], seed=1234)

    # Entrenar el modelo de regresión lineal
    lin_reg = LinearRegression(featuresCol='Caracteristicas', labelCol='Precio')
    fit = lin_reg.fit(train_data)

    # Evaluar el modelo en el conjunto de prueba
    predictions = fit.transform(test_data)
    evaluator = RegressionEvaluator(labelCol='Precio', predictionCol='prediction', metricName='rmse')
    rmse = evaluator.evaluate(predictions)

    # Mostrar los resultados del modelo
    print("\n============= MODELO DE REGRESION =============\n")
    print(f"Intercept: {fit.intercept}")
    print(f"Coefficients: {fit.coefficients}")
    print(f"Root Mean Squared Error (RMSE): {rmse}")
    print("\n\n")

    # Realizar predicciones en un bucle
    while True:
        print("\n============= REGRESION =============\n")
        x1 = float(input("Ingresa la Superficie: "))
        x2 = float(input("Ingresa el número de Recamaras: "))
        x3 = float(input("Ingresa el número de Baños: "))
        x4 = float(input("Ingresa el número de Estacionamientos: "))

        yPred = float(fit.intercept) + (float(fit.coefficients[0]) * x1) + \
                (float(fit.coefficients[1]) * x2) + \
                (float(fit.coefficients[2]) * x3) + \
                (float(fit.coefficients[3]) * x4)

        print("El precio predicho es: ", yPred)
        print("El precio predicho más el RMSE es: ", yPred + rmse)
        if yPred - rmse < 0:
            print("El precio predicho menos el RMSE es negativo")
        elif yPred - rmse >= 0:
            print("El precio predicho menos el RMSE es:", yPred - rmse)
        
        # Preguntar si el usuario desea realizar otra predicción
        continuar = input("¿Deseas realizar otra predicción? (s/n): ")
        if continuar.lower() != 's':
            break

if __name__ == "__main__":
    scrape_data()
    train_and_predict()
