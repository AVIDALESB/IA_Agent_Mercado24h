
import os
import pandas as pd
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importaciones
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_experimental.tools.python.tool import PythonAstREPLTool

# Cargar el DataFrame de Mercado Central
df = pd.read_csv("inventario.csv")

# Configurar el LLM con el nombre de modelo correcto y activo en Groq
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# Definición de herramientas usando el decorador @tool oficial de LangChain
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

tools = [informacion_dataframe, codigos_python]

# Creación del Agente
agent_graph = create_agent(model=llm, tools=tools)

if __name__ == "__main__":
    print("--- Agente de Mercado Central 24h Iniciado (LangGraph) ---")
    
    # Prueba 1: Panorama general
    print("\n[Prueba 1: Panorama General]")
    res1 = agent_graph.invoke({
        "messages": [("human", "¿Cuál es la información general del inventario?")]
    })
    print("Respuesta:", res1["messages"][-1].content)
    
    # Prueba 2: Consulta específica
    print("\n[Prueba 2: Consulta de datos específicos]")
    res2 = agent_graph.invoke({
        "messages": [("human", "¿Cuál es el precio del producto Pan de Caja Integral?")]
    })
    print("Respuesta:", res2["messages"][-1].content)