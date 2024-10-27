import streamlit as st
import streamlit.components.v1 as components
import hashlib
import time

# Page config
st.set_page_config(
    page_title="BIONIC Health Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with modern design system
st.markdown(
    """
    <style>
        /* Global Styles */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
        }
        
        .stButton button {
            background: linear-gradient(135deg, #4B79A1 0%, #283E51 100%);
            color: white;
            border-radius: 8px;
            padding: 0.5rem 2rem;
            border: none;
            box-shadow: 0 4px 6px rgba(50, 50, 93, 0.11);
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 7px 14px rgba(50, 50, 93, 0.1);
        }
        
        /* Card Styles */
        .custom-card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            border: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        /* Metrics Styling */
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            color: #2C3E50;
        }
        
        [data-testid="stMetricDelta"] {
            color: #27AE60;
            font-size: 1rem;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #2C3E50;
            padding-top: 2rem;
        }
        
        [data-testid="stSidebar"] .stRadio label {
            color: white !important;
            font-size: 1.1rem;
            padding: 0.5rem 0;
        }
        
        /* Header Styling */
        .main-title {
            font-size: 2.5rem;
            background: linear-gradient(120deg, #2C3E50, #3498DB);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 2rem;
        }
        
        /* Video Container Styling */
        .video-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .record-button {
            background: linear-gradient(135deg, #4B79A1 0%, #283E51 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            margin: 10px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .record-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 7px 14px rgba(50, 50, 93, 0.1);
        }
        
        /* Input Fields Styling */
        .stTextInput input, .stTextArea textarea {
            border-radius: 8px;
            border: 1px solid #E0E3E7;
            padding: 0.75rem;
            font-size: 1rem;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #4B79A1;
            box-shadow: 0 0 0 2px rgba(75, 121, 161, 0.1);
        }
        
        /* Progress Bar Styling */
        [data-testid="stProgress"] {
            height: 12px;
            border-radius: 6px;
            background-color: #E0E3E7;
        }
        
        [data-testid="stProgress"] > div {
            background: linear-gradient(90deg, #4B79A1 0%, #283E51 100%);
            border-radius: 6px;
        }
        
        /* Chat Message Styling */
        .chat-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 10px;
            max-width: 80%;
        }
        
        .user-message {
            background-color: #E3F2FD;
            margin-left: auto;
            border-top-right-radius: 0;
        }
        
        .bot-message {
            background-color: #F5F5F5;
            margin-right: auto;
            border-top-left-radius: 0;
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
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("<h2 style=color:gray>📹 Video Consultation Recording</h2>", unsafe_allow_html=True)

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
    components.html(html_code, height=1100)
    st.markdown('</div>', unsafe_allow_html=True)

def show_chatbot():

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("<h2 style=color:gray>💬 Healthcare Assistant</h2>", unsafe_allow_html=True)


    nlx_chatbot_html = """
        <html lang="en">
            <head>
                <title>NLX Widget Sample HTML</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
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
                        "title": "Support",
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
                        "primaryColor": "#2663da",
                        "darkMessageColor": "#2663da",
                        "lightMessageColor": "#EFEFEF",
                        "white": "#FFFFFF",
                        "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif",
                        "spacing": 12,
                        "borderRadius": 8,
                        "chatWindowMaxHeight": 640
                    }
                    });
                });
                </script>
            </body>
        </html>
        """
        
        # Inject the HTML code into Streamlit
    st.components.v1.html(nlx_chatbot_html, height=700, scrolling=True)

    # st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    # st.markdown("<h2 style=color:gray>💬 Healthcare Assistant</h2>", unsafe_allow_html=True)
    
    # # Display styled chat messages
    # for message in st.session_state.chat_history:
    #     display_chat_message(
    #         message['text'],
    #         is_user=(message['sender'] == "You")
    #     )

    # # Input area with improved styling
    # user_input = st.text_input(":gray[Type your message...]", key="chat_input")
    
    # if st.button("Send", key="send_button"):
    #     if user_input:
    #         # Add user message
    #         st.session_state.chat_history.append({
    #             "sender": "You",
    #             "text": user_input
    #         })
            
    #         # Simulate bot response
    #         response = "This is a demo response. In a real application, this would be connected to your healthcare chatbot backend."
    #         st.session_state.chat_history.append({
    #             "sender": "Bot",
    #             "text": response
    #         })
    #         st.rerun()

    # st.markdown('</div>', unsafe_allow_html=True)

def main():
    st.markdown("<h1 class='main-title'>BIONIC Health Portal</h1>", unsafe_allow_html=True)
    
    # sidebar for navigation
    with st.sidebar:
        st.image("https://your-logo-url.com", width=150)
        st.markdown("### BIONIC")
        menu_choice = st.radio(
            "",
            ["Home", "Medical Records", "Video Consultation", "Chatbot"],
            label_visibility="collapsed"
        )

    if not st.session_state.logged_in:
        st.write("<h3 style=color:gray> Welcome to BIONIC! Please sign up or login below. </h3>", unsafe_allow_html=True)

        # Initially show the signup form
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("<h3 style=color:gray>✨ Sign Up</h3>", unsafe_allow_html=True)
        with st.form("signup_form"):
            new_username = st.text_input(":gray[New Username]")
            new_password = st.text_input(":gray[New Password]", type="password")
            new_age = st.text_input(":gray[Age]", placeholder="Enter your age")
            
            # Adding gender selection
            new_gender = st.selectbox(
                ":gray[Gender]",
                options=["Select your gender", "Male", "Female", "Other"],
                index=0
            )

            submit_button = st.form_submit_button("Sign Up")
            if submit_button:
                # Check if any fields are empty or if gender is not selected
                if not new_username or not new_password or not new_age or new_gender == "Select your gender":
                    st.error("All fields are required. Please fill them out.")
                elif new_username in st.session_state.users:
                    st.error("Username already exists.")
                else:
                    # Storing user data including age and gender
                    st.session_state.users[new_username] = {
                        "password": hash_password(new_password),
                        "age": new_age,
                        "gender": new_gender
                    }
                    st.success(":gray[Sign up successful! You can now log in.]")
                    st.session_state.logged_in = True
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


        # Link to switch to the login form
        if st.button("Already have an account? Log in here."):
            st.session_state.show_login = True

        # Check if the login form should be displayed
        if st.session_state.get('show_login', False):
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("<h3 style=color:gray>🔐 Login</h3>", unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input(":gray[Username]")
                password = st.text_input(":gray[Password]", type="password")
                submit_button = st.form_submit_button("Login")
                if submit_button:
                    if username in st.session_state.users:
                        if st.session_state.users[username]["password"] == hash_password(password):
                            st.session_state.logged_in = True
                            st.success(":gray[Login successful!]")
                            st.rerun()
                        else:
                            st.error(":gray[Incorrect password.]")
                    else:
                        st.error("User not found.")
            st.markdown('</div>', unsafe_allow_html=True)



    else:
        if menu_choice == "Home":
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("<h2 style=color:gray>👋 Welcome to Your Health Portal</h2>" , unsafe_allow_html=True)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(":gray[Last Visit]", "3 days ago", "-2")
            with col2:
                st.metric(":gray[Upcoming Appointments]", "2", "+1")
            with col3:
                st.metric(":gray[Documents Pending]", "1", "-3")

            # Progress bar for profile completion
            st.write(":gray[Profile Completion]")
            completion_percentage = 75
            progress_bar = st.progress(0)
            
            for percent in range(completion_percentage + 1):
                time.sleep(0.01)
                progress_bar.progress(percent/100)
            
            st.markdown('</div>', unsafe_allow_html=True)

        elif menu_choice == "Video Consultation":
            show_video_recording()

        elif menu_choice == "Medical Records":
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("<h2 style=color:gray>📋 Medical Records</h2>", unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                ":gray[Upload Medical Records (PDF)]",
                type=["pdf"],
                help="Please upload your medical records in a PDF format"
            )
            
            symptoms = st.text_area(
                ":gray[List anything you would like the site to know...]",
                placeholder="Please describe in detail..."
            )
            
            if st.button("Submit Records"):
                st.success("Records submitted successfully!")
            st.markdown('</div>', unsafe_allow_html=True)
            
        elif menu_choice == "Chatbot":
            show_chatbot()

if __name__ == "__main__":
    main()
