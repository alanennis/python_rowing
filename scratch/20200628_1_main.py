from machine import Pin, Timer
from pyb import delay


import micropython
micropython.alloc_emergency_exception_buf(100)


# counter to be incremented each time a stroke is detected
stroke_count = 0
# counter to be used to calculate actual stroke per minute after 60 seconds
timed_stroke = 0.0
# flag to alert main that the time interval is up to so 
# calculate interval stroke rate
calc_stroke = False
# flag to calculate actual stroke rate every 60 seconds
calc_timed_stroke = False

def on_pressed(timer):
    global stroke_count
    stroke_count += 1

def debounce(pin):
    # Start or replace a timer for 200ms, and trigger on_pressed.
    debounce_timer = Timer(-1)
    debounce_timer.init(mode=Timer.ONE_SHOT, period=50, 
        callback=on_pressed)

def calc_stroke_enable(timer):
    # print("calc_stroke reached")
    global calc_stroke
    calc_stroke = True

def timed_stroke_enable(timer):
    # print ("timed stroke reached")
    global calc_timed_stroke
    calc_timed_stroke = True

# Register a new hardware timer.
# create a timer that will tell the sytem it is time to calcualte the
# stroke count
stroke_calc_timer = Timer(-1)
# initialise it
stroke_calc_timer.init(mode=Timer.PERIODIC, period=5000, 
    callback=calc_stroke_enable)

timed_stroke_timer = Timer(-1)
# initialise it
timed_stroke_timer.init(mode=Timer.PERIODIC, period=60000, 
    callback=timed_stroke_enable)

#10 second timer
tenSecond_timer = Timer(-1)




# Setup the button input pin with a pull-up resistor.
button = Pin('X17', Pin.IN, Pin.PULL_UP)

# Register an interrupt on rising button input.
button.irq(debounce, Pin.IRQ_RISING)

def clear():
    print("\x1B\x5B2J", end="")
    print("\x1B\x5BH", end="")

def main():
    global calc_stroke
    global stroke_count
    global timed_stroke
    global calc_timed_stroke
    if calc_stroke == True:
        # print("count is true")
        calculated_stroke = stroke_count * 6
        timed_stroke += stroke_count
        stroke_count = 0 # reset for next interval
        calc_stroke = False # reset to wait for another 10s
        print("calculated strokes/min = " + str(calculated_stroke))
    
    if calc_timed_stroke == True:
        clear()
        minute_stroke = timed_stroke / 2
        print ("actual strokes/min " + str(minute_stroke))
        timed_stroke = 0
        calc_timed_stroke = False


while True:
    main()
    delay(50)
