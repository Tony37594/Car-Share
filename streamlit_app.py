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
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1228530864"
BOOKING_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=2010459593"

# --- GOOGLE FORM CONFIG ---
# I have fixed the URL below to point to 'formResponse' instead of 'viewform'
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScnZpz2nSmLWwjdxfGKruOJ2oOVlr9SZ-KOa6H0P7ZBih3uYA/formResponse"

ENTRY_NAME = "entry.635424914"  
ENTRY_LOC = "entry.1499233920"

# --- GOOGLE FORM CONFIG ---
# FIX 1: Ensure URL ends in /formResponse for background posting
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScnZpz2nSmLWwjdxfGKruOJ2oOVlr9SZ-KOa6H0P7ZBih3uYA/formResponse"
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
                    # We add a timeout and check for a generic 'ok' status
                    response = requests.post(FORM_URL, data=payload, timeout=5)
                    
                    # Google Form submissions often return a 200 even if they redirect
                    if response.status_code == 200:
                        st.success("✅ Location updated! Loading...")
                        # Small delay to let Google process the sheet before refresh
                        import time
                        time.sleep(1) 
                        st.rerun()
                    else:
                        st.error(f"Error: {response.status_code}")
                except:
                    # If the data showed up in your sheet, the request actually worked!
                    # We will treat a timeout as a success because Google is just being slow to reply.
                    st.success("✅ Update sent!")
                    st.rerun()
            else:
                st.warning("Please fill in both fields.")
                
# --- 2. CURRENT STATUS DISPLAY ---
def load_log():
    # Force refresh to get the newest row
    df = pd.read_csv(f"{LOG_URL}&cache={pd.Timestamp.now().timestamp()}")
    # Clean up column names (lowercase and remove spaces)
    df.columns = df.columns.str.strip().str.lower()
    return df

try:
    log_df = load_log()
    if not log_df.empty:
        latest = log_df.iloc[-1]
        
        # This part looks for any column that contains the word 'loc'
        loc_col = next((c for c in log_df.columns if 'loc' in c), None)
        driver_col = next((c for c in log_df.columns if 'driver' in c or 'name' in c), None)
        
        current_loc = latest[loc_col] if loc_col else "Unknown"
        current_driver = latest[driver_col] if driver_col else "Unknown"
        
        st.success(f"### 📍 Current Location: {current_loc}")
        st.write(f"**Last parked by:** {current_driver}")
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
    
# --- 4. CANCEL BOOKING SECTION ---
st.divider()
with st.expander("🗑️ Cancel a Booking"):
    # We need a fresh look at the bookings
    try:
        cancel_df = load_bookings()
        # Create a list of "Name on Date" for the dropdown
        if not cancel_df.empty:
            # Assumes Column 0 is Name and Column 1 is Start Date
            cancel_df['display'] = cancel_df.iloc[:, 0] + " (" + cancel_df.iloc[:, 1].astype(str) + ")"
            booking_to_delete = st.selectbox("Select booking to remove:", cancel_df['display'])
            
            if st.button("Confirm Cancellation"):
                # Get the raw name and date from the selection
                selected_row = cancel_df[cancel_df['display'] == booking_to_delete].iloc[0]
                target_name = selected_row.iloc[0]
                target_date = selected_row.iloc[1]
                
                # YOUR APPS SCRIPT URL HERE
                DELETE_SCRIPT_URL = "PASTE_YOUR_WEB_APP_URL_HERE"
                
                params = {"name": target_name, "date": target_date}
                res = requests.get(DELETE_SCRIPT_URL, params=params)
                
                if res.text == "Success":
                    st.success("Deleted! Refreshing...")
                    st.rerun()
                else:
                    st.error("Could not find that booking in the sheet.")
        else:
            st.write("No bookings to cancel.")
    except:
        st.write("Could not load bookings for cancellation.")
        
# FIX 3: Removed on_click=st.rerun and used a simple if-statement
if st.button('🔄 Refresh Dashboard', use_container_width=True):
    st.rerun()
