<div align="center">
  
<img src="https://i.imgur.com/hWNq5jh.png" width="200"/><br>
  
<a href="https://github.com/ImPavloh/rvc-tts-discord-bot" target="_blank"><img src="https://img.shields.io/github/license/impavloh/rvc-tts-discord-bot?style=for-the-badge&logo=github&logoColor=white"></a>
<a href="https://twitter.com/ImPavloh" target="_blank"><img src="https://img.shields.io/badge/Pavloh-%231DA1F2.svg?style=for-the-badge&logo=twitter&logoColor=white"></a>

<h1>🎙️ VoiceMe: Bot de Discord Texte à Voix avec IA 🤖💬</h1>
<h3>Facile à utiliser | Support multilingue | Facile à configurer</h3>
<a href="README.md"><img alt="English" src="https://unpkg.com/language-icons/icons/en.svg" width="50px" style="border-top-left-radius: 25px; border-bottom-left-radius: 25px;"></a>
<a href="README_es.md"><img alt="Spanish" src="https://unpkg.com/language-icons/icons/es.svg" width="50px"></a>
<a href="README_pt.md"><img alt="Portuguese" src="https://unpkg.com/language-icons/icons/pt.svg" width="50px"></a>
<a href="README_de.md"><img alt="German" src="https://unpkg.com/language-icons/icons/de.svg" width="50px"></a>
<a href="README_fr.md"><img alt="French" src="https://unpkg.com/language-icons/icons/fr.svg" width="50px" style="border-top-right-radius: 25px; border-bottom-right-radius: 25px;"></a><br>

<img src="https://i.imgur.com/s6ksS9x.png" width="444"/>
</div>

## 🛠️ Installation

1. Clonez le dépôt 🗂️ 
```bash
git clone https://github.com/ImPavloh/rvc-tts-discord-bot
```

2. Changez pour le répertoire du projet 📁 
```bash
cd rvc-tts-discord-bot
```

3. Installez les dépendances nécessaires 📦
```bash
pip install -r requirements.txt
```

4. Téléchargez le modèle de base Hubert à partir de **[ici](https://huggingface.co/spaces/ImPavloh/RVC-TTS-Demo/resolve/main/hubert_base.pt)**. Enregistrez le fichier téléchargé dans le dossier racine du projet.

5.  Ajoutez vos RVC modèles en suivant le format suivant 📂
```Swift
└── Models
    └── NomDuModele
        └── NomDuModele
            ├── Fichier.pth
            └── Fichier.index
```

6. Configurez le fichier config.ini ⚙️

7. Exécutez le script principal 🚀
```bash
python bot.py
```

## 📝 Commandes 

Une fois que le bot a été invité sur votre serveur Discord, vous pouvez interagir avec lui en utilisant les commandes suivantes:

🗣️ Convertit le texte en voix et le joue dans le canal vocal.
```python
/tts <message>
```

🔗 Connecte ou déplace le bot vers le canal vocal où vous vous trouvez.
```python
/connect
```

🔌 Déconnecte le bot du canal vocal.
```python
/disconnect
```

🌍 Change la langue du TTS et du bot
```python
/language
```

❓ Affiche toutes les commandes du bot.
```python
/help
```

## 📄 Fichiers Importants

⚙️ `config.ini`: Fichier de configuration qui stocke des informations clés, comme la langue, le jeton du bot [Discord](https://discord.com/developers/applications) et la clé API de [ElevenLabs](https://elevenlabs.io). Modifiez les données avant de lancer le bot.

🗂️ `models/`: Dossier qui doit contenir les modèles de voix utilisés pour la conversion de texte en voix. Si tout est en ordre, le bot détectera automatiquement les modèles RVC et générera des fichiers d'information pour le programme.

📑 `requirements.txt`: Fichier contenant toutes les dépendances Python nécessaires pour que le bot fonctionne.

🤖 `bot.py`: Script Python qui décrit les fonctionnalités du bot en utilisant des commandes slash. Cela lance le bot avec la configuration et les modèles.

## ⚙️ Configuration

Pour configurer le bot, vous devez éditer le fichier ***[config.ini](https://github.com/ImPavloh/cpu-rvc-tts-discord-bot/blob/main/config.ini)*** et remplir les informations pertinentes :

- `[discord] token`: Vous devez entrer votre jeton de bot Discord ici. Vous pouvez obtenir un jeton en créant une nouvelle application sur le [portail des développeurs de Discord](https://discord.com/developers/applications).
- `[discord] type_activity` et `activity`: Ces champs sont utilisés pour définir l'état du bot.
- `[discord] language`: Configure la langue du bot et de edge_TTS.
- `[tts] type_tts`: Ce paramètre configure le type de Texte-à-Voix (TTS) à utiliser. Il peut être "edge_tts" ou "elevenlabs".
- `[edge_tts] voice`: Si vous choisissez "edge_tts" comme votre TTS, ce champ déterminera la```markdown
voix utilisée pour le TTS.
- `[elevenlabs] api_key` et `model_id`: Si vous choisissez "elevenlabs" comme votre TTS, vous devrez fournir votre clé API ElevenLabs et l'ID du modèle que vous souhaitez utiliser.


## ⚡ Optimisations

Tout est optimisé pour garantir une utilisation minimale de la RAM et du CPU. La conversion audio utilise la méthode "PM", qui est la plus rapide et nécessite seulement un CPU, sans avoir besoin d'une GPU. Cela rend possible l'exécution du bot sur pratiquement n'importe quel appareil/serveur.

## ⚠️ Avertissement

Au cas où le fichier config.ini n'est pas configuré ou les modèles RVC ne sont pas correctement placés, le bot ne fonctionnera pas.

## 📝 Licence

En utilisant ce projet, vous acceptez la ***[licence](https://github.com/ImPavloh/rvc-tts-discord-bot/blob/main/LICENSE)***.
