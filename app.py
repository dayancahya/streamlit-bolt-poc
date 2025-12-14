import streamlit as st
from inference_sdk import InferenceHTTPClient
import base64
import io

# --- CONFIGURATION (REPLACE THESE) ---
# Use the values from your snippet:
WORKSPACE_NAME = "samatortrial" 
WORKFLOW_ID = "find-bolts"

# --- STREAMLIT APP LAYOUT ---
st.set_page_config(page_title="Vision AI Bolt Counter", layout="wide")
st.title("🔩 Automated Small Parts Counter")
st.markdown("---")

# 1. Initialize the Roboflow Client (Uses the API key from secrets)
try:
    api_key = st.secrets["roboflow"]["api_key"]
    client = InferenceHTTPClient(
        api_url="https://serverless.roboflow.com",
        api_key=api_key
    )
except Exception as e:
    st.error("❌ Configuration Error: Could not initialize Roboflow client. Check API key in secrets.")
    st.stop()

uploaded_file = st.camera_input("📸 Take a picture of the parts in the tray:")

if uploaded_file is not None:
    # --- 3. PREPARE IMAGE DATA ---
    # The SDK works best with a file path or a binary stream
    image_bytes = uploaded_file.getvalue()
    image_stream = io.BytesIO(image_bytes) # Convert bytes to a stream object

    # --- 4. API CALL TO ROBOFLOW USING SDK ---
    try:
        with st.spinner('Sending image to Vision AI for counting...'):
            result = client.run_workflow(
                workspace_name=WORKSPACE_NAME,
                workflow_id=WORKFLOW_ID,
                images={
                    "image": image_stream # Pass the image stream directly
                }
            )

    except Exception as e:
        st.error(f"❌ Workflow Execution Error: Failed to run the workflow.")
        # The 401 error will likely show up here.
        st.code(f"Error Details: {e}")
        st.stop()

    # --- 5. PROCESS AND DISPLAY RESULTS ---

    # We need to find the predictions list within the complex workflow result structure
    # The Roboflow response usually places the output of the final block in the result dict.
    # Since your final step is a model, we look for the predictions.

    # A safer way to get the count from a Workflow result:

    # Step A: Find the model's output in the result dictionary
    # The key is often 'rapid_model' or the name you gave the detection block in your workflow

    predictions_output = result.get('rapid_model', {}).get('predictions', []) 

    # Fallback check (if predictions aren't under 'rapid_model')
    if not predictions_output:
        for key, value in result.items():
            if isinstance(value, dict) and 'predictions' in value:
                predictions_output = value['predictions']
                break

    item_count = len(predictions_output)

    # Display the result in a large, clear metric
    st.header(f"✅ COUNT COMPLETE")
    st.success(f"## Total Parts Detected: **{item_count}**")
    st.image(uploaded_file, caption="Captured Image for Verification", use_column_width=True)
    st.info("The count is derived directly from the number of prediction boxes.")
