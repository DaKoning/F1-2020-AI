import f1_2020_telemetry
from f1_2020_telemetry.packets import PacketCarTelemetryData_V1, PacketHeader, unpack_udp_packet
import socket
import math
import numpy as np
import os

# data: speed, ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront, totalDistance, totalDistance_old, currentLapInvalid
startDistance = -1004.96484375 # De oude distance moet beginnen op de startDistance, zodat de rewardbepaling bij de eerste episode klopt
data = np.array([0, 0, 0, 0, 0, 0, 0, startDistance, 0], dtype=object)
TRACK = np.genfromtxt(os.path.join('assets','Monza_Circuit.csv'), dtype=float,encoding=None, delimiter=",")
RENDERDISTANCE = int(800)


def run(data):
    # Haalt alle telementry data uit de game in packets
    print("Data Collection: Binding to socket 20777")
    udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    udp_socket.bind(("", 20777))
    udp_timeout = 2
    udp_socket.settimeout(udp_timeout)
    print("Data Collection: Bound to socket 20777")

    while True:
        try:
            udp_packet = udp_socket.recv(2048)
            packet = unpack_udp_packet(udp_packet)
        except socket.timeout:
            print(f"Data Collection: Not receiving any UDP packet after {udp_timeout} seconds")
            break

        # Het haalt de parameters die we willen uit de packets
        if isinstance(packet, f1_2020_telemetry.packets.PacketLapData_V1):
            # currentLapTime = packet.lapData[0].currentLapTime
            totalDistance = packet.lapData[0].totalDistance
            data[6] = totalDistance
            currentLapInvalid = packet.lapData[0].currentLapInvalid
            data[8] = currentLapInvalid

        elif isinstance(packet, f1_2020_telemetry.packets.PacketMotionData_V1):
            angle = 1 + packet.carMotionData[0].yaw / np.pi
           
            PosX = ((packet.carMotionData[0].worldPositionX) + 700) * 5 
            PosZ = ((packet.carMotionData[0].worldPositionZ) + 1200) * 5 
            Pos = np.array([PosX,PosZ])
            
            # print(f"Data Collection: PosX: {PosX}")
            # print(f"Data Collection: PosZ: {PosZ}")
            # print(f"Data Collection: angle:  {angle}")
            
            anglelist = calculateangle(TRACK, Pos, angle)
            ray_front, ray_right, ray_left, ray_rightfront, ray_leftfront = raycast(Pos, anglelist, angle)

            data[1] = round(ray_front / 10) * 10
            data[2] = round(ray_right / 10) * 10
            data[3] = round(ray_left / 10) * 10
            data[4] = round(ray_rightfront / 10) * 10
            data[5] = round(ray_leftfront / 10) * 10

            # print(f"Data Collection: ray_front       :  {ray_front}")
            # print(f"Data Collection: ray_right       :  {ray_right}")
            # print(f"Data Collection: ray_left        :  {ray_left}")
            # print(f"Data Collection: ray_rightfront  :  {ray_rightfront}")
            # print(f"Data Collection: ray_leftfront   :  {ray_leftfront}")
  

        elif isinstance(packet, f1_2020_telemetry.packets.PacketCarTelemetryData_V1):
            speed = packet.carTelemetryData[0].speed
            data[0] = round(speed / 10) * 10
            # print(f"Data Collection: Speed: {data[0]}")


def calculateangle(matrix,point,worldangle):
    # Worldangle unitvector
    pointV = np.array([(np.cos(-worldangle*np.pi),np.sin(-worldangle*np.pi))])
    # Doing all edits to matrixV variable instead of matrix
    matrixV = np.copy(matrix)
    matrixV[:,0] -= point[0]
    matrixV[:,1] -= point[1]
    # Calculating corrections:
    norm_points = np.copy(matrixV)
    # Calculate correction angle
    correctionangle = worldangle*np.pi
    # Calculate normalised angle with rotation matrix
    norm_points2 = np.array([(np.cos(correctionangle) * norm_points[:,0] + -np.sin(correctionangle) * norm_points[:,1]),(np.sin(correctionangle) * norm_points[:,0] + np.cos(correctionangle) * norm_points[:,1])])
    norm_points2 = np.transpose(norm_points2)
    # Calulate which points need 1pi added to angle (correction)
    correction = norm_points2[:,1] < 0
    # Angle calculation:
    dotproduct = matrixV[:,0] * pointV[0,0] + matrixV[:,1] * pointV[0,1]
    pointlength = np.sqrt(pointV[0,0]*pointV[0,0] + pointV[0,1]*pointV[0,1])
    matrixlength = np.sqrt(matrixV[:,0]*matrixV[:,0] + matrixV[:,1]*matrixV[:,1])
    anglelist = np.arccos(dotproduct/(pointlength*matrixlength))/np.pi
    # Adding correction
    anglelist[correction] = np.absolute(anglelist[correction]-1)+1
    # print(f"Anglelist: {anglelist}")
    return anglelist
    
def raycast(Pos, anglelist, Angle):
    front = distance(TRACK,anglelist,Pos,-Angle,1.5,0.1/180)
    right = distance(TRACK,anglelist,Pos,-Angle,0,10/180)
    left = distance(TRACK,anglelist,Pos,-Angle,1.0,10/180)
    rightfront = distance(TRACK,anglelist,Pos,-Angle,1.75,10/180)
    leftfront = distance(TRACK,anglelist,Pos,-Angle,1.25,10/180)
    # print("front:",round(front[0],2),"right:",round(right[0],2),"left:",round(left[0],2),"rightfront:",round(rightfront[0],2),"leftfront:",round(leftfront[0],2))

    return front, right, left, rightfront, leftfront
    

def distance(matrix, anglematrix, point, worldangle, rayangle, tolerance):
    # Calculating top and bottom bounds
    angleV = anglematrix
    matrixV = matrix
    top = rayangle + tolerance
    bottom = rayangle - tolerance
    # Checking if tolerance calculating <0 or >2pi and changing it accordingly
    if top > 2:
        top -= 2
        angleMASK = (angleV > bottom)&(angleV < 2)|(angleV > 0)&(angleV < top)
    elif bottom < 0:
        bottom += 2
        angleMASK = (angleV > bottom)&(angleV < 2)|(angleV > 0)&(angleV < top)
    else:
        angleMASK = (angleV > bottom) & (angleV < top)
    marginlist = matrix[angleMASK]
    if marginlist.size == 0:
        amin = RENDERDISTANCE
        intersectpoint = np.array([[(point[0]+RENDERDISTANCE*math.cos(worldangle*math.pi+(rayangle*math.pi))),(point[1]+RENDERDISTANCE*math.sin(worldangle*math.pi+(rayangle*math.pi)))]])
        anglepoint = np.array([rayangle])
        # print("Data Collection: Using no angle condition")
    else:
        distance = np.sqrt((marginlist[:,0]-point[0])*(marginlist[:,0]-point[0])+(marginlist[:,1]-point[1])*(marginlist[:,1]-point[1]))
        amin = np.amin(distance)

    return amin # Afstand van de ray