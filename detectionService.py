import cv2
import numpy as np
from fastsam import FastSAM, FastSAMPrompt
from pyniryo import image_functions

class DetectionService:

    def __init__(self, robotController):
        self.model = FastSAM("FastSAM-x.pt")
        # Öffne die Webcam
        self.cap = cv2.VideoCapture(0)
        # --- Configuration ---
        self.movement_threshold = 1  # Maximum allowed offset in x and y
        self.consecutive_frames_threshold = 3  # Number of frames with stable center
        self.previous_centers = []
        self.robotController = robotController
        self.minAreaPixels = 600

    def getAllMasksWithCenterAndName(self):
         
         return 
         
    # Funktion zur Umwandlung von Masken in boolesche Werte
    def masks_to_bool(self, masks):
        if type(masks) == np.ndarray:
            return masks.astype(bool)
        return masks.cpu().numpy().astype(bool)

    def findPositionOfObject(self, targetObject):
        self.cap.release()
        self.cap = cv2.VideoCapture(0)
        self.previous_centers = [] # Reset previous centers at the start of each call

        while True:
            ret, frame = self.cap.read()
            if not ret:
                return None, None # Return None if no frame is read

            frame = image_functions.extract_img_workspace(frame, 1)
            everything_results = self.model(frame, device='cpu', retina_masks=True, imgsz=200, conf=0.4, iou=0.9)
            prompt_process = FastSAMPrompt(frame, everything_results, device='cpu')

            ann = prompt_process.text_prompt(text=targetObject)

            mask = self.masks_to_bool(ann)
            mask = mask.reshape(200, 200)

            contours, hierarchy = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if len(contours) > 0:
                
                largest_contour_idx = np.argmax([cv2.contourArea(cnt) for cnt in contours])
                largest_contour = contours[largest_contour_idx]

                barry_center = image_functions.get_contour_barycenter(largest_contour)
                angle = image_functions.get_contour_angle(largest_contour)
                cx, cy = barry_center

                areaPixels = cv2.contourArea(largest_contour)
                print(f"das sind die areaPixels: {areaPixels}")
                if areaPixels < self.minAreaPixels:
                    print("area pixel nichts gefunden")
                    return None, None

                if len(self.previous_centers) < self.consecutive_frames_threshold:
                    self.previous_centers.append((cx, cy))
                else:
                    movements = [
                        max(abs(cx - prev_center[0]), abs(cy - prev_center[1]))
                        for prev_center in self.previous_centers
                    ]
                    if all(movement <= self.movement_threshold for movement in movements):
                        middle_point = image_functions.relative_pos_from_pixels(frame, barry_center[0], barry_center[1])
                        print("habe was gefunden")
                        return middle_point, angle  # Return immediately when stable
                    else:
                        self.previous_centers = []  # Reset if movement exceeds threshold
            else:  # Handle the case where no contours are found
                self.previous_centers = []  # Reset if no object is found
                # Optionally, you could return None, None here as well, depending on desired behavior.
                # For example: return None, None  # No object detected in this frame.
                print("nichts gefunden im detection service")
                return None, None

     