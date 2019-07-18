# Imports
# ===========================================================================

from bvh import Bvh
import numpy as np
import math
import json
import os
from os import listdir
from os.path import isfile, join
from tqdm import tqdm
from gpcharts import figure

# Function declarations
# ===========================================================================


def removeAllFilesInDirectory(directory):
    onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
    for i in range(0, len(onlyfiles)):
        os.remove(f"{directory}{onlyfiles[i]}")


def euler_to_quaternion(heading, attitude, bank):
    c1 = np.cos(heading/2)
    s1 = np.sin(heading/2)
    c2 = np.cos(attitude/2)
    s2 = np.sin(attitude/2)
    c3 = np.cos(bank/2)
    s3 = np.sin(bank/2)
    c1c2 = c1 * c2
    s1s2 = s1 * s2
    w = c1c2*c3 - s1s2*s3
    x = c1c2*s3 + s1s2*c3
    y = s1*c2*c3 + c1*s2*s3
    z = c1*s2*c3 - s1*c2*s3
    return [w, x, y, z]


def bvhBoneName(mimicBone):
    return humanoidRig[f"{mimicBone}"]


# Initialization
# ===========================================================================

removeAllFilesInDirectory("./OutputMimic/")

# get json of humanoidRig
with open(f"./Rigs/humanoidRig.json") as json_data:
    humanoidRig = json.load(json_data)

# Sets up list of bones used by DeepMimic humanoid
# Order is important
deepMimicHumanoidJoints = ["seconds", "hip", "hip", "chest", "neck", "right hip", "right knee", "right ankle",
                           "right shoulder", "right elbow", "left hip", "left knee", "left ankle", "left shoulder", "left elbow"]
dimensions = [1, 3, 4, 4, 4, 4, 1, 4, 4, 1, 4, 1, 4, 4, 1]

# Locks root position and rotation for dev testing
posLocked = True

# sets onlyfiles to a list of files founds in the "mypath" directory
mypath = "./inputBvh/"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]


# Start of main program
# ===========================================================================

# for all files to convert
for j in range(0, len(onlyfiles)):
    elbowXYZPlot = [["x", "y", "z"]]
    targetMimicJoint = "right hip"

    with open(f"./OutputMimic/{onlyfiles[j]}.txt", "w") as output:

        # File Header
        print(f"{{", file=output)
        print(f"\"Loop\": \"wrap\",", file=output)
        print(f"\"Frames\":", file=output)
        print(f"[", file=output)

        # open file to convert
        with open("./inputBvh/" + onlyfiles[j]) as f:
            mocap = Bvh(f.read())

            print("Converting:\t\"" + onlyfiles[j] + "\"")
            # For every keyFrame
            for i in tqdm(range(0, mocap.nframes)):
                keyFrame = []

                # for all DeepMimicHumanoid Joints
                for p in range(0, len(deepMimicHumanoidJoints)):

                    # grab joint data for graphing
                    if deepMimicHumanoidJoints[p] == targetMimicJoint:
                        x = mocap.frame_joint_channel(
                            i, bvhBoneName(deepMimicHumanoidJoints[p]), 'Xrotation')
                        y = mocap.frame_joint_channel(
                            i, bvhBoneName(deepMimicHumanoidJoints[p]), 'Yrotation')
                        z = mocap.frame_joint_channel(
                            i, bvhBoneName(deepMimicHumanoidJoints[p]), 'Zrotation')

                        elbowXYZPlot.append([x, y, z])

                    # Append Time
                    if p == 0:
                        keyFrame.append(mocap.frame_time)

                    # Append root position
                    elif p == 1:
                        if posLocked:
                            keyFrame.append(2)
                            keyFrame.append(2)
                            keyFrame.append(2)
                        else:
                            keyFrame.append(mocap.frame_joint_channel(
                                i, bvhBoneName(deepMimicHumanoidJoints[p]), 'Xposition'))
                            keyFrame.append(mocap.frame_joint_channel(
                                i, bvhBoneName(deepMimicHumanoidJoints[p]), 'Yposition'))
                            keyFrame.append(mocap.frame_joint_channel(
                                i, bvhBoneName(deepMimicHumanoidJoints[p]), 'Zposition'))

                    elif dimensions[p] == 1:

                        x = mocap.frame_joint_channel(
                            i, bvhBoneName(deepMimicHumanoidJoints[p]), 'Xrotation')
                        y = mocap.frame_joint_channel(
                            i, bvhBoneName(deepMimicHumanoidJoints[p]), 'Yrotation')
                        z = mocap.frame_joint_channel(
                            i, bvhBoneName(deepMimicHumanoidJoints[p]), 'Zrotation')

                        if deepMimicHumanoidJoints[p] == "right elbow":
                            x = -x
                            y = y
                            z = -z
                            keyFrame.append(math.radians(y))
                        elif deepMimicHumanoidJoints[p] == "left elbow":
                            x = -x
                            y = -y
                            z = -z
                            keyFrame.append(math.radians(y))
                        else:
                            x = -x
                            y = -y
                            z = -z
                            keyFrame.append(math.radians(x))

                    elif dimensions[p] == 4:
                        x = mocap.frame_joint_channel(
                            i, bvhBoneName(deepMimicHumanoidJoints[p]), 'Xrotation')
                        y = mocap.frame_joint_channel(
                            i, bvhBoneName(deepMimicHumanoidJoints[p]), 'Yrotation')
                        z = mocap.frame_joint_channel(
                            i, bvhBoneName(deepMimicHumanoidJoints[p]), 'Zrotation')

                        if deepMimicHumanoidJoints[p] == "hip" and posLocked:
                            pitch = 0
                            yaw = 0
                            roll = 0
                        elif deepMimicHumanoidJoints[p] == "right shoulder":
                            pitch = -x + 30
                            yaw = y
                            roll = z - 90
                        elif deepMimicHumanoidJoints[p] == "left shoulder":
                            pitch = -x + 30
                            yaw = y
                            roll = z + 90
                        elif deepMimicHumanoidJoints[p] == "right hip":
                            pitch = x
                            yaw = y
                            roll = z - 21
                        elif deepMimicHumanoidJoints[p] == "left hip":
                            pitch = x
                            yaw = y
                            roll = z + 21
                        else:
                            # bindings from blender test
                            pitch = x
                            yaw = y
                            roll = z

                        # filter which accounts for differences in mimic interpretation
                        pitch = -pitch     # x non inverted
                        yaw = yaw       # y inverted on blender
                        roll = roll      # z non inverted

                        quaternion = euler_to_quaternion(math.radians(
                            yaw), math.radians(pitch), math.radians(roll))
                        keyFrame.append(quaternion[0])
                        keyFrame.append(quaternion[1])
                        keyFrame.append(quaternion[2])
                        keyFrame.append(quaternion[3])

                # Turn keyFrame into a recordable JSON String
                keyFrameString = "["
                keyFrameString += str(keyFrame[0])

                for x in range(0, len(keyFrame)):
                    if x > 0:
                        keyFrameString += ","
                        keyFrameString += str(keyFrame[x])

                # Put comma at end of all keyFrame lines but the last
                keyFrameString += "]"
                if i < mocap.nframes - 1:
                    keyFrameString += ","

                print(f"{keyFrameString}", file=output)

            # Close JSON object
            print(f"]", file=output)
            print(f"}}", file=output)

    fig1 = figure(title=targetMimicJoint+" axis values in " +
                  onlyfiles[j], ylabel="axis value", xlabel="keyframes")
    fig1.plot(elbowXYZPlot)
