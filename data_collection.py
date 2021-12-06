import random

speed = 0.0 
progress = 0.0
# angle = 0.0
# pos_x = 0.0
# pos_y = 0.0
ray_dis_0 = 0.0
ray_dis_45 = 0.0
ray_dis_90 = 0.0
ray_dis_135 = 0.0
ray_dis_180 = 0.0
is_dead = False

def get_variables():
    speed = random.randint(1,100) # snelheid van de auto (speed in m/s)
    progress = random.randint(1,100) # moet de afstand die de auto tot dan toe heeft afeglegd komen
    # angle = random.randint(1,100)
    # pos_x = random.randint(1,100)
    # pos_y = random.randint(1,100)
    ray_dis_0 = random.randint(1,100)
    ray_dis_45 = random.randint(1,100)
    ray_dis_90 = random.randint(1,100)
    ray_dis_135 = random.randint(1,100)
    ray_dis_180 = random.randint(1,100)

    # return [speed, angle, pos_x, pos_y, ray_dis_0, ray_dis_45, ray_dis_90, ray_dis_135, ray_dis_180]
    return [speed, ray_dis_0, ray_dis_45, ray_dis_90, ray_dis_135, ray_dis_180], progress