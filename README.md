# inTellogence

![Header](imgs/inTellogence_logo.PNG)

# Table of Contents

- [inTellogence](#intellogence)
- [Table of Contents](#table-of-contents)
- [About](#about)
- [Introduction](#introduction)
  - [Features](#features)
  - [System Overview](#system-overview)
- [Getting Started](#getting-started)
  - [Router and Drone Connection](#router-and-drone-connection)
  - [Necessary Installations](#necessary-installations)
    - [Verify that your GPU is supported by CUDA](#verify-that-your-gpu-is-supported-by-cuda)
    - [Download and install Cuda (11.8)](#download-and-install-cuda-118)
    - [Environment Setup](#environment-setup)
  - [Mission Pad Setup](#mission-pad-setup)
- [Examples](#examples)
- [Performance](#performance)
- [Recommendations](#recommendations)
- [Supplemental Documentation](#supplemental-documentation)
- [Troublehooting resources](#troublehooting-resources)
- [References](#references)
- [Acknowledgements](#acknowledgements)

# About
<p>Drones are quickly becoming utilized in the public sphere for entertainment, photography, surveillance, high-speed delivery, and remote healthcare. InTellogence is an open-source codebase made to supplement self-education for university students and hobbyists exploring drone control topics, using the low-cost DJI Tello Edu. It integrates multi-drone centralized control, computer vision, functional safety, and a custom Graphical User Interface (GUI). All code is written in Python, powered by popular packages such as OpenCV, Flet, and NVIDIA’s CUDA. InTellogence ultimately lowers the barrier of entry to drone robotics through detailed documentation and easily modified design. We hope that students or people enthusiastic about drones are able to gain new knowledge through this repository and possibly contribute to it.</p>

<div style="text-align: center;">
<img style="max-width:95%;border:5px solid black;" src="imgs/diagram_topics.png" width="500" class="center"> 
</div>

# Introduction
<p>InTellogence is a codebase that incorporates autonomous navigation features, computer vision capabilities, centralized control via a router, a custom user interface, and functional safety engineering concepts. 
This is written for students who have at least a basic understanding of python programming and would like to learn more about concepts within the realms of various drone capabilities.
The best way to use this repository is by forking a copy over and following the setup steps covered in <a href=#getting-started> Getting Started</a>. Please also take some time to peruse this document. Due to project requirements, this ReadMe contains a lot more information about project structure than most.
Once the user attains a good understanding of the codebase and have read through the <a href=#examples>examples</a>, they can begin to create their own behaviors and states.
</p>

## Features

inTellogence has the following features:
- Ability to control 1 or 2 drones through a router
- Use of Tello Mission Pads to keep the drone within a constrained airspace
- Finite state machine that uses <a href = https://youtu.be/umkyPWDrys4>potential fields navigation</a>
- Additional safety measures using industry-relevant functional safety techniques
- Integration of <a href="https://github.com/ultralytics/ultralytics"> Ultralytics Yolov8</a> for object recognition
- Ability to quickly implement and layer reactive behaviors to objects and sensor readings
- [Flet](https://flet.dev)-powered GUI using Python
- Easy-to-understand documentation

If you are interested in learning about the development of our features based off of the projected needs of our "Users", feel free to check out the Software Requirements materials in <a href=#supplemental-documentation>Supplemental Documentation</a>.

## System Overview
<p>inTellogence forms a wrapper around the low level Tello class, from the <a href=https://github.com/damiafuentes/DJITelloPy>DJITelloPy</a> library, with some minor edits to the source code. Otherwise the structure of our repository can be seen in the abbreviated UML below. GUI classes are optional, and main files to run with the gui, with a swarm, and with a single drone are provided in the repository. </p>

<div style="text-align: center;">
  <img src="imgs/uml.png" width="700"></div><br>

<p>Further details about the design are detailed in the dropdowns below.</p>

<details><summary>Graphic User Interface (GUI)</summary><br>
  <p>inTellogence uses <a href="https://flet.dev">Flet</a>, a simplified <a href="https://flutter.dev">Flutter</a> model, to build the GUI. Python is currently supported, but Go and C# are <a href="https://flet.dev/roadmap/">coming soon</a>.
  </p> 

<p>There are two distinct GUI pages. First, the connection page allows you to input device information by running <i>connectivity_page.py.</i> This brings up a connection setup page, where the user can easily input device information for each drone.</p><br> 

<div style="text-align: center;">
  <img src="imgs/connection_page.png" width="500"></div><br>

<p>After verifying that the drone(s) are connected, the user can continue to a Main Dashboard that displays the drone video feed, text input for chosen object identification, control buttons, and a reaction (detailed later) manager.</p> <br> 

<div style="text-align: center;">
<img src="imgs/drone_screenshot.PNG" width="500">
</div><br>

<p>The GUI uses the following components</p><br>

<summary><b>Multi-threading</b></summary>
<br>
We use threading to allow the GUI to access drone functions while the drone flight algorithm is running. This becomes a problem if the threads try to read/write the same piece of memory at the exact same time, but the chances of this happening are low for this project.<br><br>

<summary><b>Drone video feed through Flet</b></summary>
<br>
The code from <a href="https://www.youtube.com/watch?v=58aPh8rKKsk">Azu Technology</a> that creates a modern GUI for an OpenCV window was modified to display the Tello video stream through the GUI. This repository is one of few, if not the only, that allows the Tello streaming window to be viewed through Flet.<br><br>
</details>

<details>
<summary>Finite State Machine</summary>
  <br><p>General control of both drones is organized around a Finite State Machine (FSM). The primary state of wander is implemented alongside a few states that support smooth and safe operation. The general control logic is shown below.</p><br>

<div style="text-align: center;">
<img src="imgs/control_loop.png" width="1000">
</div>
</details> 

<details>
<summary>Reactive Control Through Potential Fields</summary><br>
  <p>The primary path planning approach for InTellogence lies in <a href = https://youtu.be/umkyPWDrys4>reactive control through potential fields</a>. In order to allow the drones to wander in a constrained space, Tello mission pads are utitilized in a pre-defined map. These mission pads allow the drone to localize and respond appropriately when moving out of intended airspace, applying a movement force proportional to it's measured distance outside of desired airspace. If you're interested in the linear algebra behind this, check out Coordinate Modelling in <a href=#supplemental-documentation>Supplemental Documentation</a></p>


<div style="text-align: center;"><img src="imgs/boundary_force.png" width="300"></div><br> 

InTellogence provides an outline for implementing various reactions to certain stimuli. For our purposes, reactions are individual responses to certain stimuli (ie, the drone detects a banana) and behaviors are sets of those reactions. We have defined two types of reactions: blocking and movement. <br>

A blocking reaction initiates a pre-defined set of instructions, during which the drone is incapable of performing any other movements. The stimuli trigger blocks the continuation of the control loop for a time. <br>

A movement reaction defines non-blocking instructions. So, it returns a movement vector according to the same idea as potential fields. Hence, a drone could tend to fly toward certain objects or away from others. <br>
</details> 

<details>
<summary>Object Recognition using Yolov8</summary>
<br>

InTellogence performs object recognition by implementing <a href="https://github.com/ultralytics/ultralytics"> Ultralytics Yolov8 </a>. All video feed analysis is abstracted out into the VideoAnalyzer class from <i>video_analyzer.py</i>. This wrapper class adds the ability to automatically download all object recognition models, as well as adjust the model size (speed/accuracy tradeoff), and acceptable confidence level. To explore the other models available using Yolov8 (pose, image segmentation, etc), consider editing <i>video_analyzer.py</i>.<br>

The output of the network can be slightly confusing (this article was helpful determining syntax <a href=""> here</a>.)
To access results in the form of an Nx6 matrix, use syntax along the lines of results[0].boxes.boxes The indexes are shown below: <br>

0: x1 bounding box coordinate<br>
1: y1 boudning box coordinate<br>
2: x2 bounding box coordinate<br>
3: y2 bounding box coordinate<br>
4: confidence score<br>
5: class label<br>

In order to speed up this detection process, this repository assumes the use of CUDA 11.8. This offloads the inference calculations to the GPU, where it can be parallelized. Installation instructions can be found in [Getting Started](#getting-started). Yolov8 allows for very minimal setup in this respect.<br>

</details> 

<details>
<summary>Functional Safety Engineering</summary>
<br>
<p><a href="https://www.61508.org/knowledge/what-is-a-functional-safety-system.php">Functional Safety Engineering</a> provides users exposure and a framework to implement various safety features that they deem necessary. Functional Safety involves developing safety-related systems for the Electronic/Electrical/Programmable Electronic components of a system. <a href="https://www.61508.org/knowledge/what-is-iec-61508.php">IEC61508</a>, <a href="https://webstore.iec.ch/publication/24241">IEC61511</a>, <a href="https://webstore.iec.ch/publication/59927">IEC62061</a>, and <a href="https://www.iso.org/standard/43464.html">ISO26262</a> are the standards of reference we use for Functional Safety Engineering.</p>

<p>Safety-Related systems usually comprise of a sensor that provides information, a processor that provides logic to react to sensor readings, and an actuator or system component that provides output based on this logic. These are the types of systems that are studied to identify potential risks and then deliver an appropriate solution that provides the appropriate level of risk reduction, protection, or mitigation.</p>

<p>In this project, our system is the Tello drone which relies on its camera, IMU (Inertial Measurement Unit), barometer, temperature sensor, and battery charge sensor to pull in information. Some example safety features include: </p>
<li> Monitoring the battery temperature to check if it is overheating in flight and landing the drone if it does overheat. This helps preserve battery life.</li>
<li> Checking to see if the drone is oriented properly before takeoff to ensure that it does not launch into a trajectory that could cause it to hit something.</li> 
<li> Using mission pads to localize and properly constrain the flight environment that the Tello drones use to navigate. </li> 
</p>

<p>Functional Safety Engineering uses the <a href="https://www.iso.org/obp/ui/#iso:std:iso:26262:-9:ed-1:v1:en">V-model development process</a> from the <a href="https://www.iso.org/standard/43464.html">ISO26262</a> standard, which is shown below. <br><br>

<div style="text-align: center;">
<img src="https://about.gitlab.com/images/iso-26262/v-model-iso-26262.png" width="500">
</div>

<em>The left side of the V-model is conceptual development and product development. The bottom of the V-model is where the hardware and software designs are implemented. The right side of the V-model is where all testing activities of the design happen. </em>


</p>
<p>Safety Features are designed during conceptual development in a process called the ‘<a href="https://arxiv.org/pdf/1704.06140.pdf">Hazard Analysis and Risk Assessment</a>’ or HARA. HARA uses an <a href="https://www.synopsys.com/automotive/what-is-asil.html">ASIL risk rating</a> chart to properly classify the specific HARA line item in question. Collisions in this project receive a SIL1 rating based off initial severity (S1), initial exposure (E3), and initial avoidability (C2). More information on the HARA can be found in the <a href=#supplemental-documentation>Supplemental Documentation</a></p>

Once these safety features are implemented properly either through hardware or software measures, they are then tested as single units with both integration and regression testing to ensure that everything works properly. From there, the project can be deployed with assurance that there are safety features present to actively mitigate risks.

</details> 

<details>
<summary>Networking</summary>

<p>The topic under discussion revolves around two distinct methodologies employed in swarm control, namely centralized and decentralized control. Decentralized control entails equipping each individual drone within the swarm with an exclusive "brain," enabling them to independently make decisions based on the limited information they receive from other members of the swarm.</p>

<p>On the other hand, centralized control involves the utilization of a single controller for computational purposes. This controller undertakes the necessary computations and subsequently dispatches commands to the individual actors within the swarm, directing their actions accordingly.</p>

<p>In the context of this particular project, a centralized control structure was adopted, where communication among the drones occurred over Wi-Fi, facilitated through a router. This is shown below.</p>

<div style="text-align: center;">
<img src = "imgs\DroneConnectivity.png" height=250></div>
</details> 

# Getting Started
We used the following materials for this project:
- 2 Tello EDU drones
- Router (we used the <a href= "https://www.amazon.com/TP-Link-AC1750-Smart-WiFi-Router/dp/B079JD7F7G/ref=sr_1_3?keywords=WiFi%2BRouters%2Bfor%2BHome&qid=1663443788&sr=8-3&ufe=app_do%3Aamzn1.fos.006c50ae-5d4c-4777-9bc0-4513d670b6bc&th=1">TP-Link AC1750 Smart WiFi Router (Archer A7)</a>
- 16 Tello Mission Pads (a printable version is in Ref, but originally from <a href="https://tellopilots.com/threads/download-official-ryze-tello-edu-mission-pads.2756/">here</a>)

<p>NOTE: This repository was originally implemented on Windows, and does not support other operating systems.</p>

## Router and Drone Connection
This section will cover how to set up the router, connect your computer to it, and connect the drones to it.

1. Disconnect from the wifi you are connected to.
2. Turn on one of the drones by clicking on the side power button.
3. Connect to the wifi of the drone from your computer.
4. Locate the password to the router located on the bottom of the router. This should also include the specific router name.
5. Use the connectivity page to set the router information(<i>connectivity_page.py</i>)
6. Run <i>connect_to_router.py</i>
7.  Repeat steps 1-6 for the other drones you would like to link up with the router.
8.  Turn off all drones.
9.  Connect router to power source and turn on. 
10. Connect to the router (use the non 5G network if one is available).
11. Connect to the router. Type "tplinkwifi.net" and fill in the login information displayed.
12. Navigate to the DHCP section in the website.
13. Turn on one of the drones and a new IP address should appear in the DHCP section. Record the IP address shown in the DHCP section.
14. Repeat step 13 for all of the drones but ensure that only one drone is active at a time.
15. Now that all drones have a recorded IP address, use the connectivity page to save these values.

## Necessary Installations

### Verify that your GPU is supported by CUDA
First, verify that your system has a dedicated GPU. Open your Device Manager and scroll to "Display Adapters." If your system has one, the GPU will be listed here. To ensure that your system is CUDA capable, make sure your GPU is one listed as supported <a href="https://developer.nvidia.com/cuda-gpus">here</a>.<br><br>

<div style="text-align: center;">
<img src="imgs/gpu_capable.png" width="500">
</div>
<div style="text-align: center;">
<em>Here, we can see our GPU is the Nvidia Quadro P1000</em></div><br>


### Download and install Cuda (11.8)
Once you know your system is compatible, the version we used can be found <a href=https://developer.nvidia.com/cuda-toolkit-archive>here</a>. Make sure to use 11.8. Installation is as easy as downloading and installing with all defaults!


### Environment Setup

This tutorial assumes you are using the environment manager <a href= "https://www.anaconda.com/">Anaconda</a>. See <a href=#supplemental-documentation>Supplemental Documentation</a> if you are unfamiliar with Anaconda.It's an incredibly helpful tool for navigating python distributions.
<br></br>
There are multiple options to install required packages.
<br></br>

<details> <summary> Anaconda Navigator </summary>

Using from the environments page in Anaconda Navigator, simply import the inTellogence_environment.yaml file.
</details>

<details><summary>Anaconda Prompt</summary>

With your desired environment activated, and the inTellogence folder active, run the following command:

```conda env create -f drone.yaml```

</details>

<details><summary>Without Anaconda</summary>
A requirements file is included for convenience. Install through the following command in your virtual environment:

```pip install -r requirements.txt```

</details>

<br>

## Mission Pad Setup
For inTellogence to work as expected, it's important to setup the mission pads as the drone expects to see them, as mapping is currently not supported. This layout is shown below, where orientation, spacing and layout are important. Should you wish to adjust the spacing between the pads, these are easily changed in <i>repo.properties</i>. Since Tello EDU currently only supports 8 different mission pads, the flyable space is separated into two sectors marked off below. The drones track which sector they are in.

IMPORTANT: When taking off, place the drones facing the X direction and anywhere in Sector 1.

<div style="text-align: center;">
<img src="imgs/mission_pad_layout.png" width="500"></div>
<br>

# Examples
<details><summary> Create a new behavior/reaction</summary>
<br>
There are two different types of reactions: movement and blocking. Let's create a new movement reaction, which will return a force vector to the drone. Open <i>reaction.py</i>.
<br></br>
These reactions have access to all the sensory information from the drone via the input argument.
<br></br>
First extend the movementReaction class:

```python
class moveBackIfPerson(movementReaction):
```

Now lets add an identifier so the GUI can read it:

```python
identifier = "Move back if person"`
```

Define the reaction:

```python
def react(self,input: SensoryState, currentMovement: np.array):
  res = np.zeros((4,1)) #base column array to return the force vector
  if input.visibleObjects is not None: # don't iterate through something not there!
    for object in input.visibleObjects:
      if(int(object[5]) == int(vision_class.person)):
        res[1] = 5 # move the drone back

  return res
  #Note that additional information about the structure of "visible Objects" can be found above in "Object Recognition using Yolov8"

```
Almost there! Now open <i>behavior.py</i>.

Create a new behavior (set of reactions)

```python
class myNewBehavior(behaviorFramework):
  # lets not add any blocking reactions
  blockingReactions = [] 
  # Lets add a previously made reaction with our new one!
  movementReactions = [rxt.followCellPhone(),rxt.moveBackIfPerson()]
```

This behavior is what you will pass in when you create your drone object!
</details>

<details><summary> Add a custom State </summary>
Adding a new state is simple!

In <i>drone_states.py</i>, just add the name of your new state, we'll call ours "Dance", with an arbitary, unique number:

```python
class State(Enum):
    Grounded = 1
    Takeoff = 2
    Land = 3
    Wander = 4
    #new state
    Dance = 5
```

Now, in <i>drone.py</i>, find the operate function. In it is a match-case block that changes the drone's actions based on the state. Let's add a new case:

```python
  case State.Land:
    ...
  case State.Dance:
    self.dance(): 
    if (conditional):
      self.opState = State.NextState #pseudocode
```
Here, dance() could be whatever you want. Just make sure the function isn't blocking (contains no infinite loops)!
</details><br>

# Performance
<p>It's easy to adjust the size of the YOLO model being used, via the <i>repo.properties</i> file. Using a Lenovo Thinkpad P1, with Nvidia Quadro P1000, we saw the following speeds for 1 drone:

YOLOv8n:
- Inference time: ~40 ms
- Average Loop Rate: ~7.5 Hz

YOLOv8s:
- Inference time: ~55 ms
- Average Loop Rate: ~7.3 Hz

YOLOv8m:
- Inference time: ~85 ms
- Average Loop Rate: ~6.2 Hz

YOLOv8l:
- Inference time: ~145 ms
- Average Loop Rate: ~4.3 Hz

YOLOv8x:
- Inference time: ~235 ms
- Average Loop Rate: ~3 Hz

When flying more than 1 drone, it's advisable to use a smaller model, as all computation occurs in series.

</p><br>

# Recommendations
The following recommendations present valuable avenues for enhancing the capabilities and functionality of our project, allowing for future improvements and expanded possibilities:

1. GUI Improvement: Enhancing the graphical user interface (GUI) can significantly improve the user experience and ease of operation. By focusing on intuitive design, streamlined controls, and informative visualizations, we can provide users with a more efficient and user-friendly interface.

2. Memory Usage Optimization: Limiting memory usage is a crucial consideration for optimizing performance and resource utilization. Implementing efficient memory management techniques, such as reducing unnecessary data storage or optimizing algorithms, can enhance the project's efficiency and allow for smoother operation.

3. Adjustable Telemetry Displays: Introducing customizable telemetry displays within the GUI offers users greater insights into the drones' status and behavior. Features such as displaying each drone's location or visualizing different velocity vectors acting on them can provide valuable real-time information and improve situational awareness.

4. Extensibility for Multiple Drones: Modifying the swarm class to support more than just two drones would expand the project's capabilities and accommodate larger-scale operations. By enabling seamless integration and control of multiple drones, we can enhance the project's scalability and versatility.

5. Task Planning Functionality: Incorporating task planning capabilities into the project would enable automated mission execution and optimize drone coordination. Implementing algorithms or frameworks for task allocation, path planning, or collaborative decision-making would enhance the project's ability to handle complex missions efficiently.


# Supplemental Documentation

[Coordinate Modelling](Ref/Coordinate_Modelling.pdf)

[Use Cases](Ref/Use_Cases.pdf)

[Users, Needs, and Features development](Ref/Users_Needs_Features.docx)

[Software Requirements & Evidence](Ref/SFQ_reference.pdf)

[HARA](Ref/HARA.pdf)

# Troublehooting resources
+ [Tello Drone User Manual](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20User%20Manual%20v1.4.pdf)
+ [Official Flet developer community](https://discord.gg/mMJHgYEqRK)
+ [DJI Tello Online Community](https://tellopilots.com)
# References

<p>Strother, C. (2023). Codes and Ethics Advisement to Sky Guardian Team. Internal RHIT report: unpublished.</p>

<p>Berry, C. A. (2012). Mobile robotics for multidisciplinary study. Synthesis Lectures on Control and Mechatronics, 3(1), 1-95.</p>

<p>Winck, Ryder. "Coordinate Transformations” Class lecture, Robot Dynamics and Control, Rose-Hulman Institute of Technology, Terre Haute, IN, December, 2022.</p>

<p>"Hazard Analysis and Risk Assessment beyond ISO 26262: Management of Complexity via Restructuring of Risk-Generating Process," in Safety of the Intended Functionality , SAE, 2020, pp.69-78.</p>

<p>World Leaders in Research-Based User Experience. “10 Usability Heuristics for User Interface Design.” Nielsen Norman Group, https://www.nngroup.com/articles/ten-usability-heuristics/#poster.</p>

<p>An Introduction to Functional Safety and IEC 61508 - MTL INST, www.mtl-inst.com/images/uploads/datasheets/App_Notes/AN9025.pdf.</p>

# Acknowledgements 
We would like to thank our external reviewers: Dr. Sriram Mohan, and Dr. Ryder Winck for their guidance, resources, and support throughout this project. We would also like to thank Dr. Sid Stamm, Dr. Amirmasoud Momenipour, Dr. Mark Hays, and Dr. Mellor for their subject-matter expertise. Lastly, we would like to thank you dear reader as our project only gains value if it is able to benefit someone else.