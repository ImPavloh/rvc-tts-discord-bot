# RVC Discord Bot 🤖🎙️💬

Bot de texto a voz avanzado para servidores de Discord utilizando modelos de voz basados en inteligencia artificial para convertir texto en voz.

## Tabla de Contenidos 📚

- [Estructura del Repositorio](#estructura-del-repositorio-)
- [Descripción de los Archivos](#descripción-de-los-archivos-)
- [Configuración](#configuración-)
- [Cómo usar](#cómo-usar-)
- [Dependencias](#dependencias-)
- [Ejecución](#ejecución-)

## Estructura del Repositorio 📂

El repositorio está organizado de manera clara y coherente, siguiendo una estructura de directorios estándar:

RVC Discord Bot
├── config.ini
├── config.py
├── hubert_base.pt
├── lib
│ ├── infer_pack
│ └── pycache
├── models
│ └── ModelName
├── requirements.txt
├── bot.py
├── vc_infer_pipeline.py
└── pycache

## Descripción de los Archivos 📄

- `config.ini`: El archivo de configuración que almacena información clave, como el token de Discord del bot y la clave API de ElevenLabs.
- `models/`: Carpeta que alberga los modelos de voz que se utilizarán para la conversión de texto a voz.
- `requirements.txt`: Un archivo que enumera todas las dependencias de Python necesarias para el funcionamiento del bot.
- `bot.py`: Script de Python que describe la funcionalidad del bot utilizando comandos slash.

## Configuración ⚙️

Para configurar el bot, debes editar el archivo `config.ini` y rellenar la información correspondiente:

CONFIGURACIÓN | No olvides incluir el token del bot y la API de ElevenLabs si la utilizarás.
[discord]
token = PON_TU_TOKEN
type_activity = 3
activity = /ayuda

[tts]
type_tts = elevenlabs

[edge_tts]
voice = es-ES-AlvaroNeural-Male

[elevenlabs]
api_key = PON_TU_API
model_id = eleven_multilingual_v1

- `[discord] token`: Aquí debes poner el token de tu bot de Discord. Puedes obtener un token creando una nueva aplicación en el portal de desarrolladores de Discord.
- `[discord] type_activity` y `[discord] activity`: Estos campos son utilizados para establecer el estado del bot en Discord.
- `[tts] type_tts`: Este parámetro establece el tipo de Texto a Voz (TTS) que se utilizará. Puede ser "edge_tts" o "elevenlabs".
- `[edge_tts] voice`: Si eliges "edge_tts" como tu TTS, este campo determinará la voz utilizada para el TTS.
- `[elevenlabs] api_key` y `[elevenlabs] model_id`: Si eliges "elevenlabs" como tu TTS, necesitarás proporcionar tu clave API de ElevenLabs y el ID del modelo que deseas utilizar.

## Cómo usar 📝

Una vez que el bot ha sido invitado a tu servidor de Discord, puedes interactuar con él utilizando los siguientes comandos:

- `/tts <mensaje>`: Convierte el texto en voz y lo reproduce en el canal de voz. 🗣️
- `/conectar`: Conecta o mueve el bot al canal de voz en el que te encuentres. 🔗
- `/desconectar`: Desconecta el bot del canal de voz. 🔌
- `/ayuda`: Muestra un mensaje de ayuda contodos los comandos disponibles. 📖

## Dependencias 📦

Para ejecutar el bot, necesitarás instalar las siguientes dependencias:

- discord.py
- requests

Puedes instalar estas dependencias ejecutando el siguiente comando en tu terminal:

```bash
pip install -r requirements.txt
```

Esto instalará todas las bibliotecas y paquetes necesarios para el funcionamiento del bot.

## Ejecución 🚀

Para ejecutar el bot, asegúrate de haber completado la configuración en el archivo `config.ini` y haber instalado las dependencias. Luego, puedes iniciar el bot ejecutando el siguiente comando:

```bash
python prefixbot.py
```

Esto iniciará el bot y estará listo para interactuar en tu servidor de Discord. Ahora puedes disfrutar de la funcionalidad de texto a voz en tus conversaciones!

## Contribución y Soporte 💪

Si deseas contribuir a este proyecto, ¡eres bienvenido! Puedes hacerlo a través de pull requests para agregar nuevas características, solucionar problemas o mejorar la documentación.

Agradecemos tu apoyo y te pedimos que mantengas los créditos y un enlace a este repositorio en todos los archivos que contengan mi código. Esto nos ayuda como desarrolladores y permite que los nuevos programadores accedan al enlace para obtener ayuda adicional si es necesario.

Si eres nuevo en discord.py, aquí tienes algunos recursos que pueden ayudarte a aprender:

- [Documentación oficial de discord.py](https://discordpy.readthedocs.io/)
- [Tutorial de discord.py en Real Python](https://realpython.com/how-to-make-a-discord-bot-python/)
- [Comunidad de Discord.py en Discord](https://discord.gg/r3sSKJJ)

¡Gracias por usar el RVC Discord Bot! Esperamos que disfrutes de la experiencia y que este bot sea útil para tu servidor de Discord.