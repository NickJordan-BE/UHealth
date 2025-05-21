import streamlit as st
from PIL import Image
import requests
import os

# Landing Page
st.markdown(
    """
    <style>
        .logoTitle {
            font-size:60px;
            font-weight:600;
            text-align:center;
            margin-bottom:100px;
        }    
        .title {
            font-size:40px;
            font-weight:600;
            text-align:center;
            margin-bottom:20px;
        }
        .subtitle {
            font-size:20px;
            text-align:center;
            margin-bottom:40px;
            color: #fff;
        }
        .footer {
            font-size:14px;
            text-align:center;
            color:#888;
            margin-top:40px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="logoTitle">UHealth</div>', unsafe_allow_html=True)
st.markdown('<div class="title">X-Ray Diagnostic Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload chest X-ray images to receive AI-generated diagnostic suggestions</div>', unsafe_allow_html=True)

SERVER_URL = os.environ.get("SERVER_URL", "http://server:4000")

# Patient name input
patient_name = st.text_input("Enter Patient Name")

# File upload section
uploaded_file = st.file_uploader("Upload an X-ray image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

# Display uploaded image and dummy diagnosis
if uploaded_file is not None and patient_name.strip() != "":
    image = Image.open(uploaded_file)
    st.image(image, caption=f"X-ray of {patient_name}", use_container_width=True)

    st.markdown("### Diagnosis:")
    # Replace this section with your ML model diagnosis
    if st.button("Submit to Backend"):
        # Build the POST request
        files = {
            'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }
        data = {
            'name': patient_name
        }

        try:
            response = requests.post(f"{SERVER_URL}/predict", data=data, files=files)
            response.raise_for_status()  # Raises an error for 4xx/5xx responses



            result = response.json()
            st.success(f"Upload successful")
            st.write(result.get('prediction'))

        except requests.exceptions.RequestException as e:
            st.error(f"Upload failed: {e}")
elif uploaded_file is not None and patient_name.strip() == "":
    st.warning("Please enter the patient's name.")
else:
    st.info("Please upload a valid X-ray image to get started.")


# Footer
st.markdown('<div class="footer">2025 UHackathon</div>', unsafe_allow_html=True)
