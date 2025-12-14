import streamlit as st
import requests
import json
import base64

# --- 1. CONFIGURATION (REPLACE THESE) ---
# Your Roboflow Model URL (from the 'Hosted API' section, it looks like: https://detect.roboflow.com/project-name/version?...)
# IMPORTANT: DO NOT PUT YOUR API KEY HERE. USE THE SECRETS FILE.
API_URL = "https://serverless.roboflow.com/samatortrial/workflows/find-bolts" 

# --- 2. STREAMLIT APP LAYOUT ---
st.set_page_config(page_title="Vision AI Bolt Counter", layout="wide")
st.title("🔩 Automated Small Parts Counter")
st.markdown("---")

# Use st.camera_input() which works great on mobile browsers
uploaded_file = st.camera_input("📸 Take a picture of the parts in the tray:")

if uploaded_file is not None:
    # --- 3. PREPARE IMAGE DATA ---
    # Read the image file and convert it to base64 for the API call
    image_bytes = uploaded_file.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # --- 4. API CALL TO ROBOFLOW ---
    with st.spinner('Sending image to Vision AI for counting...'):
        # The Roboflow API key is securely accessed from the Streamlit secrets file
        api_key = st.secrets["roboflow"]["api_key"]
        
        # Construct the final URL with the API Key
        full_url = f"{API_URL}&api_key={api_key}"
        
        # Send the Base64 image data to the Roboflow Hosted API
        response = requests.post(
            full_url,
            data=image_base64,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
    # --- 5. PROCESS AND DISPLAY RESULTS ---
    if response.status_code == 200:
        data = response.json()
        
        # 5a. The Count (The most important part! Simple Python len() solves the issue.)
        predictions = data.get('predictions', [])
        item_count = len(predictions)
        
        # 5b. The Annotated Image (Roboflow returns a URL to the image with bounding boxes)
        # Note: Roboflow's API sometimes returns the visualization URL in the response
        # If not, you may need to use the inference library (a bit more complex)
        # For simplicity, we'll try to display the image sent and the count first.
        
        # Display the result in a large, clear metric
        st.header(f"✅ COUNT COMPLETE")
        st.success(f"## Total Parts Detected: **{item_count}**")
        st.image(uploaded_file, caption="Captured Image for Verification", use_column_width=True)
        
        # Optional: Display the raw JSON response for debugging
        # st.json(data) 
        
    else:
        st.error(f"❌ Error communicating with the Vision AI Model.")
        st.code(f"Status Code: {response.status_code}\nResponse: {response.text}")