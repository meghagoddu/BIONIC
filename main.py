import cv2
import mediapipe as mp
import numpy as np
from ultralytics import YOLO

class ProstheticDetector:
    def __init__(self):
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_draw = mp.solutions.drawing_utils
        
        # Initialize movement tracking
        self.previous_positions = {}
        self.movement_threshold = 0.03
        
        # Color ranges for prosthetic detection (HSV)
        self.prosthetic_color_ranges = [
            {'lower': np.array([0, 10, 60]), 'upper': np.array([20, 150, 255])},
            {'lower': np.array([0, 0, 0]), 'upper': np.array([180, 30, 60])}
        ]
        
    def detect_prosthetic(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        
        for color_range in self.prosthetic_color_ranges:
            current_mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
            mask = cv2.bitwise_or(mask, current_mask)
        
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        return mask

    def analyze_movement(self, landmarks):
        joints = {
            'left_knee': self.mp_pose.PoseLandmark.LEFT_KNEE,
            'right_knee': self.mp_pose.PoseLandmark.RIGHT_KNEE,
            'left_ankle': self.mp_pose.PoseLandmark.LEFT_ANKLE,
            'right_ankle': self.mp_pose.PoseLandmark.RIGHT_ANKLE
        }
        
        movement_data = {}
        for joint_name, joint_id in joints.items():
            current_pos = (
                landmarks[joint_id.value].x,
                landmarks[joint_id.value].y,
                landmarks[joint_id.value].visibility
            )
            
            if joint_name not in self.previous_positions:
                self.previous_positions[joint_name] = current_pos
                movement_data[joint_name] = 'initializing'
                continue
            
            movement = np.sqrt(
                (current_pos[0] - self.previous_positions[joint_name][0])**2 +
                (current_pos[1] - self.previous_positions[joint_name][1])**2
            )
            
            movement_data[joint_name] = {
                'movement': movement,
                'visibility': current_pos[2],
                'is_moving': movement > self.movement_threshold
            }
            
            self.previous_positions[joint_name] = current_pos
            
        return movement_data

    def process_frame(self, frame):
        # Convert to RGB for MediaPipe
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        
        if results.pose_landmarks:
            movement_analysis = self.analyze_movement(results.pose_landmarks.landmark)
            
            # Draw pose landmarks
            self.mp_draw.draw_landmarks(
                frame, 
                results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS
            )
            
            # Detect prosthetics
            prosthetic_mask = self.detect_prosthetic(frame)
            frame_with_prosthetic = cv2.bitwise_and(frame, frame, mask=prosthetic_mask)
            
            # Blend the frames
            alpha = 0.7
            frame = cv2.addWeighted(frame, alpha, frame_with_prosthetic, 1-alpha, 0)
            
            # Add movement analysis text
            y_position = 30
            for joint, data in movement_analysis.items():
                if isinstance(data, dict):
                    status = "Moving" if data['is_moving'] else "Still"
                    cv2.putText(
                        frame,
                        f"{joint}: {status} (conf: {data['visibility']:.2f})",
                        (10, y_position),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )
                    y_position += 30
                    
        return frame

def main():
    cap = cv2.VideoCapture(0)
    detector = ProstheticDetector()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        processed_frame = detector.process_frame(frame)
        cv2.imshow('Prosthetic Movement Analysis', processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
