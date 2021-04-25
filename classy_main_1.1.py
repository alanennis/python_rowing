from machine import Pin, Timer
import pyb
import utime as time
from switch import Switch

# import micropython
# micropython.alloc_emergency_exception_buf(100)


class rowtron():

    def __init__(self):
        # counter to be incremented each time a stroke is detected
        # including a field to record the time the stroke
        # was recorded so we can use the delta to calcuclate
        # the stroke per minute projection
        self.stroke_count = [0, time.ticks_ms(),0]
        # just need this tempoarily to show the time diff 
        # needs to be declared so that it has something to show
        # before the first run
        self.time_diff = 0
        # i want to only record every second switch activation
        # as the pin goes high on the out stroke and the in stroke
        # will flip flop toggle to only get every 2nd activation
        self.stroke_toggle = True

        # counter to keeptrack of seconds that we have been
        # rowing
        self.active_rowing_seconds = 0

        # Setup the button input pin with a pull-up resistor.
        # self.button = Pin('X19', Pin.IN, Pin.PULL_UP)
        self.button = Pin('X17', Pin.IN, Pin.PULL_UP)

        # create a switch using the switch library to debounce
        # the switch
        self.my_switch = Switch(self.button)

        # need one of these first so that it exists before we add
        # to it the first time
        self.output_projected_strokes = 0.0

        # need this to exist before we start adding strokes os the
        # display will be able to show zero
        self.total_strokes = 0.0

        # declared here so that it exist before the first
        # minute passes, otherwise we will have no variable to
        # print before the the first minute is up
        self.output_minute_strokes = 0.0

        # same as above but for the first projected strokes
        self.output_actual_strokes = 0.0

        # --- setup some timers ---
        # timer to update the actual strokes in a minute
        self.timed_minute_stroke = Timer(-1)
        # initialise it
        self.timed_minute_stroke.init(mode=Timer.PERIODIC, period=60000,
                callback=self.minute_stroke_calc)

        # timer to update the seconds we have been rowing
        # as long as the last stroke was less than x seconds ago
        self.active_rowing_stroke = Timer(-1)
        # initialise it
        self.active_rowing_stroke.init(mode=Timer.PERIODIC, period=1000,
                callback=self.active_rowing_timer)

    def active_rowing_timer(self, timer):
        self.activity_check = time.ticks_diff(time.ticks_ms(),
                                               self.stroke_count[1])
        if self.activity_check < 2000:
            self.active_rowing_seconds += 1

    def convert_seconds(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%d:%02d:%02d" % (hour, minutes, seconds)


    def minute_stroke_calc(self,timer):
        # use the thrid field in the stroke count to count number of
        # strokes in 60 seconds if we [0] - [2] and then update [2]
        # with the stroke count every 60 seconds we keep a running
        # tally of the number of strokes in the last 60 seconds
        self.output_minute_strokes = self.stroke_count[0] - self.stroke_count[2]
        self.stroke_count[2] = self.stroke_count[0]

    def add_stroke(self):
        # calculate the time between now and the last stroke so
        # that we can display the projected strokes/minute
        # we do this here so that it gets calculated after each
        # stroke, if we use a timer with a 1 sec period then my
        # stroke period will
        # be different to the timer period and it causes an erratic
        # result as the time between the stroke happeneing and the
        # timer checking the last stroke are happening at different
        # frequencies
        self.time_diff = time.ticks_diff(time.ticks_ms(),
                                         self.stroke_count[1])

        # so the debouncing is not working very well, i decided that
        # i can just ignore any button activations that are less than
        # a certain number of milliseconds from the previous one
        # given that 500 ms is half a secon and that if you were
        # rowing that fast you would be doing 60 strokes per min
        # which is pretty insane then i would think this is a safe 
        # number to start with. If this stroke is less than 500ms 
        # from the last one then just return with nothing
        if self.time_diff < 500:
            return

        if self.stroke_toggle:
            # set it to false so that we ignore the next pin high
            self.stroke_toggle = False

            # there are two switches per stroke so the strokes per minute
            # is halved by multiplying by 30 instead of 60 and then
            # divided by 1000 to convert from millisecond to seconds
            self.output_projected_strokes = 60 / (self.time_diff / 1000)

            if self.output_projected_strokes < 1:
                self.output_projected_strokes = 1

            elif self.output_projected_strokes > 60:
                self.output_projected_strokes = 60

            # then add the new stroke and the new time
            # there are two strokes per full movemnet
            # one when the seat slides out and one when it
            # slides in, the reed switch gets triggered twice each full
            # cycle so we add a half stroke each time the switch is
            # triggered
            self.stroke_count[1] = time.ticks_ms()
            self.stroke_count[0] += 1
            return

        elif self.stroke_toggle is False:
            # set it to true so that we get the next stroke
            self.stroke_toggle = True
            return

    def screen_update(self, dProjStrokeCount,
        dActualStrokes, dActualRowingSeconds,
        dDistance, dCalories):

        self.clear()

        self.dProjStrokeCount = dProjStrokeCount
        self.dActualStrokes = dActualStrokes
        self.dActualRowingSeconds = str(dActualRowingSeconds)
        self.distance = dDistance
        self.dCalories = dCalories

        # print("screen update at " + str(time.time()))
        print ("Total strokes = " + str(self.stroke_count[0]))
        print ("Projected-strokes = {:.0f}".format(self.dProjStrokeCount))
        print ("Actual-strokes = {:.0f}".format(self.dActualStrokes))
        print ("Workout time = " + self.dActualRowingSeconds)
        print ("Distance(10m/stroke) = " + self.distance)
        print ("Calculated Calories = " + str(self.dCalories))
        # print("time diff = " + str(self.time_diff) )

    def clear(self):
        print("\x1B\x5B2J", end="")
        print("\x1B\x5BH", end="")

    def calories_calc(self):
        self.kg = 99
        self.met = 7
        self.calories_formula = (self.met * self.kg * 3.5 ) / 200
        self.minutes = self.active_rowing_seconds / 60
        self.calories = self.minutes * self.calories_formula
        return int(self.calories)

    def update(self):
        # do stuff in here then call screen update
        # update all the variables and zero out the ones that need
        # to be reset and then reset all the flags

        if self.stroke_check():
            self.add_stroke()

        self.converted_rowing_seconds = self.convert_seconds(self.active_rowing_seconds)

        self.screen_update(self.output_projected_strokes,
                           self.output_minute_strokes,
                           self.converted_rowing_seconds,
                           str(self.stroke_count[0] * 10),
                           self.calories_calc())

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


my_rower = rowtron()

while True:
    my_rower.update()
    pyb.delay(150)
