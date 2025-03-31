from robotController import RobotController
from langchain_ollama import ChatOllama
from langchain.agents import tool
from rosa import ROSA, RobotSystemPrompts
from pyniryo import *

robot = RobotController('192.168.0.140')

exampleConversation = "*User:* Hello, what are you? , *Robot:* Hello, I am the control service for the Niryo Ned 2 robot arm., *User:* What can you do?, *Robot:* I can control the Niryo Ned 2. I can pick up and place objects. The robot operates in a space where the x, y, and z values are between 0 and 1. I need all six, values (x, y, z, roll, yaw, pitch) for each action., *User:* Pick up all the red objects., *Robot:* Calling findCoordinatesAndRotationsForObject('red_object')., *Robot:* findCoordinatesAndRotationsForObject('red_object') returns: x=0.3, y=0.2, z=0 05, roll=0.1, yaw=0.2, pitch=0.3, *Robot:* Calling pick_up(x=0.3, y=0.2, z=0.05, roll=0.1, yaw=0.2, pitch=0.3)., *Robot:* Calling findCoordinatesAndRotationsForObjec ('red_object')., *Robot:* findCoordinatesAndRotationsForObject('red_object') returns: x=0.6, y=0.7, z=0.04, roll=0.4, yaw=0.5, pitch=0.6, *Robot:* Calling pick_up(x=0.6, y=0 7, z=0.04, roll=0.4, yaw=0.5, pitch=0.6)., *Robot:* Calling findCoordinatesAndRotationsForObject('red_object')., *Robot:* findCoordinatesAndRotationsForObject('red_object') returns: None., *Robot:* All red objects have been picked up., *User:* Good. Place the red circle on the blue square., *Robot:* Calling findCoordinatesAndRotationsForObjec ('red_circle')., *Robot:* findCoordinatesAndRotationsForObject('red_circle') returns: x=0.1, y=0.5, z=0.06, roll=0.7, yaw=0.8, pitch=0.9., *Robot:* Calling findCoordinatesAndRotationsForObject('blue_square')., *Robot:* findCoordinatesAndRotationsForObject('blue_square') returns: x=0.8, y=0.2, z=0.09, roll=1.0, yaw=1.1, pitch=1 2., *Robot:* Calling place_down(x=0.8, y=0.2, z=0.09, roll=1.0, yaw=1.1, pitch=1.2). (z was adjusted), *Robot:* Task completed. Are the results okay?, *User:* Yes, everything is okay., *Robot:* Good." 


#llama3-groq-tool-use 
#MFDoom/deepseek-r1-tool-calling:14b
#llama3.1:8b"

llm = ChatOllama(
    model="MFDoom/deepseek-r1-tool-calling:14b",  
    temperature=0,
    num_ctx=9000,  
)

def main():
    print("-----------PROGRAM STARTING-----------")
    
    ned, workspace_name = robot.connect()
    prompts = RobotSystemPrompts(
        embodiment_and_persona="You're in charge of controlling the Niryo Ned 2 robot arm. Your job is to make it pick up and place objects based on commands you get from a user. When a user gives you a command (like 'Pick up all the blue objects' or 'Put the blue circle on the green square'), you need to find the objects the user is talking about and tell the robot what to do.First, use findCoordinatesAndRotationsForObject('object_name') to get information about one object: its x, y, and z position, and roll, yaw, and pitch angles. This toofinds one object at a time. Then, use pick_up(x, y, z, roll, yaw, pitch) or place_down(x, y, z, roll, yaw, pitch), using the newly found values. The robot then does ittask.  It's critical that the robot uses the new coordinates each time and never re-uses old onesFor example, if the user says 'Get all blue objects'    Call findCoordinatesAndRotationsForObject('blue_object')    Let's say you get back: x= 0.22, y= -0.12, z = 0.085, yaw= 1.5, roll= -1.3, pitch= 0.9    Call pick_up(x= 0.22, y= -0.12, z= 0.085, yaw= 1.5, roll= -1.3, pitch= 0.9)    Immediately call findCoordinatesAndRotationsForObject('blue_object') again. This will return new coordinates    Let's say you get back: x= 0.4, y= -0.89, z = 0.085, yaw= 1.2, roll= 1.0, pitch= 1.2    Call pick_up(x= 0.4, y= -0.89, z = 0.085, yaw= 1.2, roll= 1.0, pitch= 1.2). The robot must use these new coordinates    Repeat the find-and-immediately-pick-up process, using the newly returned coordinates each time, until findCoordinatesAndRotationsForObject('blue_object') returns NoneFor example, if the user says 'Put the blue circle on the green square'    Call findCoordinatesAndRotationsForObject('blue_circle')    Let's say you get back: x= 0.22, y= -0.12, z = 0.085, yaw= 1.5, roll= -1.3, pitch= 0.9    Call findCoordinatesAndRotationsForObject('green_square')    Let's say you get back: x= 0.7, y= -0.5, z = 0.09, yaw= 0.2, roll= 0.1, pitch= 0.3    Call pick_up(x= 0.22, y= -0.12, z= 0.085, yaw= 1.5, roll= -1.3, pitch= 0.9)    Call place_down(x= 0.7, y= -0.5, z = 0.09, yaw= 0.2, roll= 0.1, pitch= 0.3)For example, if the user says 'Pick up all green objects' (and doesn't specify a place)    Call findCoordinatesAndRotationsForObject('green_object')    Let's say you get back: x= 0.1, y= 0.2, z = 0.05, yaw= 0.5, roll= 0.2, pitch= 0.1    Call pick_up(x= 0.1, y= 0.2, z = 0.05, yaw= 0.5, roll= 0.2, pitch= 0.1)    Immediately call findCoordinatesAndRotationsForObject('green_object') again    Let's say you get back: x= 0.3, y= 0.7, z = 0.06, yaw= 1.0, roll= -0.1, pitch= 0.3    Call pick_up(x= 0.3, y= 0.7, z = 0.06, yaw= 1.0, roll= -0.1, pitch= 0.3)    Immediately call findCoordinatesAndRotationsForObject('green_object') again    Let's say you get back: x= 0.8, y= 0.15, z = 0.07, yaw= -0.2, roll= 0.5, pitch= 0.2    Call pick_up(x= 0.8, y= 0.15, z = 0.07, yaw= -0.2, roll= 0.5, pitch= 0.2)    Immediately call findCoordinatesAndRotationsForObject('green_object') again    Let's say it returns None. This means there are no more green objectsImportant: Because findCoordinatesAndRotationsForObject finds one object at a time, you must pick up the current object before searching for the next. The detection modewill likely keep returning the same object if it's not picked up. If no place_down is specified, the robot will hold the objects. Always use the newly found coordinatesnever old onesIf you're picking up or placing multiple objects, repeat the 'find and immediately act' steps until findCoordinatesAndRotationsForObject returns None. The robot works in space where x, y, and z values are between 0 and 1. It needs all six input values for every action. After a task, delete the object's coordinates from memory. Keecommunication brief. When done, ask if the results are okay."
    )
    
    rosa = ROSA(ros_version=1, llm=llm, tools=[pick_up, place_down, findCoordinatesAndRotationsForObject], prompts=prompts, verbose=True)

    while True:
        print("Bitte wählen Sie:")
        print("1. Objekt aufheben")
        print("2. Objekt ablegen")
        print("3. Rosa Befehl")
        print("4. Beenden")
        choice = input("Ihre Wahl: ")

        if choice == '1':
            object_name = input("Welches Objekt möchten Sie aufheben? ")
            # Get the object's pose and store it in the dictionary
            pick_pose = robot.getPickPoseForObject(object_name)
            if pick_pose is not None: 
                robot.pick_target_up(pick_pose)
                print(f"Objekt '{object_name}' wurde aufgehoben.")
            else:
                print(f"Objekt '{object_name}' nicht gefunden.")

        elif choice == '2':
            object_name = input("Wohin möchten sie das Objekt legen? ")
            # Get the object's pose and store it in the dictionary
            pick_pose = robot.getPickPoseForObject(object_name)
            if pick_pose is not None: 
                robot.pick_target_up(pick_pose)
                print(f"Objekt '{object_name}' wurde aufgehoben.")
            else:
                print(f"Objekt '{object_name}' nicht gefunden.")
        elif choice == '3':
            order = input("Was soll ROSA machen? ")
            print("Rosa is invoking...")
            result = rosa.invoke(order)  # Store the result of rosa.invoke
            print(f"Rosa finished. Result: {result}") # Print result
        elif choice == '4':
            print("Programm wird beendet.")
            break
        else:
            print("Ungültige Eingabe. Bitte wählen Sie 1, 2, 3 oder 4.")

@tool
def findCoordinatesAndRotationsForObject(object_name: str) -> str:
    """
    Finds the coordinates and rotations the robot needs to pick up the object it is looking for 

    :param object_name: The name of the target object.
    """
    print(f"Searching for pick pose for object: {object_name}")

    pickPose = robot.getPickPoseForObject(object_name)

    print("-----------------------returned PickPose:------------------------")
    print(pickPose)
    

    if pickPose is not None:
        return f"Found the object at the new values: x: {pickPose.x:.5f}, y:{pickPose.y:.5f},z:{pickPose.z:.5f},roll:{pickPose.roll:.5f},pitch:{pickPose.pitch:.5f},yaw:{pickPose.yaw:.5f} with the name {object_name}"
    else:
        print(f"Couldnt find Pose: {pickPose}")
        return f"Found no object with the name {object_name}"


@tool
def pick_up(x: float, y: float, z:float, roll:float, pitch:float, yaw:float, name:str) -> str:
    """
    Using the coordinates and rotations found for the object with the name, the robot then picks it up. But it needs the coordinates and the rotations.
    The robot needs all the coordinates and rotations determined by the tool 'findCoordinatesAndRotationsForObject' or it cant pick up the object.
    The name of the object is the same that was searched by the tool 'findCoordinatesAndRotationsForObject'

    :param x: The x-coordinate the roboter needs.
    :param y: The y-coordinate the roboter needs.
    :param z: The z-coordinate the roboter needs.
    :param roll: The rotation around the x-axis in radians the roboter needs.
    :param pitch: The rotation around the y-axis in radians the roboter needs.
    :param yaw: The rotation around the z-axis in radians the roboter needs.
    :param name: The name of the object to be picked up.
    """
    print(f"-----------------------Pick up with Object with the name: {name}")
    print(x,y,z,roll,pitch,yaw)

    robot.pick_target_up(
        PoseObject(
            x=float(x),
            y=float(y),
            z=0.085,
            roll=float(roll),
            pitch=float(pitch),
            yaw=float(yaw),
        )
    )

    return f"Succesfully picked up the object for the: {x}, y:{y},z:{z},roll:{roll},pitch:{pitch},yaw:{yaw}, with the name {name}"


@tool
def place_down(x: float, y: float, z:float, roll:float, pitch:float, yaw:float, name:str) -> str:
    """
    Place down the currently held object at the specified location. 
    Can be used to place an object at the location of another object 
    by using the coordinates and orientation obtained from `findCoordinatesAndRotationsForObject`.

    :param x: The x-coordinate of the target location.
    :param y: The y-coordinate of the target location.
    :param z: The z-coordinate of the target location.
    :param roll: The rotation around the x-axis in radians.
    :param pitch: The rotation around the y-axis in radians.
    :param yaw: The rotation around the z-axis in radians.
    :param name: The name of the target location or object.
    """

    print(f"-----------------------Place down the PoseObject with the name: {name}")
    print(x,y,z,roll,pitch,yaw)

    robot.place_on_target(
        PoseObject(
            x=float(x),
            y=float(y),
            z=0.11,
            roll=float(roll),
            pitch=float(pitch),
            yaw=float(yaw),
        ))

    return f"Succesfully placed down the object at the values: x:{x}, y:{y},z:{z},roll:{roll},pitch:{pitch},yaw:{yaw}, with the name {name}"

if __name__ == "__main__":
    main()