# ⚡ EOM RF Power Calculator

A little Streamlit tool to compute the RF drive power needed to reach a
target phase modulation depth on an electro-optic modulator.

Enter your target depth (β), modulation efficiency (η), and load impedance (Z₀)
— get back the required peak voltage and RF power in both W and dBm.

https://eom-rf-calc.streamlit.app/

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
