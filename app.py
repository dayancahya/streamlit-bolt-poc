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

    # --- 4. API CALL TO ROBOFLOW (FINAL DEFINITIVE FIX) ---
    # The URL remains the same (Correct query parameter fixed the 401)
    full_url = f"{API_URL}?api_key={api_key}" 
    
    # 1. DEFINE THE CORRECT WORKFLOW PAYLOAD STRUCTURE
    # CRITICAL: Roboflow often requires the data to be nested under "inputs"
    # AND the API key must sometimes be included in the body for the Workflow API.
    payload = {
        # This key is often REQUIRED for Workflow API payload (even if in URL)
        "api_key": api_key, 
        "inputs": [ # CRITICAL: This key replaces "images"
            {
                "type": "base64",
                "value": image_base64
            }
        ]
    }
    
    # 2. SEND THE REQUEST WITH JSON 
    response = requests.post(
        full_url,
        json=payload, # Use 'json=payload' to set Content-Type: application/json
    )
    response.raise_for_status()
                
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






