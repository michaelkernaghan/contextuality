"""test_spectral_filter.py -- Tests for spectral pre-filter module."""
import math
import numpy as np
import pytest


def test_spectral_profile_returns_all_invariants():
    from ks_spectral_filter import spectral_profile, CK31_COORDS, build_pairs_from_coords
    pairs = build_pairs_from_coords(CK31_COORDS)
    profile = spectral_profile(len(CK31_COORDS), pairs)

    expected_keys = {
        'n', 'edges', 'lambda_max', 'lambda_min',
        'hoffman_bound', 'spectral_gap', 'algebraic_connectivity',
        'energy', 'edge_density', 'eigenvalues'
    }
    assert set(profile.keys()) == expected_keys


def test_spectral_profile_ck31_basic_properties():
    from ks_spectral_filter import spectral_profile, CK31_COORDS, build_pairs_from_coords
    pairs = build_pairs_from_coords(CK31_COORDS)
    profile = spectral_profile(len(CK31_COORDS), pairs)

    assert profile['n'] == 31
    assert profile['edges'] == len(pairs)
    assert profile['lambda_max'] > 0
    assert profile['lambda_min'] < 0
    assert profile['hoffman_bound'] > 0
    assert profile['spectral_gap'] > 0
    assert profile['algebraic_connectivity'] > 0
    assert profile['energy'] > 0
    assert 0 < profile['edge_density'] < 1


def test_spectral_profile_trivial_graph():
    """A graph with no edges should have degenerate spectral properties."""
    from ks_spectral_filter import spectral_profile
    profile = spectral_profile(5, [])

    assert profile['edges'] == 0
    assert profile['energy'] == pytest.approx(0, abs=1e-10)
    assert profile['edge_density'] == 0


def test_build_pairs_from_coords_ck31():
    from ks_spectral_filter import build_pairs_from_coords, CK31_COORDS
    pairs = build_pairs_from_coords(CK31_COORDS)
    # CK-31 has 71 orthogonal pairs (known from ks_30_budget.py analysis)
    assert len(pairs) == 71
    # All pairs should be valid indices
    for i, j in pairs:
        assert 0 <= i < 31
        assert 0 <= j < 31
        assert i < j


def test_profile_known_sets_returns_profiles():
    from ks_spectral_filter import profile_known_sets
    profiles = profile_known_sets()
    assert 'CK-31' in profiles
    assert 'Peres-33' in profiles
    for name, prof in profiles.items():
        assert prof['n'] > 0
        assert prof['edges'] > 0
        assert prof['lambda_max'] > 0


def test_generate_colorable_controls():
    from ks_spectral_filter import generate_colorable_controls, build_pairs_from_coords, CK31_COORDS
    import random
    random.seed(42)
    pairs = build_pairs_from_coords(CK31_COORDS)
    controls = generate_colorable_controls(31, pairs, n_samples=50)
    assert len(controls) >= 10  # at least some controls generated
    for ctrl in controls:
        assert 'n' in ctrl
        assert ctrl['n'] < 31  # controls are subsets (smaller)


def test_discrimination_analysis():
    from ks_spectral_filter import discrimination_analysis, profile_known_sets
    import random
    random.seed(42)
    ks_profiles = profile_known_sets()
    analysis = discrimination_analysis(ks_profiles)
    assert isinstance(analysis, dict)
    # Should contain entries for each invariant
    assert 'hoffman_bound' in analysis
    assert 'spectral_gap' in analysis
    # Each entry should have ks_min, control_p95, useful flag
    for key, info in analysis.items():
        assert 'ks_min' in info or 'ks_max' in info
        assert 'useful' in info


def test_passes_fast_filter_ck31_passes():
    """CK-31 (a known KS set) should pass the filter."""
    from ks_spectral_filter import passes_fast_filter, build_pairs_from_coords, CK31_COORDS
    pairs = build_pairs_from_coords(CK31_COORDS)
    assert passes_fast_filter(31, pairs) is True


def test_passes_fast_filter_trivial_fails():
    """A trivial graph with no edges should fail."""
    from ks_spectral_filter import passes_fast_filter
    assert passes_fast_filter(5, []) is False


def test_passes_fast_filter_sparse_fails():
    """A very sparse graph (single edge) should fail."""
    from ks_spectral_filter import passes_fast_filter
    assert passes_fast_filter(30, [(0, 1)]) is False


def test_lovasz_theta_complete_graph():
    """For complete graph K_n, theta = 1."""
    pytest.importorskip("cvxpy")
    from ks_spectral_filter import lovasz_theta
    # K_4: all pairs connected
    pairs = [(i, j) for i in range(4) for j in range(i+1, 4)]
    theta = lovasz_theta(4, pairs)
    assert theta == pytest.approx(1.0, abs=0.1)


def test_lovasz_theta_empty_graph():
    """For empty graph (no edges), theta = n."""
    pytest.importorskip("cvxpy")
    from ks_spectral_filter import lovasz_theta
    theta = lovasz_theta(5, [])
    assert theta == pytest.approx(5.0, abs=0.1)


def test_lovasz_theta_ck31():
    """CK-31 should have a finite theta value."""
    pytest.importorskip("cvxpy")
    from ks_spectral_filter import lovasz_theta, build_pairs_from_coords, CK31_COORDS
    pairs = build_pairs_from_coords(CK31_COORDS)
    theta = lovasz_theta(31, pairs)
    assert 1.0 < theta < 31.0
