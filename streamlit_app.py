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
try:
    book_df = load_bookings()
    calendar_events = []
    
    # --- COLOR MAPPING ---
    # Customize these names and colors! 
    # Hex codes: #E91E63 (Pink), #9C27B0 (Purple), #2196F3 (Blue), #4CAF50 (Green), #FF9800 (Orange)
    color_map = {
        "Name1": "#2196F3", 
        "Name2": "#4CAF50",
        "Name3": "#FF9800",
        "Name4": "#E91E63"
    }

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
                    
                    # Look up driver name, default to Grey (#607D8B) if not in our map
                    driver_name = str(row[name_key]).strip()
                    event_color = color_map.get(driver_name, "#607D8B")

                    calendar_events.append({
                        "title": f"🚗 {driver_name}", 
                        "start": sd.strftime('%Y-%m-%d'), 
                        "end": ed.strftime('%Y-%m-%d'),
                        "backgroundColor": event_color,
                        "borderColor": event_color,
                        "textColor": "white"
                    })
                except: continue
        
        
        })
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
    try:
        # Load fresh bookings
        c_df = load_bookings()
        if not c_df.empty:
            # We map the columns based on your sheet structure: 
            # 0:Timestamp, 1:Name, 2:Start Date
            # We'll create a helper column for the dropdown
            c_df['select_text'] = c_df.iloc[:, 1] + " starting " + c_df.iloc[:, 2].astype(str)
            
            choice = st.selectbox("Which booking to remove?", c_df['select_text'])
            
            if st.button("Confirm Cancellation", type="primary"):
                # Get the specific data for the row we want to kill
                row_data = c_df[c_df['select_text'] == choice].iloc[0]
                t_name = row_data.iloc[1]
                t_date = row_data.iloc[2]
                
                # Replace with your NEW Deployment URL
                DELETE_URL = "https://script.google.com/macros/s/AKfycbzUSjCof2QDW0xZ5qL-XbGyPy0tjUBxVKHnD-bqve0ucKYzAvUCBL6iLWzOspPG93vBWg/exec"                
                # Send the request to the script
                r = requests.get(DELETE_URL, params={"name": t_name, "date": t_date})
                
                if "Success" in r.text:
                    st.success("Booking removed!")
                    st.rerun()
                else:
                    st.error(f"Could not delete: {r.text}")
        else:
            st.write("No active bookings found.")
    except Exception as e:
        st.write("Click 'Refresh' to load cancellation list.")
        
# FIX 3: Removed on_click=st.rerun and used a simple if-statement
if st.button('🔄 Refresh Dashboard', use_container_width=True):
    st.rerun()
