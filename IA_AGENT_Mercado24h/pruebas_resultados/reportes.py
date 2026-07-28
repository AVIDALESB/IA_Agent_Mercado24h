import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importaciones
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_agent
from langchain_experimental.tools.python.tool import PythonAstREPLTool

# Cargar el DataFrame de Mercado Central
df = pd.read_csv("inventario.csv")

# Configurar el LLM con un modelo un poco más ligero
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# Definición de Herramientas del Agente
@tool
def informacion_dataframe(pregunta: str) -> str:
    """Proporciona un panorama general del DataFrame (filas, columnas, nombres y nulos)."""
    filas, columnas = df.shape
    cols = ", ".join(df.columns.tolist())
    nulos = df.isnull().sum().to_dict()
    return f"El inventario tiene {filas} productos y {columnas} columnas. Las columnas son: {cols}. Conteo de nulos: {nulos}"

# Instanciamos la herramienta de Python para análisis seguro
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
    
    pregunta_lower = pregunta.lower()
    df_grafico = df.copy()
    
    try:
        if "menor stock" in pregunta_lower or "stock más bajo" in pregunta_lower:
            col_stock = next((c for c in df.columns if 'stock' in c.lower() or 'cantidad' in c.lower()), None)
            if col_stock:
                df_grafico = df.nsmallest(5, col_stock)
        elif "precio" in pregunta_lower and ("elevado" in pregunta_lower or "alto" in pregunta_lower or "mayor" in pregunta_lower):
            col_precio = next((c for c in df.columns if 'precio' in c.lower() or 'costo' in c.lower()), None)
            if col_precio:
                df_grafico = df.nlargest(5, col_precio)
    except Exception:
        pass

    resumen_datos = df_grafico.to_string()

    plantilla_respuesta = PromptTemplate(
        template="""
            Eres un especialista en visualización de datos. Genera **únicamente el código Python** 
            para graficar los siguientes datos usando `matplotlib.pyplot` y `seaborn`:

            ## Datos:
            {muestra}

            ## Instrucciones estrictas:
            1. Usa `sns.set_theme()`;
            2. Grafica directamente sobre el DataFrame `df`;
            3. Configura `figsize=(8, 4)`, título con `loc='left'`, rotación de 45° en X si es necesario, y `sns.despine()`;
            4. Guarda obligatoriamente con `plt.savefig('grafico_resultado.png', bbox_inches='tight')`.
            5. Devuelve ÚNICAMENTE el código Python puro, sin markdown ni explicaciones.

            Código Python:
        """,
        input_variables=['muestra']
    )

    cadena = plantilla_respuesta | llm | StrOutputParser()

    script_bruto = cadena.invoke({"muestra": resumen_datos})
    script_limpio = script_bruto.replace('```python', '').replace('```', '').strip()

    exec_globals = {
        "df": df_grafico,
        "plt": plt,
        "sns": sns
    }

    try:
        plt.clf()
        plt.close('all')
        exec(script_limpio, exec_globals, {})
        return "Gráfico generado exitosamente como 'grafico_resultado.png'."
    except Exception as e:
        return f"Error al generar el gráfico: {e}"


@tool
def generar_reporte_reabastecimiento(stock_minimo: int = 30) -> str:
    """
    Utiliza esta herramienta cuando el usuario solicite un reporte, exportar datos,
    crear un archivo Excel o listar productos críticos para reabastecimiento o con bajo stock.
    """
    col_stock = next((c for c in df.columns if 'stock' in c.lower() or 'cantidad' in c.lower()), None)
    
    if not col_stock:
        return "No se pudo identificar la columna de stock en el inventario."
    
    df_criticos = df[df[col_stock] <= stock_minimo]
    
    if df_criticos.empty:
        return f"¡Buenas noticias! No hay productos con un stock igual o menor a {stock_minimo}."
    
    nombre_archivo = "reporte_reabastecimiento.xlsx"
    df_criticos.to_excel(nombre_archivo, index=False)
    
    return f"Reporte generado exitosamente con {len(df_criticos)} productos críticos. Guardado en el archivo '{nombre_archivo}' para su descarga."


# Lista de herramientas
tools = [informacion_dataframe, codigos_python, generar_grafico, generar_reporte_reabastecimiento]

# Creación del Agente
agent_graph = create_agent(model=llm, tools=tools)

if __name__ == "__main__":
    print("--- Agente de Mercado Central 24h (Optimizado y Rápido) Iniciado ---")
    
    # Prueba de la herramienta de reportes
    print("\n[Prueba: Generar reporte de reabastecimiento con stock <= 30]")
    res_reporte = agent_graph.invoke({
        "messages": [("human", "Necesito que generes un reporte en Excel con los productos que tienen un stock menor o igual a 30 para pasárselo al proveedor")]
    })
    print("Respuesta del Agente:", res_reporte["messages"][-1].content)