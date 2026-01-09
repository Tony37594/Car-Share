import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Car Admin", page_icon="🔧")

st.title("🔧 Car Maintenance & Admin")

# --- CONFIG DATA ---
service_due_km = 154000
wof_expiry = "2026-08-26"
rego_expiry = "2026-04-28"
ruc_max_km = 158000  # Changed name (no spaces) and made it a number

# --- CALCULATION LOGIC ---
today = datetime.now().date()
wof_dt = datetime.strptime(wof_expiry, "%Y-%m-%d").date()
rego_dt = datetime.strptime(rego_expiry, "%Y-%m-%d").date()

# Note: For Road Users, we'd eventually pull the "Current Mileage" 
# from your main sheet. For now, let's assume a placeholder:
current_km_placeholder = 155000 

# --- DISPLAY SECTION ---
col1, col2 = st.columns(2)

with col1:
    # WOF Display
    if wof_dt < today:
        st.error(f"⚠️ **WOF EXPIRED**\n\n{wof_dt.strftime('%d %b %Y')}")
    else:
        st.success(f"✅ **WOF Valid**\n\nExpires: {wof_dt.strftime('%d %b %Y')}")

with col2:
    # Rego Display
    if rego_dt < today:
        st.error(f"⚠️ **REGO EXPIRED**\n\n{rego_dt.strftime('%d %b %Y')}")
    else:
        st.success(f"✅ **REGO Valid**\n\nExpires: {rego_dt.strftime('%d %b %Y')}")

# Add a third box for RUCs
st.divider()
if current_km_placeholder > ruc_max_km:
    st.error(f"⛽ **ROAD USERS EXCEEDED!**\n\nMax: {ruc_max_km:,} km")
else:
    st.info(f"🛣️ **Road Users (RUC)**\n\nCurrent limit: {ruc_max_km:,} km")

# Service Tracker
st.warning(f"🔧 **Next Service Due:** {service_due_km:,} km")

# Optional: Add a place for tire pressure or oil type
with st.expander("📝 Car Specs"):
    st.write("**Tire Pressure:** 32 PSI (Cold)")
    st.write("**Oil Type:** 5W-30 Synthetic")
