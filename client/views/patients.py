import streamlit as st

# Text Styling
st.markdown(
    """
    <style>
        .title {
            font-size:40px;
            font-weight:600;
            text-align:left;
            margin-bottom:20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title">Patient Information</div>', unsafe_allow_html=True)

st.write("View patient diagnoses")

with st.form(key="form"):
    patientName = st.text_input("Enter Patient Name")
    st.form_submit_button()