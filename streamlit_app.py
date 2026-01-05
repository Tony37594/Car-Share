import streamlit as st
import pandas as pd

st.set_page_config(page_title="AKL Car Share", page_icon="🚗")

# Replace this with YOUR actual Google Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Se6lXZLpgIarI_z4OXhHXgDdruDzjDYlwEhSg9LUYI8/edit?usp=sharing"

# This magic line converts your sheet link into a direct CSV download link
CSV_URL = SHEET_URL.replace('/edit#gid=', '/export?format=csv&gid=')

def load_data():
    # Adding storage_options makes it bypass some common browser blocks
    return pd.read_csv(CSV_URL)

st.title("🚗 Auckland Car Share")
st.markdown("### 📍 Current Status")

try:
    df = load_data()
    if not df.empty:
        # Get the very last row added to the sheet
        latest = df.iloc[-1]
        
        # Display the big status card
        st.info(f"The car was last left by **{latest['Driver']}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Parking Location", latest['Location'])
        with col2:
            st.metric("Fuel Level", latest['Fuel'])
            
        if str(latest['Notes']) != 'nan':
            st.warning(f"**Note from {latest['Driver']}:** {latest['Notes']}")
            
        st.divider()
        st.subheader("Recent History")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    else:
        st.write("The sheet is empty. Add a row in Google Sheets to see it here!")

except Exception as e:
    st.error("Could not connect to the Google Sheet. Make sure 'Anyone with the link' can view it.")
    st.write(e)

# Simple refresh button
if st.button('🔄 Refresh Location'):
    st.rerun()
