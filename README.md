<div align="center">
  
![Logo](https://support.discord.com/hc/article_attachments/115002567312/Robot.gif)
  
<a href="https://github.com/ImPavloh/cpu-rvc-tts-discord-bot" target="_blank"><img src="https://img.shields.io/github/license/impavloh/cpu-rvc-tts-discord-bot?style=for-the-badge&logo=github&logoColor=white"></a>
<a href="https://twitter.com/ImPavloh" target="_blank"><img src="https://img.shields.io/badge/Pavloh-%231DA1F2.svg?style=for-the-badge&logo=twitter&logoColor=white"></a>

<h1>🎙️ RVC TTS: AI-Powered TTS Discord Bot 🤖💬</h1>
<h3>User-friendly  |  Multi-Language Support  |  Easily Configurable</h3>
<a href="README.md"><img alt="English" src="https://unpkg.com/language-icons/icons/en.svg" width="50px" style="border-top-left-radius: 25px; border-bottom-left-radius: 25px;"></a>
<a href="README_es.md"><img alt="Spanish" src="https://unpkg.com/language-icons/icons/es.svg" width="50px"></a>
<a href="README_pt.md"><img alt="Portuguese" src="https://unpkg.com/language-icons/icons/pt.svg" width="50px"></a>
<a href="README_de.md"><img alt="German" src="https://unpkg.com/language-icons/icons/de.svg" width="50px"></a>
<a href="README_fr.md"><img alt="French" src="https://unpkg.com/language-icons/icons/fr.svg" width="50px" style="border-top-right-radius: 25px; border-bottom-right-radius: 25px;"></a>
</div>

## 🛠️ Installation

1. Clone the repository 🗂️ 
```bash
git clone https://github.com/ImPavloh/rvc-tts-discord-bot.git
```

2. Change to the project directory 📁
```bash
cd rvc-tts-discord-bot
```

3. Install the necessary dependencies 📦
```bash
pip install -r requirements.txt
```

4. Add your models following the next format 📂
```Swift
└── Models
    └── ModelName
        └── ModelName
            ├── File.pth
            └── File.index
```

6. Configure the config.ini file ⚙️

7. Run the main script 🚀
```bash
python voiceit.py
```

## 📝 Commands 

Once the bot has been invited to your Discord server, you can interact with it using the following commands:

🗣️ Converts text into speech and plays it in the voice channel.
```python
/tts <message>
```

🔗 Connects or moves the bot to the voice channel you are in.
```python
/connect
```

🔌 Disconnects the bot from the voice channel.
```python
/disconnect
```

🌍 Changes TTS and bot language
```python
/language
```

❓ Displays all the bot commands.
```python
/help
```

## 📄 Important Files

⚙️  `config.ini`: Configuration file that stores key information, such as the language, the bot's [Discord token](https://discord.com/developers/applications) and [ElevenLabs](https://elevenlabs.io) API key. Change the data before running the bot.

🗂️  `models/`: Folder that should contain the voice models that will be used for text-to-speech conversion. If everything is correct, the bot will automatically detect the models and information files for the program will be generated.

📑  `requirements.txt`: File containing all the Python dependencies needed for the bot to function.

🤖  `bot.py`: Python script that describes the bot's functionality using slash commands. This will start the bot with the configuration and models.

## ⚙️ Configuration

To configure the bot, you must edit the ***[config.ini](https://github.com/ImPavloh/cpu-rvc-tts-discord-bot/blob/main/config.ini)*** file and fill in the relevant information:

- `[discord] token`: You have to put your Discord bot token here. You can get a token by creating a new application in the [Discord developer portal](https://discord.com/developers/applications)
- `[discord] type_activity` and `activity`: These fields are used to set the bot's status.
- `[discord] language`: Set the bot and edge_TTS language.
- `[tts] type_tts`: This parameter sets the type of Text-to-Speech (TTS) to be used. It can be "edge_tts" or "elevenlabs".
- `[edge_tts] voice`: If you choose "edge_tts" as your TTS, this field will determine the voice used for the TTS.
- `[elevenlabs] api_key` and `model_id`: If you choose "elevenlabs" as your TTS, you will need to provide your ElevenLabs API key and the model ID you wish to use.

## ⚡ Optimizations

Everything is optimized to ensure minimal RAM and CPU usage. The audio conversion uses the "PM" method, which is the fastest and only requires a CPU, without the need for a GPU. This makes running the bot on virtually any device/server possible.

## ⚠️ Warning

In case the `config.ini` file is not configured or the RVC models are not properly placed, the bot won't work.

## 📝 License

By using this project, you agree to the [license](https://github.com/ImPavloh/rvc-tts-discord-bot/blob/main/LICENSE).
