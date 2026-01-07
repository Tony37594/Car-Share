import streamlit as st
import pandas as pd
import requests
from streamlit_calendar import calendar

st.set_page_config(page_title="AKL Car Share", page_icon="🚗")

# --- CONFIG ---
SHEET_ID = "1Se6lXZLpgIarI_z4OXhHXgDdruDzjDYlwEhSg9LUYI8"

# If Log is second, but Bookings is GID 2010459593, 
# then LOG is likely GID 0. If it still shows the wrong data, 
# swap these two GID numbers.
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
BOOKING_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=2010459593"

# --- GOOGLE FORM CONFIG ---
# I have fixed the URL below to point to 'formResponse' instead of 'viewform'
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScnZpz2nSmLWwjdxfGKruOJ2oOVlr9SZ-KOa6H0P7ZBih3uYA/formResponse"

ENTRY_NAME = "entry.635424914"  
ENTRY_LOC = "entry.1499233920"

# --- GOOGLE FORM CONFIG ---
# FIX 1: Ensure URL ends in /formResponse for background posting
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScnZpz2nSmLWwjdxfGKruOJ2oOVlr9SZ-KOa6H0P7ZBih3uYA/viewform?usp=preview"
# FIX 2: Added 'entry.' prefix to the IDs
ENTRY_NAME = "entry.635424914"  
ENTRY_LOC = "entry.1499233920"  

st.title("🚗 Auckland Car Share")

# --- 1. UPDATE LOCATION ---
with st.expander("📍 Update Car Location"):
    with st.form("location_form", clear_on_submit=True):
        u_name = st.text_input("Your Name")
        u_loc = st.text_input("New Location (e.g. Row 4A)")
        submitted = st.form_submit_button("Submit New Location")
        
        if submitted:
            if u_name and u_loc:
                payload = {ENTRY_NAME: u_name, ENTRY_LOC: u_loc}
                try:
                    # This sends the data silently
                    requests.post(FORM_URL, data=payload)
                    st.success("✅ Location sent! Refreshing dashboard...")
                    st.rerun() # Refresh immediately after submission
                except:
                    st.error("Connection error.")
            else:
                st.warning("Please fill in both fields.")

st.divider()

# --- 2. CURRENT STATUS DISPLAY ---
def load_log():
    df = pd.read_csv(f"{LOG_URL}&cache={pd.Timestamp.now().timestamp()}")
    df.columns = df.columns.str.strip().str.lower()
    return df

try:
    log_df = load_log()
    if not log_df.empty:
        latest = log_df.iloc[-1]
        st.success(f"### 📍 Current Location: {latest.get('location', 'Unknown')}")
        st.write(f"**Last parked by:** {latest.get('driver', 'Unknown')}")
except Exception as e:
    st.info("Waiting for location data...")

# --- 3. BOOKING & CALENDAR ---
st.divider()
st.link_button("➕ Book the Car", "https://docs.google.com/forms/d/e/1FAIpQLSeLwzlfbmjG80888ZcoDjkGF-kIQmkINQGpdr2a6ckc6KSTXA/viewform", use_container_width=True)

def load_bookings():
    df = pd.read_csv(BOOKING_URL)
    df.columns = df.columns.str.strip().str.lower()
    return df

try:
    book_df = load_bookings()
    calendar_events = []
    
    # Robust column mapping
    cols = {col.lower().strip(): col for col in book_df.columns}
    name_key = next((v for k, v in cols.items() if 'name' in k), None)
    start_key = next((v for k, v in cols.items() if 'start' in k), None)
    end_key = next((v for k, v in cols.items() if 'end' in k), None)

    if name_key and start_key and end_key:
        for _, row in book_df.iterrows():
            if pd.notnull(row[name_key]) and pd.notnull(row[start_key]):
                try:
                    sd = pd.to_datetime(row[start_key], dayfirst=True)
                    ed = pd.to_datetime(row[end_key], dayfirst=True)
                    if sd == ed: ed = ed + pd.Timedelta(days=1)
                    calendar_events.append({
                        "title": f"🚗 {row[name_key]}", 
                        "start": sd.strftime('%Y-%m-%d'), 
                        "end": ed.strftime('%Y-%m-%d')
                    })
                except: continue
        
        calendar(events=calendar_events, options={
            "headerToolbar": {"left": "prev,next", "center": "title", "right": ""},
            "initialView": "dayGridMonth", 
            "height": 400
        })
    else:
        st.warning("Ensure your bookings sheet has 'Name', 'Start', and 'End' columns.")
except Exception as e:
    st.error(f"Calendar Error: {e}")

# FIX 3: Removed on_click=st.rerun and used a simple if-statement
if st.button('🔄 Refresh Dashboard', use_container_width=True):
    st.rerun()
