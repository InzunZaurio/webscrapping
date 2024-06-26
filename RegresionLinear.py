from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

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
    if(yPred-rmse<0):
        print("El precio predicho menos el RMSE es negativo")
    elif(yPred-rmse>=0):
        print("El precio predicho menos el RMSE es:", yPred - rmse)
    
    # Preguntar si el usuario desea realizar otra predicción
    continuar = input("¿Deseas realizar otra predicción? (s/n): ")
    if continuar.lower() != 's':
        break
