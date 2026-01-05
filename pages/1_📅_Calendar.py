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
    
    # Format the data for the Calendar component
    calendar_events = []
    for _, row in df.iterrows():
        calendar_events.append({
            "title": f"🚗 {row['name']}",
            "start": str(row['start date']),
            "end": str(row['end date']),
            "notes": str(row['notes'])
        })

    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,listMonth",
        },
        "initialView": "dayGridMonth",
    }

    # Display the Calendar
    calendar(events=calendar_events, options=calendar_options)

    st.divider()
    st.info("To add a booking, simply add a row to the 'bookings' tab in your Google Sheet.")

except Exception as e:
    st.error("Make sure your 'bookings' tab exists and has 'Start Date', 'End Date', and 'Name' columns.")
    st.write(e)
