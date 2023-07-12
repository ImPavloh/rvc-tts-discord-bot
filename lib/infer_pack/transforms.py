import torch
from torch.nn import functional as F
import numpy as np

DEFAULT_MIN_BIN_WIDTH = 1e-3
DEFAULT_MIN_BIN_HEIGHT = 1e-3
DEFAULT_MIN_DERIVATIVE = 1e-3

def piecewise_rational_quadratic_transform(inputs, unnormalized_widths, unnormalized_heights, unnormalized_derivatives, inverse=False, tails=None, tail_bound=1.0, min_bin_width=DEFAULT_MIN_BIN_WIDTH, min_bin_height=DEFAULT_MIN_BIN_HEIGHT, min_derivative=DEFAULT_MIN_DERIVATIVE):
    if tails is None:
        spline_fn = rational_quadratic_spline
        spline_kwargs = {}
    else:
        spline_fn = unconstrained_rational_quadratic_spline
        spline_kwargs = {"tails": tails, "tail_bound": tail_bound}

    return spline_fn(inputs=inputs, unnormalized_widths=unnormalized_widths, unnormalized_heights=unnormalized_heights, unnormalized_derivatives=unnormalized_derivatives, inverse=inverse, min_bin_width=min_bin_width, min_bin_height=min_bin_height, min_derivative=min_derivative, **spline_kwargs)

def searchsorted(bin_locations, inputs, eps=1e-6):
    bin_locations[..., -1] += eps
    return torch.sum(inputs[..., None] >= bin_locations, dim=-1) - 1

def unconstrained_rational_quadratic_spline(inputs, unnormalized_widths, unnormalized_heights, unnormalized_derivatives, inverse=False, tails="linear", tail_bound=1.0, min_bin_width=DEFAULT_MIN_BIN_WIDTH, min_bin_height=DEFAULT_MIN_BIN_HEIGHT, min_derivative=DEFAULT_MIN_DERIVATIVE):
    if tails != "linear":
        raise RuntimeError("{} tails are not implemented.".format(tails))

    unnormalized_derivatives = F.pad(unnormalized_derivatives, pad=(1, 1))
    constant = np.log(np.exp(1 - min_derivative) - 1)
    unnormalized_derivatives[..., 0] = constant
    unnormalized_derivatives[..., -1] = constant

    inside_interval_mask = (inputs >= -tail_bound) & (inputs <= tail_bound)
    outside_interval_mask = ~inside_interval_mask
    outputs = torch.where(outside_interval_mask, inputs, torch.zeros_like(inputs))
    logabsdet = torch.zeros_like(inputs)

    inside_outputs, inside_logabsdet = rational_quadratic_spline(
        inputs=inputs[inside_interval_mask],
        unnormalized_widths=unnormalized_widths[inside_interval_mask, :],
        unnormalized_heights=unnormalized_heights[inside_interval_mask, :],
        unnormalized_derivatives=unnormalized_derivatives[inside_interval_mask, :],
        inverse=inverse, left=-tail_bound, right=tail_bound, bottom=-tail_bound, top=tail_bound,
        min_bin_width=min_bin_width, min_bin_height=min_bin_height, min_derivative=min_derivative)

    outputs[inside_interval_mask] = inside_outputs
    logabsdet[inside_interval_mask] = inside_logabsdet

    return outputs, logabsdet

def rational_quadratic_spline(inputs, unnormalized_widths, unnormalized_heights, unnormalized_derivatives, inverse=False, left=0.0, right=1.0, bottom=0.0, top=1.0, min_bin_width=DEFAULT_MIN_BIN_WIDTH, min_bin_height=DEFAULT_MIN_BIN_HEIGHT, min_derivative=DEFAULT_MIN_DERIVATIVE):
    num_bins = unnormalized_widths.shape[-1]

    if min_bin_width * num_bins > 1.0:
        raise ValueError("Minimal bin width too large for the number of bins")
    if min_bin_height * num_bins > 1.0:
        raise ValueError("Minimal bin height too large for the number of bins")

    widths, heights = compute_widths_and_heights(unnormalized_widths, unnormalized_heights, min_bin_width, min_bin_height, num_bins, left, right, bottom, top)
    cumwidths, cumheights = widths.cumsum(dim=-1), heights.cumsum(dim=-1)
    cumwidths[..., 0] = left
    cumwidths[..., -1] = right
    cumheights[..., 0] = bottom
    cumheights[..., -1] = top
    widths, heights = cumwidths[..., 1:] - cumwidths[..., :-1], cumheights[..., 1:] - cumheights[..., :-1]

    derivatives = min_derivative + F.softplus(unnormalized_derivatives)

    if inverse:
        bin_idx = searchsorted(cumheights, inputs)[..., None]
    else:
        bin_idx = searchsorted(cumwidths, inputs)[..., None]

    gather_args = (-1, bin_idx)
    input_cumwidths, input_bin_widths, input_cumheights, input_delta, input_derivatives, input_derivatives_plus_one, input_heights = map(
        lambda tensor: tensor.gather(*gather_args)[..., 0],
        (cumwidths, widths, cumheights, heights / widths, derivatives, derivatives[..., 1:], heights))

    if inverse:
        outputs, logabsdet = inverse_rational_quadratic_spline(inputs, input_cumheights, input_heights, input_derivatives, input_derivatives_plus_one, input_delta, input_bin_widths, input_cumwidths)
    else:
        outputs, logabsdet = direct_rational_quadratic_spline(inputs, input_cumwidths, input_bin_widths, input_cumheights, input_heights, input_derivatives, input_derivatives_plus_one, input_delta)

    return outputs, logabsdet

def compute_widths_and_heights(unnormalized_widths, unnormalized_heights, min_bin_width, min_bin_height, num_bins, left, right, bottom, top):
    widths = F.softmax(unnormalized_widths, dim=-1)
    widths = min_bin_width + (1 - min_bin_width * num_bins) * widths
    widths = (right - left) * widths + left

    heights = F.softmax(unnormalized_heights, dim=-1)
    heights = min_bin_height + (1 - min_bin_height * num_bins) * heights
    heights = (top - bottom) * heights + bottom

    return widths, heights

def inverse_rational_quadratic_spline(inputs, input_cumheights, input_heights, input_derivatives, input_derivatives_plus_one, input_delta, input_bin_widths, input_cumwidths):
    a = (inputs - input_cumheights) * (input_derivatives + input_derivatives_plus_one - 2 * input_delta) + input_heights * (input_delta - input_derivatives)
    b = input_heights * input_derivatives - (inputs - input_cumheights) * (input_derivatives + input_derivatives_plus_one - 2 * input_delta)
    c = -input_delta * (inputs - input_cumheights)

    discriminant = b.pow(2) - 4 * a * c
    assert (discriminant >= 0).all()

    root = (2 * c) / (-b - torch.sqrt(discriminant))
    outputs = root * input_bin_widths + input_cumwidths
    theta_one_minus_theta = root * (1 - root)
    denominator = input_delta + ((input_derivatives + input_derivatives_plus_one - 2 * input_delta)* theta_one_minus_theta)
    derivative_numerator = input_delta.pow(2) * (input_derivatives_plus_one * root.pow(2)+ 2 * input_delta * theta_one_minus_theta+ input_derivatives * (1 - root).pow(2))
    logabsdet = torch.log(derivative_numerator) - 2 * torch.log(denominator)

    return outputs, -logabsdet

def direct_rational_quadratic_spline(inputs, input_cumwidths, input_bin_widths, input_cumheights, input_heights, input_derivatives, input_derivatives_plus_one, input_delta):
    theta = (inputs - input_cumwidths) / input_bin_widths
    theta_one_minus_theta = theta * (1 - theta)
    numerator = input_heights * (input_delta * theta.pow(2) + input_derivatives * theta_one_minus_theta)
    denominator = input_delta + ((input_derivatives + input_derivatives_plus_one - 2 * input_delta) * theta_one_minus_theta)
    outputs = input_cumheights + numerator / denominator
    derivative_numerator = input_delta.pow(2) * (input_derivatives_plus_one * theta.pow(2) + 2 * input_delta * theta_one_minus_theta + input_derivatives * (1 - theta).pow(2))
    logabsdet = torch.log(derivative_numerator) - 2 * torch.log(denominator)

    return outputs, logabsdet