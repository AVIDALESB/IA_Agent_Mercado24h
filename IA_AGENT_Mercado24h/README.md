# 🛒 Asistente Inteligente de Inventario - Mercado Central 24h

¡Hola! 👋 Este proyecto es mi solución final para el **Challenge Final de Alura**. Armé este asistente inteligente pensando en resolver un problema muy real del día a día en los negocios: la pérdida de tiempo buscando información dispersa en hojas de cálculo y documentos de inventario. Con esta app, cualquier colaborador puede interactuar de forma natural y rápida.

---

## 🛑 La Problemática
En empresas como el **Mercado Central 24h**, el volumen de datos de productos, precios y stock crece constantemente. El personal operativo suele perder valiosas horas revisando manualmente archivos CSV o buscando qué productos necesitan reabastecerse urgentemente. 

## 🚀 Nuestra Solución a Futuro
Este sistema demo sienta las bases para automatizar la operación del supermercado. A futuro, la idea es escalar esta solución para que se conecte en tiempo real con las cajas registradoras, los proveedores y los almacenes físicos, permitiendo una toma de decisiones 100% basada en datos y lenguaje natural sin abrir múltiples pestañas ni sistemas complejos.

---

## 🏗️ Arquitectura de la Solución
Para lograr esto, diseñé una arquitectura ligera y modular:
1. **Dataset (`inventario.csv`):** La fuente de datos central del supermercado.
2. **Cerebro de IA (LangChain + Groq):** Utilizamos **Groq** con un modelo eficiente, rápido  y ligero (`llama-3.1-8b-instant`). Elegí este modelo ligero porque nos da respuestas en milisegundos y nos ayuda a **mantener los costos súper bajos (¡o en cero!)**, ideal para prototipos y soluciones escalables.
3. **Interfaz Gráfica (Streamlit):** Una interfaz web limpia y directa que incluye un chat interactivo y accesos rápidos laterales para funciones de prueba.

---

## 🛠️ Librerías Utilizadas
Para que todo esto funcione sin problemas, empleé las siguientes librerías de Python:
* **`streamlit`**: Para montar la interfaz web interactiva de forma rápida.
* **`pandas`**: Para la lectura y manipulación de los datos del inventario (`inventario.csv`).
* **`langchain` / `langchain-core` / `langchain-groq`**: Para construir los prompts, estructurar la lógica del agente y conectarnos con el modelo de Groq.
* **`matplotlib` y `seaborn`**: Para la generación automatizada de los gráficos estadísticos del inventario.
* **`python-dotenv`**: Para manejar de forma segura las variables de entorno (como nuestra API Key).
* **`openpyxl`**: Para exportar y dar formato a los reportes ejecutivos en archivos Excel (.xlsx).

---

## 💻 Instrucciones para Instalar y Correr el Proyecto

Si quieres probarlo localmente en tu dispositivo, solo sigue estos sencillos pasos desde tu terminal (PowerShell o Git Bash):

1. **Clonar el repositorio:**
   
git clone https://github.com/ivan02-c/challenge_final_ivan_canto_mercado24h.git

2. **Crear y activar el entorno virtual (.venv)**

python -m venv .venv

3. **Actívalo en Windows (PowerShell):**

.\venv\Scripts\Activate
   
4. **Instalar las dependencias usando el archivo requirements.txt:**

pip install -r requirements.txt

5. **Configurar tus credenciales:**

En el archivo llamado .env en la raíz de la carpeta y agrega tu API Key de Groq:
  
GROQ_API_KEY="tu_clave_de_groq_aqui"

6. **Ejecutar la aplicación:**

streamlit run main_app.py

¡Y listo! Se abrirá automáticamente una pestaña en tu navegador con la aplicación corriendo.

----
## ⚡ Funcionalidades y Accesos Rápidos

La app es capaz de responder preguntas del usuario, así como generar imágenes de gráficas, y reportes en Excel.
Quise hacer la app muy amigable, por lo que añadí una barra lateral con accesos rápidos para tareas repetitivas o clave que nos ahorran tiempo:

📉 Top 5 Menor Stock: Identifica de inmediato qué productos están bajos en inventario, ayudando al supermercado a saber qué reabastecer con urgencia. Útil para notar que productos requieren de un reestock.

📈 Top 5 Precios más Elevados: Muestra rápidamente los productos con mayor costo para un análisis rápido. Esto podría ayudar a planear ofertas para esta clase de productos.

📊 Generación de Reportes en Excel: Filtra automáticamente los productos críticos (stock menor o igual a 30) y genera un archivo .xlsx listo para descargarse con un solo clic y enviarlo a proveedores.

💬 Preguntas y Respuestas del Usuario
Gracias a la integración con el modelo ligero de Groq, el agente puede responder preguntas abiertas en lenguaje natural como:

"¿Cuál es el precio del artículo X?"

"¿Cuántos pasillos o categorías tenemos registrados?"

Consultas generales sobre la información contenida en el inventario de forma clara y directa.

--- 

## ☁️ Evidencias de Funcionamiento

📉 Test de Generación de gráficas:
<img width="1917" height="1132" alt="Test Graph Streamlit" src="https://github.com/user-attachments/assets/6d23ff05-ca65-487d-a0a8-126d7ecf77a6" />

📊 Test de Generación de Reportes en Excel:
<img width="1917" height="1150" alt="Test Reportes Streamlit" src="https://github.com/user-attachments/assets/579ba3a6-4982-47c3-b04b-5746f39a50be" />

💬 Test de Preguntas y Respuestas del Usuario:
<img width="1917" height="1130" alt="Test RAG Streamlit" src="https://github.com/user-attachments/assets/62c8e6d0-d81c-419a-8144-4f79d5f2709e" />

--- 

## 🧪 Pruebas y Resultados en el Repositorio
Para garantizar la calidad de la solución, dentro de este repositorio encontrarás la carpeta pruebas_resultados, la cual contiene scripts de prueba específicos para cada funcionalidad desarrollada, así como evidencias y archivos de resultados obtenidos durante las fases de validación local del agente.

## 👋 Agradecimientos
¡Muchas gracias por darte la vuelta en este proyecto! Fue un gran desafío armar todo el flujo desde cero y pulir cada detalle para que fuera una solución funcional. Espero que disfrutes explorando el código tanto como yo disfrute creándolo. ¡Vamos con todooooo!
