import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Car Admin", page_icon="🔧")

# --- CONFIG & LINKS ---
SHEET_ID = "1Se6lXZLpgIarI_z4OXhHXgDdruDzjDYlwEhSg9LUYI8"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1228530864"

# --- TARGETS (Update these manually) ---
service_due_km = 164000
ruc_max_km = 158000
wof_expiry = "2026-08-26"
rego_expiry = "2026-04-28"

# --- DATA LOADING ---
def get_latest_mileage():
    try:
        # Cache busting to get the freshest data
        df = pd.read_csv(f"{LOG_URL}&cache={pd.Timestamp.now().timestamp()}")
        df.columns = df.columns.str.strip().str.lower()
        # Find the mileage column (usually 'mileage' or 'loc')
        loc_col = next((c for c in df.columns if 'loc' in c or 'mile' in c), None)
        return int(df.iloc[-1][loc_col])
    except:
        return 0

current_km = get_latest_mileage()
today = datetime.now().date()
wof_dt = datetime.strptime(wof_expiry, "%Y-%m-%d").date()
rego_dt = datetime.strptime(rego_expiry, "%Y-%m-%d").date()

# --- DISPLAY ---
st.title("🔧 Car Maintenance & Admin")
st.metric("Current Odometer", f"{current_km:,} km")

col1, col2 = st.columns(2)

with col1:
    # WOF Logic
    if wof_dt < today:
        st.error(f"⚠️ **WOF EXPIRED**\n\n{wof_dt.strftime('%d %b %Y')}")
    else:
        st.success(f"✅ **WOF Valid**\n\nExpires: {wof_dt.strftime('%d %b %Y')}")

with col2:
    # Rego Logic
    if rego_dt < today:
        st.error(f"⚠️ **REGO EXPIRED**\n\n{rego_dt.strftime('%d %b %Y')}")
    else:
        st.success(f"✅ **REGO Valid**\n\nExpires: {rego_dt.strftime('%d %b %Y')}")

st.divider()

# --- DYNAMIC WARNINGS ---

# 1. Road User Charges (RUC)
if current_km >= ruc_max_km:
    st.error(f"🚨 **ROAD USERS EXCEEDED!**\n\nPlease buy more RUCs. Limit was {ruc_max_km:,} km.")
elif (ruc_max_km - current_km) < 500:
    st.warning(f"⛽ **RUC Warning:** Only {ruc_max_km - current_km} km remaining!")
else:
    st.info(f"🛣️ **RUC Current:** {ruc_max_km - current_km:,} km remaining.")

# 2. Service Logic
if current_km >= service_due_km:
    st.error(f"🛠️ **SERVICE OVERDUE**\n\nBook service now (Target: {service_due_km:,} km)")
else:
    st.info(f"📅 **Next Service:** Due in {service_due_km - current_km:,} km")

with st.expander("📝 Car Specs & Notes"):
    st.write("**Tire Pressure:** 32 PSI")
    st.write("**Oil Type:** 5W-30 Synthetic")
