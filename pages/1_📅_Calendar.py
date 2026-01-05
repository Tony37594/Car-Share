import streamlit as st
import pandas as pd
from streamlit_calendar import calendar

st.set_page_config(page_title="Car Calendar", page_icon="📅")

# --- CONFIG ---
SHEET_ID = "1Se6lXZLpgIarI_z4OXhHXgDdruDzjDYlwEhSg9LUYI8" # Use the same ID as your main page
SHEET_NAME = "bookings"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

st.title("📅 Booking Calendar")
# Replace with your actual Google Form link
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
    
    # This part finds the right columns even if Google moved them
    cols = {col.lower().strip(): col for col in df.columns}
    
    # We look for the most likely names Google Forms gave your columns
    name_key = next((v for k, v in cols.items() if 'name' in k), None)
    start_key = next((v for k, v in cols.items() if 'start' in k), None)
    end_key = next((v for k, v in cols.items() if 'end' in k), None)

    if name_key and start_key and end_key:
        for _, row in df.iterrows():
            if pd.notnull(row[name_key]) and pd.notnull(row[start_key]):
                try:
                    # 'dayfirst=True' tells Python to prioritize the NZ format (DD/MM)
                    # but it's smart enough to fallback if the month is first
                    start_dt = pd.to_datetime(row[start_key], dayfirst=True)
                    end_dt = pd.to_datetime(row[end_key], dayfirst=True)
                    
                    # If the user put the same day for start and end, 
                    # we add 1 day so it actually shows up as a block on the calendar
                    if start_dt == end_dt:
                        end_dt = end_dt + pd.Timedelta(days=1)

                    calendar_events.append({
                        "title": f"🚗 {row[name_key]}",
                        "start": start_dt.strftime('%Y-%m-%d'),
                        "end": end_dt.strftime('%Y-%m-%d'),
                    })
                except Exception as e:
                    print(f"Date error: {e}")
                    continue
