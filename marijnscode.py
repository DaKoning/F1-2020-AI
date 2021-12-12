import pygame
import os
import socket
import math
import numpy as np
import scipy
from scipy.spatial import distance
from f1_2020_telemetry.packets import unpack_udp_packet


udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_socket.bind(("", 20777))

packet1 = str("PacketSessionData_V1(header=PacketHeader(packetFormat=2020")
packet2 = str("PacketParticipantsData_V1(header=PacketHeader(packetFormat=2020")
packet3 = str("PacketCarSetupData_V1(header=PacketHeader(packetFormat=2020")
packet4 = str("PacketLapData_V1(header=PacketHeader(packetFormat=2020")
packet5 = str("PacketMotionData_V1(header=PacketHeader(packetFormat=2020")
packet6 = str("PacketCarTelemetryData_V1(header=PacketHeader(packetFormat=2020")

calcpersec = 0
PosX = 0
PosY = 0
PosZ = 0
PosXSCALED = 0
PosZSCALED = 0
VelX = 0
VelY = 0
VelZ = 0
Angle = 0
Collision_coords = np.array((0,0))
# Normaalvectoren voor de hoekberekeningen, bij monza nX: 0, nY = -1
nX = 0
nZ = -1
playerdistance = 0
Approxoffset = 0

WIDTH, HEIGHT = 629,1080
FPS = 10000
SCALE = 1080/11465
WIN = pygame.display.set_mode((WIDTH,HEIGHT))

TRACKLAYOUT = pygame.image.load(os.path.join('Assets','Tracklayout.png'))
PLAYERICON = pygame.image.load(os.path.join('Assets','Playericon7.png'))
TRACK = np.genfromtxt(os.path.join('assets','Track2.csv'), dtype=float,encoding=None, delimiter=",")
DOT = pygame.image.load(os.path.join('Assets','Playericon6.png'))
RENDERDISTANCE = int(800)
PLAYERICON_OFFSET = -7
front = 0,np.array([[],[]]),np.array([[],[]])
right = 0,np.array([[],[]]),np.array([[],[]])
left = 0,np.array([[],[]]),np.array([[],[]])
leftfront = 0,np.array([[],[]]),np.array([[],[]])
rightfront = 0,np.array([[],[]]),np.array([[],[]])

def draw_window():
    global PosX
    global PosZ
    global Angle
    global playerdistance
    global Collision_coords
    global PosXSCALED
    global PosZSCALED
    global calcpersec
    global amin
    global Approxoffset
    global front
    global left
    global right
    global leftfront
    global rightfront
    PLAYER = pygame.transform.rotate(PLAYERICON,int(round((Angle) * 180,0)))
    WIN.blit(TRACKLAYOUT,(0,0))
    WIN.blit(PLAYER,(int(round(PosXSCALED+(PLAYERICON_OFFSET*math.fabs(math.cos(Angle*math.pi))),0)),int(round(PosZSCALED+(PLAYERICON_OFFSET*math.fabs(math.sin(Angle*math.pi))),0))))
    #WIN.blit(DOT,(int(round(Collision_coords[0]*SCALE,0)),int(round(Collision_coords[1]*SCALE,0))))
    try:
        line1 = pygame.draw.line(WIN,(255,255,0),(int(round(PosXSCALED,0)),int(round(PosZSCALED,0))),(int(round(front[1][0][0]*SCALE,0)),int(round(front[1][0][1]*SCALE,0))),2)
        line2 = pygame.draw.line(WIN,(255,0,0),(int(round(PosXSCALED,0)),int(round(PosZSCALED,0))),(int(round(left[1][0][0]*SCALE,0)),int(round(left[1][0][1]*SCALE,0))),2)
        line3 = pygame.draw.line(WIN,(0,0,255),(int(round(PosXSCALED,0)),int(round(PosZSCALED,0))),(int(round(right[1][0][0]*SCALE,0)),int(round(right[1][0][1]*SCALE,0))),2)
        line4 = pygame.draw.line(WIN,(230,230,250),(int(round(PosXSCALED,0)),int(round(PosZSCALED,0))),(int(round(left[1][0][0]*SCALE,0)),int(round(left[1][0][1]*SCALE,0))),2)
        line5 = pygame.draw.line(WIN,(0,255,0),(int(round(PosXSCALED,0)),int(round(PosZSCALED,0))),(int(round(right[1][0][0]*SCALE,0)),int(round(right[1][0][1]*SCALE,0))),2)
    except Exception:
        pass
    
    pygame.display.update()
    

    #print("X:",round(PosX,0),"Z:",round(PosZ,0),"Angle:",float(round(Angle,2)),"π","distance: ",round(playerdistance,2),"Approx",round((Approxoffset/math.pi)*180,2),'Speed',calcpersec)

def raycast():
    global anglelist
    global Pos
    global Angle
    global front
    global left
    global right
    global rightfront
    global leftfront
    front = distance(TRACK,anglelist,Pos,-Angle,1.5,0.1/180)
    right = distance(TRACK,anglelist,Pos,-Angle,0,10/180)
    left = distance(TRACK,anglelist,Pos,-Angle,1.0,10/180)
    rightfront = distance(TRACK,anglelist,Pos,-Angle,1.75,10/180)
    leftfront = distance(TRACK,anglelist,Pos,-Angle,1.25,10/180)
    print("front:",round(front[0],2),"right:",round(right[0],2),"left:",round(left[0],2),"rightfront:",round(rightfront[0],2),"leftfront:",round(leftfront[0],2))

def distance(matrix,anglematrix,point,worldangle,rayangle,tolerance):
    #Calculating top and bottom bounds
    angleV = anglematrix
    matrixV = matrix
    top = rayangle + tolerance
    bottom = rayangle - tolerance
    #checking if tolerance calculating <0 or >2pi and changing it accordingly
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
        print("using no angle condition")
    else:
        distance = np.sqrt((marginlist[:,0]-point[0])*(marginlist[:,0]-point[0])+(marginlist[:,1]-point[1])*(marginlist[:,1]-point[1]))
        amin = np.amin(distance)
        bestguessmask = np.where(distance == amin)
        intersectpoint = marginlist[bestguessmask]
        anglepoint = angleV[angleMASK][bestguessmask]

    return amin, intersectpoint, anglepoint


def calculateangle(matrix,point,worldangle):
    global anglelist
    #worldangle unitvector
    pointV = np.array([(np.cos(-worldangle*np.pi),np.sin(-worldangle*np.pi))])
    #doing all edits to matrixV variable instead of matrix
    matrixV = np.copy(matrix)
    matrixV[:,0] -= point[0]
    matrixV[:,1] -= point[1]
    #calculating corrections:
    norm_points = np.copy(matrixV)
    #   calculate correction angle
    correctionangle = worldangle*np.pi
    #   calculate normalised angle with rotation matrix
    norm_points2 = np.array([(np.cos(correctionangle) * norm_points[:,0] + -np.sin(correctionangle) * norm_points[:,1]),(np.sin(correctionangle) * norm_points[:,0] + np.cos(correctionangle) * norm_points[:,1])])
    norm_points2 = np.transpose(norm_points2)
    #   calulate which points need 1pi added to angle (correction)
    correction = norm_points2[:,1] < 0
    #angle calculation:
    dotproduct = matrixV[:,0] * pointV[0,0] + matrixV[:,1] * pointV[0,1]
    pointlength = np.sqrt(pointV[0,0]*pointV[0,0] + pointV[0,1]*pointV[0,1])
    matrixlength = np.sqrt(matrixV[:,0]*matrixV[:,0] + matrixV[:,1]*matrixV[:,1])
    anglelist = np.arccos(dotproduct/(pointlength*matrixlength))/np.pi
    #adding correction
    anglelist[correction] = np.absolute(anglelist[correction]-1)+1

def getgamedata():
    global PosX
    global PosZ
    global PosXSCALED
    global PosZSCALED
    global Angle
    global Pos
    global Laptime
    global Lapdistance
    global Lapinvalid
    while True:
        udp_packet = udp_socket.recv(2048)
        packet = unpack_udp_packet(udp_packet)
        spacket = str(packet)
        split = spacket.split(',')
        if packet5 in spacket:
            PosX = ((float(split[10][48:]) + 700)*5)
            PosY = float(split[11][16:])
            PosZ = ((float(split[12][16:]) + 1200)*5)
            Pos = np.array([PosX,PosZ])
            VelX = float(split[13][16:])
            VelY = float(split[14][16:])
            VelZ = float(split[15][16:])
            PosXSCALED = ((float(split[10][48:]) + 700)*5)/(11465/1080)
            PosZSCALED = ((float(split[12][16:]) + 1200)*5)/(11465/1080)
            #Bij Monza VelX > 0, normaal VelZ < 0
            try:
                if VelX > 0:
                    Angle = float(math.fabs(math.acos((VelX*nX+VelZ*nZ)/(math.sqrt(VelX**2+VelZ**2)*math.sqrt(nX**2+nZ**2)))/math.pi-1)+1)
                else:
                    Angle = float(math.acos((VelX*nX+VelZ*nZ)/(math.sqrt(VelX**2+VelZ**2)*math.sqrt(nX**2+nZ**2)))/math.pi)
            except Exception:
                print("ERROR angle function")
                Angle = float(0)
                pass
            calculateangle(TRACK,Pos,Angle)
            raycast()
            return
        elif packet4 in spacket:
            Lapdistance = float(split[25][13:])
            Laptime = float(split[11][16:])
            Lapinvalid = float(split[32][19:])
        else:
            return

            
def main():
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        draw_window()
        getgamedata()
    else:
        pass
    pygame.quit()

if __name__ == "__main__":
     main()