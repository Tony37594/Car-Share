import streamlit as st
import pandas as pd
import requests
from streamlit_calendar import calendar
import time

st.set_page_config(page_title="AKL Car Share", page_icon="🚗")

# --- CONFIG ---
SHEET_ID = "1Se6lXZLpgIarI_z4OXhHXgDdruDzjDYlwEhSg9LUYI8"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1228530864"
BOOKING_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=2010459593"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScnZpz2nSmLWwjdxfGKruOJ2oOVlr9SZ-KOa6H0P7ZBih3uYA/formResponse"

ENTRY_NAME = "entry.635424914"  
ENTRY_LOC = "entry.1499233920" 

st.markdown("<h1 style='text-align: center;'>🚗 Dad's Car Share</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Parked at Flyaway 0800 77 66 99</h4>", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import requests
from streamlit_calendar import calendar
import time

st.set_page_config(page_title="AKL Car Share", page_icon="🚗")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    /* Target only the Submit Button inside the form */
    div.stButton > button:first-child {
        background-color: #d4edda !important; /* Light green background */
        color: #155724 !important;           /* Dark green text */
        border: 2px solid #c3e6cb !important; /* Success-style border */
        border-radius: 10px !important;
        height: 3.5em !important;             /* Makes it slightly bigger */
        width: 100% !important;
        font-weight: bold !important;
        font-size: 20px !important;           /* FIXED: changed !format to !important */
    }
    /* Hover effect */
    div.stButton > button:first-child:hover {
        background-color: #c3e6cb !important;
        border-color: #b1dfbb !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADINGS ---
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>🚗 Dad's Car Share</h1>", unsafe_allow_html=True)
# This makes the Flyaway text smaller and grey
st.markdown("<p style='text-align: center; color: gray; font-size: 16px; margin-top: 0px;'>Parked at Flyaway 0800 77 66 99</p>", unsafe_allow_html=True)

# ... [The rest of your code stays the same] ...

# --- 1. UPDATE MILEAGE (Revised for size) ---
with st.expander("📍 Update Car Mileage"):
    with st.form("location_form", clear_on_submit=True):
        u_name = st.text_input("Your Name")
        u_loc = st.text_input("Mileage at Dropoff")
        
        # We use a standard submit button, but our CSS above will 'catch' it
        submitted = st.form_submit_button("Submit New Mileage")
        
        if submitted:
            # ... (your existing logic for payload and requests) ...
            if u_name and u_loc:
                payload = {ENTRY_NAME: u_name, ENTRY_LOC: u_loc}
                try:
                    response = requests.post(FORM_URL, data=payload, timeout=5)
                    if response.status_code == 200:
                        st.success("✅ Mileage updated!")
                        time.sleep(1)
                        st.rerun()
                except:
                    st.success("✅ Update sent!")
                    st.rerun()
                    
# --- 2. CURRENT STATUS DISPLAY ---
def load_log():
    df = pd.read_csv(f"{LOG_URL}&cache={pd.Timestamp.now().timestamp()}")
    df.columns = df.columns.str.strip().str.lower()
    return df

try:
    log_df = load_log()
    if not log_df.empty:
        latest = log_df.iloc[-1]
        loc_col = next((c for c in log_df.columns if 'loc' in c), None)
        driver_col = next((c for c in log_df.columns if 'driver' in c or 'name' in c), None)
        current_loc = latest[loc_col] if loc_col else "Unknown"
        current_driver = latest[driver_col] if driver_col else "Unknown"
        st.success(f"### 📍Mileage: {current_loc}")
        st.write(f"**Last parked by:** {current_driver}")
except Exception as e:
    st.info("Waiting for location data...")

# --- 3. BOOKING & CALENDAR ---
st.divider()
st.link_button("➕ Book the Car", "https://docs.google.com/forms/d/e/1FAIpQLSeLwzlfbmjG80888ZcoDjkGF-kIQmkINQGpdr2a6ckc6KSTXA/viewform", use_container_width=True)

def load_bookings():
    df = pd.read_csv(f"{BOOKING_URL}&cache={pd.Timestamp.now().timestamp()}")
    df.columns = df.columns.str.strip().str.lower()
    return df

try:
    book_df = load_bookings()
    calendar_events = []
    
    # --- COLOR MAPPING ---
    color_map = {
        "Tony": "#2196F3", 
        "Sue": "#B66DFF",
        "Grant": "#107C10",
        "Paid": "#FFC1CB",
        "Dwight": "#FFD86C",
        "Bryce": "#D82C20",
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
        
        calendar(events=calendar_events, options={
            "headerToolbar": {"left": "prev,next", "center": "title", "right": ""},
            "initialView": "dayGridMonth", 
            "height": 400,
            "firstDay": 1
        })
except Exception as e:
    st.error(f"Calendar Error: {e}")

# --- 4. CANCEL BOOKING SECTION ---
st.divider()
with st.expander("🗑️ Cancel a Booking"):
    try:
        c_df = load_bookings()
        if not c_df.empty:
            c_df['select_text'] = c_df.iloc[:, 1].astype(str) + " starting " + c_df.iloc[:, 2].astype(str)
            choice = st.selectbox("Which booking to remove?", c_df['select_text'])
            
            if st.button("Confirm Cancellation", type="primary"):
                row_data = c_df[c_df['select_text'] == choice].iloc[0]
                t_name = row_data.iloc[1]
                t_date = row_data.iloc[2]
                
                DELETE_URL = "https://script.google.com/macros/s/AKfycbzUSjCof2QDW0xZ5qL-XbGyPy0tjUBxVKHnD-bqve0ucKYzAvUCBL6iLWzOspPG93vBWg/exec"                
                r = requests.get(DELETE_URL, params={"name": t_name, "date": t_date})
                
                if "Success" in r.text:
                    st.success("Booking removed!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Could not delete: {r.text}")
        else:
            st.write("No active bookings found.")
    except Exception as e:
        st.write("Problem loading bookings.")

if st.button('🔄 Refresh Dashboard', use_container_width=True):
    st.rerun()
