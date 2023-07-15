<div align="center">
  
![Logo](https://support.discord.com/hc/article_attachments/115002567312/Robot.gif)
  
<a href="https://github.com/ImPavloh/cpu-rvc-tts-discord-bot" target="_blank"><img src="https://img.shields.io/github/license/impavloh/cpu-rvc-tts-discord-bot?style=for-the-badge&logo=github&logoColor=white"></a>
<a href="https://twitter.com/ImPavloh" target="_blank"><img src="https://img.shields.io/badge/Pavloh-%231DA1F2.svg?style=for-the-badge&logo=twitter&logoColor=white"></a>

<h1>🎙️ RVC TTS: Bot de Discord Texto a Voz  con IA 🤖💬</h1>
<h3>Fácil de usar | Soporte multilenguaje | Fácil de configurar</h3>

<a href="README_en.md"><img alt="English" src="https://unpkg.com/language-icons/icons/en.svg" width="50px" style="border-top-left-radius: 25px; border-bottom-left-radius: 25px;"></a>
<a href="README_es.md"><img alt="Spanish" src="https://unpkg.com/language-icons/icons/es.svg" width="50px"></a>
<a href="README_pt.md"><img alt="Portuguese" src="https://unpkg.com/language-icons/icons/pt.svg" width="50px"></a>
<a href="README_de.md"><img alt="German" src="https://unpkg.com/language-icons/icons/de.svg" width="50px"></a>
<a href="README_fr.md"><img alt="French" src="https://unpkg.com/language-icons/icons/fr.svg" width="50px" style="border-top-right-radius: 25px; border-bottom-right-radius: 25px;"></a>
</div>

## 🛠️ Instalación

1. Clona el repositorio 🗂️ 
```bash
git clone https://github.com/ImPavloh/rvc-tts-discord-bot.git
```

2. Cambia al directorio del proyecto 📁 
```bash
cd rvc-tts-discord-bot
```

3. Instala las dependencias necesarias 📦
```bash
pip install -r requirements.txt
```

4. Añade tus modelos siguiendo el siguiente formato 📂
```Swift
└── Models
    └── NombreModelo
        └── NombreModelo
            ├── Archivo.pth
            └── Archivo.index
```

6. Configura el archivo config.ini ⚙️

7. Ejecuta el script principal 🚀
```bash
python bot.py
```

## 📝 Comandos 

Una vez que el bot ha sido invitado a tu servidor de Discord, puedes interactuar con él usando los siguientes comandos:

🗣️ Convierte el texto en voz y lo reproduce en el canal de voz.
```python
/tts <message>
```

🔗 Conecta o mueve el bot al canal de voz en el que te encuentras.
```python
/connect
```

🔌 Desconecta el bot del canal de voz.
```python
/disconnect
```

🌍 Cambia el idioma del TTS y del bot
```python
/language
```

❓ Muestra todos los comandos del bot.
```python
/help
```

## 📄 Archivos Importantes

⚙️ `config.ini`: Archivo de configuración que almacena información clave, como el idioma, el token de [Discord del bot](https://discord.com/developers/applications) y la clave API de [ElevenLabs](https://elevenlabs.io). Cambia los datos antes de ejecutar el bot.

🗂️ `models/`: Carpeta que debe contener los modelos de voz que se utilizarán para la conversión de texto a voz. Si todo está correcto, el bot detectará automáticamente los modelos y se generarán archivos de información para el programa.

📑 `requirements.txt`: Archivo que contiene todas las dependencias de Python necesarias para que el bot funcione.

🤖 `bot.py`: Script de Python que describe la funcionalidad del bot utilizando comandos slash. Esto iniciará el bot con la configuración y los modelos.

## ⚙️ Configuración

Para configurar el bot, debes editar el archivo ***[config.ini](https://github.com/ImPavloh/cpu-rvc-tts-discord-bot/blob/main/config.ini)*** y llenar la información relevante:

- `[discord] token`: Debes poner aquí tu token de bot de Discord. Puedes obtener un token creando una nueva aplicación en el [portal de desarrolladores de Discord](https://discord.com/developers/applications).
- `[discord] type_activity` y `activity`: Estos campos se utilizan para establecer el estado del bot.
- `[discord] language`: Configura el idioma del bot y de edge_TTS.
- `[tts] type_tts`: Este parámetro configura el tipo de Texto-a-Voz (TTS) a utilizar. Puede ser "edge_tts" o "elevenlabs".
- `[edge_tts] voice`: Si eliges "edge_tts" como tu TTS, este campo determinará la voz utilizada para el TTS.
- `[elevenlabs] api_key` y `model_id`: Si eliges "elevenlabs" como tuTTS, deberás proporcionar tu clave API de ElevenLabs y la ID del modelo que deseas utilizar.

## ⚡ Optimizaciones

Todo está optimizado para garantizar un uso mínimo de RAM y CPU. La conversión de audio utiliza el método "PM", que es el más rápido y solo requiere una CPU, sin la necesidad de una GPU. Esto hace posible ejecutar el bot en prácticamente cualquier dispositivo/servidor.

## ⚠️ Advertencia

En caso de que el archivo `config.ini` no esté configurado o los modelos RVC no estén colocados correctamente, el bot no funcionará.

## 📝 Licencia

Al usar este proyecto, aceptas la ***[licencia](https://github.com/ImPavloh/rvc-tts-discord-bot/blob/main/LICENSE)***.