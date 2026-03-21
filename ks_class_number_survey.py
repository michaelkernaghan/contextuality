#!/usr/bin/env python3
"""
KS Class Number Survey — systematic test of class-number > 1 fields.

Tests imaginary quadratic fields Q(sqrt(-d)) with class number h > 1,
quartic fields Q(d^{1/4}), and multi-generator alphabets.

Goal: either find a 7th algebraic island or strengthen the two-mechanism
thesis across ~30 new field extensions.
"""

import cmath
import math
import random
import sys
import time
from itertools import combinations

from ks_explore_new import test_alphabet
from ks_complex import hermitian_dot

# ---------------------------------------------------------------------------
# Class number data: (d, h, ring_type)
#   ring_type: "standard" => O_K = Z[sqrt(-d)], "halfint" => O_K = Z[(1+sqrt(-d))/2]
# ---------------------------------------------------------------------------

CLASS_NUMBER_DATA = [
    # h=2
    (5, 2, "standard"),
    (6, 2, "standard"),
    (10, 2, "standard"),
    (13, 2, "standard"),
    (15, 2, "halfint"),
    (22, 2, "standard"),
    (35, 2, "halfint"),
    (37, 2, "standard"),
    (51, 2, "halfint"),
    (58, 2, "standard"),
    (91, 2, "halfint"),
    # h=3
    (23, 3, "halfint"),
    (31, 3, "halfint"),
    (59, 3, "halfint"),
    (83, 3, "halfint"),
    # h=4
    (14, 4, "standard"),
    (17, 4, "standard"),
    (21, 4, "standard"),
    (30, 4, "standard"),
    (33, 4, "standard"),
    (34, 4, "standard"),
    (39, 4, "halfint"),
    (42, 4, "standard"),
    (46, 4, "standard"),
    (55, 4, "halfint"),
    (57, 4, "standard"),
]

# Fields already tested in previous work (standard generator only)
PREVIOUSLY_TESTED = {5, 6, 10, 13, 14, 15}


# ---------------------------------------------------------------------------
# Generator and alphabet construction
# ---------------------------------------------------------------------------

def ring_of_integers_generator(d):
    """Return (gen, gen_conj, ring_name, norm_sq) for Q(sqrt(-d))."""
    sd = cmath.sqrt(-d)
    if d % 4 == 3:
        gen = (1 + sd) / 2
        gen_conj = (1 - sd) / 2  # conjugate: (1 - sqrt(-d))/2
        ring_name = f"Z[(1+sqrt(-{d}))/2]"
        norm_sq = abs(gen) ** 2
    else:
        gen = sd
        gen_conj = -sd  # conjugate of sqrt(-d) = i*sqrt(d) is -i*sqrt(d)
        ring_name = f"Z[sqrt(-{d})]"
        norm_sq = abs(gen) ** 2
    return gen, gen_conj, ring_name, norm_sq


def build_basic_alphabet(gen, gen_conj):
    """Basic alphabet: {0, +/-1, +/-gen, +/-gen_conj} deduped."""
    candidates = [0, 1, -1, gen, -gen, gen_conj, -gen_conj]
    return _dedup_complex(candidates)


def build_enriched_alphabet(gen, gen_conj):
    """Enriched alphabet: basic + field-specific products/sums (NO pure integers beyond ±1)."""
    basic = [0, 1, -1, gen, -gen, gen_conj, -gen_conj]
    extra = [
        gen * gen, -(gen * gen),
        gen_conj * gen_conj, -(gen_conj * gen_conj),
        1 + gen, -(1 + gen),
        1 + gen_conj, -(1 + gen_conj),
        gen + gen_conj, -(gen + gen_conj),
        # Omit ±2: pure integers contaminate results with known integer KS sets
    ]
    candidates = basic + extra
    deduped = _dedup_complex(candidates)
    # Filter out any elements that reduced to pure real integers (besides 0, ±1)
    filtered = []
    for v in deduped:
        if abs(v.imag) < 1e-8 and abs(v.real - round(v.real)) < 1e-8:
            if abs(v.real) <= 1:
                filtered.append(v)  # keep 0, ±1
            # else skip pure integers like ±2, ±3, etc.
        else:
            filtered.append(v)
    return filtered[:15]


def _dedup_complex(vals, tol=1e-8):
    """Deduplicate complex values by rounding."""
    seen = set()
    result = []
    for v in vals:
        key = (round(v.real, 7), round(v.imag, 7))
        if key not in seen:
            seen.add(key)
            result.append(complex(v))
    return result


# ---------------------------------------------------------------------------
# Cancellation analysis
# ---------------------------------------------------------------------------

def analyze_cancellation(d, gen, alphabet):
    """Predict KS likelihood from algebraic properties."""
    norm_sq = abs(gen) ** 2
    has_mod2 = any(abs(abs(x) ** 2 - 2.0) < 1e-8 for x in alphabet if x != 0)
    has_unity = any(abs(abs(x) - 1.0) < 1e-8 and abs(x) != 0 for x in alphabet)

    # Check for cancellation identities: a^2 + b^2 + c^2 = 0
    cancellations = 0
    for a in alphabet:
        for b in alphabet:
            for c in alphabet:
                if a == 0 and b == 0 and c == 0:
                    continue
                s = a * a.conjugate() + b * b.conjugate() + c * c.conjugate()
                # This is always real and >= 0, so cancellation in norm sense
                # doesn't apply. Instead check orthogonality potential.
                pass
    # Simpler heuristic: fields with |gen|^2 <= 3 have higher KS potential
    ks_potential = "HIGH" if norm_sq <= 3.0 else ("MEDIUM" if norm_sq <= 7.0 else "LOW")

    return {
        'd': d,
        'norm_sq': round(norm_sq, 4),
        'has_mod2_element': has_mod2,
        'has_unit_element': has_unity,
        'ks_potential': ks_potential,
    }


# ---------------------------------------------------------------------------
# Survey functions
# ---------------------------------------------------------------------------

def survey_class_number_gt1():
    """Survey all class-number > 1 imaginary quadratic fields."""
    results = []
    for d, h, ring_type in CLASS_NUMBER_DATA:
        gen, gen_conj, ring_name, norm_sq = ring_of_integers_generator(d)
        is_new = d not in PREVIOUSLY_TESTED
        if d in PREVIOUSLY_TESTED and ring_type == "halfint":
            is_new = True  # halfint generator is new even if d was tested

        n_trials = 50 if is_new else 20

        print(f"\n{'='*60}")
        print(f"d={d}, h={h}, ring={ring_name}, |gen|^2={norm_sq:.2f}, new={is_new}")
        print(f"{'='*60}")

        # Cancellation analysis
        basic_alpha = build_basic_alphabet(gen, gen_conj)
        analysis = analyze_cancellation(d, gen, basic_alpha)
        print(f"  Potential: {analysis['ks_potential']}, |gen|^2={analysis['norm_sq']}, "
              f"mod2={analysis['has_mod2_element']}, units={analysis['has_unit_element']}")

        # Basic alphabet test
        name = f"Q(sqrt(-{d}))_h{h}_basic"
        print(f"\n  Testing basic alphabet ({len(basic_alpha)} elements)...")
        result_basic = test_alphabet(name, basic_alpha, use_completion=True, n_trials=n_trials)

        entry = {
            'd': d,
            'h': h,
            'ring_type': ring_type,
            'ring_name': ring_name,
            'norm_sq': round(norm_sq, 4),
            'is_new': is_new,
            'analysis': analysis,
            'basic': result_basic,
            'enriched': None,
        }

        # Enriched alphabet only if basic is colorable
        if not result_basic.get('uncol', False):
            enriched_alpha = build_enriched_alphabet(gen, gen_conj)
            name_e = f"Q(sqrt(-{d}))_h{h}_enriched"
            print(f"\n  Testing enriched alphabet ({len(enriched_alpha)} elements)...")
            # Skip completion for large alphabets to avoid 9000+ ray explosions
            use_comp = len(enriched_alpha) <= 9
            result_enriched = test_alphabet(name_e, enriched_alpha, use_completion=use_comp, n_trials=n_trials)
            entry['enriched'] = result_enriched

            if result_enriched.get('rays_raw', 0) > 500:
                print(f"  NOTE: {result_enriched['rays_raw']} raw rays (completion {'on' if use_comp else 'skipped'})")

        results.append(entry)
    return results


def survey_quartic_fields():
    """Survey quartic fields Q(d^{1/4}) for d=2,3,5."""
    results = []
    for d in [2, 3, 5]:
        fourth_root = d ** 0.25
        sqrt_d = math.sqrt(d)
        three_fourth = d ** 0.75

        print(f"\n{'='*60}")
        print(f"Quartic field: Q({d}^(1/4)), {d}^(1/4) = {fourth_root:.6f}")
        print(f"{'='*60}")

        # Basic: {0, +/-1, +/-d^{1/4}}
        basic = _dedup_complex([complex(x) for x in [0, 1, -1, fourth_root, -fourth_root]])
        name = f"Q({d}^(1/4))_basic"
        print(f"\n  Testing basic ({len(basic)} elements)...")
        result_basic = test_alphabet(name, basic, use_completion=True, n_trials=50)

        entry = {
            'field': f"Q({d}^(1/4))",
            'd': d,
            'basic': result_basic,
            'extended': None,
        }

        if not result_basic.get('uncol', False):
            extended = _dedup_complex([complex(x) for x in [
                0, 1, -1, fourth_root, -fourth_root,
                sqrt_d, -sqrt_d, three_fourth, -three_fourth
            ]])
            name_e = f"Q({d}^(1/4))_extended"
            print(f"\n  Testing extended ({len(extended)} elements)...")
            use_comp = len(extended) <= 9
            result_ext = test_alphabet(name_e, extended, use_completion=use_comp, n_trials=50)
            entry['extended'] = result_ext

        results.append(entry)
    return results


def survey_multi_generator_pairs():
    """Survey 2-generator alphabets from known algebraic constants."""
    sqrt2 = math.sqrt(2)
    sqrt3 = math.sqrt(3)
    sqrt5 = math.sqrt(5)
    phi = (1 + sqrt5) / 2
    omega = cmath.exp(2j * cmath.pi / 3)
    sqrt_neg2 = cmath.sqrt(-2)
    i = 1j
    h7 = (1 + cmath.sqrt(-7)) / 2

    generators = {
        'sqrt2': sqrt2,
        'sqrt3': sqrt3,
        'sqrt5': sqrt5,
        'phi': phi,
        'omega': omega,
        'sqrt(-2)': sqrt_neg2,
        'i': i,
        'h7': h7,
    }

    # Already tested pairs (from previous work)
    already_tested = {
        frozenset({'sqrt2', 'sqrt3'}),
        frozenset({'sqrt2', 'phi'}),
        frozenset({'i', 'omega'}),
    }

    results = []
    pairs = list(combinations(sorted(generators.keys()), 2))

    for g1_name, g2_name in pairs:
        pair_key = frozenset({g1_name, g2_name})
        is_known = pair_key in already_tested

        g1 = generators[g1_name]
        g2 = generators[g2_name]

        # Build alphabet: {0, +/-1, +/-g1, +/-g2, +/-conj(g1), +/-conj(g2)}
        candidates = [0, 1, -1, g1, -g1, g2, -g2]
        if isinstance(g1, complex) and g1.imag != 0:
            candidates.extend([g1.conjugate(), -g1.conjugate()])
        if isinstance(g2, complex) and g2.imag != 0:
            candidates.extend([g2.conjugate(), -g2.conjugate()])
        alphabet = _dedup_complex(candidates)

        n_trials = 20 if is_known else 50
        tag = " [KNOWN]" if is_known else ""

        print(f"\n{'='*60}")
        print(f"Pair: {g1_name} + {g2_name}{tag} ({len(alphabet)} elements)")
        print(f"{'='*60}")

        name = f"pair_{g1_name}+{g2_name}"
        use_comp = len(alphabet) <= 9
        result = test_alphabet(name, alphabet, use_completion=use_comp, n_trials=n_trials)

        results.append({
            'pair': f"{g1_name}+{g2_name}",
            'is_known': is_known,
            'alphabet_size': len(alphabet),
            'result': result,
        })

    return results


# ---------------------------------------------------------------------------
# Summary output
# ---------------------------------------------------------------------------

def print_summary_table(class_results, quartic_results, pair_results):
    """Print a formatted summary of all results."""
    print("\n" + "=" * 80)
    print("SUMMARY: KS CLASS NUMBER SURVEY")
    print("=" * 80)

    # Part 1: Class number fields
    print("\n--- Part 1: Imaginary Quadratic Fields (h > 1) ---")
    print(f"{'d':>4} {'h':>2} {'Ring':>20} {'|gen|^2':>8} {'New?':>5} "
          f"{'Basic':>8} {'Enriched':>10} {'MinKS':>6}")
    print("-" * 75)

    new_ks_found = []
    for r in class_results:
        basic_unc = r['basic'].get('uncol', False)
        enr = r.get('enriched')
        enr_unc = enr.get('uncol', False) if enr else False
        unc = basic_unc or enr_unc

        basic_str = "UNCOL" if basic_unc else "color"
        enr_str = "UNCOL" if enr_unc else ("color" if enr else "skip")
        min_ks = r['basic'].get('min_size') if basic_unc else (enr.get('min_size') if enr_unc else None)
        min_str = str(min_ks) if min_ks else "-"

        print(f"{r['d']:>4} {r['h']:>2} {r['ring_name']:>20} {r['norm_sq']:>8.2f} "
              f"{'YES' if r['is_new'] else 'no':>5} {basic_str:>8} {enr_str:>10} {min_str:>6}")

        if unc and r['is_new']:
            new_ks_found.append(r)

    # Part 2: Quartic fields
    print("\n--- Part 2: Quartic Fields ---")
    print(f"{'Field':>15} {'Basic':>8} {'Extended':>10} {'MinKS':>6}")
    print("-" * 45)
    for r in quartic_results:
        basic_unc = r['basic'].get('uncol', False)
        ext = r.get('extended')
        ext_unc = ext.get('uncol', False) if ext else False

        basic_str = "UNCOL" if basic_unc else "color"
        ext_str = "UNCOL" if ext_unc else ("color" if ext else "skip")
        min_ks = r['basic'].get('min_size') if basic_unc else (ext.get('min_size') if ext_unc else None)
        min_str = str(min_ks) if min_ks else "-"

        print(f"{r['field']:>15} {basic_str:>8} {ext_str:>10} {min_str:>6}")

        if (basic_unc or ext_unc):
            new_ks_found.append(r)

    # Part 3: Multi-generator pairs
    print("\n--- Part 3: Multi-Generator Pairs ---")
    print(f"{'Pair':>25} {'Known?':>7} {'AlphaSize':>10} {'Result':>8} {'MinKS':>6}")
    print("-" * 60)
    for r in pair_results:
        unc = r['result'].get('uncol', False)
        res_str = "UNCOL" if unc else "color"
        min_ks = r['result'].get('min_size')
        min_str = str(min_ks) if min_ks else "-"

        print(f"{r['pair']:>25} {'YES' if r['is_known'] else 'no':>7} "
              f"{r['alphabet_size']:>10} {res_str:>8} {min_str:>6}")

        if unc and not r['is_known']:
            new_ks_found.append(r)

    # Verdict
    print("\n" + "=" * 80)
    if new_ks_found:
        print(f"NEW KS SETS FOUND: {len(new_ks_found)}")
        for r in new_ks_found:
            if 'd' in r:
                print(f"  - d={r['d']}, h={r.get('h', '?')}")
            elif 'field' in r:
                print(f"  - {r['field']}")
            elif 'pair' in r:
                print(f"  - {r['pair']}")
        print("\nACTION: Manually verify SAT results and check against known island graphs!")
    else:
        print("NO NEW KS SETS FOUND")
        print("Two-mechanism thesis holds: all tested class-number > 1 fields are colorable.")
        print("This strengthens the evidence that KS sets require class-number-1 factorization.")
    print("=" * 80)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    random.seed(42)
    sys.stdout.reconfigure(encoding='utf-8')

    t0 = time.time()

    print("KS Class Number Survey")
    print("=" * 60)
    print("Testing class-number > 1 imaginary quadratic fields,")
    print("quartic fields, and multi-generator alphabets.")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Part 1: Class number > 1 fields
    print("\n" + "#" * 60)
    print("# PART 1: Imaginary Quadratic Fields with h > 1")
    print("#" * 60)
    class_results = survey_class_number_gt1()

    # Part 2: Quartic fields
    print("\n" + "#" * 60)
    print("# PART 2: Quartic Fields Q(d^{1/4})")
    print("#" * 60)
    quartic_results = survey_quartic_fields()

    # Part 3: Multi-generator pairs
    print("\n" + "#" * 60)
    print("# PART 3: Multi-Generator Pair Alphabets")
    print("#" * 60)
    pair_results = survey_multi_generator_pairs()

    # Summary
    print_summary_table(class_results, quartic_results, pair_results)

    elapsed = time.time() - t0
    print(f"\nTotal runtime: {elapsed/60:.1f} minutes")
