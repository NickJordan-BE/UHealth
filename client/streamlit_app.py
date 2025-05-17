import streamlit as st

# --- PAGE SETUP ---

loginPage = st.Page(
    page="./views/login.py",
    title="Sign In",
    icon=":material/person:",
    
)

patientsPage = st.Page(
    page="./views/patients.py",
    title="Patients",
    icon=":material/groups:",
)

infoPage = st.Page(
    page="./views/info.py",
    title="Information",
    icon=":material/home:",
    default=True,
)

chatbot = st.Page(
    page="./views/chatbot.py",
    title="Virtual Assistant",
    icon=":material/robot:",
)

# SHARED ON ALL PAGES
#i can't make the logo work properly :(
st.sidebar.text("UHealth")

# NAVIGATION SETUP

pg = st.navigation(
    {
        "Home": [infoPage, loginPage],
        "Information": [patientsPage, chatbot],
    }
)

pg.run()