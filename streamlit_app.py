import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="AKL Car Share", page_icon="🚗")

# --- CONFIG ---
SHEET_ID = "1Se6lXZLpgIarI_z4OXhHXgDdruDzjDYlwEhSg9LUYI8"
SHEET_NAME = "log" 
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet={SHEET_NAME}"

# --- GOOGLE FORM BACKEND (UPDATE THESE!) ---
# Replace the ID below with the ID from your Form URL
FORM_URL = "https://docs.google.com/forms/d/e/YOUR_FORM_ID_HERE/formResponse"
ENTRY_IDS = {
    "driver": "entry.11111", # Replace with your actual entry IDs
    "location": "entry.22222",
    "fuel": "entry.33333",
    "notes": "entry.44444"
}

st.title("🚗 Auckland Car Share")

# --- UPDATE SECTION ---
with st.expander("📍 Update Car Location / Fuel", expanded=False):
    with st.form("status_form", clear_on_submit=True):
        u_driver = st.text_input("Driver Name")
        u_loc = st.text_input("Parking Spot (e.g. Row 4A)")
        u_fuel = st.select_slider("Fuel Level %", options=["0", "25", "50", "75", "100"], value="100")
        u_notes = st.text_input("Notes (Optional)")
        
        submitted = st.form_submit_button("Submit Update")
        
        if submitted:
            if u_driver and u_loc:
                # This sends the data to your Google Sheet
                payload = {
                    ENTRY_IDS["driver"]: u_driver,
                    ENTRY_IDS["location"]: u_loc,
                    ENTRY_IDS["fuel"]: u_fuel,
                    ENTRY_IDS["notes"]: u_notes
                }
                try:
                    requests.post(FORM_URL, data=payload)
                    st.success("✅ Update sent! Wait 5 seconds then hit Refresh.")
                except:
                    st.error("Failed to send. Check your internet connection.")
            else:
                st.warning("Please enter your name and location.")

st.divider()

# --- DISPLAY SECTION ---
st.markdown("### 📍 Current Status")

def load_data():
    # Adding a random number to the URL prevents the browser from showing 'old' cached data
    df = pd.read_csv(f"{url}&cache_bust={pd.Timestamp.now().timestamp()}")
    df.columns = df.columns.str.strip().str.lower()
    return df

try:
    df = load_data()
    if not df.empty:
        latest = df.iloc[-1]
        
        # Use .get() to avoid errors if columns aren't named perfectly
        st.info(f"Last updated by **{latest.get('driver', 'Unknown')}**")
        
        col1, col2 = st.columns(2)
        col1.metric("Location", latest.get('location', 'Unknown'))
        # Ensure fuel is shown correctly
        fuel_val = latest.get('fuel', 'Unknown')
        col2.metric("Fuel Level", f"{fuel_val}%" if str(fuel_val).isdigit() else fuel_val)
        
        if pd.notnull(latest.get('notes')) and str(latest.get('notes')).strip() != "":
            st.warning(f"**Note:** {latest.get('notes')}")
            
except Exception as e:
    st.error("Could not load current status.")

if st.button('🔄 Refresh Dashboard'):
    st.rerun()
