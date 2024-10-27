import streamlit as st
import streamlit.components.v1 as components
import hashlib
import time

# Page config remains the same
st.set_page_config(
    page_title="BIONIC Health Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Updated CSS with horizontally narrower forms
st.markdown(
    """
    <style>
        .reportview-container {
            background-color: #181818;
        }
        .sidebar .sidebar-content {
            background-color: #181818;
        }

        body {
            margin: 0; 
            padding: 0; 
        }

        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
            margin: 0; 
            padding: 0; 
        }
        
        .stRadio > div {
            display: flex;
            flex-direction: row !important;
            gap: 1rem;
            padding: 1rem;
        }

        .stRadio > div input {
            display: none;
        }
        
        .stRadio > div label {
            background: transparent;
            color: white !important;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            font-size: 1rem;
            margin: 0 !important;
        }
        
        .stRadio > div label:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        .stRadio > div [type="radio"]:checked + label {
            background-color: rgba(255, 255, 255, 0.2);
            font-weight: bold;
        }
        
        .form-container {
            max-width: 300px;
            margin: 0 auto;
            padding: 0;
        }
        
        .stTextInput input, .stSelectbox select, div[data-baseweb="select"] > div {
            width: 100% !important;
            min-width: unset !important;
            max-width: 100% !important;
            background-color: #1c1c1c;
            color: white;
        }
        
        .stButton > button {
            width: 100% !important;
        }
        
        .stForm > div[data-testid="stForm"] {
            padding: 0 !important;
        }
        
        .stForm {
            padding: 0 !important;
        }
        
        .main-title {
            font-size: 2.5rem;
            color: #3498DB; /* Updated title color */
            margin-bottom: 2rem;
            text-align: center;
        }
        
        .stButton button {
            background: linear-gradient(135deg, #2980b9 0%, #1a1a1a 100%);
            color: white;
            border-radius: 8px;
            padding: 0.5rem 2rem;
            border: none;
            box-shadow: 0 4px 6px rgba(50, 50, 93, 0.1);
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 7px 14px rgba(50, 50, 93, 0.1);
            background: linear-gradient(135deg, #1a5276 0%, #1a1a1a 100%);
        }
        
        .stTextInput input, .stSelectbox select {
            border-radius: 8px;
            border: 1px solid #E0E3E7;
            padding: 0.75rem;
            width: 100%;
            margin-bottom: 1rem;
        }
        
        .stTextInput input:focus, .stSelectbox select:focus {
            border-color: #3498DB;
            box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
        }
        
        .custom-card {
            background: #1c1c1c;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            margin-bottom: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            color: #2980b9;
        }
        
        [data-testid="stMetricDelta"] {
            color: #27AE60;
            font-size: 1rem;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #1c1c1c;
            padding-top: 2rem;
        }
        
        [data-testid="stSidebar"] .stRadio label {
            color: white !important;
            font-size: 1.1rem;
            padding: 0.5rem 0;
        }
        
        .main-title {
            font-size: 2.5rem;
            color: #3498DB; 
            margin-bottom: 2rem;
        }

        .center-button {
            display: flex;
            justify-content: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def display_chat_message(message, is_user=True):
    message_class = "user-message" if is_user else "bot-message"
    st.markdown(
        f"""
        <div class="chat-message {message_class}">
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )

def show_video_recording():
    st.markdown("<h2 style=color:lightblue>📹 Video Recording</h2>", unsafe_allow_html=True)

    html_code = """
        <div class="video-container" style="position: relative;">
            <div id="redDot" style="height: 12px; width: 12px; background-color: red; border-radius: 50%; display: none; position: absolute; top: 10px; left: 10px;"></div>
            <video id="player" autoplay playsinline style="border: 2px solid #34495E; border-radius: 10px; width: 100%;"></video>
            <div class="button-container">
                <button id="startBtn" class="record-button" onclick="startRecording()">
                    Start Recording
                </button>
                <button id="stopBtn" class="record-button" onclick="stopRecording()" disabled>
                    Stop Recording
                </button>
            </div>
            <a id="download" href="#" style="display:none;">Download Recording</a>
        </div>
        
        <script>
            let mediaRecorder;
            let recordedBlobs = [];

            function startRecording() {
                recordedBlobs = [];
                navigator.mediaDevices.getUserMedia({ 
                    video: true, 
                    audio: false
                })
                .then(stream => {
                    document.getElementById('player').srcObject = stream;
                    mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });

                    mediaRecorder.ondataavailable = (event) => {
                        if (event.data && event.data.size > 0) {
                            recordedBlobs.push(event.data);
                        }
                    };

                    mediaRecorder.start();
                    document.getElementById("redDot").style.display = "block";
                    document.getElementById("startBtn").disabled = true;
                    document.getElementById("stopBtn").disabled = false;
                })
                .catch(error => {
                    console.error("Error accessing camera: ", error);
                    alert("Could not access camera. Please check permissions.");
                });
            }

            function stopRecording() {
                mediaRecorder.stop();
                document.getElementById("redDot").style.display = "none";

                mediaRecorder.onstop = () => {
                    const blob = new Blob(recordedBlobs, { type: 'video/webm' });
                    const url = URL.createObjectURL(blob);

                    const downloadLink = document.getElementById('download');
                    downloadLink.href = url;
                    downloadLink.download = 'recorded_video.webm';
                    downloadLink.style.display = 'block';

                    document.getElementById("startBtn").disabled = false;
                    document.getElementById("stopBtn").disabled = true;
                };
            }
        </script>
    """
    components.html(html_code, height=1100)  # Reduced height for the video section
    st.markdown('</div>', unsafe_allow_html=True)

def show_chatbot():
    nlx_chatbot_html = """
    <html lang="en">
        <head>
            <title>NLX Widget Sample HTML</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {
                    margin: 0;
                    padding: 0;
                }
                #chatbot-container {
                    position: absolute; 
                    top: 20px;
                    left: 0;
                    right: 0;
                    z-index: 1000; 
                    height: auto; 
                }
            </style>
        </head>
        <body>
            <div id="chatbot-container">
                <script defer src="https://unpkg.com/@nlxai/chat-widget/lib/index.umd.js"></script>
                <script>
                window.addEventListener("DOMContentLoaded", () => {
                    const widget = nlxai.chatWidget.create({
                        config: {
                            botUrl: "https://bots.dev.studio.nlx.ai/c/kQMVl5AV3hfwJWLcuTCF3/Ext2eq5ZAYOYpJO9mTOyo",
                            headers: {
                                "nlx-api-key": "AIzaSyCqkJscbsoqmPyFRLRpCIPi850Zi7WptYI"
                            },
                            languageCode: "en-US"
                        },
                        titleBar: {
                            "title": "Chat with BIONIC!",
                            "withCollapseButton": true,
                            "withCloseButton": true
                        },
                        onExpand: (conversationHandler) => {
                            const checkMessages = (messages) => {
                                if (messages.length === 0) {
                                    conversationHandler.sendWelcomeIntent();
                                }
                                conversationHandler.unsubscribe(checkMessages);
                            };
                            conversationHandler.subscribe(checkMessages);
                        },
                        theme: {
                            "primaryColor": "lightblue",
                            "darkMessageColor": "lightblue",
                            "lightMessageColor": "#EFEFEF",
                            "white": "#FFFFFF",
                            "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif",
                            "spacing": 12,
                            "borderRadius": 8,
                            "chatWindowMaxHeight": 800
                        }
                    });
                });
                </script>
            </div>
        </body>
    </html>
    """
    # Implement the HTML code into Streamlit
    st.components.v1.html(nlx_chatbot_html, height=600, scrolling=True)

def main():
    # Add menu choice
    menu_choice = st.sidebar.radio(" ", ["Home", "Video Recording", "Chatbot", "Medical Records"])

    if 'page' not in st.session_state:
        st.session_state.page = "Home"

    if not st.session_state.get('logged_in', False):
        # Center the forms using columns
        col1, col2, col3 = st.columns([1, 3, 1])  # Adjust the proportions as needed
        
        with col2:
            st.markdown("<h1 class='main-title' style='color: lightblue; font-size: 90px;'>BIONIC Health Portal</h1>", unsafe_allow_html=True)
            st.write("<h3 style='color: lightblue; text-align:center;'> Welcome to BIONIC! Please sign up or login below. </h3>", unsafe_allow_html=True)

            # Sign Up Form
            st.markdown("<h3 style='color:lightblue; text-align:center;'>✨ Sign Up</h3>", unsafe_allow_html=True)
            with st.form("signup_form"):
                new_username = st.text_input(":gray[New Username]")
                new_password = st.text_input(":gray[New Password]", type="password")
                new_age = st.text_input(":gray[Age]", placeholder="Enter your age")
                new_gender = st.selectbox(
                    ":gray[Gender]",
                    options=["Select your gender", "Male", "Female", "Other"],
                    index=0
                )
                submit_button = st.form_submit_button("Sign Up")
                if submit_button:
                    if not new_username or not new_password or not new_age or new_gender == "Select your gender":
                        st.error(":gray[All fields are required.]")
                    elif new_username in st.session_state.users:
                        st.error("Username already exists.")
                    else:
                        st.session_state.users[new_username] = {
                            "password": hash_password(new_password),
                            "age": new_age,
                            "gender": new_gender
                        }
                        st.success("Sign up successful!")
                        st.session_state.logged_in = True
                        st.rerun()

            # Login link
            if st.button("Already have an account? Log in here."):
                st.session_state.show_login = True

            # Login Form
            if st.session_state.get('show_login', False):
                st.markdown("<h3 style='color:lightblue; text-align:center;'>🔐 Login</h3>", unsafe_allow_html=True)
                with st.form("login_form"):
                    login_username = st.text_input(":gray[Username]")
                    login_password = st.text_input(":gray[Password]", type="password")
                    login_button = st.form_submit_button("Login")
                    if login_button:
                        if (login_username in st.session_state.users and
                                st.session_state.users[login_username]["password"] == hash_password(login_password)):
                            st.success("Login successful!")
                            st.session_state.logged_in = True
                            st.session_state.show_login = False
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")

    else:
        if menu_choice == "Home":
            # Add some spacing before the title
            for i in range(10):
                st.write(" ")

            # Custom CSS for title size
            st.markdown(
                """
                <style>
                .custom-title {
                    font-size: 72px;  /* Adjust size as needed */
                    color: white;      /* Change color if needed */
                    text-align: left;  /* Align text as desired */
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            # Typing animation function
            def typing_animation(text, delay=0.1):
                # Create a placeholder for the animation
                placeholder = st.empty()
                current_text = ""
                for char in text:
                    current_text += char  # Append the current character
                    placeholder.markdown(f"<h1 style='font-size: 100px; color: lightblue'>{current_text}</h1>", unsafe_allow_html=True)
                    time.sleep(delay)

                # Display the full sentence at the end
                placeholder.markdown(f"<h1 style='font-size: 100px; color: lightblue'>{text}</h1>", unsafe_allow_html=True)

            typing_animation("BIONIC — AI-Enhanced Prosthetic Rehabilitation Tool", delay=0.1)

        elif menu_choice == "Video Recording":
            show_video_recording()
        
        elif menu_choice == "Chatbot":
            st.markdown("<h2 style=color:lightblue>Chat with our Chatbot right here! You may inform your symptoms, concerns, and etc.</h2>", unsafe_allow_html=True)
            show_chatbot()
        
        elif menu_choice == "Medical Records":
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h2 style=color:lightblue>📋 Medical Records</h2>", unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Upload Medical Records (PDF)",
                type=["pdf"],
                help="Please upload your medical records in PDF format"
            )
            
            symptoms = st.text_area(
                "Describe Your Symptoms",
                placeholder="Please describe your symptoms in detail..."
            )
            
            if st.button("Submit Records"):
                st.success("Records submitted successfully!")
            st.markdown("</div>", unsafe_allow_html=True)


# Run the main function
if __name__ == "__main__":
    main()