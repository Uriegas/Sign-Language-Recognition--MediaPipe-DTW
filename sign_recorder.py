import cv2
import numpy as np

from dtw import dtw_distances
from models.sign_model import SignModel
from utils.landmark_utils import extract_keypoints
from utils.mediapipe_utils import draw_landmarks

BLUE_COLOR = (245, 15, 15)
RED_COLOR = (15, 15, 245)


class SignRecorder(object):
    def __init__(self, sign_dictionary, sign_distances, seq_len=50):
        # Variables for recording
        self.color = BLUE_COLOR
        self.recording = False
        self.seq_len = seq_len

        # List of landmarks of size (nb_frames x nb_landmarks)
        self.left_hand_list = []
        self.right_hand_list = []
        self.pose_list = []

        # Dictionary storing the SignModels of the reference signs
        self.sign_dictionary = sign_dictionary
        # Dictionary storing the distances between this SignModel object & the reference signs
        self.sign_distances = sign_distances

    def record(self):
        self.recording = True

    def process_results(self, results):
        if self.recording:
            if len(self.pose_list) < self.seq_len:
                self.record_movement(results)
            else:
                self.compute_distances()
        return self.sign_distances

    def record_movement(self, results):
        # Record landmarks
        pose, left_hand, right_hand = extract_keypoints(results)
        self.left_hand_list.append(left_hand)
        self.right_hand_list.append(right_hand)
        self.pose_list.append(pose)

        # Red circle while recording
        self.color = RED_COLOR

    def compute_distances(self):
        # Create a SignModel object with the landmarks gathered during recording
        recorded_sign = SignModel(self.pose_list, self.left_hand_list, self.right_hand_list)

        # Compute sign similarity with DTW (descending order)
        self.sign_distances = dtw_distances(recorded_sign, self.sign_dictionary)

        # Reset variables
        self.left_hand_list = []
        self.right_hand_list = []
        self.pose_list = []
        self.recording = False
        self.color = BLUE_COLOR

