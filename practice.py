import streamlit as st
import pandas as pd
import requests
from streamlit_calendar import calendar
import time

st.markdown("<h1 style='text-align: center;'>🚧 PRACTICE ZONE</h1>", unsafe_allow_html=True)

# 1. PAGE SETUP
st.set_page_config(page_title="Dad's Car Share", page_icon="🚗")

# 2. CONFIGURATION & LINKS
SHEET_ID = "1Se6lXZLpgIarI_z4OXhHXgDdruDzjDYlwEhSg9LUYI8"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1228530864"
BOOKING_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=2010459593"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScnZpz2nSmLWwjdxfGKruOJ2oOVlr9SZ-KOa6H0P7ZBih3uYA/formResponse"

# Google Form Entry IDs
ENTRY_NAME = "entry.635424914"  
ENTRY_LOC = "entry.1499233920" 

# 3. CUSTOM STYLING (CSS)

/* Style the Expander Header */
    .streamlit-expanderHeader {
        background-color: #f8f9fa !important; /* Soft grey background */
        border: 1px solid #dee2e6 !important;
        border-radius: 10px !important;
        padding: 15px !important;            /* Makes it taller */
    }

    /* Style the text inside the Expander Header */
    .streamlit-expanderHeader p {
        font-size: 24px !important;          /* Bigger text */
        font-weight: bold !important;
        color: #155724 !important;           /* Dark green text */
    }
st.markdown("""
    <style>
    /* Targeted 'Big Button' Style */
    div[data-testid="stForm"] button {
        background-color: #FEB5DA !important; 
        color: #155724 !important;           
        border: 2px solid #FEB5DA !important; 
        border-radius: 10px !important;      /* More rounded corners */
        
        /* SIZE CONTROLS */
        height: 3.0em !important;            /* Vertical thickness */
        width: 100% !important;              /* Stretch across the screen */
        font-size: 24px !important;          /* Text size */
        font-weight: 900 !important;         /* Extra Thick Text */
        
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 4. HEADINGS
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>🚗 Dad's Car Share</h1>", unsafe_allow_html=True)

# This version ignores the CSS block and forces the size/color right here:
st.markdown("""
    <p style='
        text-align: center; 
        color: #212529; 
        font-size: 24px; 
        font-weight: bold; 
        margin-top: -10px;
    '>
        Parked at Flyaway 0800 77 66 99
    </p>
""", unsafe_allow_html=True)

# 5. DATA LOADING FUNCTIONS
def load_log():
    # Cache busting ensures we see the latest mileage immediately
    df = pd.read_csv(f"{LOG_URL}&cache={pd.Timestamp.now().timestamp()}")
    df.columns = df.columns.str.strip().str.lower()
    return df

def load_bookings():
    df = pd.read_csv(f"{BOOKING_URL}&cache={pd.Timestamp.now().timestamp()}")
    df.columns = df.columns.str.strip().str.lower()
    return df

# 6. SECTION 1: UPDATE MILEAGE
with st.expander("📍 Update Car Mileage"):
    with st.form("location_form", clear_on_submit=True):
        u_name = st.text_input("Your Name")
        u_loc = st.text_input("Mileage at Dropoff")
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            if u_name and u_loc:
                payload = {ENTRY_NAME: u_name, ENTRY_LOC: u_loc}
                try:
                    response = requests.post(FORM_URL, data=payload, timeout=5)
                    st.success("✅ Mileage updated!")
                    time.sleep(1)
                    st.rerun()
                except:
                    # Treat timeout as success if Google Sheet updates
                    st.success("✅ Update sent!")
                    st.rerun()
            else:
                st.warning("Please fill in both fields.")

# 7. SECTION 2: CURRENT STATUS DISPLAY
try:
    log_df = load_log()
    if not log_df.empty:
        latest = log_df.iloc[-1]
        # Dynamically find columns
        loc_col = next((c for c in log_df.columns if 'loc' in c or 'mile' in c), None)
        driver_col = next((c for c in log_df.columns if 'driver' in c or 'name' in c), None)
        
        current_loc = latest[loc_col] if loc_col else "Unknown"
        current_driver = latest[driver_col] if driver_col else "Unknown"
        
        # Displaying the box with the mileage
        st.success(f"📍 **Current Mileage:** {current_loc}")
        st.write(f"**Last parked by:** {current_driver}")
except Exception as e:
    st.info("Waiting for data...")

# 8. SECTION 3: BOOKING & CALENDAR
st.divider()
st.link_button("➕ Book the Car", "https://docs.google.com/forms/d/e/1FAIpQLSeLwzlfbmjG80888ZcoDjkGF-kIQmkINQGpdr2a6ckc6KSTXA/viewform", use_container_width=True)

try:
    book_df = load_bookings()
    calendar_events = []
    
    # Color mapping for drivers
    color_map = {
        "Tony": "#2196F3", "Sue": "#B66DFF", "Grant": "#107C10",
        "Paid": "#FFC1CB", "Dwight": "#FFD86C", "Bryce": "#D82C20",
    }

    # Find the right columns for the calendar
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

# 9. SECTION 4: CANCEL BOOKING
st.divider()
with st.expander("🗑️ Cancel a Booking"):
    try:
        c_df = load_bookings()
        if not c_df.empty:
            # Create a selection string (Name + Date)
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
    except:
        st.write("Could not load cancellation list.")

# 10. REFRESH BUTTON
if st.button('🔄 Refresh Dashboard', use_container_width=True):
    st.rerun()
