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

READ_TIME = 0.01


def map_range(x, in_min, in_max, out_min, out_max):

    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def update_volume(pot_val, last_position=0, current_volume=0):
    position = int(map_range(pot_val, 200, 65520, 0, 32))

    if abs(position - last_position) > 1:
        last_position = position
        if current_volume < position:
            while current_volume < position:
                # Raise volume.
                print("Volume Up!")
                consumer_control.send(ConsumerControlCode.VOLUME_INCREMENT)
                current_volume += 2
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

# Define HID Button Output Actions
# https://circuitpython.readthedocs.io/projects/hid/en/latest/api.html#adafruit-hid-keycode-keycode
btn_actions = [
    {
        "name": "Scene 1",
        "held": False,
        "keycode": (Keycode.SHIFT, Keycode.KEYPAD_ONE),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Scene 2",
        "held": False,
        "keycode": (Keycode.SHIFT, Keycode.KEYPAD_TWO),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Scene 3",
        "held": False,
        "keycode": (Keycode.SHIFT, Keycode.KEYPAD_THREE),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Scene 4",
        "held": False,
        "keycode": (Keycode.SHIFT, Keycode.KEYPAD_FOUR),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Scene 5",
        "held": False,
        "keycode": (Keycode.SHIFT, Keycode.KEYPAD_FIVE),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Scene 6",
        "held": False,
        "keycode": (Keycode.SHIFT, Keycode.KEYPAD_SIX),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Scene 7",
        "held": False,
        "keycode": (Keycode.SHIFT, Keycode.KEYPAD_SEVEN),
        "button": None,
        "led": None,
        "type": "scene",
    },
    {
        "name": "Page UP",
        "held": False,
        "keycode": (Keycode.PAGE_UP,),
        "button": None,
        "led": None,
        "type": "hold",
    },
    {
        "name": "Hold Page Down",
        "held": False,
        "keycode": (Keycode.PAGE_DOWN,),
        "button": None,
        "led": None,
        "type": "hold",
    },
    {
        "name": "Press Mute Teams",
        "held": False,
        "keycode": (Keycode.COMMAND, Keycode.SHIFT, Keycode.M),
        "button": None,
        "led": None,
        "type": "press",
    },
    {
        "name": "Toggle Mute Zoom",
        "held": False,
        "keycode": (Keycode.COMMAND, Keycode.SHIFT, Keycode.A),
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
# Setup all LEDs as Outputs
for i, btn_pin in enumerate(btn_pins):
    button = DigitalInOut(btn_pin)
    button.direction = Direction.INPUT
    button.pull = Pull.UP
    btn_actions[i]["button"] = button

    led = DigitalInOut(led_pins[i])
    led.direction = Direction.OUTPUT
    btn_actions[i]["led"] = led

    # snake animation LEDs turning on
    btn_actions[i]["led"].value = True
    time.sleep(0.1)

# snake animation LEDs turning off
for btn_action in btn_actions:
    time.sleep(0.1)
    btn_action["led"].value = False


# Loop around and check for key presses
while True:

    if time.monotonic() - last_read > READ_TIME:

        # retrieve pot value
        pot_val = potentiometer.value

        # update volume based on pot level
        last_position, current_volume = update_volume(
            pot_val, last_position, current_volume
        )

        # update last_read to current time
        last_read = time.monotonic()

    # handle time.monotonic() overflow
    if time.monotonic() < last_read:
        last_read = time.monotonic()

    for i, btn_action in enumerate(btn_actions):

        # check if button is pressed but make sure it is not held down
        if not btn_action["button"].value and not btn_action["held"]:

            # print the name of the command for debug purposes
            print(btn_action["name"])

            if btn_action["type"] != "hold":
                # send the keyboard commands
                keyboard.press(*btn_action["keycode"])
                time.sleep(0.001)
                keyboard.release(*btn_action["keycode"])

                # rotate led on active scene for scene type buttons
                if btn_action["type"] == "scene":

                    # light up the associated LED
                    btn_action["led"].value = True

                    # turn off other LEDs that may be on
                    for j, alt_action in enumerate(btn_actions):
                        if j != i:
                            if alt_action["type"] == "scene":
                                alt_action["led"].value = False

                # toggle led for toggle type buttons
                if btn_action["type"] == "toggle":
                    btn_action["led"].value = not btn_action["led"].value

                if btn_action["type"] == "press":
                    btn_action["led"].value = True

            elif btn_action["type"] == "hold":
                keyboard.press(*btn_action["keycode"])
                btn_action["led"].value = True

            # set the held to True for debounce
            btn_action["held"] = True

        # remove the held indication if it is no longer held
        elif btn_action["button"].value and btn_action["held"]:
            btn_action["held"] = False

            if btn_action["type"] == "hold":
                keyboard.release(*btn_action["keycode"])
                btn_action["led"].value = False

            if btn_action["type"] == "press":
                btn_action["led"].value = False

        elif not btn_action["button"].value and btn_action["held"]:
            if btn_action["type"] == "hold":
                print(btn_action["name"])
