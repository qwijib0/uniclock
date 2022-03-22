#!/usr/bin/env python
import time
import sys
import os
from datetime import datetime, time
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import GifImagePlugin
from astral import LocationInfo
from astral.sun import sun


if len(sys.argv) < 2:
    sys.exit("Require an image argument")
else:
    image_file = sys.argv[1]
  
awakeframes = []    
asleepframes = []
frames = []

i = 1
print ("getting awake frames")
while os.path.exists(f"{ image_file }/awake/unicorn{ i }.png"):
    awakeframes.append(f"{ image_file }/awake/unicorn{ i }.png")
    print (f"appended { image_file }/awake/unicorn{ i }.png")
    i += 1
    
print ("getting asleepframes") 
i = 1
while os.path.exists(f"{ image_file }/asleep/unicorn{ i }.png"):
    asleepframes.append(f"{ image_file }/asleep/unicorn{ i }.png")
    print (f"appended { image_file }/asleep/unicorn{ i }.png")
    i += 1
    
print (frames)
#imageObject = Image.open(image_file)

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.gpio_slowdown = 2
options.scan_mode = 0
options.brightness = 50
options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'

matrix = RGBMatrix(options = options)
# Get sunrise/sunset times for auto-dimming

city = LocationInfo("Tucson", "USA", "America/Phoenix", 32.22, -110.97)
s = sun(city.observer, date=datetime.now())

print((
    f'Dawn:    {s["dawn"]}\n'
    f'Sunrise: {s["sunrise"]}\n'
    f'Noon:    {s["noon"]}\n'
    f'Sunset:  {s["sunset"]}\n'
    f'Dusk:    {s["dusk"]}\n'
))

# Set Font
myFont = ImageFont.load('/home/qwijib0/uniclock/monogram.pil')

def in_between(now, start, end):
    if start <= end:
        return start <= now < end
    else: # over midnight e.g., 23:30-04:15
        return start <= now or now < end
        
def sparkle(numloops, frdelay):
    i = 0
    while (i < numloops):
        for frame in frames:

            imageObject = Image.open(frame)


	        # Add time
            now = datetime.now()
            time_str = now.strftime("%a %I:%M %p")
            i1 = ImageDraw.Draw(imageObject)
            i1.text((0,54), str(time_str), font=myFont, fill=(255, 255, 255))

            # Make image fit our screen.
            #imageObject.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)

            matrix.SetImage(imageObject.convert('RGB'))
	
            time.sleep(frdelay)
        i += 1

def updateClock():
    now = datetime.now()
        
    #switch to asleep frames overnight
    if (in_between(datetime.now().time(), time(20,00), time(6,50))):
        frames = asleepframes
    else:
        frames = awakeframes
    
    time_minsec = now.strftime("%M:%S")
    if time_minsec == "00:00":
    	sparkle(20,.1)
    
    imageObject = Image.open(frames[0])


    # Add time
    time_str = now.strftime("%I:%M %P")
    #dow_str = now.strftime("%A")
    i1 = ImageDraw.Draw(imageObject)
    i1.text((8,54), str(time_str), font=myFont, fill=(255, 255, 255))
    #i1.text((3,55), str(dow_str), font=myFont, fill=(255, 255, 255))


    # Make image fit our screen.
     #imageObject.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)

    matrix.SetImage(imageObject.convert('RGB'))
    
    return

try:
    print("Press CTRL-C to stop.")
    while True:
        updateClock()

except KeyboardInterrupt:
    sys.exit(0)
