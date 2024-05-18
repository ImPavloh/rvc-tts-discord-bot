<div align="center">
  
<img src="https://i.imgur.com/hWNq5jh.png" width="200"/><br>
  
<a href="https://github.com/ImPavloh/rvc-tts-discord-bot" target="_blank"><img src="https://img.shields.io/github/license/impavloh/rvc-tts-discord-bot?style=for-the-badge&logo=github&logoColor=white"></a>
<a href="https://twitter.com/ImPavloh" target="_blank"><img src="https://img.shields.io/badge/Pavloh-%231DA1F2.svg?style=for-the-badge&logo=twitter&logoColor=white"></a>

<h1>🎙️ VoiceMe: Text-zu-Sprache Discord Bot mit KI 🤖💬</h1>
<h3>Einfach zu benutzen | Mehrsprachige Unterstützung | Einfach einzurichten</h3>
<a href="README.md"><img alt="English" src="https://unpkg.com/language-icons/icons/en.svg" width="50px" style="border-top-left-radius: 25px; border-bottom-left-radius: 25px;"></a>
<a href="README_es.md"><img alt="Spanish" src="https://unpkg.com/language-icons/icons/es.svg" width="50px"></a>
<a href="README_pt.md"><img alt="Portuguese" src="https://unpkg.com/language-icons/icons/pt.svg" width="50px"></a>
<a href="README_de.md"><img alt="German" src="https://unpkg.com/language-icons/icons/de.svg" width="50px"></a>
<a href="README_fr.md"><img alt="French" src="https://unpkg.com/language-icons/icons/fr.svg" width="50px" style="border-top-right-radius: 25px; border-bottom-right-radius: 25px;"></a><br>

<img src="https://i.imgur.com/s6ksS9x.png" width="444"/>

### [Probiere VoiceMe in Discord aus](https://github.com/ImPavloh/rvc-tts-discord-bot)
*LTS-Version (verfügbar mit nur 3 Modellen)*

<a href="https://github.com/ImPavloh/rvc-tts-discord-bot"><img alt="German" src="https://i.imgur.com/hc6AbYN.png" width="50px"></a>

</div>

## 🛠️ Installation

1. Klonen Sie das Repository 🗂️ 
```bash
git clone https://github.com/ImPavloh/rvc-tts-discord-bot
```

2. Wechseln Sie in das Projektverzeichnis 📁 
```bash
cd rvc-tts-discord-bot
```

3. Installieren Sie die erforderlichen Abhängigkeiten 📦
```bash
pip install -r requirements.txt
```

4. Lade das Hubert-Basismodell von **[hier herunter](https://huggingface.co/spaces/ImPavloh/RVC-TTS-Demo/resolve/main/hubert_base.pt)**. Speichere die heruntergeladene Datei im Stammverzeichnis des Projekts.

5. Fügen Sie Ihre RVC Modelle im folgenden Format hinzu 📂
```Swift
└── Models
    └── ModelName
        └── ModelName
            ├── File.pth
            └── File.index
```

6. Konfigurieren Sie die config.ini Datei ⚙️

7. Führen Sie das Hauptskript aus 🚀
```bash
python bot.py
```

## 📝 Befehle 

Sobald der Bot zu Ihrem Discord-Server hinzugefügt wurde, können Sie mit ihm interagieren, indem Sie die folgenden Befehle verwenden:

🗣️ Wandelt Text in Sprache um und spielt ihn im Sprachkanal ab.
```python
/say <message>
```

🔗 Verbindet oder verschiebt den Bot in den Sprachkanal, in dem Sie sich befinden.
```python
/connect
```

🔌 Trennt den Bot vom Sprachkanal.
```python
/disconnect
```

🌍 Wechselt die Sprache des TTS und des Bots
```python
/language
```

❓ Zeigt alle Befehle des Bots an.
```python
/help
```

## 📄 Wichtige Dateien

⚙️ `config.ini`: Konfigurationsdatei, die Schlüsselinformationen wie Sprache, [Discord Bot Token](https://discord.com/developers/applications) und [ElevenLabs](https://elevenlabs.io) API-Schlüssel speichert. Ändern Sie die Daten, bevor Sie den Bot ausführen.

🗂️ `models/`: Ordner, der die Sprachmodelle enthalten sollte, die für die Text-zu-Sprache-Konvertierung verwendet werden. Wenn alles korrekt ist, wird der Bot die RVC Modelle automatisch erkennen und Informationsdateien für das Programm generieren.

📑 `requirements.txt`: Datei, die alle erforderlichen Python-Abhängigkeiten für den Betrieb des Bots enthält.

🤖 `bot.py`: Python-Skript, das die Funktionalität des Bots mit Slash-Befehlen beschreibt. Dies startet den Bot mit der Konfiguration und den Modellen.

## ⚙️ Konfiguration

Um den Bot zu konfigurieren, müssen Sie die Datei ***[config.ini](https://github.com/ImPavloh/cpu-rvc-tts-discord-bot/blob/main/config.ini)*** bearbeiten und die relevanten Informationen eingeben:

- `[discord] token`: Hier müssen Sie Ihr Discord Bot Token eingeben. Ein Token können Sie erhalten, indem Sie eine neue Anwendung im [Discord Developer Portal](https://discord.com/developers/applications) erstellen.
- `[discord] type_activity` und `activity`: Diese Felder werden verwendet, um den Status des Bots festzulegen.
- `[discord] language`: Stellt die Sprache des Bots und von edge_TTS ein.
- `[tts] type_tts`: Dieser Parameter konfiguriert den zu verwendenden Text-to-Speech (TTS) Typ. Es kann "edge_tts" oder "elevenlabs" sein.
- `[edge_tts] voice`: Wenn Sie "edge_tts" als Ihr TTS wählen, bestimmt dieses Feld die für den TTS verwendete Stimme.
- `[elevenlabs] api_key` und `model_id`: Wenn Sie "elevenlabs" als Ihren TTS wählen, müssen Sie Ihren ElevenLabs API-Schlüssel und die ID des Modells, das Sie verwenden möchten, angeben.

## ⚡ Optimierungen

Alles ist optimiert, um einen minimalen Einsatz von RAM und CPU zu gewährleisten. Die Audioumwandlung verwendet die "PM"-Methode, die am schnellsten ist und nur eine CPU benötigt, ohne eine GPU zu benötigen. Dies ermöglicht es, den Bot auf nahezu jedem Gerät/Server auszuführen.

## ⚠️ Warnung

Falls die `config.ini` Datei nicht konfiguriert ist oder die RVC-Modelle nicht korrekt platziert sind, wird der Bot nicht funktionieren.

## 📝 Lizenz

Durch die Nutzung dieses Projekts akzeptieren Sie die ***[Lizenz](https://github.com/ImPavloh/rvc-tts-discord-bot/blob/main/LICENSE)***.
