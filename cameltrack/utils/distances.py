import warnings

import numpy as np

def rect_min_max(r):
    min_pt = r[..., :2]
    size = r[..., 2:]
    max_pt = min_pt + size
    return min_pt, max_pt


def quiet_divide(a, b):
    """Quiet divide function that does not warn about (0 / 0)."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        return np.true_divide(a, b)


def boxiou(a, b):
    """Computes IOU of two rectangles."""
    a_min, a_max = rect_min_max(a)
    b_min, b_max = rect_min_max(b)
    # Compute intersection.
    i_min = np.maximum(a_min, b_min)
    i_max = np.minimum(a_max, b_max)
    i_size = np.maximum(i_max - i_min, 0)
    i_vol = np.prod(i_size, axis=-1)
    # Get volume of union.
    a_size = np.maximum(a_max - a_min, 0)
    b_size = np.maximum(b_max - b_min, 0)
    a_vol = np.prod(a_size, axis=-1)
    b_vol = np.prod(b_size, axis=-1)
    u_vol = a_vol + b_vol - i_vol
    return np.where(i_vol == 0, np.zeros_like(i_vol, dtype=float),
                    quiet_divide(i_vol, u_vol))


def iou_matrix(objs, hyps, max_iou=1.):
    """Computes 'intersection over union (IoU)' distance matrix between object and hypothesis rectangles.

    The IoU is computed as

        IoU(a,b) = 1. - isect(a, b) / union(a, b)

    where isect(a,b) is the area of intersection of two rectangles and union(a, b) the area of union. The
    IoU is bounded between zero and one. 0 when the rectangles overlap perfectly and 1 when the overlap is
    zero.

    Params
    ------
    objs : Nx4 array
        Object rectangles (x,y,w,h) in rows
    hyps : Kx4 array
        Hypothesis rectangles (x,y,w,h) in rows

    Kwargs
    ------
    max_iou : float
        Maximum tolerable overlap distance. Object / hypothesis points
        with larger distance are set to np.nan signalling do-not-pair. Defaults
        to 0.5

    Returns
    -------
    C : NxK array
        Distance matrix containing pairwise distances or np.nan.
    """

    if np.size(objs) == 0 or np.size(hyps) == 0:
        return np.empty((0, 0))

    objs = np.asfarray(objs)
    hyps = np.asfarray(hyps)
    assert objs.shape[1] == 4
    assert hyps.shape[1] == 4
    iou = boxiou(objs[:, None], hyps[None, :])
    dist = 1 - iou
    return np.where(dist > max_iou, 1e10, dist)
