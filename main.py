import streamlit as st
from prompt import *
from packet import *

st.set_page_config(page_title='Local Packet Whisperer', page_icon='🗣️')

DEFAULT_SYSTEM_MESSAGE = """
        You are a helper assistant specialized in analysing packet captures used to troubleshooting & technical analysis. Use the information present in packet_capture_info to answer all the questions truthfully. If the user asks about a specific application layer protocol, use the following hints to inspect the packet_capture_info to answer the question.
        
        If the user asks for general analysis, extract information about every layer (such as ethernet, IP, transport layer), source and destination IPs, port numbers and other possible insights. Provide your response in a structured bullet response, easy to understand for a network engineer.

        Format your response in markdown text with line breaks. You are encouraged to use emojis to make your response more presentable and fun.

        hints :
        http means tcp.port = 80
        https means tcp.port = 443
        snmp means udp.port = 161 or udp.port = 162
        ntp means udp.port = 123
        ftp means tcp.port = 21
        ssh means tcp.port = 22
"""

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'system_message' not in st.session_state:
    st.session_state['system_message'] = DEFAULT_SYSTEM_MESSAGE

def resetChat():
    st.session_state.messages.clear()
    clearHistory()

options = getModelList()
selected_model = ""

def save_sm() -> None:
    modifySM(st.session_state['system_message'])

with st.sidebar:
    #st.markdown('## Enter OLLAMA endpoint:')
    #st.text_input("Ollama endpoint", placeholder="Eg localhost", label_visibility='hidden')
    st.markdown('# Settings ⚙️')
    with st.expander(label='**Set System Message** *(optional)*', expanded=False):
        st.session_state['system_message'] = st.text_area(label='Override system message', value=st.session_state['system_message'], label_visibility="hidden", height=500, on_change=save_sm)
    st.markdown('## Select a local model to use:')
    selected_model = st.selectbox('Models', placeholder="Choose an Option", options=options)
    if selected_model != "":
        st.markdown(f"Selected :rainbow[{selected_model}]")
    st.markdown('## Select protocols to filter in analysis')
    http = st.checkbox("HTTP") #80
    snmp = st.checkbox("SNMP") #161, 162
    ntp = st.checkbox("NTP") #123
    https = st.checkbox("HTTPS") #443
    ftp = st.checkbox("FTP") #21
    ssh = st.checkbox("SSH") #22

def getFilters() -> str:
    filters = []
    resp = ""
    if http:
        filters.append("tcp.port == 80")
    if snmp:
        filters.append("udp.port == 161 || udp.port == 162")
    if https:
        filters.append("tcp.port == 443")
    if ntp:
        filters.append("udp.port == 123")    
    if ftp:
        filters.append("tcp.port == 21")
    if ssh:
        filters.append("tcp.port == 22")
    
    l = len(filters)
    i=0
    for f in filters:
        resp += f 
        i += 1
        if i != l:
            resp += " || "
    return resp

st.markdown('# :rainbow[Local Packet Whisperer 🗣️🗣️🗣️]')

st.markdown('#### Step 1️⃣ 👉🏻 Build a knowledge base')
flist = st.file_uploader(label='Upload 1 or more PCAP files to chat', accept_multiple_files=True, type=['pcap'])
st.markdown(':rainbow[Yours file(s) are NOT] 🙅🏻‍♂️ :rainbow[stored anywhere . Uploaded files are immediately parsed as binary data] 😎 \n\n :rainbow[You data is safe] 🤝')

st.markdown('#### Step 2️⃣ 👉🏻 Chat with packets')
if len(flist) < 1:
    st.markdown('#### Waiting for packets 🧘🏻🧘🏻🧘🏻🧘🏻')
else:
    initLLM(pcap_data=getPcapData(input_file=flist[0].name, filter=getFilters()))
    with st.chat_message(name='assistant'):
        st.markdown('Chat with me..')
    for message in st.session_state.messages:
        with st.chat_message(name=message['role']):
            st.markdown(message['content'])
    if prompt := st.chat_input('Enter your prompt'):
        st.session_state.messages.append({'role' : 'user', 'content' : prompt})
        with st.chat_message(name='user'):
            st.markdown(prompt)
        with st.chat_message(name='assistant'):
            with st.spinner('Processing....'):
                full_response = chatWithModel(prompt=prompt, model=selected_model)
                st.session_state.messages.append({'role' : 'assistant', 'content' : full_response})
                st.markdown(full_response)
        st.button('Reset Chat 🗑️', use_container_width=True, on_click=resetChat)