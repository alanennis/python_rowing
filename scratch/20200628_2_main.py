from machine import Pin, Timer
from pyb import delay


import micropython
micropython.alloc_emergency_exception_buf(100)


#counter to be incremented each time a stroke is detected
stroke_count = 0

def on_pressed(timer):
    global stroke_count
    stroke_count += 1


def debounce(pin):
    # Start or replace a timer for 200ms, and trigger on_pressed.
    stroke_calc_timer.init(mode=Timer.ONE_SHOT, period=50, callback=on_pressed)

# Setup the button input pin with a pull-up resistor.
button = Pin('X17', Pin.IN, Pin.PULL_UP)

# Register an interrupt on rising button input.
button.irq(debounce, Pin.IRQ_RISING)

while True:
    print ("stroke count " + str(stroke_count))
    delay(500)