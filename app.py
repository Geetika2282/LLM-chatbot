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
            st.success('Proceed to entering your query!', icon='👉')
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

# Store chat history
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your medical assistant. How can I help you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your medical assistant. How can I help you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Safety check for domain
def is_medical_query(query):
    medical_keywords = [
        "symptom", "medicine", "treatment", "mental", "health", "pain", "headache", "fever", "cold",
        "flu", "diabetes", "asthma", "injury", "blood", "pressure", "stress", "anxiety", "cough",
        "dose", "side effect", "doctor", "nurse", "burn", "cut", "wound", "first aid", "disease", "hospital",
        "therapy", "nutrition", "exercise", "fitness", "body", "heart", "lungs", "cancer", "infection", "vaccine"
    ]
    return any(word.lower() in query.lower() for word in medical_keywords)

# Generate response
def generate_response(prompt_input, llm, is_medical):
    if is_medical:
        system_prompt = (
            "You are a professional medical assistant. Answer only medical questions in detail."
        )
        assistant_intro = ""
    else:
        system_prompt = (
            "You are an assistant limited to medical topics. For non-medical queries, "
            "you give only brief (50-80 word) general responses and begin with: "
            "'⚠️ I'm specialized in medical topics, but here's a brief answer to your question:'"
        )
        assistant_intro = "⚠️ I'm specialized in medical topics, but here's a brief answer to your question:\n\n"

    string_dialogue = system_prompt
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += f"\n\nUser: {dict_message['content']}"
        else:
            string_dialogue += f"\n\nAssistant: {dict_message['content']}"

    inputs = {
        "prompt": f"{string_dialogue}\n\nUser: {prompt_input}\n\nAssistant:",
        "temperature": temperature,
        "top_p": top_p,
        "system_prompt": system_prompt
    }

    output = replicate.run(llm, input=inputs)
    response_text = ''.join(output).strip()
    if not is_medical:
        response_text = assistant_intro + response_text
    return response_text

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            is_medical = is_medical_query(prompt)
            response = generate_response(prompt, llm, is_medical)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
