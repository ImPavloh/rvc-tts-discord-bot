<div align="center">
  
![Logo](https://support.discord.com/hc/article_attachments/115002567312/Robot.gif)
  
<a href="https://github.com/ImPavloh/cpu-rvc-tts-discord-bot" target="_blank"><img src="https://img.shields.io/github/license/impavloh/cpu-rvc-tts-discord-bot?style=for-the-badge&logo=github&logoColor=white"></a>
<a href="https://twitter.com/ImPavloh" target="_blank"><img src="https://img.shields.io/badge/Pavloh-%231DA1F2.svg?style=for-the-badge&logo=twitter&logoColor=white"></a>

<h1>🎙️ RVC TTS ~ A Discord bot 🤖💬</h1>
</div>

Bot de texto a voz avanzado para servidores de Discord utilizando modelos de voz basados en Inteligencia Artificial.

## 🛠️ Instalación

1. Clona el repositorio 🗂️ 
```bash
git clone https://github.com/ImPavloh/cpu-rvc-tts-discord-bot.git
```

2. Cambia al directorio del proyecto 📁 
```bash
cd cpu-rvc-tts-discord-bot
```

3. Instala las dependencias necesarias 📦
```bash
pip install -r requirements.txt
```

4. En la carpeta "models" cambia los nombres y agrega tus archivos 📂 

5. [Configura el archivo config.ini](#configuración-) ⚙️

6. Ejecuta el script principal 🚀
```bash
python voiceit.py
```

## 📝 Comandos 

Una vez que el bot ha sido invitado a tu servidor de Discord, puedes interactuar con él utilizando los siguientes comandos:

🗣️ Convierte el texto en voz y lo reproduce en el canal de voz.
```python
/tts <mensaje>
```

🔗 Conecta o mueve el bot al canal de voz en el que te encuentres.
```python
/conectar
```

🔌 Desconecta el bot del canal de voz. 
```python
/desconectar
```

❓ Muestra todos los comandos del bot.
```python
/ayuda
```

## 📄 Archivos importantes

⚙️  `config.ini`: Archivo de configuración que almacena información clave, como el [token de Discord](https://discord.com/developers/applications) del bot y la clave API de [ElevenLabs](https://elevenlabs.io). Cambia los datos antes de ejecutar el bot.

🗂️  `models/`: Carpeta que debe de contener los modelos de voz que se utilizarán para la conversión de texto a voz. Si todo está correcto, el bot detecterá automáticamente los modelos y se generarán unos archivos de información para el programa.

📑  `requirements.txt`: Un archivo que contiene todas las dependencias de Python necesarias para el funcionamiento del bot. Recuerda ejecutar el comando de [dependencias](#dependencias-).

🤖  `bot.py`: Script de Python que describe la funcionalidad del bot utilizando comandos slash.

## ⚙️ Configuración

Para configurar el bot, debes editar el archivo ***[config.ini](https://github.com/ImPavloh/cpu-rvc-tts-discord-bot/blob/main/config.ini)*** y rellenar la información correspondiente:

- `[discord] token`: Debes de poner el token de tu bot de Discord. Puedes obtener un token creando una nueva aplicación en el [portal de desarrolladores de Discord](https://discord.com/developers/applications)
- `[discord] type_activity` y `activity`: Estos campos son utilizados para establecer el estado del bot.
- `[tts] type_tts`: Este parámetro establece el tipo de Texto a Voz (TTS) que se utilizará. Puede ser "edge_tts" o "elevenlabs".
- `[edge_tts] voice`: Si eliges "edge_tts" como tu TTS, este campo determinará la voz utilizada para el TTS.
- `[elevenlabs] api_key` y `model_id`: Si eliges "elevenlabs" como tu TTS, necesitarás proporcionar tu clave API de ElevenLabs y el ID del modelo que deseas utilizar.

Esto iniciará el bot y estará listo para interactuar en tu servidor de Discord.

## ⚡ Optimizaciones

Todo está optimizado para garantizar el mínimo consumo de memoria RAM y uso de CPU. Además, la conversación del audio emplea el método "PM", que es el más rápido y solo requiere una CPU, sin necesidad de una GPU. Esto facilita la ejecución del bot en prácticamente cualquier dispositivo/servidor.

## ⚠️ Advertencia

- En caso de no configurar el archivo `config.ini` o haber colocado y editado correctamente los modelos RVC el bot no funcionará.

## 📝 Licencia y términos de uso

Al utilizar este proyecto, aceptas la [licencia](https://github.com/ImPavloh/cpu-rvc-tts-discord-bot/blob/main/LICENSE).
