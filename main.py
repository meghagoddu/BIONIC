import cv2
import mediapipe as mp
import numpy as np

class JointDetector:
    def __init__(self):
        # Initialize MediaPipe Pose with higher confidence thresholds for better detection
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize movement tracking
        self.previous_positions = {}
        self.movement_threshold = 0.03  # Adjust this value to change movement sensitivity
        
    def analyze_movement(self, landmarks):
        """Analyze movement of key joints"""
        joints = {
            'left_shoulder': self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            'right_shoulder': self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            'left_elbow': self.mp_pose.PoseLandmark.LEFT_ELBOW,
            'right_elbow': self.mp_pose.PoseLandmark.RIGHT_ELBOW,
            'left_wrist': self.mp_pose.PoseLandmark.LEFT_WRIST,
            'right_wrist': self.mp_pose.PoseLandmark.RIGHT_WRIST,
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
                movement_data[joint_name] = {'status': 'initializing', 'confidence': current_pos[2]}
                continue
            
            # Calculate movement
            movement = np.sqrt(
                (current_pos[0] - self.previous_positions[joint_name][0])**2 +
                (current_pos[1] - self.previous_positions[joint_name][1])**2
            )
            
            movement_data[joint_name] = {
                'status': 'moving' if movement > self.movement_threshold else 'still',
                'confidence': current_pos[2],
                'movement_amount': movement
            }
            
            self.previous_positions[joint_name] = current_pos
            
        return movement_data

    def process_frame(self, frame):
        """Process a single frame to detect joints and analyze movement"""
        # Convert to RGB for MediaPipe
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.pose.process(image_rgb)
        
        if results.pose_landmarks:
            # Analyze movement
            movement_analysis = self.analyze_movement(results.pose_landmarks.landmark)
            
            # Draw pose landmarks with custom style
            self.mp_draw.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            # Add movement analysis text
            y_position = 30
            for joint, data in movement_analysis.items():
                # Only show joints with good visibility
                if data['confidence'] > 0.5:
                    color = (0, 255, 0) if data['status'] == 'moving' else (0, 165, 255)
                    cv2.putText(
                        frame,
                        f"{joint}: {data['status']} ({data['confidence']:.2f})",
                        (10, y_position),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        2
                    )
                    y_position += 25
                    
        return frame

def main():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    detector = JointDetector()
    
    # Set camera resolution (optional)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process frame
        processed_frame = detector.process_frame(frame)
        
        # Add instructions
        cv2.putText(
            processed_frame,
            "Press 'q' to quit",
            (10, processed_frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )
        
        # Show the frame
        cv2.imshow('Joint Movement Analysis', processed_frame)
        
        # Break loop on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    # Clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
