import cv2
import numpy as np
import face_recognition
from collections import defaultdict
import time

class AdvancedFaceRecognition:
    def __init__(self):
        self.face_encodings = {}
        self.face_names = {}
        self.quality_threshold = 0.6
        self.confidence_threshold = 0.6
        self.anti_spoofing_enabled = True
        
    def assess_face_quality(self, face_image):
        """Assess face image quality"""
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        
        # Check brightness
        brightness = np.mean(gray)
        if brightness < 50 or brightness > 200:
            return False, "Poor lighting conditions"
        
        # Check blur using Laplacian variance
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_score < 100:
            return False, "Image too blurry"
        
        # Check face size
        height, width = gray.shape
        if height < 100 or width < 100:
            return False, "Face too small"
        
        return True, "Good quality"
    
    def detect_spoofing(self, face_image):
        """Basic anti-spoofing detection"""
        if not self.anti_spoofing_enabled:
            return True, "Anti-spoofing disabled"
        
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        
        # Check for texture variation (real faces have more texture)
        texture_score = np.std(gray)
        if texture_score < 20:
            return False, "Possible photo/screen attack"
        
        # Check for color variation in different channels
        b, g, r = cv2.split(face_image)
        color_variance = np.var([np.mean(b), np.mean(g), np.mean(r)])
        if color_variance < 10:
            return False, "Suspicious color distribution"
        
        return True, "Live face detected"
    
    def add_face_encoding(self, student_id, name, face_image):
        """Add multiple encodings for better accuracy"""
        quality_ok, quality_msg = self.assess_face_quality(face_image)
        if not quality_ok:
            return False, quality_msg
        
        spoofing_ok, spoofing_msg = self.detect_spoofing(face_image)
        if not spoofing_ok:
            return False, spoofing_msg
        
        # Get face encoding
        rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        
        if not face_locations:
            return False, "No face detected"
        
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        if not face_encodings:
            return False, "Could not encode face"
        
        # Store multiple encodings for the same person
        if student_id not in self.face_encodings:
            self.face_encodings[student_id] = []
            self.face_names[student_id] = name
        
        self.face_encodings[student_id].append(face_encodings[0])
        
        # Keep only last 5 encodings per person
        if len(self.face_encodings[student_id]) > 5:
            self.face_encodings[student_id] = self.face_encodings[student_id][-5:]
        
        return True, "Face encoding added successfully"
    
    def recognize_face(self, face_image):
        """Recognize face with improved accuracy"""
        if not self.face_encodings:
            return None, 0, "No registered faces"
        
        quality_ok, quality_msg = self.assess_face_quality(face_image)
        if not quality_ok:
            return None, 0, quality_msg
        
        spoofing_ok, spoofing_msg = self.detect_spoofing(face_image)
        if not spoofing_ok:
            return None, 0, spoofing_msg
        
        # Get face encoding
        rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        
        if not face_locations:
            return None, 0, "No face detected"
        
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        if not face_encodings:
            return None, 0, "Could not encode face"
        
        unknown_encoding = face_encodings[0]
        
        # Compare with all registered faces
        best_match = None
        best_confidence = 0
        
        for student_id, known_encodings in self.face_encodings.items():
            distances = face_recognition.face_distance(known_encodings, unknown_encoding)
            min_distance = np.min(distances)
            confidence = 1 - min_distance
            
            if confidence > best_confidence and confidence > self.confidence_threshold:
                best_confidence = confidence
                best_match = student_id
        
        if best_match:
            return best_match, best_confidence, "Face recognized"
        else:
            return None, 0, "Face not recognized"
    
    def update_confidence_threshold(self, threshold):
        """Update confidence threshold"""
        self.confidence_threshold = max(0.3, min(0.9, threshold))
    
    def get_statistics(self):
        """Get recognition statistics"""
        return {
            'total_registered_faces': len(self.face_encodings),
            'total_encodings': sum(len(encodings) for encodings in self.face_encodings.values()),
            'confidence_threshold': self.confidence_threshold,
            'anti_spoofing_enabled': self.anti_spoofing_enabled
        }