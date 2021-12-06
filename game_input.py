import time
import vgamepad as vg

gamepad = vg.VX360Gamepad()

def run(actions):
    throttle, brakes, steering = actions
    throttle = throttle / 10
    brakes = brakes / 10
    steering = steering / 10
    
    gamepad.right_trigger_float(value_float=throttle)
    gamepad.left_trigger_float(value_float=brakes)
    gamepad.left_joystick_float(x_value_float=steering, y_value_float=0)

    gamepad.update()


def special(input):
    if input == 'B':
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        gamepad.update()
        time.sleep(0.001)
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        gamepad.update()