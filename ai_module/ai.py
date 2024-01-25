import mediapipe as mp
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, HandLandmarkerResult, RunningMode
import cv2
import numpy as np
import math


landmarks = HandLandmarkerResult(handedness=[], hand_landmarks=[], hand_world_landmarks=[])

def recognition_handler(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global landmarks
    landmarks = result

model_path = '../assets/hand_landmarker_model.task'

options = HandLandmarkerOptions(
base_options= BaseOptions(model_asset_path=model_path),
running_mode= RunningMode.LIVE_STREAM,
num_hands= 1,
min_hand_detection_confidence=0.3,
min_hand_presence_confidence=0.3,
result_callback= recognition_handler)


if __name__ == "__main__":

    vid = cv2.VideoCapture(0)     

    landmarker = HandLandmarker.create_from_options(options)

    while(True): 

        ret, frame = vid.read()

        timestamp_ms = vid.get(cv2.CAP_PROP_POS_MSEC)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data= np.array(frame))
        landmarker.detect_async(mp_image, int(timestamp_ms))
        
        # hand detected
        if(landmarks.hand_landmarks!=[]):

            # landmarks coloration
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (100, 200, 100), (70, 140, 120), (255, 255, 0)] 
            for i, landmark in enumerate(landmarks.hand_landmarks[0]):
                center = (int(landmark.x*frame.shape[1]), int(landmark.y*frame.shape[0]))
                color_index = math.ceil(i/4)
                cv2.circle(frame, center, 2, colors[color_index], 2)

            # shoot detector
            # index tip near the hand center
            index_tip_relative_hand_center = landmarks.hand_world_landmarks[0][4]
            if(abs(index_tip_relative_hand_center.y) <0.041):
                cv2.putText(frame, "shoot", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
            else:
                # index movment detector
                # relative distance between tip and ip
                index_tip_relative_image = landmarks.hand_landmarks[0][4]
                index_ip_relative_image = landmarks.hand_landmarks[0][3]
                if(index_tip_relative_image.x-index_ip_relative_image.x>0.02):
                    cv2.putText(frame, "left", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
                elif(index_tip_relative_image.x-index_ip_relative_image.x<-0.02):
                    cv2.putText(frame, "right", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
                else:
                    cv2.putText(frame, "stright", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))

        cv2.imshow('frame', frame) 
        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # release
    vid.release() 
    cv2.destroyAllWindows() 
    landmarker.close()