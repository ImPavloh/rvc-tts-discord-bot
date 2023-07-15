import os
import sys
import json
import logging
import warnings
import configparser

warnings.filterwarnings(action='ignore',module='.*paramiko.*')

configdata = configparser.ConfigParser()
configdata.read('config.ini')

try:
    discord_token = configdata.get('discord', 'token')
    bot_activity = configdata.get('discord', 'activity')
    bot_type_activity = configdata.get('discord', 'type_activity')
    current_language = configdata.get('discord', 'language')
    tts_voice = configdata.get('edge_tts', 'voice')
    apikey = configdata.get('elevenlabs', 'api_key')
    modelid = configdata.get('elevenlabs', 'model_id')
    tts_type = configdata.get('tts', 'type_tts')
except configparser.NoSectionError:
    print(language_data["error_config"])
    sys.exit(1)
    
def load_language_data():
    global language_data
    with open(os.path.join(os.path.dirname(__file__), "locales", f"{current_language}.json"), "r", encoding="utf-8") as lang_file: language_data = json.load(lang_file)
load_language_data()

for logger_name in ("paramiko", "xformers", "fairseq", "discord.client", "discord.gateway", "discord.voice_client", "discord.player"):logging.getLogger(logger_name).setLevel(logging.ERROR)

print("RVC TTS Discord Bot  -  @impavloh")
print("-------------------------------------")
print(language_data["loading"])

import glob
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
import concurrent.futures
from vc_infer_pipeline import VC
from fairseq import checkpoint_utils
from lib.infer_pack.models import (SynthesizerTrnMs256NSFsid, SynthesizerTrnMs256NSFsid_nono, SynthesizerTrnMs768NSFsid, SynthesizerTrnMs768NSFsid_nono)
if tts_type == "elevenlabs": import requests
else: import edge_tts

config = config.Config()

client = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(client)

tts_queue = queue.Queue()
is_playing_audio = False

def file_checksum(file_path):
    with open(file_path, 'rb') as f:
        file_data = f.read()
        return hashlib.md5(file_data).hexdigest()

def get_existing_model_info(category_directory):
    model_info_path = os.path.join(category_directory, 'model_info.json')
    if os.path.exists(model_info_path):
        with open(model_info_path, 'r') as f: return json.load(f)
    return None

def get_model_files(model_path): return [f for f in os.listdir(model_path) if f.endswith('.pth') or f.endswith('.index')]

def should_regenerate_model_info(existing_model_info, model_name, pth_checksum, index_checksum):
    if existing_model_info is None or model_name not in existing_model_info: return True
    return (existing_model_info[model_name]['model_path_checksum'] != pth_checksum or existing_model_info[model_name]['index_path_checksum'] != index_checksum)

def gather_model_info(category_directory, model_name, model_path, existing_model_info):
    model_files = get_model_files(model_path)
    if len(model_files) != 2: return None, False

    pth_file = [f for f in model_files if f.endswith('.pth')][0]
    index_file = [f for f in model_files if f.endswith('.index')][0]
    pth_checksum = file_checksum(os.path.join(model_path, pth_file))
    index_checksum = file_checksum(os.path.join(model_path, index_file))
    regenerate = should_regenerate_model_info(existing_model_info, model_name, pth_checksum, index_checksum)

    return {"title": model_name, "model_path": pth_file, "feature_retrieval_library": index_file, "model_path_checksum": pth_checksum, "index_path_checksum": index_checksum}, regenerate

def generate_model_info_files():
    print(language_data["model_info_generation"])
    folder_info = {}
    model_directory = "models/"
    for category_name in os.listdir(model_directory):
        category_directory = os.path.join(model_directory, category_name)
        if not os.path.isdir(category_directory): continue

        folder_info[category_name] = {"title": category_name, "folder_path": category_name}
        existing_model_info = get_existing_model_info(category_directory)
        model_info = {}
        regenerate_model_info = False

        for model_name in os.listdir(category_directory):
            model_path = os.path.join(category_directory, model_name)
            if not os.path.isdir(model_path): continue

            model_data, regenerate = gather_model_info(category_directory, model_name, model_path, existing_model_info)
            if model_data is not None:
                model_info[model_name] = model_data
                regenerate_model_info |= regenerate

        if regenerate_model_info:
            with open(os.path.join(category_directory, 'model_info.json'), 'w') as f: json.dump(model_info, f, indent=4)

    folder_info_path = os.path.join(model_directory, 'folder_info.json')
    with open(folder_info_path, 'w') as f: json.dump(folder_info, f, indent=4)

generate_model_info_files()

allowed_voices = {}
options = []

model_info_files = glob.glob('models/**/model_info.json', recursive=True)
for model_info_file in model_info_files:
    with open(model_info_file, 'r') as f: model_info = json.load(f)
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
                else: asyncio.run(edge_tts.Communicate(tts_text, "-".join(tts_voice.split('-')[:-1])).save(tts_mp3_filename))
                audio, sr = librosa.load(tts_mp3_filename, sr=16000, mono=True)
            audio_opt = vc.pipeline(hubert_model, net_g, 0, audio, tts_mp3_filename, [0, 0, 0], -1, "pm", file_index, 0.7, if_f0, 3, tgt_sr, 0, 1, version, 0.5, f0_file=None)
            os.remove(tts_mp3_filename)
            return None if audio_opt is None else (tgt_sr, audio_opt)
        except Exception: return None
    return vc_fn

def load_specific_model(target_category_name, target_model_name):
    global categories
    categories = []
    categories.clear()
    with open("models/folder_info.json", "r", encoding="utf-8") as f: folder_info = json.load(f)
    for category_name, category_info in folder_info.items():
        if category_name != target_category_name: continue
        category_title = category_info['title']
        category_folder = category_info['folder_path']
        models = []
        with open(f"models/{category_folder}/model_info.json", "r", encoding="utf-8") as f: models_info = json.load(f)
        for character_name, info in models_info.items():
            if character_name != target_model_name: continue
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
    net_g = net_g.half() if config.is_half else net_g.float()
    vc = VC(tgt_sr, config)
    print(language_data["model_loaded"].format(character_name=character_name, version=version))
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
    hubert_model = hubert_model.half() if config.is_half else hubert_model.float()
    hubert_model.eval()

def remove_special_characters(text): return ''.join(c for c in text if not unicodedata.category(c).startswith('So'))

async def play_audio(voice_client):
    global is_playing_audio, tts_queue
    audio_started = asyncio.Future()

    def after_play(_):
        voice_client.stop()
        audio_started.set_result(None)

    while not tts_queue.empty():
        output_filename, audio_data, sample_rate = tts_queue.get()
        audio_source = discord.FFmpegPCMAudio(executable="ffmpeg", source=output_filename)
        audio_source = discord.PCMVolumeTransformer(audio_source, volume=0.7)
        voice_client.play(audio_source, after=after_play)
        num_frames = len(audio_data) // 2
        duration = num_frames / sample_rate
        await asyncio.sleep(duration + 1)

    is_playing_audio = False
    return audio_started

async def run_in_executor(func, *args):
    loop = asyncio.get_event_loop()
    if asyncio.iscoroutinefunction(func): return await func(*args)
    with concurrent.futures.ThreadPoolExecutor() as executor: result = await loop.run_in_executor(executor, func, *args)
    return result

async def get_vc_fn_result(vc_fn, text): return await run_in_executor(vc_fn, text)

load_hubert()
categories = load_specific_model(target_category_name, target_model_name)
models = categories[0][2]
print(language_data["bot_started"])

@client.event
async def on_ready():
    await tree.sync()
    print(language_data["bot_online"].format(client_user_name=client.user.name))
    activity = discord.Game(name=bot_activity, type=bot_type_activity)
    await client.change_presence(status=discord.Status.online, activity=activity)

@tree.command(name="join", description=language_data["command_connect_description"])
async def conectar(interaction: discord.Interaction):
    if interaction.user.voice is not None:
        voice_channel = interaction.user.voice.channel
        if interaction.guild.voice_client is None:
            await voice_channel.connect()
            await interaction.response.send_message(embed=discord.Embed(title=language_data["bot_connected_to_voice_channel"].format(voice_channel=voice_channel), color=0XBABBE1), ephemeral=True)
        elif interaction.guild.voice_client.channel != voice_channel:
            await interaction.guild.voice_client.disconnect()
            await voice_channel.connect()
            await interaction.response.send_message(embed=discord.Embed(title=language_data["bot_moved_to_voice_channel"].format(voice_channel=voice_channel), color=0XBABBE1), ephemeral=True)
        else: await interaction.response.send_message(embed=discord.Embed(title=language_data["bot_already_in_voice_channel"].format(voice_channel=voice_channel), color=0XBABBE1), ephemeral=True)
    else: await interaction.response.send_message(embed=discord.Embed(title=language_data["user_not_in_voice_channel"], color=0xBABBE1), ephemeral=True)

@tree.command(name="leave", description=language_data["command_disconnect_description"])
async def salir(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if not voice_client:
        await interaction.response.send_message(embed=discord.Embed(title=language_data['bot_not_in_voice_channel'], color=0XBABBE1), ephemeral=True)
        return
    await voice_client.disconnect()
    await interaction.response.send_message(embed=discord.Embed(title=language_data['bot_disconnected_from_voice_channel'], color=0XBABBE1), ephemeral=True)

@tree.command(name="help", description=language_data["help_command_description"])
async def ayuda(interaction: discord.Interaction):
    embed = discord.Embed(title=f"🎤  {language_data['dialog_title']} 🔊 ", color=0XBABBE1, timestamp=datetime.datetime.now())
    embed.add_field(name=f":loud_sound: {language_data['dialog_tts_command']}", value=f"`/tts <message>`: {language_data['tts_command_description']}", inline=False)
    embed.add_field(name=f":speaker: {language_data['dialog_voice_command']}", value=f"`/join`: {language_data['command_connect_description']}\n" f"`/leave`: {language_data['command_disconnect_description']}", inline=False)
    embed.add_field(name=f":microphone2: {language_data['dialog_change_voice']}", value=f"`/voice`: {language_data['voice_command_description']}", inline=False)
    embed.add_field(name=f":question: {language_data['dialog_extra_commands']}", value=f"`/help`: {language_data['help_command_description']}", inline=False)
    embed.set_footer(text="RVC TTS Discord Bot • @impavloh ")
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label='Twitter', style=discord.ButtonStyle.blurple, url='https://twitter.com/impavloh'))
    view.add_item(discord.ui.Button(label='GitHub', style=discord.ButtonStyle.link, url='https://github.com/ImPavloh/rvc-tts-discord-bot'))
    await interaction.response.send_message(embed=embed, view=view)

class LanguageDropdown(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label="English", emoji='🇺🇸', value="en"), discord.SelectOption(label="Español", emoji='🇪🇸', value="es"), discord.SelectOption(label="Français", emoji='🇫🇷', value="fr"), discord.SelectOption(label="Deutsch", emoji='🇩🇪', value="ge"), discord.SelectOption(label="Português", emoji='🇵🇹', value="pt")]
        super().__init__(placeholder=language_data["language_select"], min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        global current_language
        global tts_voice

        current_language = interaction.data['values'][0]
        load_language_data()
        if current_language == "es": tts_voice = "es-ES-AlvaroNeural-Male"
        elif current_language == "pt": tts_voice = "pt-PT-DuarteNeural-Male"
        elif current_language == "de": tts_voice = "de-AT-JonasNeural-Male"
        elif current_language == "fr": tts_voice = "fr-FR-HenriNeural-Male"
        elif current_language == "en": tts_voice = "en-US-GuyNeural-Male"
        await interaction.response.send_message(embed=discord.Embed(title=language_data["language_changed"].format(new_language=current_language), color=0XBABBE1), ephemeral=True)

@tree.command(name="language", description=language_data["change_language_command_description"])
async def language(interaction: discord.Interaction):
    view = discord.ui.View()
    view.add_item(LanguageDropdown())
    await interaction.response.send_message(view=view, ephemeral=True)

class CommandDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())

class Dropdown(discord.ui.Select):
    def __init__(self): super().__init__(placeholder=language_data['choose_voice'], min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        global target_category_name, target_model_name, current_voice

        selected_voice = self.values[0]

        if selected_voice in allowed_voices:
            target_category_name, target_model_name = allowed_voices[selected_voice]
            load_specific_model(target_category_name, target_model_name)
            current_voice = selected_voice
            print(language_data["model_changed"].format(current_voice=current_voice))
            embed = discord.Embed(title=language_data['voice_changed'].format(selected_voice=selected_voice) , color=0XBABBE1)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title=language_data['voice_not_valid'] , color=0XBABBE1)
            await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="voice", description=language_data["voice_command_description"])
async def voz(interaction: discord.Interaction): 
    global current_voice
    if current_voice is None: await interaction.response.send_message(embed=discord.Embed(title=language_data["voice_not"], color=0XBABBE1), view=CommandDropdownView(), ephemeral=True)
    else: await interaction.response.send_message(embed=discord.Embed(title=language_data["current_voice"].format(current_voice=current_voice), color=0XBABBE1), view=CommandDropdownView(), ephemeral=True)

class BotonesTTS2(discord.ui.View):
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.green)
    async def reanudar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        interaction.guild.voice_client.resume()
        await interaction.edit_original_response(view=BotonesTTS(), embed=discord.Embed(title=language_data["tts_playing"], color=0X07ce1b, timestamp=datetime.datetime.now()).set_footer(text=language_data["tts_continue"]))
    @discord.ui.button(label="⏹️", style=discord.ButtonStyle.red)
    async def detener(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        interaction.guild.voice_client.stop()
        await interaction.edit_original_response(view=None, embed=discord.Embed(title=language_data["tts_playing"], color=0Xce0743, timestamp=datetime.datetime.now()).set_footer(text=language_data["tts_stop"]))
class BotonesTTS(discord.ui.View):
    @discord.ui.button(label="⏸️", style=discord.ButtonStyle.green)
    async def pausar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        interaction.guild.voice_client.pause()
        await interaction.edit_original_response(view=BotonesTTS2(), embed=discord.Embed(title=language_data["tts_playing"], color=0Xce6307, timestamp=datetime.datetime.now()).set_footer(text=language_data["tts_pause"]))
    @discord.ui.button(label="⏹️", style=discord.ButtonStyle.red)
    async def detener(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        interaction.guild.voice_client.stop()
        await interaction.edit_original_response(view=None, embed=discord.Embed(title=language_data["tts_playing"], color=0Xce0743, timestamp=datetime.datetime.now()).set_footer(text=language_data["tts_stop"]))

@tree.command(name="tts", description=language_data["tts_command_description"])
async def tts(interaction, mensaje: str):
    global is_playing_audio, tts_queue
    if not interaction.user.voice:
        await interaction.response.send_message(embed=discord.Embed(title=language_data["not_in_voice_channel"], color=0XBABBE1), ephemeral=True)
        return

    sanitized_text = remove_special_characters(mensaje)
    await interaction.response.send_message(embed=discord.Embed(title=language_data["tts_generating"], color=0XBABBE1, timestamp=datetime.datetime.now()).set_footer(text=language_data["tts_generating2"]), ephemeral=True)
    voice_client = next((vc for vc in client.voice_clients if vc.guild == interaction.guild), None)
    if voice_client is None: voice_client = await interaction.user.voice.channel.connect()

    try:
        for (folder_title, folder, models) in categories:
            print(language_data["tts_process"].format(folder_title=folder_title))
            for character_name, model_title, model_version, vc_fn in models:
                sample_rate, audio_data = await get_vc_fn_result(vc_fn, sanitized_text)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile: output_filename = tmpfile.name
                with wave.open(output_filename, "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_data)
                    wav_file.close()

                tts_queue.put((output_filename, audio_data, sample_rate))

                if not is_playing_audio:
                    is_playing_audio = True
                    await interaction.edit_original_response(embed=discord.Embed(title=language_data["tts_playing"], color=0XBABBE1), view=BotonesTTS())
                    audio_started = await play_audio(voice_client)
                    await audio_started
                    if not voice_client.is_playing() and not voice_client.is_paused():
                        await interaction.edit_original_response(view=None, embed=discord.Embed(title=language_data["tts_played"], color=0XBABBE1, timestamp=datetime.datetime.now()))
                        print(language_data["tts_success"])
                else:
                    queue_position = tts_queue.qsize() - 1
                    await interaction.edit_original_response(view=None, embed=discord.Embed(title=language_data["tts_added_to_queue"], color=0XBABBE1, timestamp=datetime.datetime.now()).set_footer(text=language_data["tts_added_to_queue2"].format(queue_position=queue_position)))
                    print(language_data["tts_queue_added"].format(queue_position=queue_position))

    except Exception:
        print(language_data["tts_error_print"])
        await interaction.edit_original_response(view=None, embed=discord.Embed(title=language_data["tts_error"], color=0X990033))
        await voice_client.disconnect()

client.run(discord_token)
