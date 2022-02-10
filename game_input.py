import time
import vgamepad as vg

gamepad = vg.VX360Gamepad()

def run(actions):
    steering = actions
    
    gamepad.right_trigger_float(value_float=0.15)    
    gamepad.left_joystick_float(x_value_float=steering, y_value_float=0.0)

    gamepad.update()

input_time = 0.01
def special(input):
    if input == 'B':
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        gamepad.update()
        time.sleep(input_time)
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        gamepad.update()
    elif input == 'A':
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
        time.sleep(input_time)
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
    elif input == 'start':
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
        gamepad.update()
        time.sleep(input_time)
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
        gamepad.update()
    elif input == 'left_thumb':
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
        gamepad.update()
        time.sleep(input_time)
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
        gamepad.update()
    elif input == 'go_to_location':
        gamepad.right_trigger_float(value_float=0.15)
        gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
        gamepad.update()
        time.sleep(3)
        gamepad.left_trigger_float(value_float=1.0)  
        gamepad.left_joystick_float(x_value_float=0.25, y_value_float=0.0)
        gamepad.update()
        time.sleep(2.25)
        gamepad.left_trigger_float(value_float=0.0)
        gamepad.update()
