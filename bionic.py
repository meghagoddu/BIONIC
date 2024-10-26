import streamlit as st
import streamlit.components.v1 as components
import hashlib
import requests

# homepage
st.set_page_config(
    page_title="BIONIC Health Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# logging in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'users' not in st.session_state:
    st.session_state.users = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# video recording
def show_video_recording():
    st.markdown("<h2 class='subtitle'>📹 Video Consultation Recording</h2>", unsafe_allow_html=True)

    
    cols = st.columns(3)
    with cols[0]:
        st.markdown("#### 1. Start Recording")
    with cols[1]:
        st.markdown("#### 2. Speak Clearly")
    with cols[2]:
        st.markdown("#### 3. Save Recording")

    # html
    html_code = """
        <div class="video-container card" style="position: relative;">
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
                navigator.mediaDevices.getUserMedia({ video: true, audio: true })
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
    components.html(html_code, height=800)


def main():
    st.markdown("<h1 class='main-title'>BIONIC Health Portal</h1>", unsafe_allow_html=True)
    st.write("Welcome to BIONIC! Please sign up or login below.")
    # sidebar for navigation
    with st.sidebar:
        st.image("https://your-logo-url.com", width=150)
        st.markdown("### BIONIC")
        menu_choice = st.radio(
            "",
            ["Home", "Medical Records", "Video Consultation", "Settings"],
            label_visibility="collapsed"
        )

    if not st.session_state.logged_in:
        # logging in and signing up
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🔐 Login")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit_button = st.form_submit_button("Login")
                if submit_button:
                    if username in st.session_state.users:
                        if st.session_state.users[username] == hash_password(password):
                            st.session_state.logged_in = True
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Incorrect password.")
                    else:
                        st.error("User not found.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### ✨ Sign Up")
            with st.form("signup_form"):
                new_username = st.text_input("New Username")
                new_password = st.text_input("New Password", type="password")
                submit_button = st.form_submit_button("Sign Up")
                if submit_button:
                    if new_username in st.session_state.users:
                        st.error("Username already exists.")
                    else:
                        st.session_state.users[new_username] = hash_password(new_password)
                        st.success("Sign up successful! You can now log in.")
                        st.session_state.logged_in = True
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        if menu_choice == "Home":
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 👋 Welcome to Your Health Portal")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Last Visit", "3 days ago", "-2")
            with col2:
                st.metric("Upcoming Appointments", "2", "+1")
            with col3:
                st.metric("Documents Pending", "1", "-3")
            st.markdown("</div>", unsafe_allow_html=True)

        elif menu_choice == "Video Consultation":
            show_video_recording()

        elif menu_choice == "Medical Records":
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 📋 Medical Records")
            
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

if __name__ == "__main__":
    main()