import streamlit as st
import sympy as sp

# ============================================================
#  Page config
# ============================================================
st.set_page_config(page_title="EOM RF Power Calculator",
                   page_icon=None, layout="wide")

# ============================================================
#  Symbolic backend
# ============================================================
beta, eta, Z0, Vp, P, P_dBm = sp.symbols(
    'beta eta Z_0 V_p P P_dBm', positive=True
)

Vp_eq    = sp.Eq(Vp,    beta / (eta / 1000))
P_eq     = sp.Eq(P,     Vp**2 / (2 * Z0))
P_dBm_eq = sp.Eq(P_dBm, 10 * sp.log(P / sp.Rational(1, 1000), 10))

expr_Vp    = Vp_eq.rhs
expr_P     = P_eq.rhs.subs(Vp, expr_Vp)
expr_P_dBm = P_dBm_eq.rhs.subs(P, expr_P)

# ============================================================
#  Sidebar inputs
# ============================================================
st.sidebar.header("Parameters")
target_beta = st.sidebar.number_input("Target modulation depth  β  [rad]",
                                       min_value=0.001, value=1.0, step=0.1, format="%.3f")
efficiency  = st.sidebar.number_input("Modulation efficiency  η  [mrad/Vp]",
                                       min_value=0.01, value=50.0, step=1.0, format="%.2f")
Z0_load     = st.sidebar.number_input("Load impedance  Z₀  [Ω]",
                                       min_value=0.01, value=50.0, step=1.0, format="%.2f")

# (#3) Optional precision control
decimals = st.sidebar.select_slider("Output decimals", options=[2, 3, 4], value=2)

# ============================================================
#  Evaluate (with #7 error handling)
# ============================================================
try:
    nums = {beta: target_beta, eta: efficiency, Z0: Z0_load}
    Vp_val    = float(expr_Vp.subs(nums))
    P_val     = float(expr_P.subs(nums))
    P_dBm_val = float(expr_P_dBm.subs(nums))
    ok = True
except Exception as e:                                  # noqa: BLE001
    ok = False
    st.error(f"Could not evaluate with these inputs: {e}")

# ============================================================
#  Output
# ============================================================
st.title("EOM RF Power Calculator")
st.write(
    "Calculate the RF drive power required to achieve a target phase "
    "modulation depth on an electro-optic modulator. "
    "Enter the relevant parameters in the sidebar."
)

if ok:
    st.subheader("Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Peak Voltage", f"{Vp_val:.{decimals}f} V")
    c2.metric("Drive Power", f"{P_dBm_val:.{decimals}f} dBm")
    c3.metric("Drive Power", f"{P_val:.{decimals}f} W")

    # (#1) Lightweight, physically-motivated range warnings
    if P_dBm_val > 50:
        st.warning(
            f"Required power is **{P_dBm_val:.1f} dBm** "
            f"(≈ {P_val:.1f} W). This exceeds the output of most benchtop "
            "RF amplifiers (typically ≤ ~50 dBm) and may risk damaging the "
            "modulator — verify against your device and amplifier limits."
        )
    if efficiency < 1.0:
        st.info(
            "η below ~1 mrad/Vp is unusually low for a typical phase EOM — "
            "double-check the value and its units (mrad/Vp)."
        )
    if not (1.0 <= Z0_load <= 1000.0):
        st.info("Z₀ is outside the usual 1–1000 Ω range (50 Ω is standard for RF).")

# ============================================================
#  Equations + (#5) assumptions / model validity
# ============================================================
with st.expander("Equations & assumptions"):
    st.latex(sp.latex(Vp_eq))
    st.latex(sp.latex(P_eq))
    st.latex(r"P_{dBm} = 10\,\log_{10}\!\left(\frac{P}{1\,\text{mW}}\right)")
    st.markdown(
        "- **β** — target phase modulation index [rad]\n"
        "- **η** — modulation efficiency [mrad/Vp], at the peak drive voltage\n"
        "- **Z₀** — load impedance [Ω]\n"
        "- Drive power assumes a sinusoidal signal: "
        r"$P = V_p^2 / (2 Z_0)$, with $V_{rms} = V_p/\sqrt{2}$." "\n"
        "- dBm referenced to 1 mW (0 dBm = 1 mW, 30 dBm = 1 W)"
    )
    st.markdown("**Model assumptions / limitations**")
    st.markdown(
        "- Assumes a **linear, lossless, impedance-matched** drive — no "
        "cable/connector insertion loss or amplifier saturation included.\n"
        "- **η is treated as a single constant**, but real modulators show "
        "**wavelength and frequency dependence** (efficiency typically rolls "
        "off with increasing RF frequency). Use the η value appropriate for "
        "your operating wavelength and drive frequency.\n"
        "- Valid in the **small-to-moderate modulation** regime; very large β "
        "may involve effects this simple model omits."
    )

st.divider()
st.caption("🛠️ Code's open on GitHub if you want to peek under the hood or build "
           "on it: https://github.com/sterafix/eom-rf-calc")