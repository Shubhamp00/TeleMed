import cv2
import mediapipe as mp
import numpy as np
import base64
from io import BytesIO
from PIL import Image

class CVAnalyzer:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.face_detection = self.mp_face_detection.FaceDetection(
            min_detection_confidence=0.5
        )
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5
        )
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5
        )
    
    def decode_frame(self, frame_data):
        try:
            if ',' in frame_data:
                frame_data = frame_data.split(',')[1]
            
            img_bytes = base64.b64decode(frame_data)
            img = Image.open(BytesIO(img_bytes))
            img_array = np.array(img)
            
            if len(img_array.shape) == 2:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
            elif img_array.shape[2] == 4:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            
            return img_array
        except Exception as e:
            print(f'Error decoding frame: {e}')
            return None
    
    def analyze_facial_expressions(self, image):
        results = self.face_mesh.process(image)
        
        if not results.multi_face_landmarks:
            return None
        
        face_landmarks = results.multi_face_landmarks[0]
        landmarks = face_landmarks.landmark
        
        left_eye_top = landmarks[159].y
        left_eye_bottom = landmarks[145].y
        left_eye_openness = abs(left_eye_top - left_eye_bottom)
        
        right_eye_top = landmarks[386].y
        right_eye_bottom = landmarks[374].y
        right_eye_openness = abs(right_eye_top - right_eye_bottom)
        
        avg_eye_openness = (left_eye_openness + right_eye_openness) / 2
        
        mouth_top = landmarks[13].y
        mouth_bottom = landmarks[14].y
        mouth_openness = abs(mouth_top - mouth_bottom)
        
        left_mouth = landmarks[61].x
        right_mouth = landmarks[291].x
        mouth_width = abs(right_mouth - left_mouth)
        
        left_eyebrow = landmarks[107].y
        right_eyebrow = landmarks[336].y
        avg_eyebrow_height = (left_eyebrow + right_eyebrow) / 2
        
        expression = "Neutral"
        indicators = []
        
        if mouth_openness > 0.03:
            expression = "Mouth Open (Possible Distress/Pain)"
            indicators.append("mouth_open")
        elif mouth_width > 0.25 and mouth_openness < 0.02:
            expression = "Smiling"
            indicators.append("smile")
        
        if avg_eye_openness < 0.015:
            expression = "Eyes Squinting (Possible Pain)"
            indicators.append("squinting")
        elif avg_eye_openness < 0.02:
            indicators.append("tired_eyes")
        
        if avg_eyebrow_height < 0.35:
            indicators.append("frowning")
            if "Pain" not in expression:
                expression = "Concerned/Worried"
        
        return {
            'expression': expression,
            'indicators': indicators,
            'metrics': {
                'eye_openness': round(avg_eye_openness, 4),
                'mouth_openness': round(mouth_openness, 4),
                'mouth_width': round(mouth_width, 4)
            }
        }
    
    def analyze_skin_condition(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        indicators = []
        if brightness < 80:
            indicators.append("low_brightness")
        if contrast > 60:
            indicators.append("high_contrast_variations")
        if edge_density > 0.15:
            indicators.append("texture_irregularities")
        
        return {
            'brightness': round(float(brightness), 2),
            'contrast': round(float(contrast), 2),
            'edge_density': round(float(edge_density), 4),
            'indicators': indicators
        }
    
    def analyze_posture(self, image):
        results = self.pose.process(image)
        
        if not results.pose_landmarks:
            return None
        
        landmarks = results.pose_landmarks.landmark
        
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE]
        
        shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
        shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
        
        head_tilt = abs(nose.x - shoulder_center_x)
        
        shoulder_slope = abs(left_shoulder.y - right_shoulder.y)
        
        posture_status = "Good Posture"
        indicators = []
        
        if head_tilt > 0.1:
            posture_status = "Head Tilted"
            indicators.append("head_tilt")
        
        if shoulder_slope > 0.05:
            posture_status = "Shoulders Uneven"
            indicators.append("shoulder_imbalance")
        
        if nose.y < shoulder_center_y - 0.2:
            indicators.append("leaning_forward")
        
        return {
            'status': posture_status,
            'indicators': indicators,
            'metrics': {
                'head_tilt': round(float(head_tilt), 4),
                'shoulder_slope': round(float(shoulder_slope), 4)
            }
        }
    
    def analyze_frame(self, frame_data):
        image = self.decode_frame(frame_data)
        
        if image is None:
            return None
        
        try:
            h, w = image.shape[:2]
            if w > 640:
                scale = 640 / w
                new_w = 640
                new_h = int(h * scale)
                image = cv2.resize(image, (new_w, new_h))
            
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if len(image.shape) == 3 else image
            
            facial_analysis = self.analyze_facial_expressions(rgb_image)
            skin_analysis = self.analyze_skin_condition(rgb_image)
            posture_analysis = self.analyze_posture(rgb_image)
            
            analysis_result = {
                'facial_expression': facial_analysis,
                'skin_condition': skin_analysis,
                'posture': posture_analysis,
                'overall_indicators': []
            }
            
            if facial_analysis and 'Pain' in facial_analysis['expression']:
                analysis_result['overall_indicators'].append('pain_detected')
            
            if skin_analysis and len(skin_analysis['indicators']) > 1:
                analysis_result['overall_indicators'].append('skin_variations_detected')
            
            if posture_analysis and len(posture_analysis['indicators']) > 0:
                analysis_result['overall_indicators'].append('posture_issue_detected')
            
            return analysis_result
        
        except Exception as e:
            print(f'Error in CV analysis: {e}')
            return None
