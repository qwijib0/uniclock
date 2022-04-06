#!/usr/bin/env python
import time as t
import sys
import os
from math import trunc
from pytz import timezone
from datetime import datetime, time
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont
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

#auto-dimming range
minbrt = 2
maxbrt = 60

def TODAdjustBrightness():
    
    #create the geolocation for sun calculations
    tuc = timezone('America/Phoenix')

    # Get sunrise/sunset times for auto-dimming
    city = LocationInfo("Tucson", "USA", "America/Phoenix", 32.22, -110.97)
    s = sun(city.observer, date=datetime.now(), tzinfo=city.timezone)
    sunrisen = 0
    sunsetted = 0

    print((
        f'Dawn:    {s["dawn"]}\n'
        f'Sunrise: {s["sunrise"]}\n'
        f'Noon:    {s["noon"]}\n'
        f'Sunset:  {s["sunset"]}\n'
        f'Dusk:    {s["dusk"]}\n'
    ))

    diff = s["dawn"] - tuc.localize(datetime.now())
    diffmindawn = diff.total_seconds() / 60

    #if it's not dawn yet
    if s["dawn"] > tuc.localize(datetime.now()):
        print (f"not dawn yet")
        print (f"now is {datetime.now()}")
        print (f"dawn in {diffmindawn} min")
    else:
        print ("it's after dawn")
        sunrisen = 1

    diff = s["dusk"] - tuc.localize(datetime.now())
    diffmindusk = diff.total_seconds() / 60

    #if it's not sunset yet
    if s["dusk"] > tuc.localize(datetime.now()):
        print (f"not sunset yet")
        print (f"now is {datetime.now()}")
        print (f"sunset in {diffmindusk} min")
    else:
        print(f"it's after dusk")
        sunsetted = 1

    if not sunrisen and not sunsetted:
        newbrt = trunc(30 - (diffmindawn/2))
        if newbrt < minbrt:
            newbrt = minbrt
        print ("before dawn")

    if sunrisen and not sunsetted:
        print ("midday")
        newbrt = trunc(30 - (diffmindawn/2))
        if newbrt > maxbrt:
            newbrt = maxbrt

        newbrt = trunc(30 + (diffmindusk/2))
        if newbrt > maxbrt:
            newbrt = maxbrt

    if sunrisen and sunsetted:
        newbrt = trunc(30 + (diffmindusk/2))
        if newbrt < minbrt:
            newbrt = minbrt

    matrix.brightness = newbrt
    
    return

# Set Font
myFont = ImageFont.load('/home/qwijib0/uniclock/monogram.pil')

def in_between(now, start, end):
    if start <= end:
        return start <= now < end
    else: # over midnight e.g., 23:30-04:15
        return start <= now or now < end
        
def sparkle(numloops, frdelay):
    print (f"sparkling for {numloops}!")
    t.sleep(1)
    i = 0
    while (i < numloops):
        print(f"sparkle loop {i} with {len(frames)} frames")
        t.sleep(1)
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
	
            t.sleep(frdelay)
        i += 1

def updateClock(topOfHour):
    now = datetime.now()
    
    
    print(f"top of hours status is {topOfHour}")
    
    t.sleep(1)

    
    if topOfHour:
        print("let's sparkle")
        t.sleep(1)
        sparkle(20,.1)
    else:
        print ("no sparkle")
        t.sleep(1)
    
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
        topOfHour = 0
        now = datetime.now()
        
        if now.minute == 0:
            print (f"top of the hour")
            topOfHour = 1
        else:
            print (f"not top of hour, it's {now.minute}")
        if now.second == 0:
            #do top of the minute checks/tasks
            print (f"top of the minute, it's {now.second}")
            
            #switch to asleep frames overnight
                if (in_between(datetime.now().time(), time(20,00), time(6,50))):
                    frames = asleepframes
                else:
                    frames = awakeframes
            
            topOfHour = 1
            TODAdjustBrightness()
            updateClock(topOfHour)
        else:
            print (f"not top of the minute, it's {now.second}")

except KeyboardInterrupt:
    sys.exit(0)
