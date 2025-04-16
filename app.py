import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="🩺 MedWise Chatbot")

# Replicate Credentials
with st.sidebar:
    st.title('🩺 MedWise - Your Friendly Health Chatbot')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API key already provided!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api) == 40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your medical query!', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    st.subheader('Model and Parameters')
    selected_model = st.sidebar.selectbox('LLM model: ', [
        'LLaMA 3 (8B Instruct)'
    ], key='selected_model')

    if selected_model == 'LLaMA 3 (8B Instruct)':
        llm = 'meta/meta-llama-3-8b-instruct'

    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=2.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    st.markdown("🤝🏻 Let's connect on [LinkedIn](https://www.linkedin.com/in/geetika-kanwar-61a33b223)!")

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your medical assistant. How can I help you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your medical assistant. How can I help you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating medical assistant response
def generate_llama2_response(prompt_input, llm):
    medical_prompt = (
        "You are a professional medical assistant. "
        "You help users by giving information related to general health, symptoms, medications, mental wellness, "
        "and basic first aid. You do not provide diagnosis or prescribe medications. "
        "Always suggest consulting a certified doctor for serious issues."
    )

    string_dialogue = medical_prompt
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "\n\nUser: " + dict_message["content"]
        else:
            string_dialogue += "\n\nAssistant: " + dict_message["content"]

    inputs = {
        "prompt": f"{string_dialogue}\n\nUser: {prompt_input}\n\nAssistant:",
        "temperature": temperature,
        "top_p": top_p,
        "system_prompt": medical_prompt
    }

    output = replicate.run(llm, input=inputs)
    return output

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt, llm)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
