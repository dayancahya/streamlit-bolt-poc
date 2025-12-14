import streamlit as st
import requests
import base64
import json # Ensure this is here, although not strictly needed for this basic app

# --- 1. CONFIGURATION (REPLACE THIS URL ONLY) ---
# The Roboflow API Endpoint URL (from the 'Hosted API' section, without the API key)
# Example: "https://detect.roboflow.com/your-project-name/version-number?"
API_URL = "https://serverless.roboflow.com/samatortrial/workflows/find-bolts" 

# --- 2. STREAMLIT APP LAYOUT ---
st.set_page_config(page_title="Vision AI Bolt Counter", layout="wide")
st.title("🔩 Automated Small Parts Counter")
st.markdown("---")

# The st.camera_input() triggers the phone camera
uploaded_file = st.camera_input("📸 Take a picture of the parts in the tray:")

if uploaded_file is not None:
    # --- 3. PREPARE IMAGE DATA ---
    image_bytes = uploaded_file.getvalue()
    # Convert image bytes to a base64 string, as required by the Roboflow API body
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # --- 4. API CALL TO ROBOFLOW ---
    try:
        with st.spinner('Sending image to Vision AI for counting...'):
            # Securely retrieve the API Key from the Streamlit secrets
            api_key = st.secrets["roboflow"]["api_key"]
            
            # Construct the final URL with the API Key appended as a query parameter
            full_url = f"{API_URL}&api_key={api_key}"
            
            # Send the base64 image string as the POST body
            response = requests.post(
                full_url,
                data=image_base64, # The body of the request is the base64 string
                # This header is crucial for Roboflow to correctly interpret the base64 body
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status() # Raise an HTTPError for bad responses (401, 500, etc.)
            
    except requests.exceptions.RequestException as e:
        # Handle connection errors, 401 Unauthorized, 404 Not Found, etc.
        st.error(f"❌ API Communication Error. Please check your API Key and URL.")
        st.code(f"Error Status: {response.status_code if 'response' in locals() else 'N/A'}\nDetails: {e}")
        st.stop() # Stop execution on failure

    # --- 5. PROCESS AND DISPLAY RESULTS ---
    data = response.json()
    
    # The Count: This simple Python line is the core POC deliverable!
    predictions = data.get('predictions', [])
    item_count = len(predictions)
    
    # Display the result in a clear, high-impact format
    st.header(f"✅ COUNT COMPLETE")
    st.success(f"## Total Parts Detected: **{item_count}**")
    st.image(uploaded_file, caption="Captured Image for Verification", use_column_width=True)
    
    # Optional: Display the raw predictions array (uncomment for debugging)
    # st.markdown(f"**Individual Predictions (JSON):**")
    # st.json(predictions)

