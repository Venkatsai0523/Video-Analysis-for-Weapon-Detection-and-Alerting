import cv2
import numpy as np
import pygame
import os

# Initialize pygame mixer
pygame.mixer.init()

# Load the sound file
sound_file = "alert.mp3"
if not os.path.isfile(sound_file):
    raise FileNotFoundError(f"No file '{sound_file}' found in the working directory '{os.getcwd()}'.")

alert_sound = pygame.mixer.Sound(sound_file)

# Load Yolo
net = cv2.dnn.readNet("yolov3_training_2000.weights", "yolov3_testing.cfg")
classes = ["Weapon"]
# with open("coco.names", "r") as f:
#     classes = [line.strip() for line in f.readlines()]

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

# Enter file name for example "ak47.mp4" or press "Enter" to start webcam
def value():
    val = input("Enter file name or press enter to start webcam: \n")
    if val == "":
        val = 0
    return val

# for video capture
cap = cv2.VideoCapture(value())

while True:
    ret, img = cap.read()
    if not ret:
        break
    
    height, width, channels = img.shape
    
    # Detecting objects
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Showing information on the screen
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    
    if len(indexes) > 0:
        alert_sound.play()  # Play sound alert when a weapon is detected

    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = colors[class_ids[i]]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label, (x, y + 30), font, 3, color, 3)
    
    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
