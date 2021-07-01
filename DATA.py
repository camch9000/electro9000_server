# coding=utf-8
import os

OS_PATH = os.path.dirname(os.path.abspath(__file__)) #Path donde se ejecuta la aplicación

#LOG
LOG_PATH = os.path.join(OS_PATH,"logs") #Path para la carpeta de logs
LOG_PATH_LOG = "log.log" #Nombre del archivo de log

#PATH
PATH_ARCHIVOS = os.path.join(OS_PATH,"datos") # Path donde se guardaran los archivos
PATH_ARCHIVOS_PVPC = os.path.join(PATH_ARCHIVOS,"pvpc") # Path donde se guardara los datos de precios PVPC

#Link API pvpc
LINK_API_PVPC = "https://api.esios.ree.es/archives/70/download_json?locale=es&date=[FECHA_DIA]"

DIVISOR_PRECIO = 1000

DIAS_PROMEDIO = 30

TIEMPO_ESPERA_DIA = 10