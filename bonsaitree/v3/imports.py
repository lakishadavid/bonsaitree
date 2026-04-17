import os
import pickle

import pandas as pd

from .constants import LBD_PATH, V3_MODELS_DIR


# @functools.lru_cache(maxsize=None)
def load_total_ibd_bounds(
    lbd_path: str=LBD_PATH,
):
    df = pd.read_csv(lbd_path)
    df = df.fillna(0)
    return df


# @functools.lru_cache(maxsize=None)
def load_ibd_moments(
    min_seg_len: float=0,
    models_dir: str=V3_MODELS_DIR,
):
    """
    Load the moments of the conditional and unconditional IBD number and length distributions.
    These moments are for the marginal distribution of n and the marginal distribution of the
    total length L separately.

    Args:
        min_seg_len (int): The minimum segment length used to generate the moments.

    Returns:
        cond_dict (dict): A dictionary of the conditional moments.
            {m: {a: {mean_num_1: val, mean_L_1: val, std_L_1: val, mean_num_2: val, mean_L_2: val, std_L_2: val}}}
            where
                m: number of meioses
                a: number of common ancestors
                mean_num_1: mean number of IBD1 segments
                mean_L_1: mean total length of IBD1 segments
                std_L_1: standard deviation of total length of IBD1 segments
                mean_num_2: mean number of IBD2 segments
                mean_L_2: mean total length of IBD2 segments
                std_L_2: standard deviation of total length of IBD2 segments
        uncond_dict (dict): A dictionary of the unconditional moments. Same format as cond_dict.
    """  # noqa: E501
    cond_fp = os.path.join(
        models_dir,
        "ibd_moments",
        f"min_seg_len_{min_seg_len}",
        "cond_moments.pkl",
    )
    uncond_fp = os.path.join(
        models_dir,
        "ibd_moments",
        f"min_seg_len_{min_seg_len}",
        "uncond_moments.pkl",
    )
    cond_dict = pickle.loads(open(cond_fp, "rb").read())
    uncond_dict = pickle.loads(open(uncond_fp, "rb").read())
    return cond_dict, uncond_dict


def load_ph_params(min_seg_len: float = 0):
    """Load Press-Hawkins parameters fitted from ped-sim.

    Returns an object with get_params_from_rel_tuple(rel_tuple) method
    that maps BonsaiTree (up, down, num_ancs) tuples to (k1, k2, alpha).
    """
    params_dir = os.path.join(V3_MODELS_DIR, "press_hawkins_params")
    params_file = os.path.join(params_dir, "fitted_params.pkl")

    if os.path.exists(params_file):
        params = pickle.loads(open(params_file, "rb").read())
        return PHParamsLookup(params)
    else:
        # Try TSV fallback
        tsv_file = os.path.join(params_dir, "fitted_press_hawkins_params.tsv")
        if os.path.exists(tsv_file):
            import csv
            params = {}
            with open(tsv_file) as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    m1 = int(float(row['m1']))
                    m2 = int(float(row['m2']))
                    a = int(float(row['a']))
                    params[(m1, m2, a)] = {
                        'k1': float(row['k1']),
                        'k2': float(row['k2']),
                        'alpha': float(row['alpha']),
                    }
            return PHParamsLookup(params)
        else:
            raise FileNotFoundError(
                f"Press-Hawkins params not found at {params_file} or {tsv_file}. "
                f"Run fit_press_hawkins_from_pedsim.py first."
            )


class PHParamsLookup:
    """Lookup Press-Hawkins parameters by BonsaiTree relationship tuple."""

    def __init__(self, params_dict):
        """params_dict: {(m1, m2, a): {'k1': float, 'k2': float, 'alpha': float}}"""
        self.params = params_dict

    def get_params_from_rel_tuple(self, rel_tuple):
        """Map BonsaiTree (up, down, num_ancs) to Press-Hawkins (k1, k2, alpha).

        Args:
            rel_tuple: (up, down, num_ancs) or None for unrelated

        Returns:
            dict with k1, k2, alpha, or None if not found
        """
        if rel_tuple is None:
            return None
        up, down, num_ancs = rel_tuple
        # Canonical: smaller first
        m1, m2 = min(up, down), max(up, down)
        total_mei = m1 + m2
        a = num_ancs

        # Direct lookup
        key = (m1, m2, a)
        if key in self.params:
            return self.params[key]

        # Try total meioses lookup (for symmetric relationships stored as total)
        key_total = (total_mei, a)
        if key_total in self.params:
            return self.params[key_total]

        return None
