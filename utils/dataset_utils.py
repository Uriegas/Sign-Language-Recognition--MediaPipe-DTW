import os

import pandas as pd
from tdqm import tdqm

from models.sign_model import SignModel
from utils.landmark_utils import save_landmarks_from_video, load_array


def load_dataset():
    videos = [
        file_name.replace(".mp4", "")
        for root, dirs, files in os.walk(os.path.join("data", "videos"))
        for file_name in files
        if file_name.endswith(".mp4")
    ]
    dataset = [
        file_name.replace(".pickle", "").replace("pose_", "")
        for root, dirs, files in os.walk(os.path.join("data", "dataset"))
        for file_name in files
        if file_name.endswith(".pickle") and file_name.startswith("pose_")
    ]

    # Create the dataset from the reference videos
    videos_not_in_dataset = list(set(videos).difference(set(dataset)))
    n = len(videos_not_in_dataset)
    if n > 0:
        print(f"Extracting landmarks from new videos: {n} videos detected\n")

        for video_name in tdqm(range(n)):
            save_landmarks_from_video(video_name)

    return videos


def load_reference_signs(videos):
    reference_signs = pd.DataFrame(columns=["name", "sign_model", "distance"])
    for video_name in videos:
        sign_name = video_name.split("-")[0]
        path = os.path.join("data", "dataset", sign_name, video_name)

        left_hand_list = load_array(os.path.join(path, f"lh_{video_name}.pickle"))
        right_hand_list = load_array(os.path.join(path, f"rh_{video_name}.pickle"))

        reference_signs = reference_signs.append(
            {
                "name": sign_name,
                "sign_model": SignModel(left_hand_list, right_hand_list),
                "distance": 0,
            },
            ignore_index=True,
        )
    print(
        f'Dictionary count: {reference_signs.drop["sign_model"].groupby(["name"]).count()}'
    )
    return reference_signs