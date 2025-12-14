import streamlit as st
import requests
import base64
import json # Still needed for payload serialization

# --- 1. CONFIGURATION ---
# The Roboflow Workflow Endpoint URL (without the API key)
API_URL = "https://serverless.roboflow.com/samatortrial/workflows/find-bolts" 

# --- 2. STREAMLIT APP LAYOUT ---
st.set_page_config(page_title="Vision AI Bolt Counter", layout="wide")
st.title("🔩 Automated Small Parts Counter")
st.markdown("---")

# **CHANGED:** Use file_uploader instead of camera_input
uploaded_file = st.file_uploader("📂 Upload an image of the parts in the tray:", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # --- 3. PREPARE IMAGE DATA ---
    image_bytes = uploaded_file.getvalue()
    # Convert image bytes to a base64 string
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # --- 4. API CALL TO ROBOFLOW (FINAL CLEAN PAYLOAD) ---
    try:
        with st.spinner('Sending image to Vision AI for counting...'):
            api_key = st.secrets["roboflow"]["api_key"]
            
            # URL: Use the correct structure with the API key as a query parameter (Fixed the 401)
            full_url = f"{API_URL}?api_key={api_key}" 
            
            # 1. DEFINE THE CORRECT WORKFLOW PAYLOAD STRUCTURE (Final best guess for 422 fix)
            # This structure uses the 'inputs' array wrapper and omits the redundant api_key from the body.
            payload = {
                "inputs": {
                    "image": { # <-- Assume 'image' is the name of your first workflow input variable
                        "type": "base64",
                        "value": image_base64
                    }
                }
            }
            
            # 2. SEND THE REQUEST WITH JSON 
            response = requests.post(
                full_url,
                json=payload, # requests handles the serialization and Content-Type header
            )
            response.raise_for_status() # Catches 4xx and 5xx errors

    except requests.exceptions.RequestException as e:
        # Handle connection errors, 401 Unauthorized, 404 Not Found, etc.
        st.error(f"❌ API Communication Error. Please check your API Key and URL.")
        st.code(f"Error Status: {response.status_code if 'response' in locals() else 'N/A'}\nDetails: {e}")
        st.stop()

    # --- 5. PROCESS AND DISPLAY RESULTS ---
    data = response.json()
    
    # The Count: This simple Python line is the core POC deliverable!
    # NOTE: The predictions key here assumes your Roboflow Workflow outputs a 'predictions' array.
    predictions = data.get('predictions', []) 
    item_count = len(predictions)
    
    # Display the result in a clear, high-impact format
    st.header(f"✅ COUNT COMPLETE")
    st.success(f"## Total Parts Detected: **{item_count}**")
    st.image(image_bytes, caption="Uploaded Image for Verification", use_column_width=True)
    
    # Optional: Display the raw predictions array (uncomment for debugging)
    # st.markdown(f"**Raw API Response (JSON):**")
    # st.json(data)

