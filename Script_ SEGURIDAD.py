import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
from itertools import cycle
import feedparser
from dateutil import parser


## España - Seguridad
def seguridad_aemps():
    #URL del año 2024
    url='https://www.aemps.gob.es/comunicacion/notas-de-seguridad/notas-informativas-de-seguridad-de-medicamentos-de-uso-humano/?fec=2024&cat=266'
    data=[]

    response = requests.get(url, verify=False)
    '''
    if response.status_code != 200:
        break  # Rompe el bucle si la página no existe o no es accesible
    '''
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', class_='aemps-tabla__03 tabla-text-left__02')

    '''
    if not table:
        break  # Rompe el bucle si no se encuentra la tabla
    '''

    rows = table.find_all('tr')[1:]  # Omitir la cabecera de la tabla
    '''
    if not rows:
        #break  # Si no hay filas, sal del bucle
    '''

    for row in rows:
        cells = row.find_all('td')

        fecha = cells[0].text.strip()
        titulo_1 = cells[1].find('a').text.strip()
        enlace = cells[1].find('a')['href']
        titulo_2 = cells[1].find('p').text.strip()
        #enlace = titulo['href'] if titulo else None

        time.sleep(1)  # Retraso entre peticiones para evitar sobrecargar el servidor

        data.append({
            "PAIS": "España",
            "AGENCIA": "AEMPS",
            "FECHA": fecha,
            "NOMBRE": titulo_1+' - '+ titulo_2,
            "TIPO DE PRODUCTO": "Medicamentos",
            "ENLACE": enlace
        })

    # Crear DataFrame y guardarlo en Excel directamente sin retornar nada
    seguridad_aemps = pd.DataFrame(data, columns=["PAIS", "AGENCIA", "FECHA", "NOMBRE", "TIPO DE PRODUCTO", "ENLACE"])
    #df_aemps_m.to_excel('alertas_españa_m.xlsx', index=False)

    return seguridad_aemps


    ## CHILE
def seguridad_chile():
    #Configuración inicial del DataFrame
    data=[]

    url = "https://www.ispch.cl/categorias-alertas/anamed/?buscar&tipo_alerta=farmacovigilancia&tipo_producto=farmaceutico#038;tipo_alerta=farmacovigilancia&tipo_producto=farmaceutico"
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'class': 'table table-bordered table-striped table-responsive'})

    while table:
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            fecha = cols[0].text.strip().replace('-', '/')

            if int(fecha[-4:]) < 2024: # Detener si el año es menor a 2024
                table=False
                break

            nombre = cols[3].text.strip()
            enlaces = '; '.join([f"{a.text.strip()}, {a['href']}" for a in cols[4].find_all('a')])  # Extrae todos los enlaces y textos

            # Agregar fila al DataFrame
            #seguridad_chile.loc[len(seguridad_chile)] = ['Chile', 'ANAMED', fecha, nombre, 'Medicamentos', enlaces]
            data.append({
                "PAIS": "Chile",
                "AGENCIA": "ANAMED",
                "FECHA": fecha,
                "NOMBRE": nombre,
                "TIPO DE PRODUCTO": "Medicamentos",
                "ENLACE": enlaces
            })

    seguridad_chile = pd.DataFrame(data, columns=["PAIS", "AGENCIA", "FECHA", "NOMBRE", "TIPO DE PRODUCTO", "ENLACE"])
    # Mostrar el DataFrame final
    #df_chile_m.to_excel('alertas_chile_m.xlsx', index=False)
    return seguridad_chile


def seguridad_peru():
  page=1
  webscraping=True
  data=[]

  headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
  }

  while webscraping:
    url = f"https://www.digemid.minsa.gob.pe/webDigemid/publicaciones/alertas-modificaciones/alerta-seguridad/page/{page}/"

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    lista = soup.find('div',class_='blog-posts posts-full posts-container')
    alertas=lista.find_all('article')

    for i in range(0,len(alertas)):
      alerta=alertas[i]
      nombre=alerta.find('h2').text +' - '+ alerta.find('p').text.strip().replace('Descargar','')
      fecha=alerta.find('time').text
      enlace=alerta.find('a')['href']

      año=int(fecha[-4:])

      if año >= 2024:
        data.append(["Perú", "DIGEMID", fecha, nombre, "Medicamentos", enlace])
      else:
        webscraping=False

    page+=1

  # Crear el DataFrame
  seguridad_peru = pd.DataFrame(data, columns=["PAIS", "AGENCIA", "FECHA", "NOMBRE", "TIPO DE PRODUCTO", "ENLACE"])
  return seguridad_peru


def seguridad_ecuador():
  #Se deja para la última tabla, sin embargo actualmente no hay alertas de seguridad del año 2024
  url = "https://www.controlsanitario.gob.ec/reportes-de-farmacovigilancia/"

  session = requests.Session()
  user_agents = [
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
      'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
      'Mozilla/5.0 (iPad; CPU OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
  ]
  agent_cycle = cycle(user_agents)
  data=[]

  headers = {'User-Agent': next(agent_cycle)}
  response = session.get(url, headers=headers)
  soup = BeautifulSoup(response.content, 'html.parser')
  tables = soup.find_all('table')
  titulos=soup.find_all('h1')

  for titulo in titulos[:-1]:
    año=titulo.text.strip()
    if año and int(año)==2024:
      alertas=tables[-1].find_all('a')
      for alerta in alertas:
        nombre=alerta.text.strip()
        enlace=alerta['href']
        data.append(["Ecuador", "ARCSA", '01/01/2024', nombre, "Medicamentos", enlace])

  seguridad_ecuador = pd.DataFrame(data, columns=["PAIS", "AGENCIA", "FECHA", "NOMBRE", "TIPO DE PRODUCTO", "ENLACE"])

  return seguridad_ecuador



def seguridad_panama():
    base_url = "https://www.minsa.gob.pa/"
    page = 0
    webscraping = True
    data = []

    while webscraping:
        url = f"https://www.minsa.gob.pa/informacion-salud/alertas-y-comunicados?page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table', class_='views-view-grid')

        if not tables:  # Si no hay tablas, salir del bucle
            break

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if not cells:  # En caso de que la fila no tenga celdas
                    continue

                for cell in cells:
                    link_element = cell.find('a')
                    if link_element:
                        nombre = link_element.text.strip()
                        enlace = base_url + link_element['href']
                    else:
                        # Continuar al siguiente elemento si no hay un enlace
                        continue

                    date_element = cell.find('span', class_='date-display-single')
                    if date_element:
                        fecha_iso = date_element['content']
                        fecha_dt = datetime.fromisoformat(fecha_iso)
                        fecha = fecha_dt.strftime('%d/%m/%Y')

                        if int(fecha.split('/')[-1]) < 2024:  # Extraer los últimos cuatro dígitos que corresponden al año para colocar límite de año de extracción
                            webscraping = False  # Detener si el año es menor a 2024
                            break

                        data.append(["Panamá", "Dirección Nacional de Farmacia y Droga", fecha, nombre, "Medicamentos", enlace])

                if not webscraping:
                    break
            if not webscraping:
                break

            page += 1

    # Crear DataFrame y retornarlo
    seguridad_panama_df = pd.DataFrame(data, columns=["PAIS", "AGENCIA", "FECHA", "NOMBRE", "TIPO DE PRODUCTO", "ENLACE"])
    return seguridad_panama_df



def seguridad_aemps_2():
  #URL del año 2024
  url = 'https://cima.aemps.es/cima/psusa.do'
  data = []

  response = requests.get(url, verify=False)  # Ignorar los avisos de verificación SSL
  soup = BeautifulSoup(response.content, 'html.parser')

  table = soup.find('table', class_='simple')  # Asegúrate de que esta es la clase correcta
  rows = table.find_all('tr')[1:]  # Asumiendo que la primera fila es el encabezado

  for row in rows:
      cells = row.find_all('td')

      # Asegurarte de que la fila tenga el mínimo de celdas esperadas para evitar IndexError
      if len(cells) >= 6:  # Cambia '6' al número mínimo de celdas esperado
          nombre = f'Principio/s afectado/s: {cells[1].text.strip()} - Tipo de procedimiento: {cells[0].text.strip()}'
          fecha = cells[-2].text.strip()
          año=int(fecha.split('/')[-1])
          if año < 2024:
            break
          enlace_container = cells[2]
          enlace = enlace_container.find('a')['href'] if enlace_container.find('a') else 'No link available'

          data.append({
              "PAIS": "España",
              "AGENCIA": "AEMPS",
              "FECHA": fecha,
              "NOMBRE": nombre,
              "TIPO DE PRODUCTO": "Medicamentos",
              "ENLACE": enlace
          })

  # Crear DataFrame y mostrarlo
  seguridad_aemps_2 = pd.DataFrame(data, columns=["PAIS", "AGENCIA", "FECHA", "NOMBRE", "TIPO DE PRODUCTO", "ENLACE"])
  return seguridad_aemps_2



def seguridad_uk():
  # URL del feed RSS
  url = 'https://www.gov.uk/drug-safety-update.atom'

  # Configurar un tiempo de espera
  timeout = 10  # segundos

  data=[]
  webscraping=True

  #Función para formato de la fecha
  def convertir_fecha(date_str):
      # Parsear la fecha usando dateutil.parser para manejar varios formatos
      date_obj = parser.parse(date_str)
      # Formatear la fecha en el formato deseado 'dia/mes/año'
      formatted_date = date_obj.strftime('%d/%m/%Y')
      return formatted_date

  try:
      # Usar requests para obtener el contenido del feed con un tiempo de espera
      response = requests.get(url, timeout=timeout)
      # Parsear el contenido del feed con feedparser
      feed = feedparser.parse(response.content)

      # Recorrer las entradas del feed
      for entry in feed.entries:
          fecha_sin_formato = entry.updated
          año = parser.parse(fecha_sin_formato).year

          if año >= 2024:
              nombre = entry.title
              enlace = entry.link
              fecha = convertir_fecha(fecha_sin_formato)
              data.append(["Reino Unido", "MHRA", fecha, nombre, "Medicamentos", enlace])
          else:
              # Si encuentra una entrada menor que 2024, detiene el procesamiento.
              break

          df_uk_seguridad = pd.DataFrame(data, columns=['PAIS', 'AGENCIA', 'FECHA', 'NOMBRE', 'TIPO DE PRODUCTO', 'ENLACE'])

  except requests.exceptions.Timeout:
      print("El tiempo de espera para la solicitud ha expirado.")
  except requests.exceptions.RequestException as e:
      print("Ocurrió un error al realizar la solicitud:", e)

  return df_uk_seguridad


def seguridad_cuba():
  # Crear un DataFrame vacío con las columnas especificadas
  df_cuba_seguridad = pd.DataFrame(columns=["PAIS", "AGENCIA", "FECHA", "NOMBRE", "TIPO DE PRODUCTO", "ENLACE"])

  # Información constante
  pais = "Cuba"
  agencia = "CECMED"
  tipo_producto = "Medicamentos"
  base_url = "https://www.cecmed.cu"


  # Función para procesar cada página
  def scrape_cuba(url):

      response = requests.get(url, timeout=10)
      soup = BeautifulSoup(response.content, 'html.parser')
      # Buscar todas las alertas en la página
      alertas = soup.find_all('div', class_='col-sm-6 col-md-4 views-row')
      for alerta in alertas:
          fecha1 = alerta.find('div', class_='feature').get_text(strip=True)[:10]
          año=int(fecha1[-4:])

          # Comprobar si la fecha es menor al año 2024
          if año < 2024:
              return False
          nombre = alerta.find('div', class_='feature').get_text(strip=True)[10:]
          enlace = base_url + alerta.find('a')['href']

          # Añadir la fila al dataframe
          df_cuba_seguridad.loc[len(df_cuba_seguridad)] = [pais, agencia, fecha1, nombre, tipo_producto, enlace]
      return True

  # Iterar sobre las páginas
  pagina = 0
  while True:
      url = f"https://www.cecmed.cu/vigilancia/medicamentos/alertas?page={pagina}"
      if not scrape_cuba(url):
          break
      pagina += 1

  return df_cuba_seguridad


# Lista de funciones
funciones = [
    seguridad_aemps, seguridad_chile, seguridad_peru, seguridad_ecuador, seguridad_panama, seguridad_aemps_2, seguridad_uk, seguridad_cuba
    ]

def ejecutar_funciones_seguridad():
    dfs = []  # Lista para almacenar los DataFrames
    for funcion in funciones:
        try:
            # Suponemos que cada función devuelve un DataFrame
            df = funcion()
            dfs.append(df)
        except Exception as e:
            print(f"Error al ejecutar {funcion.__name__}: {e}")

    # Concatenar todos los DataFrames en uno solo
    df_nuevo = pd.concat(dfs, ignore_index=True)

    # Guardar el DataFrame total en un archivo Excel
    #df_nuevo.to_excel("Base_seguridad_02.10.xlsx", index=False)

    return df_nuevo


# Función para filtrar y guardar la tabla ordenada
def filtrar_guardar(df, fecha_limite=None):

    # Convertir la columna de fecha a tipo datetime con formato específico
    df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d/%m/%Y')

    # Ordenar las fechas de más reciente a más antigua
    df_ordenado = df.sort_values('FECHA', ascending=False)

    if fecha_limite:
        # Convertir la fecha límite a datetime con el mismo formato
        fecha_limite = pd.to_datetime(fecha_limite, format='%d/%m/%Y')
        # Filtrar las fechas mayores o iguales a la fecha límite
        df_ordenado = df_ordenado[df_ordenado['FECHA'] >= fecha_limite]

    # Formatear la columna de fecha para eliminar la hora
    df_ordenado['FECHA'] = df_ordenado['FECHA'].dt.strftime('%d/%m/%Y')

    # Guardar el nuevo DataFrame ordenado y filtrado en un archivo Excel
    df_ordenado.to_excel('Base_seguridad_ordenada_02.10.xlsx', index=False)


df_nuevo= ejecutar_funciones_seguridad()


# Ejemplo de uso:
# Para filtrar hasta una fecha límite, descomenta la siguiente línea y sustituye '01/01/2023' por tu fecha deseada
filtrar_guardar(df_nuevo, '01/10/2024')