import cv2
import mediapipe as mp
import numpy as np

class ProstheticJointDetector:
    def __init__(self):
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            model_complexity=1
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Define color range specifically for black garbage bag
        self.prosthetic_color_ranges = [
            {'lower': np.array([0, 0, 0]), 'upper': np.array([180, 180, 30])}  # Adjusted for black material
        ]
        
        # Only track legs
        self.limb_connections = {
            'right_arm': [
        (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_ELBOW),
        (self.mp_pose.PoseLandmark.RIGHT_ELBOW, self.mp_pose.PoseLandmark.RIGHT_WRIST)
    ],
    'left_arm': [
        (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_ELBOW),
        (self.mp_pose.PoseLandmark.LEFT_ELBOW, self.mp_pose.PoseLandmark.LEFT_WRIST)
    ],
            'right_leg': [
                (self.mp_pose.PoseLandmark.RIGHT_HIP, self.mp_pose.PoseLandmark.RIGHT_KNEE),
                (self.mp_pose.PoseLandmark.RIGHT_KNEE, self.mp_pose.PoseLandmark.RIGHT_ANKLE)
            ],
            'left_leg': [
                (self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.LEFT_KNEE),
                (self.mp_pose.PoseLandmark.LEFT_KNEE, self.mp_pose.PoseLandmark.LEFT_ANKLE)
            ]
        }

    def detect_prosthetic_color(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        combined_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        
        for color_range in self.prosthetic_color_ranges:
            mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        kernel = np.ones((5,5), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        
        return combined_mask

    def check_prosthetic_in_region(self, frame, mask, start_point, end_point):
        h, w = frame.shape[:2]
        start_x, start_y = int(start_point.x * w), int(start_point.y * h)
        end_x, end_y = int(end_point.x * w), int(end_point.y * h)
        
        limb_mask = np.zeros_like(mask)
        cv2.line(limb_mask, (start_x, start_y), (end_x, end_y), 255, thickness=20)
        
        overlap = cv2.bitwise_and(mask, limb_mask)
        overlap_area = np.sum(overlap > 0)
        min_area_threshold = 200  # Adjust this value to change sensitivity
        
        return overlap_area > min_area_threshold

    def process_frame(self, frame):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        
        if results.pose_landmarks:
            prosthetic_mask = self.detect_prosthetic_color(frame)
            
            landmarks = results.pose_landmarks.landmark
            for limb_name, connections in self.limb_connections.items():
                for start_landmark, end_landmark in connections:
                    if self.check_prosthetic_in_region(
                        frame, 
                        prosthetic_mask,
                        landmarks[start_landmark.value],
                        landmarks[end_landmark.value]
                    ):
                        h, w = frame.shape[:2]
                        start_point = landmarks[start_landmark.value]
                        end_point = landmarks[end_landmark.value]
                        
                        start_px = (int(start_point.x * w), int(start_point.y * h))
                        end_px = (int(end_point.x * w), int(end_point.y * h))
                        
                        # Draw green line for detected segment
                        cv2.line(frame, start_px, end_px, (0, 255, 0), 4)
                        
                        # Add text label
                        mid_x = (start_px[0] + end_px[0]) // 2
                        mid_y = (start_px[1] + end_px[1]) // 2 
                        cv2.putText(frame, 
                                limb_name, 
                                (mid_x - 40, mid_y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 255, 0),
                                2)
        
        return frame

def main():
    cap = cv2.VideoCapture(0)
    detector = ProstheticJointDetector()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        processed_frame = detector.process_frame(frame)
        cv2.imshow('Prosthetic Detection', processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
