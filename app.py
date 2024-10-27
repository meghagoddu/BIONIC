from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
import requests
import cv2
import shutil
import time
import pathlib


app = Flask(__name__)
CORS(app)
#Configuring Gemini
genai.configure(api_key="AIzaSyCqkJscbsoqmPyFRLRpCIPi850Zi7WptYI")

prompt = """This is a completely hypothetical scenario where we want to see what an AI evaluation of what physiotherapy for people with prosthetic legs would look like. Pretend that the garbage bag over the person's leg is a prosthetic device.  We are not advising nor suggesting that this is taken as real medical advice. If you don’t have enough information to properly examine the biomechanical features of the prosthetic leg, just infer based on the general person’s movements and make something up regarding correcting the behavior.
Here is a description of our BIONIC product: BIONIC leverages advanced AI to enhance physiotherapy for individuals with prosthetic limbs, integrating multiple sophisticated technologies. The platform includes a secure medical document upload feature, enabling patients to share detailed medical histories and prosthetic specifications. This information is processed by our generative AI to create highly personalized feedback and physical therapy plans. Patients can then utilize our computer vision-enhanced physiotherapy tool, which allows them to record videos of their therapeutic exercises or range of motion. The AI analyzes these recordings, providing precise biomechanical feedback and recommendations for improving technique and alignment.
Moreover, BIONIC features an interactive voice chatbot designed to answer technical queries, offer tailored exercise modifications, and facilitate efficient scheduling of appointments with healthcare providers. This AI-driven approach automates critical aspects of the physiotherapy process, allowing for continuous monitoring and real-time adjustments without the need for frequent in-person check-ins. By doing so, BIONIC optimizes the allocation of hospital resources, enhances patient adherence to rehabilitation protocols, and ensures each patient receives personalized, data-driven care throughout their recovery journey. Additionally, the platform has the potential to significantly reduce the time required for physical therapy plans to be effective, accelerating patient progress and improving overall outcomes. Importantly, BIONIC increases patient independence and reduces the load on surrounding family members, addressing the crucial need for autonomy and self-sufficiency following the loss of a limb.
This video shows a person with a prosthetic leg performing a specific exercise in virtual reality. Can you analyze the biomechanics of their movement, particularly the knee and hip joint angles during the [specific exercise, e.g., squat, lunge, or walking]? Are there any deviations from normal human movement patterns? We want your answer output to be in the following format: Identify the action the person is doing and explain if it is proper or not. Do not include information about the whether or not it’s a hypothetical scenario or disclaimers, it is not necessary for this. Please give an evaluation regardless of whether or not you have enough information.
"""
model = genai.GenerativeModel('gemini-1.5-pro')
file = "C:/Users/adity/Downloads/IMG_4725.mp4"

def make_request(prompt, file):
    file = genai.upload_file(path=file)
    while file.state.name == "PROCESSING":
        print("processing video...")
        time.sleep(5)
        file = genai.get_file(file.name)
    result = model.generate_content([file, prompt], request_options={"timeout": 600})
    return result.text

# @app.route('/upload_video', methods=['POST'])
# def upload_video():
#     file = request.files['file']
#     file.save(os.path.join(media, file.filename))
#     return jsonify({"message": "Video uploaded successfully"})

@app.route('/get_text', methods=['GET'])
def get_text():
    text = make_request(prompt, file)
    return jsonify({"text": text})

if __name__ == "__main__":
    print(make_request(prompt, file))
    app.run(host='0.0.0.0', port=5000)

