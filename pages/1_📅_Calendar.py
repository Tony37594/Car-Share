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
            # Only add to calendar if the row isn't empty
            if pd.notnull(row[name_key]):
                calendar_events.append({
                    "title": f"🚗 {row[name_key]}",
                    "start": str(row[start_key]),
                    "end": str(row[end_key]),
                })
        
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
        st.warning("Could not find 'Name', 'Start', or 'End' columns in the sheet.")

except Exception as e:
    st.error("The calendar is having trouble reading the form data.")
    st.write(e)
