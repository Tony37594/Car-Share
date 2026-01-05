import streamlit as st
import pandas as pd
from streamlit_calendar import calendar

st.set_page_config(page_title="Car Calendar", page_icon="📅")

# --- CONFIG ---
SHEET_ID = "1Se6lXZLpgIarI_z4OXhHXgDdruDzjDYlwEhSg9LUYI8" 
SHEET_NAME = "bookings"
# Using the /export URL format for better stability
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet={SHEET_NAME}"

st.title("📅 Booking Calendar")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeLwzlfbmjG80888ZcoDjkGF-kIQmkINQGpdr2a6ckc6KSTXA/viewform?usp=header"

st.link_button("➕ Click Here to Book the Car", FORM_URL, use_container_width=True)
st.divider()

def load_bookings():
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.lower()
    return df

try:
    df = load_bookings()
    calendar_events = []
    
    # Map columns regardless of order or extra spaces
    cols = {col.lower().strip(): col for col in df.columns}
    name_key = next((v for k, v in cols.items() if 'name' in k), None)
    start_key = next((v for k, v in cols.items() if 'start' in k), None)
    end_key = next((v for k, v in cols.items() if 'end' in k), None)

    if name_key and start_key and end_key:
        for _, row in df.iterrows():
            if pd.notnull(row[name_key]) and pd.notnull(row[start_key]):
                try:
                    # NZ Friendly Date Parsing
                    start_dt = pd.to_datetime(row[start_key], dayfirst=True)
                    end_dt = pd.to_datetime(row[end_key], dayfirst=True)
                    
                    # Fix for single-day display
                    if start_dt == end_dt:
                        end_dt = end_dt + pd.Timedelta(days=1)

                    calendar_events.append({
                        "title": f"🚗 {row[name_key]}",
                        "start": start_dt.strftime('%Y-%m-%d'),
                        "end": end_dt.strftime('%Y-%m-%d'),
                    })
                except:
                    continue
        
        # --- THE MISSING PART ---
        calendar_options = {
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridMonth,listMonth",
            },
            "initialView": "dayGridMonth",
        }
        
        calendar(events=calendar_events, options=calendar_options)
    else:
        st.warning("Could not find the Name or Date columns. Please check your Form questions!")

except Exception as e:
    st.error("The app is having trouble reading the Google Sheet.")
    st.info("Check that your Google Sheet tab is named 'bookings' and is shared correctly.")
