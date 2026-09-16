import numpy as np

def calculate_ground_up_loss(tiv: np.ndarray, damage_ratio: np.ndarray) -> np.ndarray:
    """
    Calculates the Ground-Up Loss (GUL).
    GUL = TIV * Mean Damage Ratio
    """
    return tiv * damage_ratio

def calculate_net_loss(ground_up_loss: np.ndarray, deductible: np.ndarray, policy_limit: np.ndarray) -> np.ndarray:
    """
    Applies financial structures to calculate the Net (Insured) Loss.
    NET = min(max(GUL - Deductible, 0), Policy Limit)
    """
    loss_after_ded = np.maximum(ground_up_loss - deductible, 0.0)
    net_loss = np.minimum(loss_after_ded, policy_limit)
    return net_loss
