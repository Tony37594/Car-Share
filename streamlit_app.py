import streamlit as st
import pandas as pd

st.set_page_config(page_title="AKL Car Share", page_icon="🚗")

# --- CONFIGURE YOUR SHEET HERE ---
# Paste your ID between the quotes below
SHEET_ID = "1Se6lXZLpgIarI_z4OXhHXgDdruDzjDYlwEhSg9LUYI8"
SHEET_NAME = "log"
# Ensure your tab in Google Sheets is named 'log'
# ---------------------------------

url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

st.title("🚗 Auckland Car Share")
st.markdown("### 📍 Current Status")

def load_data():
    # We add a custom header to mimic a browser so Google doesn't block the request
    return pd.read_csv(url)

try:
    df = load_data()
    
    if not df.empty:
        # Get the very last row
        latest = df.iloc[-1]
        
        # Display the Big Metrics
        st.info(f"Last updated by **{latest['Driver']}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Parking Location", latest['Location'])
        with col2:
            st.metric("Fuel Level", latest['Fuel'])
            
        if 'Notes' in latest and pd.notnull(latest['Notes']):
            st.warning(f"**Note:** {latest['Notes']}")
            
        st.divider()
        st.subheader("Recent History")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    else:
        st.write("The sheet is empty. Add a row in Google Sheets!")

except Exception as e:
    st.error("Connection Error: Make sure your Google Sheet is shared as 'Anyone with the link can view'.")
    st.exception(e)

if st.button('🔄 Refresh Data'):
    st.rerun()
