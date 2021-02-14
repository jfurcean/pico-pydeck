
# SPDX-FileCopyrightText: 2021 John Furcean
# SPDX-License-Identifier: MIT

# Modified from Pete Gallagher 2021 
# Raspberry Pi Pico Producer 
# Twitter:  https://www.twitter.com/pete_codes
# Blog:     https://www.petecodes.co.uk

# Imports
import time
import usb_hid
import board
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.consumer_control import ConsumerControl

READ_TIME = .01

def map_function(x, in_min, in_max, out_min, out_max):

  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;


def update_volume(pot_val, last_position=0, current_volume = 0):
        position = int(map_function(pot_val, 200, 65520, 0, 32))

        if abs(position - last_position) > 1:
            last_position = position
            if current_volume < position:
                while current_volume < position:
                    # Raise volume.
                    print("Volume Up!")
                    consumer_control.send(ConsumerControlCode.VOLUME_INCREMENT)
                    current_volume+= 2
                    print(pot_val)
            elif current_volume > position:
                while current_volume > position:
                    # Lower volume.
                    print("Volume Down!")
                    consumer_control.send(ConsumerControlCode.VOLUME_DECREMENT)
                    current_volume -= 2
                    print(pot_val)

        return last_position, current_volume

# initialize hid device as consumer control 
consumer_control = ConsumerControl(usb_hid.devices)

# initialize potentiometer (pot) wiper connected to GP26_A0
potentiometer = AnalogIn(board.GP26)  

# intialize the read time
last_read = time.monotonic()

# decrease volume all the way down 
# this allows the volume to be set by the current value of the pot
for i in range(32):
    consumer_control.send(ConsumerControlCode.VOLUME_DECREMENT)


# initalize volume and last position
current_volume = 0
last_position = 0

pot_val = potentiometer.value
last_position, current_volume = update_volume(pot_val, last_position, current_volume)


# Initialize Keybaord
keyboard = Keyboard(usb_hid.devices)

# Define HID Key Output Actions
hid_actions = [
    {
        "name": "Scene 1",
        "held": False,
        "keycode": (Keycode.ALT, Keycode.F1),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Scene 2",
        "held": False,
        "keycode": (Keycode.ALT, Keycode.F2),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Scene 3",
        "held": False,
        "keycode": (Keycode.ALT, Keycode.F3),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Scene 4",
        "held": False,
        "keycode": (Keycode.ALT, Keycode.F4),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Scene 5",
        "held": False,
        "keycode": (Keycode.ALT, Keycode.F5),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Scene 6",
        "held": False,
        "keycode": (Keycode.ALT, Keycode.F6),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Scene 7",
        "held": False,
        "keycode": (Keycode.ALT, Keycode.F7),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Scene 8",
        "held": False,
        "keycode": (Keycode.ALT, Keycode.F8),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Scene 9",
        "held": False,
        "keycode": (Keycode.ALT, Keycode.F9),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Press ",
        "held": False,
        "keycode": (Keycode.ALT, Keycode.F10),
        "button": None,
        "led": None,
        "type": "press",
    },
    {
        "name": "Toggle Mute",
        "held": False,
        "keycode": (Keycode.ALT, Keycode.F11),
        "button": None,
        "led": None,
        "type": "toggle",
    },
]



# Define button pins
btn_pins = [
    board.GP0,
    board.GP1,
    board.GP2,
    board.GP3,
    board.GP4,
    board.GP5,
    board.GP6,
    board.GP7,
    board.GP8,
    board.GP9,
    board.GP10,
]

# Define led pins
led_pins = [
    board.GP11,
    board.GP12,
    board.GP13,
    board.GP14,
    board.GP16,
    board.GP17,
    board.GP18,
    board.GP19,
    board.GP20,
    board.GP21,
    board.GP22,
]

# Setup all Buttons as Inputs with PullUps
# Setup all LEDs
for i in range(len(btn_pins)):
    button = DigitalInOut(btn_pins[i])
    button.direction = Direction.INPUT
    button.pull = Pull.UP
    hid_actions[i]["button"] = button

    led = DigitalInOut(led_pins[i])
    led.direction = Direction.OUTPUT
    hid_actions[i]["led"] = led
    hid_actions[i]["led"].value = True
    time.sleep(.1)

for i in range(len(led_pins)):
    time.sleep(.1)
    hid_actions[i]["led"].value = False


print(hid_actions)

# Loop around and check for key presses
while True:

    if time.monotonic() - last_read > READ_TIME:
        pot_val = potentiometer.value
        last_position, current_volume = update_volume(pot_val, last_position, current_volume)

        # update last_read to current time
        last_read = time.monotonic()

    # handle time.monotonic() overflow
    if time.monotonic() < last_read:
        last_read = time.monotonic()


    for i in range(len(hid_actions)):

        # check if button is pressed but make sure it is not held down
        if not hid_actions[i]["button"].value and not hid_actions[i]["held"]:

            # print the name of the command for debug purposes
            print(hid_actions[i]["name"])


            if hid_actions[i]["type"] == "scene" or hid_actions[i]["type"] == "toggle":
                # send the keyboard commands
                keyboard.press(*hid_actions[i]["keycode"])
                time.sleep(0.001)
                keyboard.release(*hid_actions[i]["keycode"])


                # rotate led on active scene for scene type buttons
                if hid_actions[i]["type"] == "scene":
                    print("here")
                    # light up the associated LED
                    hid_actions[i]["led"].value = True

                    # turn off other LEDs that may be on
                    for j in range(len(hid_actions)):
                        if j != i:
                            if hid_actions[j]["type"] == "scene":
                                hid_actions[j]["led"].value = False

                # toggle led for toggle type buttons
                if hid_actions[i]["type"] == "toggle":
                    hid_actions[i]["led"].value = not hid_actions[i]["led"].value

            if hid_actions[i]["type"] == "press":
                keyboard.press(*hid_actions[i]["keycode"])
                hid_actions[i]["led"].value = True

            # set the held to True for debounce
            hid_actions[i]["held"] = True

        # remove the held indication if it is no longer held
        elif hid_actions[i]["button"].value and hid_actions[i]["held"]:
            hid_actions[i]["held"] = False

            if hid_actions[i]["type"] == "press":
                keyboard.release(*hid_actions[i]["keycode"])
                hid_actions[i]["led"].value = False

        elif not hid_actions[i]["button"].value and hid_actions[i]["held"]:
            if hid_actions[i]["type"] == "press":
                print(hid_actions[i]["name"])



