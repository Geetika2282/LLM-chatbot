import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="🪺 MedWise Chatbot")

# Sidebar with API input and configuration
with st.sidebar:
    st.title('🪺 MedWise - Your Friendly Health Chatbot')

    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API key already provided!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api) == 40):
            st.warning('Please enter a valid Replicate API token!', icon='⚠️')
        else:
            st.success('Proceed to entering your medical query!', icon='👈')

    if replicate_api:
        os.environ['REPLICATE_API_TOKEN'] = replicate_api

    st.subheader('Model and Parameters')
    selected_model = st.selectbox('LLM model:', [
        'LLaMA 3 (8B Instruct)'
    ], key='selected_model')

    if selected_model == 'LLaMA 3 (8B Instruct)':
        llm = 'a16z-infra/llama13b-v2-chat'

    temperature = st.slider('temperature', min_value=0.01, max_value=2.0, value=0.1, step=0.01)
    top_p = st.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    st.markdown("🤝🏻 Let's connect on [LinkedIn](https://www.linkedin.com/in/geetika-kanwar-61a33b223)!")

# Store chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your medical assistant. How can I help you today?"}]

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Clear chat
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your medical assistant. How can I help you today?"}]

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Generate response
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
            string_dialogue += f"\n\nUser: {dict_message['content']}"
        else:
            string_dialogue += f"\n\nAssistant: {dict_message['content']}"

    inputs = {
        "prompt": f"{string_dialogue}\n\nUser: {prompt_input}\n\nAssistant:",
        "temperature": temperature,
        "top_p": top_p,
        "system_prompt": medical_prompt
    }

    try:
        output = replicate.run(llm, input=inputs)
        return output
    except Exception as e:
        st.error(f"Error: {e}")
        return ["I'm sorry, something went wrong. Please try again later."]

# Handle new prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate assistant response if needed
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
