import mediapipe as mp
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, HandLandmarkerResult, RunningMode
import cv2
from cv2 import VideoCapture
import numpy as np
import math
import sys
from enum import Enum
import time
import threading


class Controlles(Enum):
    LEFT = 1
    RIGHT = 2
    SHOOT = 3
    STRAIGHT = 4

class AIController:

    def __init__(self, camera_stream: VideoCapture, model_path: str, show_camera_window: bool) -> None:
        self.camera_stream = camera_stream
        self.detector = self.__prepareModel__(model_path)
        self.hand_landmarks = None
        self.hand_world_landmarks= None
        self.show_camera_window= show_camera_window
        self.hand_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (100, 200, 100), (70, 140, 120), (255, 255, 0)] 


    def control(self) -> Controlles:

        # read a frame
        if(not self.camera_stream.isOpened()):
            print("There is a problem in the camera device")
            sys.exit()

        # print("control")
        ret, frame = self.camera_stream.read()
        
        timestamp_ms = self.camera_stream.get(cv2.CAP_PROP_POS_MSEC)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data= np.array(frame))

        # detect handedness
        self.detector.detect_async(mp_image, int(timestamp_ms))

        # detect movement
        movement = self.__infere_movement__()

        # show camera window
        if(self.show_camera_window):
            # add annotations
            self.__annotate_hand__(frame)
            self.__annotate_control__(frame, movement)
            cv2.imshow('frame', frame) 

        return movement

        
    def __infere_movement__(self) -> Controlles:
        if(self.hand_landmarks == None):
            return Controlles.STRAIGHT

        # index tip near the hand center
        index_tip_relative_hand_center = self.hand_world_landmarks[4]
        if(abs(index_tip_relative_hand_center.y) <0.04):
            return Controlles.SHOOT
        else:
            # index movment detector
            # relative distance between tip and ip
            index_tip_relative_image = self.hand_landmarks[4]
            index_ip_relative_image = self.hand_landmarks[3]
            if(index_tip_relative_image.x-index_ip_relative_image.x>0.02):
                return Controlles.LEFT
            elif(index_tip_relative_image.x-index_ip_relative_image.x<-0.02):
                return Controlles.RIGHT
            else:
                return Controlles.STRAIGHT

    def __annotate_hand__(self, frame: cv2.Mat) -> None:
        if(self.hand_landmarks!= None):
            for i, landmark in enumerate(self.hand_landmarks):
                center = (int(landmark.x*frame.shape[1]), int(landmark.y*frame.shape[0]))
                color_index = math.ceil(i/4)
                cv2.circle(frame, center, 2, self.hand_colors[color_index], 2)

    def __annotate_control__(self, frame: cv2.Mat, movement: Controlles) -> None:
        cv2.putText(frame, movement.name, (10, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,0), 1)
    
    def __detection_handler__(self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int ) -> None:
        if(result.hand_landmarks!=[]):
            self.hand_landmarks = result.hand_landmarks[0]
            self.hand_world_landmarks = result.hand_world_landmarks[0]
        else:
            self.hand_landmarks = None
            self.hand_world_landmarks = None
        

    def __prepareModel__(self, model_path: str) -> HandLandmarker:
        options = HandLandmarkerOptions(
        base_options= BaseOptions(model_asset_path=model_path),
        running_mode= RunningMode.LIVE_STREAM,
        num_hands= 1,
        min_hand_detection_confidence=0.3,
        min_hand_presence_confidence=0.3,
        result_callback= self.__detection_handler__)
        return HandLandmarker.create_from_options(options)

    def close(self)-> None:
        self.camera_stream.release()
        cv2.destroyAllWindows()
        self.detector.close()