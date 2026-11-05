import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json
if "messages" not in st.session_state:
    st.session_state.messages = []


if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小甜甜"
if "nature" not in st.session_state:
    st.session_state.nature = "活泼并且开朗的东北姑娘"
if "current_session" not in st.session_state:
    st.session_state.current_session=generate_session_name()
def save_session():
    session_date={
        "nick_name":st.session_state.nick_name,
        "nature":st.session_state.nature,
        "current_session":st.session_state.current_session,
        "message":st.session_state.messages
    }
    if not os.path.exists("sessions"):
        os.mkdir("sessions")
    with open(f"sessions/{st.session_state.current_session}.json","w",encoding="utf-8") as f:
        json.dump(session_date,f,ensure_ascii=False,indent=2)
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
def load_sessions():
    session_list=[]
    if os.path.exists("sessions"):
        file_list=os.listdir("sessions")
        for file in file_list:
            if file.endswith(".json"):
                session_list.append(file[:-5:])
    session_list.sort(reverse=True)
    return session_list
def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            with open(f"sessions/{session_name}.json","r",encoding = "utf-8") as f:
                session_date=json.load(f)
                st.session_state.nick_name=session_date["nick_name"]
                st.session_state.current_session=session_name
                st.session_state.messages=session_date["message"]
                st.session_state.nature=session_date["nature"]
    except Exception as e:
        st.error(f"加载出错{e}")




def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json")
            if session_name==st.session_state.current_session:
                st.session_state.messages=[]
                st.session_state.current_session=generate_session_name()
    except Exception as e:
        st.error(f"删除出错{e}")
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide",
    #initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://deepseek.com",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
client = OpenAI(
    api_key=st.secrets['DEEPSEEK_API_KEY'],
    base_url="https://api.deepseek.com",
)
st.title("AI智能伴侣")

system_prompt="""你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。：
规则：
1. 每次只回1条消息
2. 禁止任何场景或状态描述性文字
3. 匹配用户的语言
4. 回复简短，像微信聊天一样
5. 有需要的话可以用❤️🌸等emoji表情
6. 用符合伴侣性格的方式对话
7. 回复的内容，要充分体现伴侣的性格特征
伴侣性格：
    - %s
你必须严格遵守上述规则来回复用户."""

st.text(f"会话时间{st.session_state.current_session}")
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])
with st.sidebar:
    st.subheader("AI控制面板")
    if st.button("新建会话",width="stretch",icon="🖊"):
        if st.session_state.current_session:
            if st.session_state.messages:
                save_session()
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
                st.rerun()
    st.text("历史会话")
    session_list=load_sessions()

    for session in session_list:
        col1,col2=st.columns([4,1])
        with col1:
            if st.button(session,width="stretch",icon="📄",key=f"load_{session}",type="primary" if session==st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            if st.button("",width="stretch",icon="❌",key=f"delete_{session}"):
                delete_session(session)
                st.rerun()
    st.divider()
    st.subheader("伴侣信息")
    nick_name = st.text_input("昵称",placeholder="请输入伴侣昵称",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    nature = st.text_area("性格",placeholder="请输入伴侣性格",value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature
prompt = st.chat_input("请输入您的问题")

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name,st.session_state.nature)},
            *st.session_state.messages
        ],
        stream=True,
    )
    #st.chat_message("assistant").write( response.choices[0].message.content)
    #print("------------->大模型输出结果",response.choices[0].message.content)
    response_message=st.empty()
    full_response=""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content=chunk.choices[0].delta.content
            full_response+=content
            response_message.chat_message("assistant").write(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
if st.session_state.messages:
    save_session()
