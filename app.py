import streamlit as st
from agent import create_agent, process_question
from tools import all_tools

st.set_page_config(
    page_title="Multi-Tool AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .example-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_agent():
    return create_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("ℹ️ How to use")
    st.markdown("""
    #### 🧮 Calculator
    ```plaintext
    87 ** 2
    ```

    #### 💱 Currency Converter
    ```plaintext
    100 USD to BRL
    ```
    ```plaintext
    50 EUR to USD
    ```
    ```plaintext
    63 USD to BRL
    ```

    #### 📅 Date & Time
    ```plaintext
    date and time
    ```

    #### 💬 General Questions
    ```plaintext
    Explain what LLMs are
    ```
    """, unsafe_allow_html=True)

    st.divider()

    st.header("📊 Statistics")
    user_messages = [m for m in st.session_state.messages if m["role"] == "user"]
    st.metric("Questions Sent", len(user_messages))
    st.metric("Available Tools", len(all_tools))
    
    st.divider()
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.caption("✨ Technical Challenge - AI Engineer Jr")

# Title
st.title("🤖 Multi-Tool AI Assistant")
st.markdown("""
This assistant can help you with **multiple tasks**:
""")

# Icons and tool descriptions - aligned in one row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("🧮 **Calculator**")
    st.caption("Exact numerical calculations")
with col2:
    st.markdown("💱 **Currency Converter**")
    st.caption("Exchange rates")
with col3:
    st.markdown("📅 **Date & Time**")
    st.caption("Time-related information")
with col4:
    st.markdown("💬 **General Questions**")
    st.caption("Examples of questions you can ask")

st.divider()

# Main chat container
chat_container = st.container()
 
# Show message history
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show used tool if available
            if "tool_used" in message and message["tool_used"]:
                st.caption(f"🔧 Tool used: **{message['tool_used']}**")

# User input
prompt = st.chat_input("💬 Type your question here...")

if prompt:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Show the user's message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process the assistant's response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                agent_executor = get_agent()
                result = process_question(prompt, agent_executor)

                # Support both Portuguese and English keys
                success = result.get("success", result.get("sucesso", False))
                response_text = result.get("response", result.get("resposta", ""))

                if success:
                    st.markdown(response_text)
                    # Add assistant response to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "tool_used": result.get("tool_used")
                    })
                else:
                    error_msg = response_text or "An error occurred"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
            except Exception as e:
                error_msg = f"❌ Unexpected error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
    
    st.rerun()

# Footer
footer_col1, footer_col2 = st.columns(2)
with footer_col1:
    st.caption("💡 Tip: The assistant automatically decides which tool to use!")
with footer_col2:
    st.caption("🔍 Debug: See full reasoning in the terminal")