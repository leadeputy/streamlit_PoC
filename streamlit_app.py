import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# 1. Load data and Initialize session state for DataFrame
if 'df' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv('user_messages.csv')
    except FileNotFoundError:
        st.session_state.df = pd.DataFrame(columns=['message', 'response', 'label', 'analyze', 'connect'])

# Streamlit 앱이 재실행될 때마다 세션 상태 초기화 방지
# 'chat_history'가 세션 상태에 없으면 빈 리스트로 초기화
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 2. Page layout
st.set_page_config(page_title="Mission AI PoC", layout="wide")
st.title("Mission AI Chatbot PoC")

col1, col2 = st.columns(2)

# --- Chat Interface (col1) ---
with col1:
    st.header("Chat with AI Bot")

    # 대화 기록 표시 영역 (스크롤 가능하게)
    chat_placeholder = st.container(height=400, border=True)

    with chat_placeholder:
        for chat_entry in st.session_state.chat_history:
            with st.chat_message("user"):
                st.markdown(chat_entry['user_message'])
            with st.chat_message("assistant"):
                st.markdown(chat_entry['bot_response'])

    # 입력 필드
    user_input = st.chat_input("Enter your message here...")

    if user_input:
        # 'Negative' 키워드
        negative_words = [
            'blame', 'go die', 'get out', 'curse', 'not', 'hate', 'stupid', 'idiot',
            'awful', 'terrible', 'worst', 'angry', 'disappointed', 'bad', 'shame',
            'unhappy', 'furious', 'annoying', 'pathetic', 'useless', 'garbage',
            'shit', 'fuck', 'damn', 'bitch', 'asshole', 'hell', 'crap', 'bullshit',
            'kill', 'die', 'murder', 'destroy', 'violence', 'harm', 'assault',
            'attack', 'bomb', 'terror', 'threat', 'danger', 'suck', 'lame', 'rubbish'
        ]
        
        # 'Positive' 키워드
        positive_words = [
            "jesus", "gospel", "god", "christian", "amen", "bible", "cross",
            "savior", "redeemer", "heaven", "prayer", "faith", "holy", "spirit",
            "church", "bless", "grace", "love", "hope", "peace", "joy", "truth",
            "salvation", "worship", "hallelujah", "christ", "lord", "almighty",
            "divine", "miracle", "eternal", "resurrection"
        ]

        # 감성 분류 로직
        response = "" 
        label = "Neutral"
        analyze_output = "Neutral 100%, Positive 0%, Negative 0%"

        if user_input.lower() in ["hello", "hi"]:
            response = "Hello, what can I help you?"
        elif any(bad_word in user_input.lower() for bad_word in negative_words):
            response = "That is an inappropriate comment. Please maintain a respectful conversation."
            label = "Negative"
            analyze_output = "Negative 100%, Neutral 0%, Positive 0%"
        elif any(good_word in user_input.lower() for good_word in positive_words):
            response = "God is the only one God and He gave His only son, Jesus. Jesus is the son of God and died in the cross for us 2 thousands years ago."
            label = "Positive"
            analyze_output = "Positive 100%, Neutral 0%, Negative 0%"
        else:
            response = "Any other questions?"

        # 새로운 대화 항목을 세션 상태의 chat_history에 추가 (채팅 UI용)
        new_chat_entry = {
            'user_message': user_input,
            'bot_response': response,
            'label': label,
            'analyze': analyze_output,
            'connect': 'True' if label == 'Positive' else 'False'
        }
        st.session_state.chat_history.append(new_chat_entry)

        # 로그 저장 (DataFrame에 추가)
        new_log_entry = pd.DataFrame([{
            'message': user_input, 
            'response': response, 
            'label': label,
            'analyze': analyze_output,
            'connect': 'True' if label == 'Positive' else 'False'
        }]) 
        st.session_state.df = pd.concat([st.session_state.df, new_log_entry], ignore_index=True)

        # 메시지가 입력되면 즉시 화면 업데이트
        st.rerun()

# --- Analysis & Dataframe (col2) ---
with col2:
    st.header("Overall Analyze") 
    current_df_for_analysis = st.session_state.df

    if not current_df_for_analysis.empty:
        label_counts = current_df_for_analysis['label'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(label_counts, labels=label_counts.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.write("No data to display in the pie chart yet.")

# 5. Dataframe (로그 테이블)
st.markdown("User message log")
current_df_for_log = st.session_state.df

if not current_df_for_log.empty:
    st.dataframe(current_df_for_log.tail(10), use_container_width=True)
else:
    st.write("No messages logged yet.")

# 6. Save updates (앱이 리로드될 때마다 저장)
final_df_to_save = st.session_state.df
if not final_df_to_save.empty:
    final_df_to_save.to_csv('user_messages.csv', index=False)
