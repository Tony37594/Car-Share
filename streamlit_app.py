import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AKL Car Share", page_icon="🚗")

st.title("🚗 Auckland Car Share")
st.markdown("Track the car at Auckland Airport.")

# 1. Connect to Google Sheets
# You will paste your Google Sheet URL in the Streamlit Secrets later
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Fetch Data
df = conn.read(worksheet="log", ttl=0) # ttl=0 means no caching, always fresh data

# 3. Display Current Status
if not df.empty:
    latest = df.iloc[-1]
    st.success(f"**Current Status:** The car is currently **{latest['Action']}**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Last Seen At", latest['Location'])
    with col2:
        st.metric("Fuel Level", latest['Fuel'])
    
    if latest['Notes']:
        st.info(f"**Notes:** {latest['Notes']}")
else:
    st.warning("No logs found. Start by logging a Drop-off!")

st.divider()

# 4. Form to Log Activity
st.subheader("Update Status")
with st.form("log_form"):
    driver = st.selectbox("Who are you?", ["Driver 1", "Driver 2", "Driver 3"])
    action = st.radio("What are you doing?", ["Dropping Off", "Picking Up"])
    location = st.text_input("Parking Spot (e.g. Row K, Bay 42)", placeholder="Only needed for Drop-off")
    fuel = st.select_slider("Fuel Level", options=["Empty", "1/4", "1/2", "3/4", "Full"])
    notes = st.text_area("Notes (e.g. Lockbox code, car needs a wash)")
    
    submit = st.form_submit_button("Update App")

    if submit:
        # Create new row
        new_data = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Driver": driver,
            "Action": action,
            "Location": location if action == "Dropping Off" else "In Use",
            "Fuel": fuel,
            "Notes": notes
        }])
        
        # Add to existing data
        updated_df = pd.concat([df, new_data], ignore_index=True)
        
        # Update Google Sheet
        conn.update(worksheet="log", data=updated_df)
        st.balloons()
        st.rerun()

# 5. Show History
with st.expander("View Full History"):
    st.dataframe(df.sort_index(ascending=False))
