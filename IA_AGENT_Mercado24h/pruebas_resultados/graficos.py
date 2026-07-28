# Importaciones para funcionalidad de gráficos y análisis de datos
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importaciones LangChain y herramientas de Groq
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_agent
from langchain_experimental.tools.python.tool import PythonAstREPLTool

# Cargar el DataFrame de Mercado Central
df = pd.read_csv("inventario.csv")

# Configurar el LLM con un modelo vigente en Groq, para no generar costos innecesarios, se utilizo un modelo más pequeño para pruebas locales
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# Definición de Herramientas del Agente
@tool
def informacion_dataframe(pregunta: str) -> str:
    """Proporciona un panorama general del DataFrame (filas, columnas, nombres y nulos)."""
    filas, columnas = df.shape
    cols = ", ".join(df.columns.tolist())
    nulos = df.isnull().sum().to_dict()
    return f"El inventario tiene {filas} productos y {columnas} columnas. Las columnas son: {cols}. Conteo de nulos: {nulos}"

# Instanciamos la herramienta de Python para análisis
repl_tool = PythonAstREPLTool(locals={"df": df})

@tool
def codigos_python(query: str) -> str:
    """Utilízala para cálculos, filtros específicos, promedios o consultas particulares sobre el DataFrame `df` mediante código Python."""
    return repl_tool.run(query)

@tool
def generar_grafico(pregunta: str) -> str:
    """
    Utiliza esta herramienta siempre que el usuario solicite un gráfico, visualización,
    histograma, gráfico de barras, distribución o representación visual a partir del DataFrame.
    """
    plt.switch_backend('Agg')
    
    # Calcular el Top 5 desde Python
    pregunta_lower = pregunta.lower()
    df_grafico = df.copy()
    
    try:
        if "menor stock" in pregunta_lower or "stock más bajo" in pregunta_lower:
            col_stock = next((c for c in df.columns if 'stock' in c.lower() or 'cantidad' in c.lower()), None)
            col_prod = next((c for c in df.columns if 'prod' in c.lower() or 'nombre' in c.lower() or 'articulo' in c.lower()), df.columns[0])
            if col_stock:
                df_grafico = df.nsmallest(5, col_stock)
        elif "precio" in pregunta_lower and ("elevado" in pregunta_lower or "alto" in pregunta_lower or "mayor" in pregunta_lower):
            col_precio = next((c for c in df.columns if 'precio' in c.lower() or 'costo' in c.lower()), None)
            if col_precio:
                df_grafico = df.nlargest(5, col_precio)
    except Exception:
        pass 

    columnas_info = '\n'.join([f'- {col} ({dtype})' for col, dtype in df.dtypes.items()])
    
    # Le pasamos al LLM los datos ya filtrados y listos para graficar
    muestra_datos = df_grafico.to_dict(orient='records')

    plantilla_respuesta = PromptTemplate(
        template="""
            Eres un especialista en visualización de datos. Tu tarea es generar **únicamente el código Python**
            para graficar los datos proporcionados.

            ## Solicitud del usuario:
            "{pregunta}"

            ## Datos listos para graficar (ya procesados de todo el inventario):
            {muestra}

            ## Instrucciones obligatorias:
            1. Usa las bibliotecas `matplotlib.pyplot` (como `plt`) y `seaborn` (como `sns`);
            2. Define el tema con `sns.set_theme()`;
            3. Grafica directamente los datos contenidos en la variable `df` (que en este contexto ya contiene exactamente los elementos requeridos);
            4. Configura el tamaño con `figsize=(8, 4)`;
            5. Añade título y etiquetas apropiadas;
            6. Posiciona el título con `loc='left'`, `pad=20` y `fontsize=14`;
            7. Mantén los ticks del eje X legibles usando `plt.xticks(rotation=45)` si es necesario;
            8. Elimina los bordes con `sns.despine()`;
            9. Guarda la figura obligatoriamente usando `plt.savefig('grafico_resultado.png', bbox_inches='tight')` en lugar de plt.show().

            Devuelve ÚNICAMENTE el código Python puro, sin bloques de código markdown (como ```python) ni explicaciones.

            Código Python:
        """,
        input_variables=['pregunta', 'muestra']
    )

    cadena = plantilla_respuesta | llm | StrOutputParser()

    script_bruto = cadena.invoke({
        "pregunta": pregunta,
        "muestra": muestra_datos
    })

    script_limpio = script_bruto.replace('```python', '').replace('```', '').strip()

    exec_globals = {
        "df": df_grafico,  # Pasamos el DataFrame ya filtrado
        "plt": plt,
        "sns": sns
    }

    try:
        plt.clf()
        plt.close('all')
        
        exec(script_limpio, exec_globals, {})
        
        return "Gráfico generado y guardado exitosamente como 'grafico_resultado.png' en la carpeta del proyecto."
    except Exception as e:
        return f"Error al generar el gráfico: {e}"

tools = [informacion_dataframe, codigos_python, generar_grafico]

# Creación del Agente
agent_graph = create_agent(model=llm, tools=tools)

if __name__ == "__main__":
    print("--- Agente de Mercado Central 24h Iniciado con Gráficos ---")
    
    # Prueba 1: Gráfico de los 5 productos con menor stock de todo el inventario
    print("\n[Prueba 1: Top 5 productos con MENOR stock global]")
    res_stock = agent_graph.invoke({
        "messages": [("human", "Crea un gráfico de barras horizontales que muestre los 5 productos con menor stock de todo el inventario")]
    })
    print("Respuesta 1:", res_stock["messages"][-1].content)
    
    if os.path.exists("grafico_resultado.png"):
        os.rename("grafico_resultado.png", "menor_stock.png")
        print("Gráfico guardado como 'menor_stock.png'")

    # Prueba 2: Gráfico de los 5 productos con precios más elevados de todo el inventario
    print("\n[Prueba 2: Top 5 productos con precios más elevados globales]")
    res_precios = agent_graph.invoke({
        "messages": [("human", "Crea un gráfico de barras para mostrar los 5 productos con los precios más elevados de todo el inventario")]
    })
    print("Respuesta 2:", res_precios["messages"][-1].content)
    
    if os.path.exists("grafico_resultado.png"):
        os.rename("grafico_resultado.png", "precios_elevados.png")
        print("Gráfico guardado como 'precios_elevados.png'")