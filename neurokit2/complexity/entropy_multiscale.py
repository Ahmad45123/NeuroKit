# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .complexity_coarsegraining import _get_scales, complexity_coarsegraining
from .entropy_approximate import entropy_approximate
from .entropy_sample import entropy_sample
from .optim_complexity_tolerance import complexity_tolerance
from .utils import _get_coarsegrained_rolling, _phi, _phi_divide


def entropy_multiscale(
    signal,
    scale="default",
    dimension=2,
    tolerance="sd",
    approximate=False,
    composite=False,
    refined=False,
    fuzzy=False,
    show=False,
    **kwargs
):
    """**Multiscale entropy (MSE) and its Composite (CMSE), Refined (RCMSE) or fuzzy versions**

    Compute the multiscale entropy (MSE), the composite multiscale entropy (CMSE),
    the refined composite multiscale entropy (RCMSE), or their fuzzy version (FuzzyMSE, FuzzyCMSE or
    FuzzyRCMSE).

    One of the limitation of :func:`SampEn <entropy_sample>` is that it characterizes
    complexity strictly on the time scale defined by the sampling procedure (via the ``delay``
    argument). To address this, Costa et al. (2002) proposed the multiscale entropy (MSE),
    which compute sample entropies at multiple scales.

    The conventional MSE algorithm consists of two steps:
    1. A :func:`coarse-graining <complexity_coarsegraining>` procedure is used to represent the
       signal at different time scales.
    2. SampEn is used to quantify the regularity of a coarse-grained time series at each time scale
       factor.

    However, in the traditional coarse-graining procedure, the larger the scale factor is, the
    shorter the coarse-grained time series is. As such, the variance of the entropy of the
    coarse-grained series estimated by SampEn increases as the time scale factor increases, making
    it problematic for shorter signals.

    - **CMSE**: In order to reduce the variance of estimated entropy values at large scales, Wu et
      al. (2013) introduced the **composite multiscale entropy (CMSE)** algorithm, which computes
      multiple coarse-grained series for each scale factor (via the **time-shift** method for
      :func:`coarse-graining <complexity_coarsegraining>`).
    - **MMSE**: Wu et al. (2013) also introduced the **modified multiscale entropy (MMSE)**
      algorithm, which is based on rolling-average :func:`coarse-graining <complexity_coarsegraining>`.
    - **IMSE**: Liu et al. (2012) introduced an adaptive-resampling procedure to resample the
      coarse-grained series. We implement a generalization of this via interpolation that can be
      referred to as **interpolated multiscale entropy (IMSE)**.

    This function can be called either via ``entropy_multiscale()`` or ``complexity_mse()``.
    Moreover, variants can be directly accessed via ``complexity_cmse()``, `complexity_rcmse()``,
    ``complexity_fuzzymse()``, ``complexity_fuzzycmse()`` and ``complexity_fuzzyrcmse()``.

    Parameters
    ----------
    signal : Union[list, np.array, pd.Series]
        The signal (i.e., a time series) in the form of a vector of values.
        or dataframe.
    scale : str or int or list
        A list of scale factors used for coarse graining the time series. If 'default', will use
        ``range(len(signal) / (dimension + 10))`` (see discussion
        `here <https://github.com/neuropsychology/NeuroKit/issues/75#issuecomment-583884426>`_).
        If 'max', will use all scales until half the length of the signal. If an integer, will
        create a range until the specified int.
    dimension : int
        Embedding dimension (often denoted 'm' or 'd', sometimes referred to as 'order'). Typically
        2 or 3. It corresponds to the number of compared runs of lagged data. If 2, the embedding
        returns an array with two columns corresponding to the original signal and its delayed (by
        Tau) version.
    tolerance : float
        Tolerance (often denoted as 'r', i.e., filtering level - max absolute difference between
        segments). If 'default', will be set to 0.2 times the standard deviation of the signal (for
        dimension = 2).
    composite : bool
        Returns the composite multiscale entropy (CMSE), more accurate than MSE.
    refined : bool
        Returns the 'refined' composite MSE (RCMSE; Wu, 2014)
    fuzzy : bool
        Returns the fuzzy (composite) multiscale entropy (FuzzyMSE, FuzzyCMSE or FuzzyRCMSE).
    show : bool
        Show the entropy values for each scale factor.
    **kwargs
        Optional arguments.


    Returns
    ----------
    mse : float
        The point-estimate of multiscale entropy (MSE) of the single time series corresponding to the
        area under the MSE values curve, which is essentially the sum of sample entropy values over
        the range of scale factors.
        series.
    info : dict
        A dictionary containing additional information regarding the parameters used
        to compute multiscale entropy. The entropy values corresponding to each ``"Scale"``
        factor are stored under the ``"Value"`` key.

    See Also
    --------
    entropy_shannon, entropy_approximate, entropy_sample, entropy_fuzzy, entropy_permutation

    Examples
    ----------
    * **MSE** (basic coarse-graining)
    .. ipython:: python

      import neurokit2 as nk

      signal = nk.signal_simulate(duration=2, frequency=[5, 12, 40])

      @savefig p_entropy_multiscale1.png scale=100%
      mse, info = nk.entropy_multiscale(signal, show=True)
      @suppress
      plt.close()

    .. ipython:: python

      mse

    * **CMSE** (time-shifted coarse-graining)
    .. ipython:: python

      @savefig p_entropy_multiscale2.png scale=100%
      cmse, info = nk.entropy_multiscale(signal, method="timeshift", show=True)
      @suppress
      plt.close()

    .. ipython:: python

      cmse

    * **MMSE** (rolling-window coarse-graining)
    .. ipython:: python

      @savefig p_entropy_multiscale3.png scale=100%
      mmse, info = nk.entropy_multiscale(signal, method="rolling", show=True)
      @suppress
      plt.close()

    .. ipython:: python

      mmse

    * **IMSE** (interpolated coarse-graining)
    .. ipython:: python

      @savefig p_entropy_multiscale3.png scale=100%
      imse, info = nk.entropy_multiscale(signal, method="interpolate", show=True)
      @suppress
      plt.close()

    .. ipython:: python

      imse

    References
    -----------
    * Richman, J. S., & Moorman, J. R. (2000). Physiological time-series analysis using approximate
      entropy and sample entropy. American Journal of Physiology-Heart and Circulatory Physiology,
      278(6), H2039-H2049.
    * Costa, M., Goldberger, A. L., & Peng, C. K. (2002). Multiscale entropy analysis of complex
      physiologic time series. Physical review letters, 89(6), 068102.
    * Costa, M., Goldberger, A. L., & Peng, C. K. (2005). Multiscale entropy analysis of biological
      signals. Physical review E, 71(2), 021906.
    * Wu, S. D., Wu, C. W., Lin, S. G., Wang, C. C., & Lee, K. Y. (2013). Time series analysis
      using composite multiscale entropy. Entropy, 15(3), 1069-1084.
    * Gow, B. J., Peng, C. K., Wayne, P. M., & Ahn, A. C. (2015). Multiscale entropy analysis of
      center-of-pressure dynamics in human postural control: methodological considerations. Entropy,
      17(12), 7926-7947.
    * Norris, P. R., Anderson, S. M., Jenkins, J. M., Williams, A. E., & Morris Jr, J. A. (2008).
      Heart rate multiscale entropy at three hours predicts hospital mortality in 3,154 trauma
      patients. Shock, 30(1), 17-22.
    * Liu, Q., Wei, Q., Fan, S. Z., Lu, C. W., Lin, T. Y., Abbod, M. F., & Shieh, J. S. (2012).
      Adaptive computation of multiscale entropy and its application in EEG signals for monitoring
      depth of anesthesia during surgery. Entropy, 14(6), 978-992.

    """
    # Sanity checks
    if isinstance(signal, (np.ndarray, pd.DataFrame)) and signal.ndim > 1:
        raise ValueError(
            "Multidimensional inputs (e.g., matrices or multichannel data) are not supported yet."
        )
    # Prevent multiple arguments error in case 'delay' is passed in kwargs
    if "delay" in kwargs.keys():
        kwargs.pop("delay")

    # Store parameters
    info = {
        "Dimension": dimension,
        "Scale": _get_scales(signal, scale=scale, dimension=dimension),
        "Tolerance": complexity_tolerance(
            signal,
            method=tolerance,
            dimension=dimension,
            show=False,
        )[0],
    }

    # Select function
    if approximate is False:
        algorithm = entropy_sample
    else:
        algorithm = entropy_approximate

    # Mean that is robust to NaN,
    def _validmean(x):
        x = np.array(x)[np.isfinite(x)]
        if len(x) == 0:
            return np.nan
        else:
            return np.mean(x)

    # Define function that works both on 1D and 2D coarse-grained (for composite)
    def _run_algo(coarse, algorithm, dimension, tolerance, **kwargs):
        # For 1D coarse-graining
        if coarse.ndim == 1:
            return algorithm(
                coarse,
                delay=1,
                dimension=dimension,
                tolerance=tolerance,
                **kwargs,
            )[0]

        # For composite time-shifted coarse-graining
        else:
            return _validmean(
                [
                    algorithm(
                        coarse[i],
                        delay=1,
                        dimension=dimension,
                        tolerance=tolerance,
                        **kwargs,
                    )[0]
                    for i in range(len(coarse))
                ]
            )

    # Compute entropy for each coarsegrained segment
    info["Value"] = np.array(
        [
            _run_algo(
                coarse=complexity_coarsegraining(
                    signal,
                    scale=scale,
                    show=False,
                    **kwargs,
                ),
                algorithm=algorithm,
                dimension=dimension,
                tolerance=info["Tolerance"],
                **kwargs,
            )
            for scale in info["Scale"]
        ]
    )

    # Remove inf, nan and 0
    mse = info["Value"][np.isfinite(info["Value"])]

    # The MSE index is quantified as the area under the curve (AUC),
    # which is like the sum normalized by the number of values. It's similar to the mean.
    mse = np.trapz(mse) / len(mse)

    # Plot overlay
    if show is True:
        _entropy_multiscale_plot(info)

    return mse, info


# =============================================================================
# Internal
# =============================================================================
def _entropy_multiscale(
    signal,
    tolerance,
    scale_factors,
    dimension=2,
    composite=False,
    fuzzy=False,
    refined=False,
    show=False,
    **kwargs
):

    # Initalize mse vector
    mse_vals = np.full(len(scale_factors), np.nan)
    for i, tau in enumerate(scale_factors):

        # Regular MSE
        if refined is False and composite is False:
            mse_vals[i] = _entropy_multiscale_mse(
                signal, tau, dimension, tolerance, fuzzy, **kwargs
            )

        # Composite MSE
        elif refined is False and composite is True:
            mse_vals[i] = _entropy_multiscale_cmse(
                signal, tau, dimension, tolerance, fuzzy, **kwargs
            )

        # Refined Composite MSE
        else:
            mse_vals[i] = _entropy_multiscale_rcmse(
                signal, tau, dimension, tolerance, fuzzy, **kwargs
            )

    # Remove inf, nan and 0
    mse = mse_vals.copy()[~np.isnan(mse_vals)]
    mse = mse[(mse != np.inf) & (mse != -np.inf)]

    # The MSE index is quantified as the area under the curve (AUC),
    # which is like the sum normalized by the number of values. It's similar to the mean.
    mse = np.trapz(mse) / len(mse)

    # Plot overlay
    if show is True:
        _entropy_multiscale_plot(scale_factors, mse_vals)

    return mse, mse_vals


def _entropy_multiscale_plot(info):

    fig = plt.figure(constrained_layout=False)
    fig.suptitle("Entropy values across scale factors")
    plt.ylabel("Entropy values")
    plt.xlabel("Scale")
    plt.plot(
        info["Scale"][np.isfinite(info["Value"])],
        info["Value"][np.isfinite(info["Value"])],
        color="#FF9800",
    )

    return fig


# =============================================================================
# Methods
# =============================================================================
def _entropy_multiscale_mse(signal, tau, dimension, tolerance, fuzzy, **kwargs):
    y = complexity_coarsegraining(signal, scale=tau)
    if len(y) < 10 ** dimension:  # Compute only if enough values (Liu et al., 2012)
        return np.nan

    return entropy_sample(
        y, delay=1, dimension=dimension, tolerance=tolerance, fuzzy=fuzzy, **kwargs
    )[0]


def _entropy_multiscale_cmse(signal, tau, dimension, tolerance, fuzzy, **kwargs):
    y = _get_coarsegrained_rolling(signal, tau)
    if y.size < 10 ** dimension:  # Compute only if enough values (Liu et al., 2012)
        return np.nan

    mse_y = np.full(len(y), np.nan)
    for i in np.arange(len(y)):
        mse_y[i] = entropy_sample(
            y[i, :], delay=1, dimension=dimension, tolerance=tolerance, fuzzy=fuzzy, **kwargs
        )[0]

    if len(np.where((mse_y == np.inf) | (mse_y == -np.inf) | (mse_y == np.nan))[0]) == len(mse_y):
        # return nan if all are infinity/nan values
        return np.nan
    else:
        # Remove inf, nan and 0
        mse_y = mse_y[(mse_y != np.inf) & (mse_y != -np.inf) & ~np.isnan(mse_y)]

        return np.mean(mse_y)


def _entropy_multiscale_rcmse(signal, tau, dimension, tolerance, fuzzy, **kwargs):
    y = _get_coarsegrained_rolling(signal, tau)
    if y.size < 10 ** dimension:  # Compute only if enough values (Liu et al., 2012)
        return np.nan

    # Get phi for all kth coarse-grained time series
    phi_ = np.full([len(y), 2], np.nan)
    for i in np.arange(len(y)):
        phi_[i] = _phi(
            y[i, :],
            delay=1,
            dimension=dimension,
            tolerance=tolerance,
            fuzzy=fuzzy,
            approximate=False,
            **kwargs,
        )

    # Average all phi of the same dimension, then divide, then log
    return _phi_divide([np.mean(phi_[:, 0]), np.mean(phi_[:, 1])])
