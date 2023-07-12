# RVC Discord Bot 🤖🎙️💬

Bot de texto a voz avanzado para servidores de Discord utilizando modelos de voz basados en inteligencia artificial para convertir texto en voz.

## Archivos importantes📄

- `config.ini`: El archivo de configuración que almacena información clave, como el token de Discord del bot y la clave API de ElevenLabs.
- `models/`: Carpeta que debe de contener los modelos de voz que se utilizarán para la conversión de texto a voz.
- `requirements.txt`: Un archivo que enumera todas las dependencias de Python necesarias para el funcionamiento del bot.
- `bot.py`: Script de Python que describe la funcionalidad del bot utilizando comandos slash.

## Configuración ⚙️

Para configurar el bot, debes editar el archivo `config.ini` y rellenar la información correspondiente:

- `[discord] token`: Debes de poner el token de tu bot de Discord. Puedes obtener un token creando una nueva aplicación en el [portal de desarrolladores de Discord](https://discord.com/developers/applications)
- `[discord] type_activity` y `activity`: Estos campos son utilizados para establecer el estado del bot.
- `[tts] type_tts`: Este parámetro establece el tipo de Texto a Voz (TTS) que se utilizará. Puede ser "edge_tts" o "elevenlabs".
- `[edge_tts] voice`: Si eliges "edge_tts" como tu TTS, este campo determinará la voz utilizada para el TTS.
- `[elevenlabs] api_key` y `model_id`: Si eliges "elevenlabs" como tu TTS, necesitarás proporcionar tu clave API de ElevenLabs y el ID del modelo que deseas utilizar.

## Cómo usar 📝

Una vez que el bot ha sido invitado a tu servidor de Discord, puedes interactuar con él utilizando los siguientes comandos:

- `/tts <mensaje>`: Convierte el texto en voz y lo reproduce en el canal de voz. 🗣️
- `/conectar`: Conecta o mueve el bot al canal de voz en el que te encuentres. 🔗
- `/desconectar`: Desconecta el bot del canal de voz. 🔌
- `/ayuda`: Muestra un mensaje de ayuda con todos los comandos disponibles. 📖

## Dependencias 📦

Para ejecutar el bot, necesitarás instalar todas las bibliotecas y paquetes necesarios, puedes instalar todo ejecutando el siguiente comando en tu terminal:

```bash
pip install -r requirements.txt
```

## Ejecución 🚀

Para ejecutar el bot, asegúrate de haber completado la configuración en el archivo `config.ini` y haber instalado las dependencias. Luego, puedes iniciar el bot ejecutando el siguiente comando:

```bash
python bot.py
```

Esto iniciará el bot y estará listo para interactuar en tu servidor de Discord.
