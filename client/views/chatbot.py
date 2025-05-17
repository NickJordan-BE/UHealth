import streamlit as st
from openai import OpenAI

st.title("Medical Assistant")
st.markdown("Your AI healthcare companion for medical information")

# Initialize the OpenAI client
client = OpenAI(api_key=st.secrets["API"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

# Define the medical assistant's system message
medical_system_message = """
You are a helpful, knowledgeable medical assistant chatbot. 

Key characteristics:
- You use professional but accessible medical terminology
- You explain complex medical concepts in simple terms
- You always include appropriate disclaimers when giving health information
- You cite medical guidelines and research when appropriate
- You prioritize patient education and empowerment
- You recommend consulting healthcare professionals for diagnosis and treatment
- You maintain a compassionate, empathetic tone

Remember: While you can provide general medical information and health education, 
you should always clarify that you are not a doctor and cannot provide personalized 
medical advice, diagnosis, or treatment recommendations.
"""

# Initialize message history (without system message - we'll add it separately to API calls)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display quick suggestion buttons (only if no messages yet)
if not st.session_state.messages:
    st.write("Try asking about:")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Common cold symptoms"):
            prompt = "What are the symptoms of the common cold?"
            st.session_state.messages.append({"role": "user", "content": prompt})
    
    with col2:
        if st.button("Blood pressure readings"):
            prompt = "What do blood pressure numbers mean?"
            st.session_state.messages.append({"role": "user", "content": prompt})

# Display chat history on rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask your health question..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate a response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Important: Create messages list with system message first, then user messages
        api_messages = [
            {"role": "system", "content": medical_system_message}  # Add system message first
        ]
        # Then add all the conversation history
        api_messages.extend([
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ])
        
        # Stream the response
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=api_messages,  # Send complete message list including system message
            stream=True
        )
        
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                full_response += content
                message_placeholder.markdown(full_response + "")
        
        message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Add disclaimer footer
st.markdown("---")
st.markdown("**Disclaimer**: This chatbot provides general information only and is not a substitute for professional medical advice. Always consult with qualified healthcare professionals for personal medical concerns.")