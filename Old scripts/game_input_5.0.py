import time
import vgamepad as vg

gamepad = vg.VX360Gamepad()

def run(actions):
    throttle, steering = actions
    
    if throttle == 1: # Throttle full, brakes none
        gamepad.right_trigger_float(value_float=1.0)
        gamepad.left_trigger_float(value_float=0.0)
    elif throttle == -1: # Throttle none, brakes full
        gamepad.left_trigger_float(value_float=1.0)
        gamepad.right_trigger_float(value_float=0.0)
    
    gamepad.left_joystick_float(x_value_float=steering, y_value_float=0)

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