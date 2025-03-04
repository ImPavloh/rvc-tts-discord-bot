from scipy import signal
from functools import lru_cache
import torch.nn.functional as F
import numpy as np, parselmouth, torch
import librosa, os, traceback, faiss, librosa

bh, ah = signal.butter(N=5, Wn=48, btype="high", fs=16000)

@lru_cache
def cache_harvest_f0(input_audio_path, fs, f0max, f0min, frame_period, input_audio_path2wav):
    audio = input_audio_path2wav[input_audio_path]
    f0, voiced_flag, voiced_probs = librosa.pyin(audio, fmin=f0min, fmax=f0max, sr=fs, frame_length=int(fs*frame_period/1000), hop_length=int(fs*frame_period/1000))
    f0 = np.where(voiced_flag, f0, 0)
    return f0

def change_rms(data1, sr1, data2, sr2, rate):
    rms1 = librosa.feature.rms(y=data1, frame_length=sr1 // 2 * 2, hop_length=sr1 // 2)
    rms2 = librosa.feature.rms(y=data2, frame_length=sr2 // 2 * 2, hop_length=sr2 // 2)
    rms1 = torch.from_numpy(rms1).unsqueeze(0)
    rms2 = torch.from_numpy(rms2).unsqueeze(0)
    rms1 = F.interpolate(rms1, size=data2.shape[0], mode="linear").squeeze()
    rms2 = F.interpolate(rms2, size=data2.shape[0], mode="linear").squeeze()
    rms2 = torch.max(rms2, torch.zeros_like(rms2) + 1e-6)
    data2 *= (torch.pow(rms1, 1 - rate) * torch.pow(rms2, rate - 1)).numpy()
    
    return data2

class VC:
    def __init__(self, tgt_sr, config):
        self.x_pad = config.x_pad
        self.x_query = config.x_query
        self.x_center = config.x_center
        self.x_max = config.x_max
        self.is_half = config.is_half
        self.sr = 16000
        self.window = 160
        self.t_pad = self.sr * self.x_pad
        self.t_pad_tgt = tgt_sr * self.x_pad
        self.t_pad2 = self.t_pad * 2
        self.t_query = self.sr * self.x_query
        self.t_center = self.sr * self.x_center
        self.t_max = self.sr * self.x_max
        self.device = config.device

    def get_f0(self, input_audio_path, x, p_len, f0_up_key, f0_method, filter_radius, inp_f0=None):
        global input_audio_path2wav
        time_step = self.window / self.sr * 1000
        f0_min = 50
        f0_max = 1100
        f0_mel_min = 1127 * np.log(1 + f0_min / 700)
        f0_mel_max = 1127 * np.log(1 + f0_max / 700)

        if f0_method == "pm":
            f0 = (parselmouth.Sound(x, self.sr).to_pitch_ac(time_step=time_step / 1000, voicing_threshold=0.6, pitch_floor=f0_min, pitch_ceiling=f0_max).selected_array["frequency"])
            pad_size = (p_len - len(f0) + 1) // 2
            if pad_size > 0 or p_len - len(f0) - pad_size > 0: f0 = np.pad(f0, [[pad_size, p_len - len(f0) - pad_size]], mode="constant")
        f0 *= pow(2, f0_up_key / 12)
        tf0 = self.sr // self.window

        if inp_f0 is not None:
            delta_t = np.round((inp_f0[:, 0].max() - inp_f0[:, 0].min()) * tf0 + 1).astype("int16")
            replace_f0 = np.interp(list(range(delta_t)), inp_f0[:, 0] * 100, inp_f0[:, 1])
            shape = f0[self.x_pad * tf0: self.x_pad * tf0 + len(replace_f0)].shape[0]
            f0[self.x_pad * tf0: self.x_pad * tf0 + len(replace_f0)] = replace_f0[:shape]

        f0bak= f0.copy()
        f0_mel = 1127 * np.log(1 + f0 / 700)
        f0_mel[f0_mel > 0] = (f0_mel[f0_mel > 0] - f0_mel_min) * 254 / (f0_mel_max - f0_mel_min) + 1
        f0_mel[f0_mel <= 1] = 1
        f0_mel[f0_mel > 255] = 255
        f0_coarse = np.rint(f0_mel).astype(np.int)
        return f0_coarse, f0bak

    def vc(self, model, net_g, sid, audio0, pitch, pitchf, times, index, big_npy, index_rate, version, protect):
        feats = torch.from_numpy(audio0)
        feats = feats.half() if self.is_half else feats.float()
        
        if feats.dim() == 2: feats = feats.mean(-1)
        assert feats.dim() == 1, feats.dim()
        feats = feats.view(1, -1)
        padding_mask = torch.BoolTensor(feats.shape).to(self.device).fill_(False)

        inputs = { "source": feats.to(self.device), "padding_mask": padding_mask, "output_layer": 9 if version == "v1" else 12}

        with torch.no_grad():
            logits = model.extract_features(**inputs)
            feats = model.final_proj(logits[0]) if version == "v1" else logits[0]
        
        if protect < 0.5 and pitch is not None and pitchf is not None:
            feats0 = feats.clone()
        
        if index is not None and big_npy is not None and index_rate != 0:
            npy = feats[0].cpu().numpy()
            if self.is_half: npy = npy.astype("float64")

            score, ix = index.search(npy, k=8)
            weight = np.square(1 / score)
            weight /= weight.sum(axis=1, keepdims=True)
            npy = np.sum(big_npy[ix] * np.expand_dims(weight, axis=2), axis=1)

            if self.is_half: npy = npy.astype("float16")
            feats = ( torch.from_numpy(npy).unsqueeze(0).to(self.device) * index_rate + (1 - index_rate) * feats)

        feats = F.interpolate(feats.permute(0, 2, 1), scale_factor=2).permute(0, 2, 1)
        if protect < 0.5 and pitch is not None and pitchf is not None: feats0 = F.interpolate(feats0.permute(0, 2, 1), scale_factor=2).permute(0, 2, 1)

        p_len = audio0.shape[0] // self.window
        if feats.shape[1] < p_len:
            p_len = feats.shape[1]
            if pitch is not None and pitchf is not None:
                pitch = pitch[:, :p_len]
                pitchf = pitchf[:, :p_len]

        if protect < 0.5 and pitch is not None and pitchf is not None:
            pitchff = pitchf.clone()
            pitchff[pitchf > 0] = 1
            pitchff[pitchf < 1] = protect
            pitchff = pitchff.unsqueeze(-1)
            feats = feats * pitchff + feats0 * (1 - pitchff)
            feats = feats.to(feats0.dtype)
        p_len = torch.tensor([p_len], device=self.device).long()
        
        with torch.no_grad():
            if pitch is not None and pitchf is not None: audio1 = ((net_g.infer(feats, p_len, pitch, pitchf, sid)[0][0, 0]).data.cpu().float().numpy())
            else: audio1 = ((net_g.infer(feats, p_len, sid)[0][0, 0]).data.cpu().float().numpy())
        
        del feats, p_len, padding_mask
        return audio1

    def pipeline(self,model, net_g, sid, audio, input_audio_path, times, f0_up_key, f0_method, file_index, index_rate, if_f0, filter_radius, tgt_sr, resample_sr, rms_mix_rate, version, protect, f0_file=None):
        if (file_index != "" and os.path.exists(file_index) == True and index_rate != 0):
            try:
                index = faiss.read_index(file_index)
                big_npy = index.reconstruct_n(0, index.ntotal)
            except:
                traceback.print_exc()
                index = big_npy = None
        else: index = big_npy = None
        audio = signal.filtfilt(bh, ah, audio)
        audio_pad = np.pad(audio, (self.window // 2, self.window // 2), mode="reflect")
        opt_ts = []
        if audio_pad.shape[0] > self.t_max:
            audio_sum = np.zeros_like(audio)
            for i in range(self.window): audio_sum += audio_pad[i : i - self.window]
            for t in range(self.t_center, audio.shape[0], self.t_center): opt_ts.append(t - self.t_query + np.where(np.abs(audio_sum[t - self.t_query : t + self.t_query]) == np.abs(audio_sum[t - self.t_query : t + self.t_query]).min())[0][0])
        s = 0
        audio_opt = []
        t = None
        audio_pad = np.pad(audio, (self.t_pad, self.t_pad), mode="reflect")
        p_len = audio_pad.shape[0] // self.window
        inp_f0 = None
        if hasattr(f0_file, "name") == True:
            try:
                with open(f0_file.name, "r") as f: lines = f.read().strip("\n").split("\n")
                inp_f0 = [[float(i) for i in line.split(",")] for line in lines]
                inp_f0 = np.array(inp_f0, dtype="float64")
            except Exception: traceback.print_exc()
        sid = torch.tensor(sid, device=self.device).unsqueeze(0).long()
        pitch, pitchf = None, None
        if if_f0 == 1:
            pitch, pitchf = self.get_f0(input_audio_path,audio_pad,p_len,f0_up_key,f0_method,filter_radius,inp_f0)
            pitch = pitch[:p_len]
            pitchf = pitchf[:p_len]
            pitch = torch.tensor(pitch, device=self.device).unsqueeze(0).long()
            pitchf = torch.tensor(pitchf, device=self.device).unsqueeze(0).float()
        for t in opt_ts:
            t = t // self.window * self.window
            if if_f0 == 1: audio_opt.append(self.vc(model, net_g, sid,audio_pad[s : t + self.t_pad2 + self.window], pitch[:, s // self.window : (t + self.t_pad2) // self.window],pitchf[:, s // self.window : (t + self.t_pad2) // self.window],times,index,big_npy,index_rate,version,protect,)[self.t_pad_tgt : -self.t_pad_tgt])
            else: audio_opt.append(self.vc(model,net_g,sid,audio_pad[s : t + self.t_pad2 + self.window],None,None,times,index,big_npy,index_rate,version,protect)[self.t_pad_tgt : -self.t_pad_tgt])
            s = t
        if if_f0 == 1: audio_opt.append(self.vc(model,net_g,sid,audio_pad[t:],pitch[:, t // self.window :] if t is not None else pitch,pitchf[:, t // self.window :] if t is not None else pitchf,times,index,big_npy,index_rate,version,protect,)[self.t_pad_tgt : -self.t_pad_tgt])
        else: audio_opt.append(self.vc(model, net_g, sid, audio_pad[t:], None, None, times, index, big_npy, index_rate, version, protect)[self.t_pad_tgt : -self.t_pad_tgt])
        audio_opt = np.concatenate(audio_opt)
        if rms_mix_rate != 1: audio_opt = change_rms(audio, 16000, audio_opt, tgt_sr, rms_mix_rate)
        if resample_sr >= 16000 and tgt_sr != resample_sr: audio_opt = librosa.resample(audio_opt, orig_sr=tgt_sr, target_sr=resample_sr)
        audio_max = np.abs(audio_opt).max() / 0.99
        max_int16 = 32768
        if audio_max > 1: max_int16 /= audio_max
        audio_opt = (audio_opt * max_int16).astype(np.int16)
        del pitch, pitchf, sid
        if torch.cuda.is_available(): torch.cuda.empty_cache()
        return audio_opt
