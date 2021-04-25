from machine import Pin, Timer
import pyb
import utime as time
from switch import Switch

# import micropython
# micropython.alloc_emergency_exception_buf(100)


class rower():

    def __init__(self):
        # counter to be incremented each time a stroke is detected
        self.stroke_count = [0, time.ticks_ms()]
        # self.projected_stroke_count = 0
        # counter to be used to calculate actual stroke per minute after 60 seconds
        self.timed_stroke = 0.0
        # flag to alert main that the time interval is up to so
        # calculate interval stroke rate
        self.timed_stroke = False
        # flag to calculate actual stroke rate every 60 seconds
        self.calc_timed_stroke = False

        # Setup the button input pin with a pull-up resistor.
        # self.button = Pin('X19', Pin.IN, Pin.PULL_UP)
        self.button = Pin('X17', Pin.IN, Pin.PULL_UP)
        # create a switch
        self.my_switch = Switch(self.button)

        # need one of these first so that it exists before we add
        # to it the first time
        self.output_projected_strokes = 0.0

        # need this to exist before we start adding strokes os the
        # display will be able to show zero
        self.total_strokes = 0.0
        # self.stroke_interval = 0.0

        # declared here so that it exist before the first
        # minute passes, otherwise we will have no variable to
        # print before the the first minute is up
        self.output_minute_strokes = 0.0
        # same as above but for the first projected strokes
        self.output_actual_strokes = 0.0

        # ------ CREATE SOME TIMERS -------
        # timer to calcualte the actual number of strokes after 60
        # seconds has passed
        self.timed_stroke_timer = Timer(-1)
        # initialise it
        self.timed_stroke_timer.init(mode=Timer.PERIODIC, period=60000,
                                     callback=self.timed_stroke_enable)

    def timed_stroke_enable(self, timer):
        # print("timed_stroke")
        self.calc_timed_stroke = True

    # def add_stroke(self,timer):
    def add_stroke(self):
        # calculate the time between now and the last stroke
        self.time_diff = time.ticks_diff(time.ticks_ms(), self.stroke_count[1])
        self.output_projected_strokes = 30 / (self.time_diff / 1000)
        if self.output_projected_strokes < 1:
            self.output_projected_strokes = 1

        elif self.output_projected_strokes > 60:
            self.output_projected_strokes = 60

        # then add the new stroke and the new time
        self.stroke_count[1] = time.ticks_ms()
        self.stroke_count[0] += 0.5
        self.total_strokes += 0.5

    def screen_update(self, dProjStrokeCount, dActualStrokes):
        self.clear()

        # self.dStrokes = str(dStrokes)
        self.dProjStrokeCount = dProjStrokeCount
        self.dActualStrokes = str(dActualStrokes)

        print("screen update at " + str(time.time()))
        print("Total strokes = " + str(self.total_strokes))

        # print("Interval stroke count " + self.dStrokes)
        print ("P-strokes = {:.1f}".format(self.dProjStrokeCount))
        print ("A-strokes = " + self.dActualStrokes)
        self.stroke_interval = time.ticks_diff(time.ticks_ms(), self.stroke_count[1])
        # print ("stroke interval = " + str(self.stroke_interval))
        # print ("stroke completed at " + str(self.stroke_count[1]))

    def clear(self):
        print("\x1B\x5B2J", end="")
        print("\x1B\x5BH", end="")

    def update(self):
        # do stuff in here then call screen update
        # update all the variables and zero out the ones that need
        # to e reset and then reset all the flags

        if self.stroke_check():
            self.add_stroke()

        if self.calc_timed_stroke is True:
            self.output_minute_strokes = self.output_actual_strokes
            self.output_actual_strokes = 0
            self.calc_timed_stroke = False

        self.screen_update(self.output_projected_strokes,
                           self.output_minute_strokes)

    def stroke_check(self):
        self.my_switch_new_value = False

        self.irq_state = machine.disable_irq()
        if self.my_switch.new_value_available:
            self.my_switch_value = self.my_switch.value
            self.my_switch_new_value = True
            self.my_switch.new_value_available = False
        machine.enable_irq(self.irq_state)

        # If my switch had a new value, then return true
        if self.my_switch_new_value:
            if self.my_switch_value:
                return True


# making waves below this surface
# ------------------------------


my_rower = rower()

while True:
    my_rower.update()
    pyb.delay(150)
