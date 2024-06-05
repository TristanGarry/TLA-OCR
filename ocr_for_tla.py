import pytesseract
import cv2
from PIL import Image
import numpy as np
import os
import csv


# Tesseract location for MacOS when installed through brew
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'


def preprocess_image(image, roi):
    x, y, w, h = roi
    cropped_image = image[y:y+h, x:x+w]
    return cropped_image

def preprocess_for_names(roi_image):
    gray_image = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
    resized_image = cv2.resize(gray_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return resized_image

def preprocess_for_characters(roi_image):
    gray_image = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)

    # Increase contrast and adjust brightness
    alpha = 1.5  # Contrast control (1.0-3.0)
    beta = 0    # Brightness control (0-100)
    adjusted_image = cv2.convertScaleAbs(gray_image, alpha=alpha, beta=beta)
    
    # Apply dilation and erosion
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    dilated = cv2.dilate(adjusted_image, kernel, iterations=1)
    eroded = cv2.erode(dilated, kernel, iterations=1)
    
    # Invert the image
    inverted_image = cv2.bitwise_not(eroded)

    resized_image = cv2.resize(inverted_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return resized_image


def extract_player_info(image_path):
    image = cv2.imread(image_path)
    extracted_info = {}

    roi_characters = {
        "player_1_character": (305, 110, 60, 19),
        "player_2_character": (1096, 109, 60, 22),
    }

    roi_names = {
        "player_1_name": (291, 657, 228, 34), 
        "player_2_name": (939, 658, 227, 32),
    }
    for key, roi in roi_names.items():
        preprocessed_roi = preprocess_image(image, roi)
        preprocessed_ocr = preprocess_for_names(preprocessed_roi)
        roi_image = Image.fromarray(preprocessed_ocr)
        custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 "'
        text = pytesseract.image_to_string(roi_image, config=custom_config)
        extracted_info[key] = text.strip()
    for key, roi in roi_characters.items():
        preprocessed_roi = preprocess_image(image, roi)
        preprocessed_ocr = preprocess_for_characters(preprocessed_roi)
        roi_image = Image.fromarray(preprocessed_ocr)
        custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist="BeefPorkOnionGarlicRiceNoodle"'
        text = pytesseract.image_to_string(roi_image, config=custom_config)
        extracted_info[key] = text.strip()
    return extracted_info

def process_video(video_path, frames_folder, output_csv):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    success, frame = cap.read()
    count = 0
    if not os.path.exists(frames_folder):
        os.makedirs(frames_folder)

    # # Uncomment the following if you need to process your video
    # while success:
    #     if count % 2000 == 0:
    #         frame_path = os.path.join(frames_folder, f"frame_{count}.jpg")
    #         cv2.imwrite(frame_path, frame)
    #     success, frame = cap.read()
    #     count += 1
    # cap.release()
    
    # Comment this out if you're not me
    count = 592000

    win_data = []

    for i in range(2000, count, 2000):
        frame_path = os.path.join(frames_folder, f"frame_{i}.jpg")
        player_info = extract_player_info(frame_path)
        if player_info:
            win_data.append({
                "win_frame": frame_path,
                "player_1_name": player_info["player_1_name"],
                "player_1_character": player_info["player_1_character"],
                "player_2_name": player_info["player_2_name"],
                "player_2_character": player_info["player_2_character"]
            })

    cap.release()

    # Write to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ["win_frame", "player_1_name", "player_1_character", "player_2_name", "player_2_character"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in win_data:
            writer.writerow(row)

# Path to the video
video_path = 'output_videos.mp4'
frames_folder = 'frames_folder'

process_video(video_path, frames_folder, "test.csv")
