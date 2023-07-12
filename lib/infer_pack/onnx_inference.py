import onnxruntime
import librosa
import numpy as np
from lib.infer_pack.modules.F0Predictor.PMF0Predictor import PMF0Predictor

VEC_PATH = "pretrained/vec-768-layer-12.onnx"
MAX_LENGTH = 50.0
F0_MIN = 50
F0_MAX = 1100
F0_MEL_MIN = 1127 * np.log(1 + F0_MIN / 700)
F0_MEL_MAX = 1127 * np.log(1 + F0_MAX / 700)
RESAMPLING_RATE = 16000

class ContentVectorModel:
    def __init__(self, vector_path=VEC_PATH):
        providers = ["CPUExecutionProvider"]
        self.model = onnxruntime.InferenceSession(vector_path, providers=providers)

    def __call__(self, audio_wave):
        return self.process_audio(audio_wave)

    @staticmethod
    def process_audio(audio_wave):
        features = audio_wave.mean(-1) if audio_wave.ndim == 2 else audio_wave
        features = np.expand_dims(np.expand_dims(features, 0), 0)
        onnx_input = {self.model.get_inputs()[0].name: features}
        logits = self.model.run(None, onnx_input)[0]
        return logits.transpose(0, 2, 1)


class OnnxRVC:
    def __init__(self, model_path, sampling_rate=40000, hop_size=512, vector_path=VEC_PATH):
        self.vec_model = ContentVectorModel(f"{vector_path}.onnx")
        providers = ["CPUExecutionProvider"]
        self.model = onnxruntime.InferenceSession(model_path, providers=providers)
        self.sampling_rate = sampling_rate
        self.hop_size = hop_size

    def forward(self, hubert, hubert_length, pitch, pitchf, ds, rnd):
        onnx_input = {
            self.model.get_inputs()[0].name: hubert,
            self.model.get_inputs()[1].name: hubert_length,
            self.model.get_inputs()[2].name: pitch,
            self.model.get_inputs()[3].name: pitchf,
            self.model.get_inputs()[4].name: ds,
            self.model.get_inputs()[5].name: rnd,
        }
        return (self.model.run(None, onnx_input)[0] * 32767).astype(np.int16)

    def inference(self, raw_path, sid, f0_method="pm", f0_up_key=0, pad_time=0.5, cr_threshold=0.02):
        f0_predictor = PMF0Predictor(hop_length=self.hop_size, sampling_rate=self.sampling_rate, threshold=cr_threshold)
        wav, sr = librosa.load(raw_path, sr=self.sampling_rate)
        org_length = len(wav)
        if org_length / sr > MAX_LENGTH:
            raise RuntimeError("Reached Max Length")

        wav16k = librosa.resample(wav, orig_sr=self.sampling_rate, target_sr=RESAMPLING_RATE)
        hubert = self.vec_model(wav16k)
        hubert = np.repeat(hubert, 2, axis=2).transpose(0, 2, 1).astype(np.float32)
        hubert_length = hubert.shape[1]

        pitchf = f0_predictor.compute_f0(wav, hubert_length)
        pitchf *= 2 ** (f0_up_key / 12)
        pitch = pitchf.copy()
        f0_mel = 1127 * np.log(1 + pitch / 700)
        f0_mel = np.clip(f0_mel - F0_MEL_MIN, 0, None) * 254 / (F0_MEL_MAX - F0_MEL_MIN) + 1
        pitch = np.rint(f0_mel).astype(np.int64)

        pitchf = pitchf.reshape(1, -1).astype(np.float32)
        pitch = pitch.reshape(1, -1)
        ds = np.array([sid]).astype(np.int64)
        rnd = np.random.randn(1, 192, hubert_length).astype(np.float32)
        hubert_length = np.array([hubert_length]).astype(np.int64)

        out_wav = self.forward(hubert, hubert_length, pitch, pitchf, ds, rnd).squeeze()
        out_wav = np.pad(out_wav, (0, 2 * self.hop_size), "constant")
        return out_wav[0:org_length]