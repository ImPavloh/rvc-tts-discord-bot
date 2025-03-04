import math
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

def init_weights(m, mean=0.0, std=0.01):
    classname = m.__class__.__name__
    if "Conv" in classname: m.weight.data.normal_(mean, std)

def get_padding(kernel_size, dilation=1):
    return (kernel_size * dilation - dilation) // 2

def convert_pad_shape(pad_shape):
    l = pad_shape[::-1]
    return [item for sublist in l for item in sublist]

def kl_divergence(m_p, logs_p, m_q, logs_q):
    kl = logs_q - logs_p - 0.5
    kl += 0.5 * (torch.exp(2.0 * logs_p) + (m_p - m_q) ** 2) * torch.exp(-2.0 * logs_q)
    return kl

def rand_gumbel(shape):
    return -torch.log(-torch.log(torch.rand(shape) + 1e-5))

def rand_gumbel_like(x):
    return rand_gumbel(x.size()).to(dtype=x.dtype, device=x.device)

def slice_segments(x, ids_str, segment_size=4, slice_dim=2):
    if slice_dim == 1: ret = torch.zeros_like(x[:, :segment_size])
    else: ret = torch.zeros_like(x[:, :, :segment_size])

    for i in range(x.size(0)):
        idx_str = ids_str[i]
        idx_end = idx_str + segment_size
        ret[i] = x[i, ..., idx_str:idx_end]
    return ret

def rand_slice_segments(x, x_lengths=None, segment_size=4):
    b, d, t = x.size()

    if x_lengths is None: x_lengths = t

    ids_str_max = x_lengths - segment_size + 1
    ids_str = (torch.rand([b]).to(device=x.device) * ids_str_max).to(dtype=torch.long)
    ret = slice_segments(x, ids_str, segment_size)
    return ret, ids_str

def get_timing_signal_1d(length, channels, min_timescale=1.0, max_timescale=1.0e4):
    position = torch.arange(length, dtype=torch.float)
    num_timescales = channels // 2
    log_timescale_increment = math.log(float(max_timescale) / float(min_timescale)) / (num_timescales - 1)
    inv_timescales = min_timescale * torch.exp(torch.arange(num_timescales, dtype=torch.float) * -log_timescale_increment)
    scaled_time = position.unsqueeze(0) * inv_timescales.unsqueeze(1)
    signal = torch.cat([torch.sin(scaled_time), torch.cos(scaled_time)], 0)
    signal = F.pad(signal, [0, 0, 0, channels % 2])
    signal = signal.view(1, channels, length)
    return signal

def apply_timing_signal_1d(x, operation='add', min_timescale=1.0, max_timescale=1.0e4):
    b, channels, length = x.size()
    signal = get_timing_signal_1d(length, channels, min_timescale, max_timescale)
    signal = signal.to(dtype=x.dtype, device=x.device)

    if operation == 'add': return x + signal
    elif operation == 'cat': return torch.cat([x, signal], axis=1)

def subsequent_mask(length):
    return torch.tril(torch.ones(length, length)).unsqueeze(0).unsqueeze(0)

@torch.jit.script
def fused_add_tanh_sigmoid_multiply(input_a, input_b, n_channels):
    n_channels_int = n_channels[0]
    in_act = input_a + input_b
    t_act = torch.tanh(in_act[:, :n_channels_int, :])
    s_act = torch.sigmoid(in_act[:, n_channels_int:, :])
    return t_act * s_act

def shift_1d(x):
    x = F.pad(x, convert_pad_shape([[0, 0], [0, 0], [1, 0]]))[:, :, :-1]
    return x

def sequence_mask(length, max_length=None):
    if max_length is None: max_length = length.max()
    x = torch.arange(max_length, dtype=length.dtype, device=length.device)
    return x.unsqueeze(0) < length.unsqueeze(1)

def generate_path(duration, mask):
    device = duration.device
    b, _, t_y, t_x = mask.shape
    cum_duration = torch.cumsum(duration, -1)
    cum_duration_flat = cum_duration.view(b * t_x)
    path = sequence_mask(cum_duration_flat, t_y).to(mask.dtype)
    path = path.view(b, t_x, t_y)
    path = path - F.pad(path, convert_pad_shape([[0, 0], [1, 0], [0, 0]]))[:, :-1]
    path = path.unsqueeze(1).transpose(2, 3) * mask
    return path

def clip_grad_value_(parameters, clip_value, norm_type=2):
    if isinstance(parameters, torch.Tensor): parameters = [parameters]
    parameters = list(filter(lambda p: p.grad is not None, parameters))
    norm_type = float(norm_type)

    if clip_value is not None: clip_value = float(clip_value)

    total_norm = 0
    for p in parameters:
        param_norm = p.grad.data.norm(norm_type)
        total_norm += param_norm.item() ** norm_type
        if clip_value is not None: p.grad.data.clamp_(min=-clip_value, max=clip_value)
    total_norm = total_norm ** (1.0 / norm_type)
    return total_norm
