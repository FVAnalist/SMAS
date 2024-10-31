import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# Este debe ser el primer comando ejecutado en tu script
st.set_page_config(layout="wide", page_title="Sistema de Monitoreo de Alertas Sanitarias (SMAS)")

st.markdown("""
<style>
[data-testid="stSidebarContent"] {
    background: #F4F7FD;
}
</style>
""", unsafe_allow_html=True)

# Cargar la imagen del logo
logo = Image.open("logo_blanco.png")

lista_activos ='APIs.xlsx'

# Función para cargar datos desde un archivo Excel especificado
@st.cache_data(ttl=43200)
def cargar_datos(archivo):
    def ajustar_fecha(fecha):
        try:
            return pd.to_datetime(fecha, format='%d/%m/%Y')
        except ValueError:
            try:
                return pd.to_datetime(fecha, format='%Y').replace(day=1, month=1)
            except ValueError:
                return None
    df = pd.read_excel(archivo, converters={'Fecha': ajustar_fecha})
    df['FECHA'] = df['FECHA'].apply(ajustar_fecha)
    df = df.sort_values('FECHA', ascending=False)
    df['NOMBRE'] = df['NOMBRE'].str.replace('_x000D_', ' ')
    return df

def aplicar_filtros(df, filtro_pais, filtro_agencia, filtro_tipo, fecha_inicio, fecha_fin):
    if filtro_pais:
        df = df[df['PAIS'].isin(filtro_pais)]
    if filtro_agencia:
        df = df[df['AGENCIA'].isin(filtro_agencia)]
    if filtro_tipo:
        df = df[df['TIPO DE PRODUCTO'].isin(filtro_tipo)]
    df = df[(df['FECHA'] >= pd.to_datetime(fecha_inicio)) & (df['FECHA'] <= pd.to_datetime(fecha_fin))]
    return df

# Crear columnas para el diseño de la página de login
col1, col2 = st.columns([2,8], vertical_alignment="center")

with col1:
    st.image(logo, width=220)

with col2:
    #st.title("Superintendencia de Regulación Sanitaria")
    st.markdown("<h1 style='text-align: center; color: black;'><em>Superintendencia de Regulación Sanitaria</em></h1>", unsafe_allow_html=True)

st.write("")
st.markdown("""
<div style="text-align: center; font-size: 36px;">
    <strong><em>Sistema de Monitoreo de Alertas Sanitarias (SMAS)</em></strong>
</div>
""", unsafe_allow_html=True)


# Botones para seleccionar la base de datos
opcion_base = st.sidebar.radio("Seleccione base a visualizar", ("Alertas Sanitarias", "Seguridad"))

# Verificar si la base seleccionada ha cambiado
if 'ultima_base_seleccionada' not in st.session_state:
    st.session_state.ultima_base_seleccionada = opcion_base

# Si cambia la base seleccionada, reiniciar los valores correspondientes
if st.session_state.ultima_base_seleccionada != opcion_base:
    if opcion_base == "Alertas Sanitarias":
        st.session_state.palabra_clave_activos = ''
    elif opcion_base == "Seguridad":
        st.session_state.palabra_clave = ''
    
    # Actualizar el estado de la última base seleccionada
    st.session_state.ultima_base_seleccionada = opcion_base
'''
# Carga la base de datos seleccionada
if opcion_base == "Alertas Sanitarias":
    df = cargar_datos('BASES FUENTE/Base_alertas.xlsx')
else:
    df = cargar_datos('BASES FUENTE/Base_SEGURIDAD.xlsx')
'''
    
# Carga la base de datos seleccionada
if opcion_base == "Alertas Sanitarias":
    df = cargar_datos('BASES FUENTE/Base_alertas.xlsx')
elif opcion_base == "Seguridad":
    df = cargar_datos('BASES FUENTE/Base_SEGURIDAD.xlsx')


# Opciones de filtro
paises = df['PAIS'].unique().tolist()
agencias = df['AGENCIA'].unique().tolist()
tipo_producto = df['TIPO DE PRODUCTO'].unique().tolist()

#Construcción de filtros

st.sidebar.title("Filtros")
filtro_pais = st.sidebar.multiselect('País', paises)
filtro_agencia = st.sidebar.multiselect('Agencia', agencias)
filtro_tipo = st.sidebar.multiselect('Tipo de Producto', tipo_producto)


# Suponiendo que los datos están cargados y la columna 'FECHA' ya está convertida a datetime
df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d/%m/%Y', errors='coerce')  # Asegura la conversión correcta

# Definir los valores por defecto para el selector de fecha
fecha_min = df['FECHA'].min().date() if not df['FECHA'].isnull().all() else pd.to_datetime('today').date()
fecha_max = df['FECHA'].max().date() if not df['FECHA'].isnull().all() else pd.to_datetime('today').date()


# Selector de fechas para el rango de fechas
st.sidebar.title("Por fecha")
fecha_inicio = st.sidebar.date_input("Fecha de inicio", value=fecha_min, min_value=fecha_min, max_value=fecha_max, format="DD/MM/YYYY")
fecha_fin = st.sidebar.date_input("Fecha de fin", value=fecha_max, min_value=fecha_min, max_value=fecha_max, format="DD/MM/YYYY")

# Crear una variable de estado para almacenar los valores de los filtros
if 'filtro_pais' not in st.session_state:
    st.session_state.filtro_pais = []
if 'filtro_agencia' not in st.session_state:
    st.session_state.filtro_agencia = []
    # Inicializar session_state para las palabras clave
if 'palabra_clave' not in st.session_state:
    st.session_state.palabra_clave = ''
if 'palabra_clave_activos' not in st.session_state:
    st.session_state.palabra_clave_activos = ''
if 'filtro_tipo' not in st.session_state:
    st.session_state.filtro_tipo = []
if 'fecha_inicio' not in st.session_state:
    st.session_state.fecha_inicio = fecha_min
if 'fecha_fin' not in st.session_state:
    st.session_state.fecha_fin = fecha_max

# Filtrado de datos basado en el rango de fecha seleccionado
#1)  df_filtrado = df[(df['FECHA'] >= pd.to_datetime(fecha_inicio)) & (df['FECHA'] <= pd.to_datetime(fecha_fin))]


# Aplicar todos los filtros de una vez
df_filtrado = aplicar_filtros(df, filtro_pais, filtro_agencia, filtro_tipo, fecha_inicio, fecha_fin)

col1_a, col2_a = st.sidebar.columns([1, 3])
with col1_a:
    st.write("**Por Palabras Claves**")
with col2_a:
    st.session_state.palabra_clave = st.text_input("", placeholder="Escriba para filtrar...")

# Filtrar basado en palabras clave en ambas opciones
if st.session_state.palabra_clave:
    df_filtrado = df_filtrado[df_filtrado['NOMBRE'].str.contains(st.session_state.palabra_clave, case=False, na=False)]

if opcion_base == "Seguridad":
    st.session_state.palabra_clave_activos = ''
    st.session_state.palabra_clave = ''
    col1_b, col2_b = st.sidebar.columns([1, 3])
    with col1_b:
        st.write("**Por Principio Activo**")
    with col2_b:
        df_prin_activos = pd.read_excel(lista_activos, sheet_name="Hoja1")
        activos_options = df_prin_activos['PRINCIPIO ACTIVO'].astype(str).tolist()  # Convertir a cadena
        st.session_state.palabra_clave_activos = st.selectbox(label="",options=activos_options, placeholder="Seleccione principio activo..", index=None)
        #st.session_state.palabra_clave_activos = st.selectbox(label="", options=["Seleccione..."] + activos_options, index=0)
    
      # Filtrar basado en el principio activo seleccionado
    if st.session_state.palabra_clave_activos != None:
        df_filtrado = df_filtrado[df_filtrado['NOMBRE'].str.contains(st.session_state.palabra_clave_activos, case=False, na=False)]


col1, col2 = st.columns([1, 1])
with col1:
    # Mostrar número de resultados
    num_results = len(df_filtrado)
    st.write(f"Hay {num_results} resultados")
with col2:
    st.markdown(f"""
        <style>
            .small-font {{
                font-size:16px;
                font-style: italic;
            }}
        </style>
        <p style="text-align: right;" class="small-font">
            Última actualización: 26-sept-2024  
        </p>
    """, unsafe_allow_html=True)


#Conversion de enlaces en agencia de Chile
def format_chile_links(enlaces):
    if not enlaces:
        return ""
    # Divide los enlaces y sus descripciones, suponiendo que están separados por "; "
    enlaces = enlaces.split('; ')
    formatted_links = []
    for enlace in enlaces:
        if ',' in enlace:
            texto, url = enlace.split(',', 1)
            formatted_link = f'<a href="{url.strip()}" target="_blank">{texto.strip()}</a>'
            formatted_links.append(formatted_link)
    return '<br>'.join(formatted_links)

#Conversion de enlaces en agencia AEMPS de DDMM
def format_aemps_dm_links(enlaces):
    if not enlaces:
        return ""
    # Divide los enlaces que están separados por ";"
    enlaces = enlaces.split(';')
    formatted_links = []
    # Etiquetas para cada posición de enlace
    link_texts = ['Información', 'Nota de aviso', 'Otra']
    for i, url in enumerate(enlaces):
        if i < len(link_texts):
            # Crea un enlace HTML con la etiqueta correspondiente
            formatted_link = f'<a href="{url.strip()}" target="_blank">{link_texts[i]}</a>'
            formatted_links.append(formatted_link)
    # Une los enlaces con un separador HTML para visualización en línea
    return '<br>'.join(formatted_links)



# Definición de estilos CSS
st.markdown("""
<style>
.mini-table {
    width: 100%;
    border: 1px solid #000;
    border-collapse: collapse;
}
.mini-table:hover {
    background-color: #f0f0f0;
    border: 1px solid #ccc;
    cursor: pointer;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}
.mini-table td, .mini-table th {
    border: none;
}
.left-col {
    width: 25%;
    text-align: center;
    vertical-align: middle;
    font-size: 14px;
    color: darkblue;
}
.left-col-agency{
    width: 25%;
    text-align: center;
    vertical-align: middle;
    font-size: 16px;
    font-weight: bold;  
    color: black;     
}
.left-col-date {
    font-size: 20px;
    color: white;
    background-color: #436ab2;
    font-weight: bold;
}
.right-col {
    width: 75%;
    text-align: center;
    vertical-align: middle;
}
.product-name {
    font-size: 18px;
}
.product-type {
    font-size: 14px;
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)

#Banderas
def flag_shortcode(country):
    country_flags = {
        'Argentina': '&#x1F1E6;&#x1F1F7;',  # :flag-ar:
        'Bolivia': '&#x1F1E7;&#x1F1F4;',  # :flag-bo:
        'Brasil': '&#x1F1E7;&#x1F1F7;',  # :flag-br:
        'Canada': '&#x1F1E8;&#x1F1E6;',  # :flag-ca:
        'Chile': '&#x1F1E8;&#x1F1F1;',  # :flag-cl:
        'Costa Rica': '&#x1F1E8;&#x1F1F7;',  # :flag-cr:
        'Cuba': '&#x1F1E8;&#x1F1FA;',  # :flag-cu:
        'Ecuador': '&#x1F1EA;&#x1F1E8;',  # :flag-ec:
        'España': '&#x1F1EA;&#x1F1F8;',  # :flag-es:
        'Guatemala': '&#x1F1EC;&#x1F1F2;',  # :flag-gt:
        'Mexico': '&#x1f1f2;&#x1f1fd;',  # :flag-mx:
        'México': '&#x1f1f2;&#x1f1fd;',  # :flag-mx:
        'Perú': '&#x1F1F5;&#x1F1EA;',  # :flag-pe:
        'Suiza': '&#x1F1E8;&#x1F1ED;',  # :flag-ch:
        'Reino Unido': '&#x1F1EC;&#x1F1E7;',  # :flag-gb:
        'USA': '&#x1F1FA;&#x1F1F8;',  # :flag-us:
        'Australia': '&#x1F1E6;&#x1F1FA;',  # :flag-au:
        'Panamá': '&#x1F1F5;&#x1F1E6;',  # :flag-pa:
        'El Salvador': '&#x1F1F8;&#x1F1FB;',  # :flag-sv:
    }
    return country_flags.get(country, '')

# Creación de mini tablas para cada fila
for index, row in df_filtrado.iterrows():

    # Solo aplicar formato especial de enlaces para Chile
    if row['PAIS'] == 'Chile':
        links_html = format_chile_links(row['ENLACE'])
        product_html = f"{row['NOMBRE']}<br>{links_html}"

    elif row['PAIS']=='España' and row['TIPO DE PRODUCTO']=='Dispositivo Médico':
        links_html = format_aemps_dm_links(row['ENLACE'])
        product_html = f"{row['NOMBRE']}<br>{links_html}"
    else:
        product_html = f'<a href="{row["ENLACE"]}" target="_blank">{row["NOMBRE"]}</a>'

    st.markdown(f"""
    <table class="mini-table">
        <tr>
            <td class="left-col left-col-date">{row['FECHA'].strftime('%d/%m/%Y')}</td>
            <td rowspan="2" class="right-col product-name">{product_html}</td>
        </tr>
        <tr>
            <td class="left-col"><span style="font-size: 1.5em">{flag_shortcode(row['PAIS'])}</span>{row['PAIS']}</td>
        </tr>
        <tr>
            <td class="left-col-agency">{row['AGENCIA']}</td>
            <td class="right-col product-type">{row['TIPO DE PRODUCTO']}</td>
        </tr>
    </table>
    <br>
    """, unsafe_allow_html=True)
