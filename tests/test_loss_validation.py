import numpy as np
import pytest
from src.validation import validate_losses
from src.loss import calculate_ground_up_loss, calculate_net_loss

def test_validate_losses_success():
    gul = np.array([[1000, 2000], [500, 100]])
    net = np.array([[900, 1500], [400, 50]])
    ded = np.array([100, 500])
    lim = np.array([1000, 2000])
    
    # Should not raise
    assert validate_losses(gul, net, ded, lim) == True

def test_validate_losses_negative():
    gul = np.array([[-100, 2000]])
    net = np.array([[-100, 1500]])
    ded = np.array([0, 0])
    lim = np.array([10000, 10000])
    
    with pytest.raises(ValueError, match="Negative losses detected"):
        validate_losses(gul, net, ded, lim)

def test_validate_losses_net_exceeds_gul():
    gul = np.array([[100, 200]])
    net = np.array([[150, 200]]) # 150 > 100
    ded = np.array([0, 0])
    lim = np.array([1000, 1000])
    
    with pytest.raises(ValueError, match="Net loss exceeds Ground-Up loss"):
        validate_losses(gul, net, ded, lim)

def test_calculate_net_loss():
    gul = np.array([1000, 5000, 100])
    ded = np.array([500, 1000, 200])
    lim = np.array([10000, 2000, 1000])
    
    net = calculate_net_loss(gul, ded, lim)
    
    # property 1: gul 1000 - ded 500 = 500 (limit 10k ok) -> 500
    # property 2: gul 5000 - ded 1000 = 4000 (limit 2000 caps it) -> 2000
    # property 3: gul 100 - ded 200 = 0 -> 0
    
    np.testing.assert_array_equal(net, [500, 2000, 0])
