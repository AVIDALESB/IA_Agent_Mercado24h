# Importaciones para funcionalidad de gráficos y análisis de datos
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from dotenv import load_dotenv

# Configuración de la página
st.set_page_config(
    page_title="Asistente Mercado Central 24h",
    page_icon="🛒",
    layout="centered"
)

# Carga de variable de entorno
load_dotenv()

@st.cache_data
def cargar_datos():
    return pd.read_csv("inventario.csv")

df = cargar_datos()

# Importaciones LangChain
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# ==========================================
# Funciones de consulta y generación de gráficos/reportes
# ==========================================
def consultar_datos(pregunta: str) -> str:
    resumen = df.to_string()
    prompt = PromptTemplate(
        template="""
        Eres un asistente experto en inventarios de 'Mercado Central 24h'. 
        Utiliza exclusivamente los siguientes datos del inventario para responder la pregunta del usuario. 
        Sé preciso, directo y profesional.

        ## Datos del Inventario:
        {datos}

        ## Pregunta:
        {pregunta}

        Respuesta:
        """,
        input_variables=["datos", "pregunta"]
    )
    cadena = prompt | llm | StrOutputParser()
    return cadena.invoke({"datos": resumen, "pregunta": pregunta})

def generar_grafico_inventario(tipo_grafico: str) -> str:
    plt.switch_backend('Agg')
    df_grafico = df.copy()
    instruccion_extra = ""
    
    if tipo_grafico == "menor_stock":
        col_stock = next((c for c in df.columns if 'stock' in c.lower() or 'cantidad' in c.lower()), None)
        if col_stock:
            df_grafico = df.nsmallest(5, col_stock)
            instruccion_extra = "Crea un gráfico de barras horizontales. El eje Y debe ser el nombre del producto y el eje X el stock."
    elif tipo_grafico == "mayor_precio":
        col_precio = next((c for c in df.columns if 'precio' in c.lower() or 'costo' in c.lower()), None)
        if col_precio:
            df_grafico = df.nlargest(5, col_precio)
            instruccion_extra = "Crea un gráfico de barras verticales. El eje X debe ser el nombre del producto y el eje Y el precio."

    prompt = PromptTemplate(
        template="""
            Eres un especialista estricto en visualización de datos con Python. 
            Genera **únicamente el código Python puro** usando `matplotlib.pyplot` y `seaborn` para representar los datos provistos.

            ## Datos a Graficar:
            {muestra}

            ## Instrucciones Estrictas:
            1. Usa `sns.set_theme()`.
            2. {instruccion}
            3. Configura un tamaño de `figsize=(10, 5)`, añade etiquetas claras en los ejes X e Y (`plt.xlabel`, `plt.ylabel`), un título descriptivo con `loc='left'`, y aplica `plt.xticks(rotation=45)` si los textos son largos.
            4. Guarda obligatoriamente la imagen usando exactamente: `plt.savefig('grafico_temp.png', bbox_inches='tight')`.
            5. Devuelve **ÚNICAMENTE** el código Python puro. Sin bloques markdown (` ``` `), sin explicaciones, sin texto adicional.

            Código Python:
        """,
        input_variables=['muestra', 'instruccion']
    )

    cadena = prompt | llm | StrOutputParser()
    script_bruto = cadena.invoke({"muestra": df_grafico.to_string(), "instruccion": instruccion_extra})
    script_limpio = script_bruto.replace('```python', '').replace('```', '').strip()

    exec_globals = {"df": df_grafico, "plt": plt, "sns": sns}

    try:
        plt.clf()
        plt.close('all')
        exec(script_limpio, exec_globals, {})
        
        timestamp = int(time.time())
        nombre_archivo = f"grafico_{timestamp}.png"
        
        if os.path.exists("grafico_temp.png"):
            os.rename("grafico_temp.png", nombre_archivo)
            return nombre_archivo
        return None
    except Exception as e:
        st.error(f"Error generando gráfico: {e}")
        return None

def generar_excel_stock(stock_minimo: int = 30) -> str:
    col_stock = next((c for c in df.columns if 'stock' in c.lower() or 'cantidad' in c.lower()), None)
    if not col_stock:
        return None
    
    df_criticos = df[df[col_stock] <= stock_minimo]
    if df_criticos.empty:
        return None
    
    timestamp = int(time.time())
    nombre_archivo = f"reporte_reabastecimiento_{timestamp}.xlsx"
    df_criticos.to_excel(nombre_archivo, index=False)
    return nombre_archivo


# ==========================================
# Interfaz de Usuario con Streamlit, esta incluye la barra lateral, el historial de chat y la entrada de usuario
# ==========================================
st.title("🛒 Asistente Inteligente - Mercado Central 24h")
st.markdown("Controla el inventario, analiza métricas visuales y obtén reportes ejecutivos al instante.")

# --- Barra lateral, la idea es tener funciones predeterminadas para probar el modelo ---
st.sidebar.header("⚡ Accesos Rápidos")
st.sidebar.markdown("Haz clic para ejecutar consultas clave:")

if st.sidebar.button("📉 Top 5: Menor Stock"):
    query_shortcut = "Crea un gráfico de barras horizontales con los 5 productos con menor stock"
    st.session_state.messages.append({"role": "user", "content": query_shortcut})
    archivo_img = generar_grafico_inventario("menor_stock")
    if archivo_img:
        resp = "Aquí tienes el gráfico con los 5 productos con menor stock:"
        st.session_state.messages.append({"role": "assistant", "content": resp, "image": archivo_img})

if st.sidebar.button("📈 Top 5: Precios más Elevados"):
    query_shortcut = "Crea un gráfico de barras con los 5 productos con precios más elevados"
    st.session_state.messages.append({"role": "user", "content": query_shortcut})
    archivo_img = generar_grafico_inventario("mayor_precio")
    if archivo_img:
        resp = "Aquí tienes el gráfico con los 5 productos de mayor precio:"
        st.session_state.messages.append({"role": "assistant", "content": resp, "image": archivo_img})

if st.sidebar.button("📊 Generar Reporte Excel (Stock <= 30)"):
    query_shortcut = "Genera un reporte en Excel con productos con stock menor o igual a 30"
    st.session_state.messages.append({"role": "user", "content": query_shortcut})
    archivo_excel = generar_excel_stock(30)
    if archivo_excel:
        resp = "¡Reporte generado con éxito! Descárgalo abajo:"
        st.session_state.messages.append({"role": "assistant", "content": resp, "file": archivo_excel})

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** También puedes escribir tus preguntas directamente en el chat central.")

# --- Historial de Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message and message["image"]:
            st.image(message["image"])
        if "file" in message and message["file"]:
            with open(message["file"], "rb") as f:
                st.download_button(
                    label="📥 Descargar Reporte en Excel",
                    data=f,
                    file_name=message["file"],
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_{message['file']}"
                )

# --- Entrada/Input para el Chat ---
if prompt_usuario := st.chat_input("¿Qué deseas consultar o generar hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(prompt_usuario)

    with st.chat_message("assistant"):
        consulta_lower = prompt_usuario.lower()
        
        if "menor stock" in consulta_lower or "stock más bajo" in consulta_lower or "menos stock" in consulta_lower:
            with st.spinner("Generando gráfico de menor stock..."):
                archivo_img = generar_grafico_inventario("menor_stock")
                if archivo_img:
                    texto_resp = "Aquí tienes el gráfico de barras horizontales con los 5 productos con menor stock:"
                    st.markdown(texto_resp)
                    st.image(archivo_img)
                    st.session_state.messages.append({"role": "assistant", "content": texto_resp, "image": archivo_img})
                else:
                    st.error("No se pudo generar la imagen.")
                    
        elif "precio" in consulta_lower and ("elevado" in consulta_lower or "alto" in consulta_lower or "mayor" in consulta_lower):
            with st.spinner("Generando gráfico de precios elevados..."):
                archivo_img = generar_grafico_inventario("mayor_precio")
                if archivo_img:
                    texto_resp = "Aquí tienes el gráfico de barras con los 5 productos con precios más elevados:"
                    st.markdown(texto_resp)
                    st.image(archivo_img)
                    st.session_state.messages.append({"role": "assistant", "content": texto_resp, "image": archivo_img})
                else:
                    st.error("No se pudo generar la imagen.")
                    
        elif "reporte" in consulta_lower or "excel" in consulta_lower or "proveedor" in consulta_lower:
            with st.spinner("Generando reporte en Excel..."):
                archivo_excel = generar_excel_stock(30)
                if archivo_excel:
                    texto_resp = "¡Reporte generado con éxito! Puedes descargarlo aquí:"
                    st.markdown(texto_resp)
                    with open(archivo_excel, "rb") as f:
                        st.download_button(
                            label="📥 Descargar Reporte en Excel",
                            data=f,
                            file_name=archivo_excel,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_chat_{archivo_excel}"
                        )
                    st.session_state.messages.append({"role": "assistant", "content": texto_resp, "file": archivo_excel})
                else:
                    texto_resp = "No se encontraron productos críticos."
                    st.markdown(texto_resp)
                    st.session_state.messages.append({"role": "assistant", "content": texto_resp})
                    
        else:
            with st.spinner("Consultando inventario..."):
                texto_resp = consultar_datos(prompt_usuario)
                st.markdown(texto_resp)
                st.session_state.messages.append({"role": "assistant", "content": texto_resp})