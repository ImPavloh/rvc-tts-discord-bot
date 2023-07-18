<div align="center">
  
![Logo](https://support.discord.com/hc/article_attachments/115002567312/Robot.gif)
  
<a href="https://github.com/ImPavloh/rvc-tts-discord-bot" target="_blank"><img src="https://img.shields.io/github/license/impavloh/rvc-tts-discord-bot?style=for-the-badge&logo=github&logoColor=white"></a>
<a href="https://twitter.com/ImPavloh" target="_blank"><img src="https://img.shields.io/badge/Pavloh-%231DA1F2.svg?style=for-the-badge&logo=twitter&logoColor=white"></a>

<h1>🎙️ RVC TTS: Bot de Discord de Texto para Voz com IA 🤖💬</h1>
<h3>Fácil de usar | Suporte multilíngue | Fácil de configurar</h3>
<a href="README.md"><img alt="English" src="https://unpkg.com/language-icons/icons/en.svg" width="50px" style="border-top-left-radius: 25px; border-bottom-left-radius: 25px;"></a>
<a href="README_es.md"><img alt="Spanish" src="https://unpkg.com/language-icons/icons/es.svg" width="50px"></a>
<a href="README_pt.md"><img alt="Portuguese" src="https://unpkg.com/language-icons/icons/pt.svg" width="50px"></a>
<a href="README_de.md"><img alt="German" src="https://unpkg.com/language-icons/icons/de.svg" width="50px"></a>
<a href="README_fr.md"><img alt="French" src="https://unpkg.com/language-icons/icons/fr.svg" width="50px" style="border-top-right-radius: 25px; border-bottom-right-radius: 25px;"></a>
</div>

## 🛠️ Instalação

1. Clone o repositório 🗂️ 
```bash
git clone https://github.com/ImPavloh/rvc-tts-discord-bot
```

2. Altere para o diretório do projeto 📁 
```bash
cd rvc-tts-discord-bot
```

3. Instale as dependências necessárias 📦
```bash
pip install -r requirements.txt
```

4. Baixe o modelo base do Hubert a partir daqui [aqui](https://huggingface.co/spaces/ImPavloh/RVC-TTS-Demo/resolve/main/hubert_base.pt). Salve o arquivo baixado na pasta raiz do projeto.
    
5. Adicione seus RVC modelos no seguinte formato 📂
```Swift
└── Models
    └── NomeModelo
        └── NomeModelo
            ├── Arquivo.pth
            └── Arquivo.index
```

6. Configure o arquivo config.ini ⚙️

7. Execute o script principal 🚀
```bash
python bot.py
```

## 📝 Comandos 

Depois que o bot for convidado para o seu servidor Discord, você poderá interagir com ele usando os seguintes comandos:

🗣️ Converte texto em voz e o reproduz no canal de voz.
```python
/tts <message>
```

🔗 Conecta ou move o bot para o canal de voz em que você está.
```python
/connect
```

🔌 Desconecta o bot do canal de voz.
```python
/disconnect
```

🌍 Muda a língua do TTS e do bot
```python
/language
```

❓ Mostra todos os comandos do bot.
```python
/help
```

## 📄 Arquivos Importantes

⚙️ `config.ini`: Arquivo de configuração que armazena informações chave, como o idioma, o token do [bot do Discord](https://discord.com/developers/applications) e a chave API do [ElevenLabs](https://elevenlabs.io). Altere os dados antes de executar o bot.

🗂️ `models/`: Pasta que deve conter os modelos de voz a serem utilizados para a conversão de texto em voz. Se tudo estiver correto, o bot detectará automaticamente os modelos e gerará arquivos de informação para o programa.

📑 `requirements.txt`: Arquivo que contém todas as dependências Python necessárias para o bot funcionar.

🤖 `bot.py`: Script Python que descreve a funcionalidade do bot usando comandos slash. Isso iniciará o bot com a configuração e os modelos.

## ⚙️ Configuração

Para configurar o bot, você precisa editar o arquivo ***[config.ini](https://github.com/ImPavloh/cpu-rvc-tts-discord-bot/blob/main/config.ini)*** e preencher as informações relevantes:

- `[discord] token`: Você deve colocar aqui o seu token de bot Discord. Você pode obter um token criando um novo aplicativo no [portal de desenvolvedores do Discord](https://discord.com/developers/applications).
- `[discord] type_activity` e `activity`: Esses campos são usados para definir o status do bot.
- `[discord] language`: Configura o idioma do bot e do edge_TTS.
- `[tts] type_tts`: Este parâmetro configura o tipo de Texto-para-Voz (TTS) a ser usado. Pode ser "edge_tts" ou "elevenlabs".
- `[edge_tts] voice`: Se você escolher "edge_tts" como seu TTS, este campo determinará a voz usada para o TTS.
- `[elevenlabs] api_key` e `model_id`: Se você escolher "elevenlabs" como seu TTS, você precisará fornecer sua chave API ElevenLabs e o ID do modelo que você quer usar.

## ⚡ Otimizações

Tudo está otimizado para garantir um uso mínimo de RAM e```markdown
CPU. A conversão de áudio usa o método "PM", que é o mais rápido e só requer uma CPU, sem a necessidade de uma GPU. Isso torna possível rodar o bot em praticamente qualquer dispositivo/servidor.

## ⚠️ Aviso

Caso o arquivo `config.ini` não esteja configurado ou os modelos RVC não estejam corretamente colocados, o bot não funcionará.

## 📝 Licença

Ao usar este projeto, você concorda com a ***[licença](https://github.com/ImPavloh/rvc-tts-discord-bot/blob/main/LICENSE)***.
