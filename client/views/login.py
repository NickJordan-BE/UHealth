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

st.markdown('<div class="title">Welcome Back!</div>', unsafe_allow_html=True)


st.write("Login to your account")

# Login Form
with st.form(key="my_form"):
    username = st.text_input("Username")
    password = st.text_input("Password")
    st.form_submit_button("Login")