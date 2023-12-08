import WIFI_CONFIG
import LIGHTJAR_CONFIG

import uasyncio
import ujson
import time
import plasma
from plasma import plasma_stick
from random import randrange, uniform
from machine import Timer, Pin

wifi_led = lambda _ : None  # Only one LED
blue_led = Pin('LED', Pin.OUT)

from mqtt_as import MQTTClient, config

NUM_LEDS = LIGHTJAR_CONFIG.NUM_LEDS

config['ssid'] = WIFI_CONFIG.SSID
config['wifi_pw'] = WIFI_CONFIG.PSK
config['server'] = LIGHTJAR_CONFIG.BROKER
config ['port'] = LIGHTJAR_CONFIG.PORT
MQTT_Topic = LIGHTJAR_CONFIG.TOPIC
config['user'] ='' #Your MQTT User Name
config ['password'] ='' # Your MQTT Password

# set up the WS2812 / NeoPixel™ LEDs
led_strip = plasma.WS2812(NUM_LEDS, 0, 0, plasma_stick.DAT, color_order=plasma.COLOR_ORDER_RGB)

# start updating the LED strip
led_strip.start()

current_leds = [[0] * 3 for i in range(NUM_LEDS)]
target_leds = [[0] * 3 for i in range(NUM_LEDS)]

#Start with snow:
S_INTENSITY = 0.0003
B_COLOUR = [30, 50, 50]  # dim blue
S_COLOUR = [240, 255, 255]  # bluish white
FADE_UP_SPEED = 255  # abrupt change for a snowflake
FADE_DOWN_SPEED = 1

blue_led(True)

def sparkle():
    for i in range(NUM_LEDS):
        # randomly add sparkles
        if S_INTENSITY > uniform(0, 1):
            # set a target to start a sparkle
            target_leds[i] = S_COLOUR
        # for any sparkles that have achieved max sparkliness, reset them to background
        if current_leds[i] == target_leds[i]:
            target_leds[i] = B_COLOUR
    move_to_target()   # nudge our current colours closer to the target colours
    display_current()  # display current colours to strip

def display_current():
    # paint our current LED colours to the strip
    for i in range(NUM_LEDS):
        led_strip.set_rgb(i, current_leds[i][0], current_leds[i][1], current_leds[i][2])


def move_to_target():
    # nudge our current colours closer to the target colours
    for i in range(NUM_LEDS):
        for c in range(3):  # 3 times, for R, G & B channels
            if current_leds[i][c] < target_leds[i][c]:
                current_leds[i][c] = min(current_leds[i][c] + FADE_UP_SPEED, target_leds[i][c])  # increase current, up to a maximum of target
            elif current_leds[i][c] > target_leds[i][c]:
                current_leds[i][c] = max(current_leds[i][c] - FADE_DOWN_SPEED, target_leds[i][c])  # reduce current, down to a minimum of target

def sub_cb(topic, msg, retained):
    global B_COLOUR, S_COLOUR, FADE_UP_SPEED, FADE_DOWN_SPEED, S_INTENSITY
    print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
    js = ujson.loads(msg.decode())
    if "basecolour" in js:
        B_COLOUR = [js["basecolour"]["r"], js["basecolour"]["g"], js["basecolour"]["b"]]
    if "sparklecolour" in js:
        S_COLOUR = [js["sparklecolour"]["r"], js["sparklecolour"]["g"], js["sparklecolour"]["b"]]
    if "fadeup" in js:
        FADE_UP_SPEED = min(255, max(1, int(js["fadeup"])))
    if "fadedown" in js:
        FADE_DOWN_SPEED = min(255, max(1, int(js["fadedown"])))
    if "intensity" in js:
        S_INTENSITY = float(js["intensity"])
    #ToDo: make this publish successfully    
    #client.publish(MQTT_Topic+'/ALIVE', create_msg(True), qos = 1)

def create_msg(changed=False):
    global B_COLOUR, S_COLOUR, FADE_UP_SPEED, FADE_DOWN_SPEED, S_INTENSITY
    js = {"lightjar": LIGHTJAR_CONFIG.CLIENTID,
              "basecolour": {"r":B_COLOUR[0],"g":B_COLOUR[1],"b":B_COLOUR[2]},
              "sparklecolour":{"r":S_COLOUR[0],"g":S_COLOUR[1],"b":S_COLOUR[2]},
              "fadeup": FADE_UP_SPEED,
              "fadedown": FADE_DOWN_SPEED,
              "intensity": S_INTENSITY}
    return ujson.dumps(js)

# Demonstrate scheduler is operational.
async def heartbeat():
    s = True
    while True:
        blue_led(s)
        await client.publish(MQTT_Topic+'/ALIVE', create_msg(), qos = 1)
        await uasyncio.sleep_ms(1000)
        s = not s

async def wifi_han(state):
    wifi_led(not state)
    print('Wifi is ', 'up' if state else 'down')
    await uasyncio.sleep(15)

# If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
async def conn_han(client):
    await client.subscribe(MQTT_Topic, 1)
    print("Subscribed to {}".format(MQTT_Topic))

async def main(client):
    try:
        await client.connect()
    except OSError:
        print('Connection failed.')
        #machine.reset()
        return
    n = 0
    conn_han(client)
    while True:
        sparkle()
        await uasyncio.sleep(0)
       # print('publish', n)
        # If WiFi is down the following will pause for the duration.
        n += 1

# Define configuration
config['subs_cb'] = sub_cb
config['wifi_coro'] = wifi_han
config['connect_coro'] = conn_han
config['clean'] = True

# Set up client
MQTTClient.DEBUG = True  # Optional
client = MQTTClient(config)

print("Setup: OK")
blue_led(False)

uasyncio.create_task(heartbeat())

try:
    uasyncio.run(main(client))
    
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
    uasyncio.new_event_loop()

