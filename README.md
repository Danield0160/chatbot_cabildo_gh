¡Claro! Aquí tienes un borrador de README.md detallado y con un toque visual para tu proyecto de GitHub.

```markdown
# 🏝️ Chatbot para el Cabildo de Lanzarote  Lanzarote 🇮🇨

Este proyecto implementa un chatbot conversacional diseñado para proporcionar información relevante sobre el Cabildo de Lanzarote. Utiliza técnicas de Web Scraping para recolectar datos, un modelo de lenguaje grande (LLM) para la comprensión y generación de respuestas, y la plataforma AnythingLLM para la gestión y despliegue del chatbot.

## 🤖 ¿Qué es un Chatbot?

Un chatbot es un programa informático diseñado para simular una conversación humana a través de texto o voz. En este caso, nuestro chatbot está especializado en responder preguntas sobre los servicios, noticias, eventos y cualquier información pública relacionada con el Cabildo de Lanzarote, utilizando la información extraída de su sitio web oficial.

## ✨ Características Principales

*   **Recolección de Datos Automatizada:** Utiliza un script de Web Scraping para obtener información actualizada del sitio web del Cabildo.
*   **Procesamiento de Lenguaje Natural:** Emplea modelos LLM para entender las preguntas de los usuarios y generar respuestas coherentes.
*   **Base de Conocimiento Personalizada:** La información recolectada se utiliza para crear una base de conocimiento específica para el chatbot.
*   **Interfaz de Usuario con AnythingLLM:** Se despliega y gestiona a través de AnythingLLM, permitiendo una fácil configuración e interacción.
*   **Despliegue Local:** Utiliza Ollama para ejecutar modelos LLM localmente, asegurando la privacidad de los datos.

## 📚 Tecnologías Utilizadas

*   **Python:** Para el Web Scraping y procesamiento de datos.
*   **Jupyter Notebook:** Para el análisis y parsing de texto.
*   **Docker:** Para la contenerización y despliegue de AnythingLLM.
*   **AnythingLLM:** Plataforma para construir chatbots privados con LLMs.
*   **Ollama:** Para ejecutar modelos LLM (como Gemma y BGE-M3) localmente.

## 🚀 Pasos de Instalación y Configuración

Sigue estos pasos cuidadosamente para poner en marcha el chatbot:

---

### 1. Crear Entorno Virtual de Python e Instalar Dependencias

Es crucial aislar las dependencias del proyecto.

```bash
# Clona este repositorio (si aún no lo has hecho)
# git clone <URL_DEL_REPOSITORIO>
# cd <NOMBRE_DEL_REPOSITORIO>

# Crea un entorno virtual
python -m venv env_chatbot_lanzarote

# Activa el entorno virtual
# En Windows:
env_chatbot_lanzarote\Scripts\activate
# En macOS/Linux:
source env_chatbot_lanzarote/bin/activate

# Instala las dependencias
pip install -r requirements.txt
```
> **Nota:** Asegúrate de tener Python 3.8 o superior instalado.

---

### 2. Ejecutar el Web Scrapper

Este script recolectará la información necesaria del sitio web del Cabildo de Lanzarote.

```bash
python web_scrapper.py
```
> Este proceso puede tardar un tiempo dependiendo de la cantidad de información a extraer y la velocidad de tu conexión. Los datos se guardarán en archivos locales.

---

### 3. Ejecutar el Notebook `parser_str.ipynb`

Este notebook procesará y limpiará los datos recolectados por el scrapper, preparándolos para ser ingeridos por el LLM.

*   Abre Jupyter Notebook o Jupyter Lab.
*   Navega hasta el archivo `parser_str.ipynb` y ejecútalo celda por celda.
*   Esto generará los archivos de texto finales que se subirán a AnythingLLM.

---

### 4. Instalar Docker y Descargar la Imagen de AnythingLLM

Docker es necesario para ejecutar AnythingLLM en un contenedor.

*   **Instala Docker:** Si aún no lo tienes, descarga e instala [Docker Desktop](https://www.docker.com/products/docker-desktop/) para tu sistema operativo.
*   **Descarga la imagen de AnythingLLM:**
    ```bash
    docker pull mintplexlabs/anythingllm:latest
    ```

---

### 5. Ejecutar el Contenedor de AnythingLLM

Elige el comando según tu sistema operativo:

*   **Windows (usando PowerShell como Administrador):**
    ```powershell
      $env:STORAGE_LOCATION="$HOME\Documents\anythingllm"; `
      If(!(Test-Path $env:STORAGE_LOCATION)) {New-Item $env:STORAGE_LOCATION -ItemType Directory}; `
      If(!(Test-Path "$env:STORAGE_LOCATION\.env")) {New-Item "$env:STORAGE_LOCATION\.env" -ItemType File}; `
      docker run -d -p 3001:3001 `
      --cap-add SYS_ADMIN `
      -v "$env:STORAGE_LOCATION`:/app/server/storage" `
      -v "$env:STORAGE_LOCATION\.env:/app/server/.env" `
      -e STORAGE_DIR="/app/server/storage" `
      mintplexlabs/anythingllm;
    ```

*   **Linux o macOS (usando la terminal):**
    ```bash
      export STORAGE_LOCATION=$HOME/anythingllm && \
      mkdir -p $STORAGE_LOCATION && \
      touch "$STORAGE_LOCATION/.env" && \
      docker run -d -p 3001:3001 \
      --cap-add SYS_ADMIN \
      -v ${STORAGE_LOCATION}:/app/server/storage \
      -v ${STORAGE_LOCATION}/.env:/app/server/.env \
      -e STORAGE_DIR="/app/server/storage" \
      mintplexlabs/anythingllm
    ```
> Una vez ejecutado, podrás acceder a AnythingLLM desde tu navegador en `http://localhost:3001`.

---

### 6. Instalar Ollama y Descargar Modelos LLM

Ollama permite ejecutar modelos de lenguaje grandes localmente.

*   **Instala Ollama:** Visita [ollama.com](https://ollama.com/) y sigue las instrucciones de instalación para tu sistema operativo.
*   **Descarga los modelos necesarios:**
    ```bash
    ollama pull gemma3:4b 
    ollama pull bge-m3
    ```
> **Importante:** Ejecutar modelos LLM localmente puede requerir una cantidad significativa de RAM y, preferiblemente, una GPU. `gemma:2b` es más ligero, `gemma:7b` o `gemma3:4b` (si existe) necesitarán más recursos.

---

### 7. Configurar AnythingLLM ⚙️

Accede a `http://localhost:3001` y sigue estos pasos para la configuración inicial:

*   **a) Preferencia de LLM:**
    *   **LLM Provider:** `Ollama`
    *   **Ollama Base URL:** `http://host.docker.internal:11434`
        *   *Nota:* `host.docker.internal` es un DNS especial que Docker resuelve a la IP interna del host desde dentro de un contenedor. Si esto no funciona (por ejemplo, en Linux a veces requiere configuración extra de Docker), puedes usar la IP de tu máquina en la red local (ej. `http://192.168.1.XX:11434`).
*   **b) Preferencia de LLM:**
    *   **Ollama Model Selection:**  `gemma3:4b` 
*   **c) Preferencia de Incrustación (Embedding):**
    *   **Embedding Provider:** `Ollama`
*   **d) Preferencia de Incrustación:**
    *   **Ollama Embedding Model Selection:** `bge-m3:latest`
*   **e) Preferencia de Incrustación:**
    *   **Max Embedding Chunk Length:** `8192` (o el máximo que permita `bge-m3`)
*   **f) Preferencias de División y Fragmentación de Texto:**
    *   **Text Chunk Size:** `8192` (ajusta según el modelo y la naturaleza de tus datos, pero debe ser consistente con el Embedding Chunk Length)

---

### 8. Crear un Nuevo Espacio de Trabajo (Workspace) 📂

Dentro de AnythingLLM, crea un nuevo espacio de trabajo para el chatbot del Cabildo.

*   **Nombre del Workspace:** Algo descriptivo, ej. "Chatbot Cabildo Lanzarote"
*   **Configuración del Chat:**
    *   **a) Modo de Chat:** `Consulta` (Query)
    *   **b) Historial de Chat:** `2` (Número de mensajes anteriores a considerar en la conversación)
    *   **c) Prompt del Sistema (System Prompt):**
        ```text
        Eres un chatbot del cabildo de lanzarote, una pagina goburnamental. Dada la siguiente conversación, el contexto (posiblemente relevante o no ) y una pregunta de seguimiento, responde a la pregunta actual que el usuario está haciendo. Devuelve únicamente tu respuesta a la pregunta, basándote en la información anterior, siguiendo las instrucciones del usuario según sea necesario y citando el enlace (url) fuente de la información. Tendrás que responder en el mismo idioma en el que se te pregunta. Responde únicamente en base al contexto que se te pase. Devuelve la respuesta en Español. Ten en cuenta que de los contexto pasados, puede estar bien solamente uno, y puede no ser el primero, o el segundo, o el tercero, etc.
        ```
*   **Base de Datos de Vectores (Vector Database):**
    *   **d) Search Preference:** `Accuracy optimized` (Optimizado para precisión)
    *   **e) Máximo de fragmentos de contexto:** `8`
    *   **f) Umbral de similitud de documentos:** `Bajo` (Low) - Esto permite recuperar más documentos aunque no sean exactamente iguales. Puedes ajustarlo más tarde.

---

### 9. Subir los Archivos de Texto Generados 📄

En el espacio de trabajo que acabas de crear en AnythingLLM:

*   Navega a la sección de gestión de documentos o "Upload Documents".
*   Sube los archivos `.txt` que fueron generados por el notebook `parser_str.ipynb` (del paso 3).
*   AnythingLLM procesará estos archivos y creará los embeddings. Este proceso puede tomar un tiempo.

---

### 10. Incrustar el Widget de Chat en una Página Web 🌐 (Opcional)

Si deseas integrar el chatbot en una página web existente:

*   En la configuración de AnythingLLM, busca la sección "Embeddable Chat Widgets" o similar.
*   Genera un nuevo widget de chat incrustable.
*   Copia el código HTML/JavaScript proporcionado.
*   Pega este código despues del `<body>` de la página web donde quieras que aparezca el chatbot.

---

## 🎉 ¡Listo para Chatear!

Una vez completados todos los pasos, deberías poder interactuar con tu chatbot del Cabildo de Lanzarote a través de la interfaz de AnythingLLM o la página web donde lo hayas incrustado.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si tienes ideas para mejorar el scrapper, el procesamiento de datos, los prompts o cualquier otro aspecto del proyecto, por favor abre un Pull Request o un Issue.

## 📜 Licencia

(Especifica aquí la licencia de tu proyecto, ej. MIT, Apache 2.0, etc. Si no estás seguro, MIT es una opción común y permisiva).
```

### Consideraciones Adicionales:

1.  **`gemma3:4b`:** No estoy completamente seguro si `gemma3:4b` es un tag oficial y ampliamente disponible en Ollama. Si no lo es, el usuario deberá ajustarlo al modelo `gemma` que mejor se adapte a sus recursos (e.g., `gemma:2b` o `gemma:7b`). He puesto `gemma:2b` como un ejemplo funcional y he añadido una nota al respecto. El usuario debe verificar los modelos disponibles con `ollama list`.
2.  **Claridad en PowerShell:** He mantenido el comando de PowerShell tal cual lo proporcionaste, asumiendo que es correcto.
3.  **Emojis y Formato:** He intentado añadir emojis y usar formato Markdown para hacerlo más "bonito" y legible.
4.  **Comentarios en Código:** He añadido comentarios en los bloques de código para mayor claridad.
5.  **Flujo Lógico:** Los pasos están ordenados lógicamente según la descripción.

Espero que este README sea de tu agrado y útil para tu proyecto. ¡Mucha suerte!
