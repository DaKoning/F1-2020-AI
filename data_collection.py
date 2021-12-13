"""
we hebben nodig:
-speed
-progress (lapDistance, totalDistance)
-rays (angle)



"""

import random
import f1_2020_telemetry
from f1_2020_telemetry.packets import PacketCarTelemetryData_V1, PacketHeader, unpack_udp_packet
import socket
from math import pi
import numpy as np

# data: speed, ray_dis_0, ray_dis_45, ray_dis_90, ray_dis_135, ray_dis_180, totalDistance, totalDistance_old, currentLapInvalid
data = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=object)

def run_data_collection():
    #haalt alle telementry data uit de game in packets
    print("Data Collection: Binding to socket 20777")
    udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    udp_socket.bind(("", 20777))
    udp_timeout = 1
    udp_socket.settimeout(udp_timeout)
    print("Data Collection: Bound to socket 20777")

    while True:
        try:
            udp_packet = udp_socket.recv(2048)
            packet = unpack_udp_packet(udp_packet)
        except socket.timeout:
            print(f"Data Collection: Not receiving any udp packet after {udp_timeout} second(s)")
            break

        #geen idee wat het doet maar het haalt de parameters die we willen uit de packets
        if isinstance(packet, f1_2020_telemetry.packets.PacketLapData_V1):
            # currentLapTime = packet.lapData[0].currentLapTime
            # lapDistance = packet.lapData[0].lapDistance
            totalDistance = packet.lapData[0].totalDistance
            data[6] = totalDistance
            currentLapInvalid = packet.lapData[0].currentLapInvalid
            data[8] = currentLapInvalid

        elif isinstance(packet, f1_2020_telemetry.packets.PacketMotionData_V1):
            angle = packet.carMotionData[0].yaw
            angle_degrees = angle * (180 / pi)
            car_angle_0 = angle - (0.5 * pi)
            car_angle_45 = angle - (0.25 * pi)
            car_angle_90 = angle
            car_angle_135 = angle + (0.25 * pi)
            car_angle_180 = angle + (0.5 * pi)
            
        elif isinstance(packet, f1_2020_telemetry.packets.PacketCarTelemetryData_V1):
            speed = packet.carTelemetryData[0].speed
            data[0] = speed

        ray_dis_0 = random.randint(1,100)
        ray_dis_45 = random.randint(1,100)
        ray_dis_90 = random.randint(1,100)
        ray_dis_135 = random.randint(1,100)
        ray_dis_180 = random.randint(1,100)

        data[1] = ray_dis_0
        data[2] = ray_dis_45
        data[3] = ray_dis_90
        data[4] = ray_dis_135
        data[5] = ray_dis_180

        

def ray_dis_0():
    pass

def ray_dis_45():
    pass

def ray_dis_90():
    pass

def ray_dis_135():
    pass

def ray_dis_180():
    pass
