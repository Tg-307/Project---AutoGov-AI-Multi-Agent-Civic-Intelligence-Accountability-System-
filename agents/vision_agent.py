"""
VisionAgent: Analyzes uploaded image and detects civic issue type.
Uses filename/size heuristics as mock detection logic for prototype.
In production, replace with a real CV model (YOLOv8, ResNet, etc.)
"""
import random
import os
import hashlib


ISSUE_TYPES = ['pothole', 'garbage', 'broken_streetlight', 'open_drain', 'encroachment']

ISSUE_KEYWORDS = {
    'pothole': ['pothole', 'road', 'crack', 'pit', 'hole', 'asphalt', 'pavement'],
    'garbage': ['garbage', 'trash', 'waste', 'dump', 'litter', 'bin', 'debris', 'rubbish'],
    'broken_streetlight': ['light', 'lamp', 'street', 'dark', 'bulb', 'pole'],
    'open_drain': ['drain', 'sewer', 'water', 'flood', 'nala', 'gutter'],
    'encroachment': ['encroach', 'block', 'obstruct', 'illegal', 'footpath', 'sidewalk'],
}


class VisionAgent:
    """
    Agent responsible for detecting the type of civic issue in an image.
    Mock implementation uses filename + size-based heuristics.
    """

    def __init__(self):
        self.agent_name = "VisionAgent"
        self.confidence_threshold = 0.55

    def analyze(self, image_path: str, filename: str = '') -> dict:
        """
        Analyze image and return detection result.
        Returns: {issue_type, confidence, raw_scores}
        """
        print(f"[{self.agent_name}] Analyzing image: {filename}")

        # Keyword matching on filename (mock CV)
        detected_type, confidence = self._keyword_detect(filename)

        # If no keyword match, use hash-based deterministic mock
        if detected_type is None:
            detected_type, confidence = self._hash_detect(image_path, filename)

        result = {
            'issue_type': detected_type,
            'confidence': confidence,
            'raw_scores': self._generate_mock_scores(detected_type),
            'agent': self.agent_name,
        }

        print(f"[{self.agent_name}] Detected: {detected_type} (confidence: {confidence:.2f})")
        return result

    def _keyword_detect(self, filename: str):
        """Check filename for issue keywords."""
        fname = filename.lower()
        for issue, keywords in ISSUE_KEYWORDS.items():
            for kw in keywords:
                if kw in fname:
                    confidence = round(random.uniform(0.78, 0.97), 2)
                    return issue, confidence
        return None, 0.0

    def _hash_detect(self, image_path: str, filename: str):
        """Deterministic mock detection using file hash."""
        try:
            seed_str = filename + str(os.path.getsize(image_path))
        except Exception:
            seed_str = filename

        hash_val = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
        idx = hash_val % len(ISSUE_TYPES)
        detected_type = ISSUE_TYPES[idx]
        confidence = 0.55 + (hash_val % 40) / 100.0
        return detected_type, round(confidence, 2)

    def _generate_mock_scores(self, detected_type: str) -> dict:
        """Generate mock probability scores for all classes."""
        scores = {}
        remaining = 1.0
        types = ISSUE_TYPES.copy()
        types.remove(detected_type)

        # Detected type gets highest score
        top_score = round(random.uniform(0.55, 0.92), 2)
        scores[detected_type] = top_score
        remaining = 1.0 - top_score

        random.shuffle(types)
        for i, t in enumerate(types):
            if i == len(types) - 1:
                scores[t] = round(remaining, 2)
            else:
                share = round(random.uniform(0, remaining / (len(types) - i)), 2)
                scores[t] = share
                remaining -= share

        return scores
