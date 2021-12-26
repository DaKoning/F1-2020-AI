if timeToEnd < time.time():
    # print(f"Main: Episode: {current_episode}")
    # frequency -= 1
    # print(f"Main: Frequency: {frequency}")
    # period = (1.0/frequency)
    print("Main: Can't keep up! Frequency is to high!")
    print(f"Main: Episode: {current_episode}")
    break
    # if frequency < 1:
    #         print("Main: Can't keep up! Frequency is to high!")
    #         break
while timeToEnd > time.time(): # dit is zodat het proces niet opnieuw start wanneer de periode nog niet is afgerond
    time.sleep(0)