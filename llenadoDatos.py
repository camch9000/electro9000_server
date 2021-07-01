# coding=utf-8
import requests, os, json, fcntl, io, time
from datetime import timedelta, datetime
import simplejson as json2
from threading import Timer


import DATA as DATA
import Log as LOG

class llenadoDatos:

    log_file_name = ""
    nombreClase = "ShowMeText_Offline_Conexion"

    def __init__(self,log_name):
        self.log_file_name = log_name

    # Para recorrer fechas
    def daterange(self,start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    # Fechas en formato %Y-%m-%d
    def descargarArchivosFecha(self,fechaDesde,fechaHasta):
        mensajeError = self.nombreClase + "-descargarArchivosFecha"
        try:

            # Transforma los string en datetime
            fechaInicio = datetime.strptime(fechaDesde, '%Y-%m-%d')
            fechaFin = datetime.strptime(fechaHasta, '%Y-%m-%d') + timedelta(days=1)

            # Para seguir revisando hasta que cargue el dia siguiente
            recorrer = True

            # Fecha del dia actual
            fechaActual = datetime.today()
            pathArchivoDiaActual = os.path.join(DATA.PATH_ARCHIVOS_PVPC,(fechaActual.strftime("%Y-%m-%d")+".json"))
            encontroActual = 0

            # Fecha del dia siguiente
            fechaSiguiente = datetime.today() + timedelta(days=1)
            pathArchivoDiaSiguiente = os.path.join(DATA.PATH_ARCHIVOS_PVPC,(fechaSiguiente.strftime("%Y-%m-%d")+".json"))
            encontroSiguiente = 0

            while recorrer:

                # Recorre los dias dentro del rango
                for dia in self.daterange(fechaInicio,fechaFin):

                    # Crea el path del archivo para el dia
                    pathArchivoDia = os.path.join(DATA.PATH_ARCHIVOS_PVPC,(dia.strftime("%Y-%m-%d")+".json"))

                    if(pathArchivoDia == pathArchivoDiaActual): encontroActual = 1
                    elif(pathArchivoDia == pathArchivoDiaSiguiente): encontroSiguiente = 1

                    # Comprueba si el archivo no existe
                    if(not os.path.isfile(pathArchivoDia)):

                        # Busca los datos del archivo
                        linkApi = DATA.LINK_API_PVPC.replace("[FECHA_DIA]",dia.strftime("%Y-%m-%d"))
                        req = requests.get(linkApi)

                        # Comprueba la respuesta
                        if(not req.ok):
                            LOG.write_to_log(self.log_file_name+"_ERROR",mensajeError,"ERROR","Error llamando API PVPC ("+linkApi+")->"+str(req.text))
                            continue

                        # obtiene los datos
                        response = json.loads(req.text)

                        # Variable para almacenar los datos limpios
                        datosDia = []

                        if(not "PVPC" in response): continue

                        LOG.write_to_log(self.log_file_name,mensajeError,"INFO","Encontro datos para dia "+dia.strftime("%Y-%m-%d"))

                        # Recorre y limpia los datos 
                        for data in response["PVPC"]:

                            hora = int(data["Hora"].split("-")[0])
                            pcb = round(float(data["PCB"].replace(",",".")) / DATA.DIVISOR_PRECIO,5)
                            cym = round(float(data["CYM"].replace(",",".")) / DATA.DIVISOR_PRECIO,5)

                            # prom = self.calcularPromedio(fecha=dia,hora=hora,dias=DATA.DIAS_PROMEDIO)
                            # promPcb = round(((prom["pcb"] + pcb) / 2) ,5) if prom["estado"] ==0 and prom["pcb"] != 0 else pcb
                            # promCym = round(((prom["cym"] + cym) / 2) ,5) if prom["estado"] ==0 and prom["cym"] != 0 else cym
                            
                            # datosDia.append({"hora":hora,"pcb":pcb, "pcb_prom": promPcb, "cym":cym, "cym_prom":promCym, "alta_pcb_prom":prom["altapcb"], "alta_cym_prom":prom["altacym"], "baja_pcb_prom":prom["bajapcb"], "baja_cym_prom":prom["bajacym"]})

                            datosDia.append({"hora":hora,"pcb":pcb, "cym":cym})

                        # Escribir json
                        with open(pathArchivoDia, mode='w', encoding='utf-8') as jsonFile:

                            # Bloquea el archivo (JSON)
                            fcntl.flock(jsonFile, fcntl.LOCK_EX)

                            # Escribe el json (JSON)
                            json2.dump(datosDia, jsonFile, ensure_ascii=False, indent=2)

                            # Desbloquea el archivo (JSON)
                            fcntl.flock(jsonFile, fcntl.LOCK_UN)

                # Si se encontraron los dos dias y existen los archivos
                if(encontroActual == 1 and os.path.isfile(pathArchivoDiaActual) and encontroSiguiente == 1 and os.path.isfile(pathArchivoDiaSiguiente)): recorrer = False

                # Si se encontro solo el dia actual y existe el path
                elif(encontroActual == 1 and os.path.isfile(pathArchivoDiaActual) and encontroSiguiente == 0): recorrer = False

                # Si se encontro solo el dia siguiente y existe el path
                elif(encontroActual == 0 and encontroSiguiente == 0 and os.path.isfile(pathArchivoDiaSiguiente)): recorrer = False

                # Si no encontro ninguno
                elif(encontroActual == 0 and encontroSiguiente == 0): recorrer = False

                # Si encontro algun dia pero no existe los paths
                else: time.sleep(DATA.TIEMPO_ESPERA_DIA)

        except Exception as e:
            LOG.write_to_log(self.log_file_name+"_ERROR",mensajeError,"ERROR",str(e))
            return {"estado":-1,"ERROR": str(e)}

    def calcularPromedio(self,fecha,hora,dias):
        mensajeError = self.nombreClase + "-descargarArchivosFecha"
        try:

            # Transforma los string en datetime
            fechaInicio = fecha - timedelta(days=dias)
            fechaFin = fecha + timedelta(days=1)

            cantDias = 0
            SumaPreciosPcb = 0
            masAltaPcb = -200
            masBajaPcb = 200
            SumaPreciosCym = 0
            masAltaCym = -200
            masBajaCym = 200

            # Recorre los dias dentro del rango
            for dia in self.daterange(fechaInicio,fechaFin):

                # Crea el path del dia
                pathDia = os.path.join(DATA.PATH_ARCHIVOS_PVPC,(dia.strftime("%Y-%m-%d")+".json"))

                # Comprueba si existe
                if(os.path.isfile(pathDia)):

                    dataDia = None

                    # Abrir el archivo
                    dataDia = json.loads(io.open(pathDia,"r",encoding="utf-8").read())

                    # Recorre el dia
                    for precio in dataDia:

                        # Si es la hora buscada
                        if(precio["hora"] == hora):

                            SumaPreciosPcb += precio["pcb"]
                            SumaPreciosCym += precio["cym"]
                            cantDias += 1

                            if(masAltaPcb < precio["pcb"]): masAltaPcb = precio["pcb"]
                            if(masAltaCym < precio["cym"]): masAltaCym = precio["cym"]
                            if(masBajaPcb > precio["pcb"]): masBajaPcb = precio["cym"]
                            if(masBajaCym > precio["cym"]): masBajaCym = precio["cym"]

                            break

            promPCB = round((SumaPreciosPcb/cantDias),5) if cantDias > 0 else 0
            promCym = round((SumaPreciosCym/cantDias),5) if cantDias > 0 else 0
            
            return {"estado":0, "pcb": promPCB, "cym": promCym, "altapcb":masAltaPcb, "altacym":masAltaCym, "bajapcb":masBajaPcb, "bajacym":masBajaCym }

        except Exception as e:
            LOG.write_to_log(self.log_file_name+"_ERROR",mensajeError,"ERROR",str(e))
            return {"estado":-1,"ERROR": str(e)}

if __name__ == "__main__":
    # Crear el nombre del log
    log_file_name = datetime.now().strftime("%Y_%m_%d")

    try:
        # Instanciar clase
        classDatos = llenadoDatos(log_file_name)

        x=datetime.today()
        # y=x.replace(day=x.day, hour=20, minute=30, second=0, microsecond=0) + timedelta(days=1)
        y=x + timedelta(days=1)
        # delta_t=y-x

        # secs=delta_t.total_seconds()

        # t = Timer(secs, classDatos.descargarArchivosFecha(fechaDesde=x.strftime("%Y-%m-%d"),fechaHasta=y.strftime("%Y-%m-%d")))
        # t.start()

        classDatos.descargarArchivosFecha(fechaDesde=x.strftime("%Y-%m-%d"),fechaHasta=y.strftime("%Y-%m-%d"))

        # classDatos.descargarArchivosFecha(fechaDesde='2021-06-01',fechaHasta='2021-07-02')
        
    except Exception as e:
        mensajeError = "Problema al iniciar script"
        LOG.write_to_log(log_file_name,"INIT","ERROR",str(e))