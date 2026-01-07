import streamlit as st
import pandas as pd
from streamlit_calendar import calendar

st.set_page_config(page_title="AKL Car Share", page_icon="🚗")

# --- CONFIG ---
SHEET_ID = "1Se6lXZLpgIarI_z4OXhHXgDdruDzjDYlwEhSg9LUYI8"
# gid=0 is usually the first tab (log), sheet=bookings is the other
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
BOOKING_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet=bookings"

st.title("🚗 Auckland Car Share")

# --- 1. CURRENT STATUS SECTION ---
def load_log():
    # Adding timestamp to force refresh and avoid 'old' data
    df = pd.read_csv(f"{LOG_URL}&cache={pd.Timestamp.now().timestamp()}")
    df.columns = df.columns.str.strip().str.lower()
    return df

try:
    log_df = load_log()
    if not log_df.empty:
        latest = log_df.iloc[-1]
        
        # Big, clear location header
        st.success(f"### 📍 Current Location: {latest.get('location', 'Unknown')}")
        
        col1, col2 = st.columns(2)
        col1.write(f"**Last Driver:** {latest.get('driver', 'Unknown')}")
        
        # Check if there is a note, and display it if so
        note = latest.get('notes')
        if pd.notnull(note) and str(note).strip() != "":
            st.info(f"**Note:** {note}")
except:
    st.warning("Update the log in the Google Sheet to see current car status.")

st.divider()

# --- 2. BOOKING BUTTON ---
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeLwzlfbmjG80888ZcoDjkGF-kIQmkINQGpdr2a6ckc6KSTXA/viewform?usp=header"
st.link_button("➕ Book the Car", FORM_URL, use_container_width=True)

# --- 3. CALENDAR SECTION ---
def load_bookings():
    df = pd.read_csv(BOOKING_URL)
    df.columns = df.columns.str.strip().str.lower()
    return df

try:
    book_df = load_bookings()
    calendar_events = []
    
    # Map columns for Calendar
    cols = {col.lower().strip(): col for col in book_df.columns}
    name_key = next((v for k, v in cols.items() if 'name' in k), None)
    start_key = next((v for k, v in cols.items() if 'start' in k), None)
    end_key = next((v for k, v in cols.items() if 'end' in k), None)

    if name_key and start_key and end_key:
        for _, row in book_df.iterrows():
            if pd.notnull(row[name_key]) and pd.notnull(row[start_key]):
                try:
                    start_dt = pd.to_datetime(row[start_key], dayfirst=True)
                    end_dt = pd.to_datetime(row[end_key], dayfirst=True)
                    if start_dt == end_dt:
                        end_dt = end_dt + pd.Timedelta(days=1)
                    
                    calendar_events.append({
                        "title": f"🚗 {row[name_key]}",
                        "start": start_dt.strftime('%Y-%m-%d'),
                        "end": end_dt.strftime('%Y-%m-%d'),
                    })
                except: continue

        calendar_options = {
            "headerToolbar": {"left": "prev,next", "center": "title", "right": ""},
            "initialView": "dayGridMonth",
            "height": 450,
        }
        calendar(events=calendar_events, options=calendar_options)
except:
    st.error("Calendar could not load.")

st.button('🔄 Refresh Dashboard', on_click=st.rerun, use_container_width=True)
