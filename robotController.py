from pyniryo import NiryoRobot
from detectionService import DetectionService
import time
import cv2
import numpy as np

class RobotController:
        
    def __init__(self, robot_ip):
        self.robot_ip = robot_ip
        self.ned = None 
        self.workspace_name = "niryo_ws"  
        self.offset_x = 0.003
        self.offset_y = 0.003
        self.offset_z_pick = 0.085
        self.offset_z_place = 0.095
        

    def connect(self):
        self.ned = NiryoRobot(self.robot_ip)
        print("calibrating")
        self.ned.calibrate_auto()
        self.detectionService = DetectionService(self.ned)

        return self.ned, self.workspace_name
    
    def disconnect(self):
      if self.ned:
          self.ned.close_connection()
          print("Verbindung zum Roboter wurde getrennt.")
    
    def get_robot_instance(self):
      return self.ned
    
    def get_workspace_name(self):
      return self.workspace_name
    
    def move_to_start_position(self):
        if self.ned:
          print("moving to start position")
          self.ned.move_joints(0.0,0.0,-0.85,0.0,-1.0,0.0)

    def get_image(self):
          compressed_image = self.ned.get_img_compressed()
          image = np.asarray(bytearray(compressed_image), dtype="uint8")
          image = cv2.imdecode(image, cv2.IMREAD_COLOR)
          
          # Here, you can use cv2 on the variable image
          cv2.imshow("Niryo Image", image)
          cv2.waitKey(0)

    def getPickPoseForObject(self, targetObject):
       if self.ned:
          self.move_to_start_position()
          middle_point, angle = self.detectionService.findPositionOfObject(targetObject) 
          if middle_point is not None and angle is not None:
            pick_pose = self.ned.get_target_pose_from_rel(self.workspace_name,1,middle_point[0],middle_point[1],0)
            pick_pose.z = self.offset_z_pick
            pick_pose.x = pick_pose.x + self.offset_x
            pick_pose.y = pick_pose.y + self.offset_y
            pick_pose.yaw = -angle
          else: 
             print("nichts gefunden")
             return None
       else:
            print("Robot not connected")
       return pick_pose
    
    def pick_target_up(self, pickPose):
        if self.ned:
          self.ned.pick_from_pose(pickPose)
          """Führt eine Pick-Operation mit der gegebenen Pose aus."""
        else:
            print("Robot not connected")
      

    def place_on_target(self, pickPose):
        if self.ned:
          self.ned.place_from_pose(pickPose)
          """Führt eine Pick-Operation mit der gegebenen Pose aus."""
        else:
            print("Robot not connected")
