import streamlit as st
import sympy as sp

# ============================================================
#  Page config
# ============================================================
st.set_page_config(page_title="EOM RF Power Calculator",
                   page_icon="⚡", layout="wide")

# ============================================================
#  Symbolic backend
# ============================================================
beta, eta, Z0, Vp, P, P_dBm = sp.symbols(
    'beta eta Z_0 V_p P P_dBm', positive=True
)

# Core textbook equations (bare symbols -> clean display form)
Vp_eq    = sp.Eq(Vp,    beta / (eta / 1000))                       # Vp    = 1000*beta/eta
P_eq     = sp.Eq(P,     Vp**2 / (2 * Z0))                          # P     = Vp^2/(2*Z0)
P_dBm_eq = sp.Eq(P_dBm, 10 * sp.log(P / sp.Rational(1, 1000), 10)) # P_dBm = 10*log10(P/1mW)

# Master expressions, resolved once (runtime is a single flat .subs)
expr_Vp    = Vp_eq.rhs
expr_P     = P_eq.rhs.subs(Vp, expr_Vp)
expr_P_dBm = P_dBm_eq.rhs.subs(P, expr_P)

# ============================================================
#  Sidebar inputs  (round, generic placeholder defaults)
# ============================================================
st.sidebar.header("⚙️ Inputs")
target_beta = st.sidebar.number_input("Target modulation depth  β  [rad]",
                                       min_value=0.001, value=1.0, step=0.1, format="%.2f")
efficiency  = st.sidebar.number_input("Modulation efficiency  η  [mrad/Vp]",
                                       min_value=0.01, value=50.0, step=1.0, format="%.2f")
Z0_load     = st.sidebar.number_input("Load impedance  Z₀  [Ω]",
                                       min_value=0.01, value=50.0, step=1.0, format="%.2f")

# ============================================================
#  Evaluate (single flat substitution)
# ============================================================
nums = {beta: target_beta, eta: efficiency, Z0: Z0_load}
Vp_val    = float(expr_Vp.subs(nums))
P_val     = float(expr_P.subs(nums))
P_dBm_val = float(expr_P_dBm.subs(nums))

# ============================================================
#  Output
# ============================================================
st.title("⚡ EOM RF Power Calculator")
st.write(
    "A little tool I hacked together to figure out the **RF drive power** "
    "needed to hit a target phase **modulation depth** on an electro-optic "
    "modulator. Punch your numbers into the sidebar. 🙂"
)

st.subheader("Results")
c1, c2, c3 = st.columns(3)
c1.metric("Peak voltage", f"{Vp_val:.2f} V", delta=f"{2*Vp_val:.2f} Vpp")
c2.metric("RF power",     f"{P_dBm_val:.2f} dBm")
c3.metric("RF power",     f"{P_val:.2f} W")

# ============================================================
#  Equations used (clean, hand-written dBm LaTeX)
# ============================================================
with st.expander("Show the math"):
    st.latex(sp.latex(Vp_eq))   # V_p = 1000*beta/eta  -> clean from SymPy
    st.latex(sp.latex(P_eq))    # P   = V_p^2/(2*Z_0)  -> clean from SymPy
    st.latex(r"P_{dBm} = 10\,\log_{10}\!\left(\frac{P}{1\,\text{mW}}\right)")
    st.markdown(
        "- **β** — target phase modulation index [rad]\n"
        "- **η** — modulation efficiency [mrad/Vp]\n"
        "- **Z₀** — load impedance [Ω]\n"
        "- dBm referenced to 1 mW (0 dBm = 1 mW, 30 dBm = 1 W)"
    )

st.divider()
st.caption("Built for fun with Python, SymPy & Streamlit. Use at your own risk! 🔧")
