# LightJar
#### <i>Convey with wizardry!</i>

<img src="lightjarhtml.png" height="400px"><img src="redblue.gif" height="400px">

A decorative/mood light that you can update live using any web browser on your network. This uses MQTT via websockets to send the data. Works with Pimoroni Skully hardware etc. It uses [this](https://github.com/digitalurban/MQTT-Plasma-Stick-2040W/blob/main/mqtt_as.py) lightweight micropython MQTT client by Peter Hinch, and assumes you have an existing MQTT broker on your network. Essentially, this project takes code from the [Pimoroni examples](https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/plasma_stick) (sparkles.py) and makes it easier to change the colour/intensity/fade settings via a colourful web interface. You don't need to know code or Thonny to change the ambience, and anyone on the network can join in (or have a colour fight!)

## Requirements:
1) MQTT Broker

You must have a broker on the network you wish to use. I am using Mosquitto which is running on my Synology NAS. This must be configured to use websockets on a specified port.

No MQTT Broker? Try the similar but simpler project [Starlights](https://github.com/mattura/starlights)

2) Hardware

You can obtain the following components separately, or get [the full kit](https://shop.pimoroni.com/products/wireless-plasma-kit)

- [Plasma Stick 2040 W](https://shop.pimoroni.com/products/plasma-stick-2040-w)
- String of RGB LEDs ([These ones are ideal](https://shop.pimoroni.com/products/5m-flexible-rgb-led-wire-50-rgb-leds-aka-neopixel-ws2812-sk6812))
- USB (Micro B) power cable and a decent power supply (at least 2A)

  Note: If you are using APA instead of NeoPixel/WS2812 style LEDs, you will need to change the code accordingly

3) Vessel

You need a large glass jar or vase (mine is from a Swedish furniture shop), though 50 LEDs can more-or-less fit in an empty(!) 70cl rum bottle.

You also need some filler material, to diffuse and soften the light, and space out the LEDs. I found some gold mesh fabric, but you could try crumpled tracing paper, bubblewrap, fabrics, hessian, sackcloth etc! The colour of the material will affect the tone of the LEDs slightly (eg my gold mesh makes the whites warmer)

<img src="gold_mesh_crop.jpg" height="300px">
<em>A roll of gold mesh works well to diffuse and warm the LEDs</em>

## Setup

1) Configure your MQTT Broker to use websockets

For Mosquitto, edit the ```mosquitto.conf``` as follows.

Scroll to the ```Listeners``` section, note there may already be one or more listeners followed by a port number. Choose a (different) port number to use for your websocket (eg 9001), and append the following to the end of the section:
```
#Configure a listener on port 9001, using websockets:
listener 9001
protocol websockets
```
> If you are using MQTT over TLS/SSL, you need to specify additional options here for the certificate

Restart your MQTT service (check mosquitto.log for errors)
>On Synology, the config file (and log file) may be located at:
```/var/packages/mosquitto/var/```

2) Assemble your LightJar
- Connect the LED wire (dotted wire to 5V; middle wire to PIXELS; other wire to GND)
- Wrap the LEDs around and within the filler material (if using), try to get uniform spacing
- Stuff the bundle into the jar, try to fill out the corners and space the LEDs evenly - more on the outside than the centre
- Trail the USB cable out of the jar (you may wish to use Something Sticky™ to attach the Plasma Stick to the jar at the back)
- Check everything works and all LEDs light up

3) Configure ```lightjar.html```
You need edit the HTML document to specify the MQTT Broker address (eg IP address or domain name) and the correct port. Ideally copy this to a locally running webserver (on the same network as the MQTT broker of course), but you can use it standalone.

4) Upload the code!
   
Using Thonny, for example:
- Update the firmware if necessary, **make sure to use the '[Pirate-branded](https://github.com/pimoroni/pimoroni-pico/releases)' micropython for picow** (tested using version ```1.23.0```)
- Edit ```WIFI_CONFIG.py``` to include your WiFi credentials if necessary
- Edit ```LIGHTJAR_CONFIG.py``` to include your broker details, ```NUM_LEDS``` etc
- Upload the files:
   1) ```mqtt_as.py```
   2) ```WIFI_CONFIG.py```
   3) ```LIGHTJAR_CONFIG.py```
   4) ```main.py``` 

   to the Plasma Stick. Run the code while in Thonny to check for errors. Make sure the MQTT broker is running first! Keep to the dim colours while plugged into the computer or your USB power will invariably be overwhealmed!

## Use your LightJar

Open ```lightjar.html``` in a browser. All being well the 'Connected' indicator should be green!

Use the colour pickers and sliders to send different light patterns to the LightJar. The values are transmitted over MQTT to the LightJar (as you change them), which then sets the parameters accordingly.

You could extend this code to perform different functions, allow for different patterns etc - your creative potential is bound solely by the scope of your imagination ;)

Thanks to Pimoroni of Sheffield-on-Sea for the excellent hardware and library, and Peter Hinch for the MQTT micropython client

## Troubleshooting

- Power: Using an old inadequate mobile phone charger might not cut the mustard, if you experience flickering, or general not-working-ness try changing it!
- Power: Seriously! The (intentionally dim) colour preset after initial boot *should* work from most laptop USBs, but if you change to bright white, it will certainly reset the plasma stick! When you've set up the WiFi etc, plug in to a proper supply to play.
