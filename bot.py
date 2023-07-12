import logging
import warnings

warnings.filterwarnings(action='ignore',module='.*paramiko.*')
for logger_name in ("paramiko", "xformers", "fairseq", "discord.client", "discord.gateway", "discord.voice_client", "discord.player"): logging.getLogger(logger_name).setLevel(logging.ERROR)

print("RVC TTS Discord Bot  -  @impavloh")
print("-------------------------------------")
print("Cargando configuración y modelos")

import os
import sys
import glob
import json
import wave
import queue
import torch
import config
import asyncio
import librosa
import hashlib
import discord
import tempfile
import datetime
import unicodedata
import configparser
import concurrent.futures
from vc_infer_pipeline import VC
from fairseq import checkpoint_utils
from lib.infer_pack.models import (SynthesizerTrnMs256NSFsid, SynthesizerTrnMs256NSFsid_nono, SynthesizerTrnMs768NSFsid, SynthesizerTrnMs768NSFsid_nono)

configdata = configparser.ConfigParser()
configdata.read('config.ini')

try:
    discord_token = configdata.get('discord', 'token')
    bot_activity = configdata.get('discord', 'activity')
    bot_type_activity = configdata.get('discord', 'type_activity')
    tts_voice = configdata.get('edge_tts', 'voice')
    apikey = configdata.get('elevenlabs', 'api_key')
    modelid = configdata.get('elevenlabs', 'model_id')
    tts_type = configdata.get('tts', 'type_tts')
except configparser.NoSectionError as e:
    print(f"Error al cargar la configuración: {e}")
    sys.exit(1)

if tts_type == "elevenlabs":
    import requests
else:
    import edge_tts

config = config.Config()

client = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(client)

tts_queue = queue.Queue()
is_playing_audio = False

def file_checksum(file_path):
    with open(file_path, 'rb') as f:
        file_data = f.read()
        return hashlib.md5(file_data).hexdigest()

def generate_model_info_files():
    print("Generando archivos de información del modelo")
    folder_info = {}
    model_directory = "models/"

    for category_name in os.listdir(model_directory):
        category_directory = os.path.join(model_directory, category_name)
        if os.path.isdir(category_directory):
            folder_info[category_name] = {
                "title": category_name,
                "folder_path": category_name
            }

            model_info = {}
            regenerate_model_info = False
            model_info_path = os.path.join(model_directory, category_name, 'model_info.json')
            if os.path.exists(model_info_path):
                with open(model_info_path, 'r') as f:
                    existing_model_info = json.load(f)
            else:
                existing_model_info = None
                regenerate_model_info = True

            for model_name in os.listdir(category_directory):
                model_path = os.path.join(category_directory, model_name)
                if os.path.isdir(model_path):
                    model_files = os.listdir(model_path)
                    model_files = [f for f in model_files if f.endswith('.pth') or f.endswith('.index')]
                    if len(model_files) == 2:
                        pth_file = [f for f in model_files if f.endswith('.pth')][0]
                        index_file = [f for f in model_files if f.endswith('.index')][0]
                        pth_checksum = file_checksum(os.path.join(model_path, pth_file))
                        index_checksum = file_checksum(os.path.join(model_path, index_file))
                        
                        if existing_model_info is None or model_name not in existing_model_info or \
                           existing_model_info[model_name]['model_path_checksum'] != pth_checksum or \
                           existing_model_info[model_name]['index_path_checksum'] != index_checksum:
                            regenerate_model_info = True

                        model_info[model_name] = {
                            "title": model_name,
                            "model_path": pth_file,
                            "feature_retrieval_library": index_file,
                            "model_path_checksum": pth_checksum,
                            "index_path_checksum": index_checksum
                        }

            if regenerate_model_info:
                with open(os.path.join(model_directory, category_name, 'model_info.json'), 'w') as f:
                    json.dump(model_info, f, indent=4)

    folder_info_path = os.path.join(model_directory, 'folder_info.json')
    if not os.path.exists(folder_info_path):
        with open(folder_info_path, 'w') as f:
            json.dump(folder_info, f, indent=4)

generate_model_info_files()

allowed_voices = {}
options = []

model_info_files = glob.glob('models/**/model_info.json', recursive=True)
for model_info_file in model_info_files:
    with open(model_info_file, 'r') as f:
        model_info = json.load(f)
    for model_name in model_info:
        allowed_voices[model_name] = (model_name, model_name)
        options.append(discord.SelectOption(label=model_name, emoji='📦'))

first_model_name = list(allowed_voices.keys())[0]

target_category_name = first_model_name
target_model_name = first_model_name
current_voice = first_model_name

def create_vc_fn(model_title, tgt_sr, net_g, vc, if_f0, version, file_index):
    def vc_fn(tts_text):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                tts_mp3_filename = tmpfile.name

                if tts_type == "elevenlabs":
                    url = "https://api.elevenlabs.io/v1/text-to-speech/VR6AewLTigWG4xSOukaG"
                    d = {"text": tts_text, "model_id": modelid, "voice_settings": { "stability": 0.75, "similarity_boost": 1}}
                    h = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": apikey}
                    response = requests.post(url, json=d, headers=h)
                    tmpfile.write(response.content)
                    tmpfile.seek(0)
                else:
                    asyncio.run(edge_tts.Communicate(tts_text, "-".join(tts_voice.split('-')[:-1])).save(tts_mp3_filename))

                audio, sr = librosa.load(tts_mp3_filename, sr=16000, mono=True)

            audio_opt = vc.pipeline(hubert_model, net_g, 0, audio, tts_mp3_filename, [0, 0, 0], -1, "pm", file_index, 0.7, if_f0, 3, tgt_sr, 0, 1, version, 0.5, f0_file=None)
            os.remove(tts_mp3_filename)
            if audio_opt is None:
                return None
            return (tgt_sr, audio_opt)
        except:
            return None
    return vc_fn

def load_specific_model(target_category_name, target_model_name):
    global categories
    categories = []
    categories.clear()
    with open("models/folder_info.json", "r", encoding="utf-8") as f:
        folder_info = json.load(f)
    for category_name, category_info in folder_info.items():
        if category_name != target_category_name:
            continue
        category_title = category_info['title']
        category_folder = category_info['folder_path']
        models = []
        with open(f"models/{category_folder}/model_info.json", "r", encoding="utf-8") as f:
            models_info = json.load(f)
        for character_name, info in models_info.items():
            if character_name != target_model_name:
                continue
            models = load_model_data(category_folder, character_name, info)
        categories.append([category_title, category_folder, models])
    return categories

def load_model_data(category_folder, character_name, info):
    model_title = info['title']
    model_name = info['model_path']
    model_index = f"models/{category_folder}/{character_name}/{info['feature_retrieval_library']}"
    cpt = torch.load(f"models/{category_folder}/{character_name}/{model_name}", map_location="cpu")
    tgt_sr = cpt["config"][-1]
    cpt["config"][-3] = cpt["weight"]["emb_g.weight"].shape[0]
    if_f0 = cpt.get("f0", 1)
    version = cpt.get("version", "v1")
    net_g = load_model_net_g(cpt, if_f0, version)
    del net_g.enc_q
    net_g.load_state_dict(cpt["weight"], strict=False)
    net_g.eval().to(config.device)
    if config.is_half:
        net_g = net_g.half()
    else:
        net_g = net_g.float()
    vc = VC(tgt_sr, config)
    print(f"Modelo {character_name} RVC ({version.upper()}) cargado")
    return [(character_name, model_title, version.upper(), create_vc_fn(model_title, tgt_sr, net_g, vc, if_f0, version, model_index))]

def load_model_net_g(cpt, if_f0, version):
    if version == "v1":
        if if_f0 == 1: net_g = SynthesizerTrnMs256NSFsid(*cpt["config"], is_half=config.is_half)
        else: net_g = SynthesizerTrnMs256NSFsid_nono(*cpt["config"])
    elif version == "v2":
        if if_f0 == 1: net_g = SynthesizerTrnMs768NSFsid(*cpt["config"], is_half=config.is_half)
        else: net_g = SynthesizerTrnMs768NSFsid_nono(*cpt["config"])
    return net_g

def load_hubert():
    global hubert_model
    models, _, _ = checkpoint_utils.load_model_ensemble_and_task(["hubert_base.pt"], suffix="")
    hubert_model = models[0]
    hubert_model = hubert_model.to(config.device)
    if config.is_half: hubert_model = hubert_model.half()
    else: hubert_model = hubert_model.float()
    hubert_model.eval()

def remove_special_characters(text):
    return ''.join(c for c in text if not unicodedata.category(c).startswith('So'))

async def play_audio(voice_client):
    global is_playing_audio, tts_queue
    while not tts_queue.empty():
        output_filename, audio_data, sample_rate = tts_queue.get()
        audio_source = discord.FFmpegPCMAudio(executable="ffmpeg", source=output_filename)
        audio_source = discord.PCMVolumeTransformer(audio_source, volume=0.8)

        def play_next(_):
            voice_client.stop()

        voice_client.play(audio_source, after=play_next)

        num_frames = len(audio_data) // 2
        duration = num_frames / sample_rate
        await asyncio.sleep(duration + 1)

    is_playing_audio = False

async def run_in_executor(func, *args):
    loop = asyncio.get_event_loop()
    if asyncio.iscoroutinefunction(func): return await func(*args)
    with concurrent.futures.ThreadPoolExecutor() as executor: result = await loop.run_in_executor(executor, func, *args)
    return result

async def get_vc_fn_result(vc_fn, text):
    return await run_in_executor(vc_fn, text)

load_hubert()
categories = load_specific_model(target_category_name, target_model_name)
print("Iniciando bot")

@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot en línea como \"{client.user.name}\"") 
    activity = discord.Game(name=bot_activity, type=bot_type_activity)
    await client.change_presence(status=discord.Status.online, activity=activity)

@tree.command(name="conectar", description="Conecta el bot al canal de voz en el que te encuentres")
async def conectar(interaction: discord.Interaction):
    if interaction.user.voice is not None:
        voice_channel = interaction.user.voice.channel
        if interaction.guild.voice_client is not None:
            if interaction.guild.voice_client.channel != voice_channel:
                await interaction.guild.voice_client.disconnect()
                await voice_channel.connect()
                await interaction.response.send_message(embed=discord.Embed(title=f'Me he movido al canal de voz {voice_channel.mention}', color=0XBABBE1), ephemeral=True)
            else:
                await interaction.response.send_message(embed=discord.Embed(title=f'Ya estoy conectado al canal de voz {voice_channel.mention}', color=0XBABBE1), ephemeral=True)
        else:
            await voice_channel.connect()
            await interaction.response.send_message(embed=discord.Embed(title=f'Me he conectado al canal de voz {voice_channel.mention}', color=0XBABBE1), ephemeral=True)
    else: await interaction.response.send_message(embed=discord.Embed(title=f'No estás en un canal de voz, únete a uno para que pueda conectarme.', color=0XBABBE1), ephemeral=True)

@tree.command(name="desconectar", description="Desconecta el bot del canal donde se encuentre")
async def salir(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if not voice_client:
        await interaction.response.send_message(embed=discord.Embed(title=f'No estoy conectado a un canal de voz', color=0XBABBE1), ephemeral=True)
        return
    await voice_client.disconnect()
    await interaction.response.send_message(embed=discord.Embed(title=f'Me he desconectado del canal de voz', color=0XBABBE1), ephemeral=True)

@tree.command(name="ayuda", description="Muestra una lista con todos los comandos del bot")
async def ayuda(interaction: discord.Interaction): 
    embed = discord.Embed(title="🎤 TTS + IA 🔊", color=0XBABBE1, timestamp=datetime.datetime.now())

    embed.add_field(name=":loud_sound: Comando TTS",
                    value="`/tts <mensaje>`: Convierte texto a voz y reprodúcelo en el canal de voz",
                    inline=False)

    embed.add_field(name=":speaker: Comandos del canal de voz",
                    value="`/conectar`: Conecta/mueve el bot al canal\n"
                          "`/desconectar`: Desconecta el bot del canal",
                    inline=False)

    embed.add_field(name=":microphone2: Cambiar voz",
                    value="`/voz`: Cambia la voz del TTS a la voz especificada.",
                    inline=False)

    embed.add_field(name=":question: Comandos extra",
                    value="`/ayuda`: Muestra este mensaje de ayuda",
                    inline=False)

    embed.set_footer(text="RVC TTS Discord Bot  -  @impavloh")
    await interaction.response.send_message(embed=embed)

class CommandDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())

class Dropdown(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder='Elige un modelo de voz', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        global target_category_name, target_model_name, current_voice

        selected_voice = self.values[0]

        if selected_voice in allowed_voices:
            target_category_name, target_model_name = allowed_voices[selected_voice]
            load_specific_model(target_category_name, target_model_name)
            current_voice = selected_voice
            print(f'Modelo de voz cambiado a {current_voice}')
            embed = discord.Embed(title=f'La voz se ha cambiado a {selected_voice}', color=0XBABBE1)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title=f'La voz no es válida', color=0XBABBE1)
            await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="voz", description="Cambia el modelo de voz final del TTS")
async def voz(interaction: discord.Interaction): 
    global current_voice

    if current_voice is None:
        embed = discord.Embed(title=f'No se ha seleccionado ninguna voz', color=0XBABBE1)
    else:
        embed = discord.Embed(title=f'La voz actual es {current_voice}', color=0XBABBE1)

    await interaction.response.send_message(embed=embed, view=CommandDropdownView(), ephemeral=True)

async def send_embed_with_buttons(interaction: discord.Interaction, title: str):
    embed = discord.Embed(title=title, color=0XBABBE1)
    view = BotonesTTS()
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

class BotonesTTS(discord.ui.View):
    @discord.ui.button(label="⏸️", style=discord.ButtonStyle.gray)
    async def pausar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        interaction.guild.voice_client.pause()
        await send_embed_with_buttons(interaction, title='TTS pausado')

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.green)
    async def reanudar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        interaction.guild.voice_client.resume()
        await send_embed_with_buttons(interaction, title='TTS reanudado')

    @discord.ui.button(label="⏹️", style=discord.ButtonStyle.red)
    async def detener(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        interaction.guild.voice_client.stop()
        await send_embed_with_buttons(interaction, title='TTS detenido')

@tree.command(name="tts", description="Escribe el mensaje que quieres decir por voz")
async def tts(interaction, mensaje: str):
    global is_playing_audio, tts_queue
    if not interaction.user.voice:
        await interaction.response.send_message(embed=discord.Embed(title=f'Necesitas estar en un canal de voz para usar este comando', color=0XBABBE1), ephemeral=True)
        return

    sanitized_text = remove_special_characters(mensaje)
    await interaction.response.send_message(embed=discord.Embed(title=f'Generando TTS', color=0XBABBE1, timestamp=datetime.datetime.now()).set_footer(text="Puede demorarse unos segundos."), ephemeral=True)

    voice_client = None
    for vc in client.voice_clients:
        if vc.guild == interaction.guild:
            voice_client = vc
            break

    if voice_client is None:
        voice_client = await interaction.user.voice.channel.connect()

    try:
        for (folder_title, folder, models) in categories:
            print(f'Procesando TTS con la voz de {folder_title}')
            for character_name, model_title, model_version, vc_fn in models:
                sample_rate, audio_data = await get_vc_fn_result(vc_fn, sanitized_text)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                    output_filename = tmpfile.name
                with wave.open(output_filename, "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_data)
                    wav_file.close()

                tts_queue.put((output_filename, audio_data, sample_rate))

                if not is_playing_audio:
                    is_playing_audio = True
                    await interaction.followup.send(embed=discord.Embed(title="Reproduciendo TTS", color=0XBABBE1), view=BotonesTTS(), ephemeral=True)
                    await play_audio(voice_client)
                    await interaction.followup.send(embed=discord.Embed(title=f'TTS reproducido', color=0XBABBE1, timestamp=datetime.datetime.now()), ephemeral=True)
                    print(f"TTS procesado y reproducido correctamente")
                else:
                    queue_position = tts_queue.qsize() - 1
                    await interaction.followup.send(embed=discord.Embed(title=f'TTS agregado a la cola', color=0XBABBE1, timestamp=datetime.datetime.now()).set_footer(text=f'Tu solicitud de TTS está en la posición {queue_position} de la cola.'), ephemeral=True)
                    print(f'TTS agregado a la cola en la posición {queue_position}')

    except Exception as e:
        print(f"Ocurrió un error: {str(e)}")
        await interaction.followup.send(embed=discord.Embed(title=f'Ocurrió un error al generar el TTS', color=0X990033), ephemeral=True)
        await voice_client.disconnect()

client.run(discord_token)
