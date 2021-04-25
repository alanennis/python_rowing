from machine import Pin, Timer
import pyb
import utime as time
from switch import Switch

# import micropython
# micropython.alloc_emergency_exception_buf(100)


class rower():

    def __init__(self):
        # counter to be incremented each time a stroke is detected
        self.stroke_count = 0
        # counter to be used to calculate actual stroke per minute after 60 seconds
        self.timed_stroke = 0.0
        # flag to alert main that the time interval is up to so 
        # calculate interval stroke rate
        self.calc_projected_stroke = False
        # flag to calculate actual stroke rate every 60 seconds
        self.calc_timed_stroke = False
        # Setup the button input pin with a pull-up resistor.
        # self.button = Pin('X19', Pin.IN, Pin.PULL_UP)
        self.button = Pin('X17', Pin.IN, Pin.PULL_UP)
        # Register an interrupt on rising button input.
        # self.button.irq(self.debounce, Pin.IRQ_RISING)
        self.my_switch = Switch(self.button)


        self.output_projected_strokes = 0.0
        
        # so we have a full stroke counter
        self.total_strokes = 0.0
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

        # Register a new hardware timer.
        # create a timer that will tell the sytem it is time to calcualte the
        # stroke count
        self.stroke_calc_timer = Timer(-1)
        # initialise it
        self.stroke_calc_timer.init(mode=Timer.PERIODIC, period=5000, 
            callback=self.calc_stroke_enable)




    def calc_stroke_enable(self, timer):
        # print("projected stroke calc")
        self.calc_projected_stroke = True

    def timed_stroke_enable(self, timer):
        # print("timed_stroke")
        self.calc_timed_stroke = True

    def add_stroke(self,timer):
        self.stroke_count +=1 
        self.total_strokes +=0.5

    def debounce(self, pin):
        # Start or replace a timer for 50ms, and trigger add_stroke to
        # add a count to the stroke counter
        # print(pin)
        # self.add_stroke()
        
        machine.disable_irq()
        self.debounce_timer = Timer(-1)
        self.debounce_timer.init(mode=Timer.ONE_SHOT, period=20, 
            callback=self.add_stroke)
        machine.enable_irq()



        # testing debounce here
        # print(pin.value())
        # self.cur_value = pin.value()
        # self.active = 0
        # while self.active < 20:
        #     if pin.value() != self.cur_value:
        #         self.active += 1
        #     else:
        #         self.active = 0
                
            
        #     pyb.delay(1)



    def screen_update(self, dProjStrokeCount, dActualStrokes):
        self.clear()


        # self.dStrokes = str(dStrokes)
        self.dProjStrokeCount = str(dProjStrokeCount)
        self.dActualStrokes = str(dActualStrokes)

        print("screen update at " + str(time.time()))
        print("Total strokes = " + str(self.total_strokes))

        # print("Interval stroke count " + self.dStrokes)
        print ("P-strokes = " + self.dProjStrokeCount)
        print ("A-strokes = " + self.dActualStrokes)

    def clear(self):
        print("\x1B\x5B2J", end="")
        print("\x1B\x5BH", end="")

    def update(self):
        # do stuff in here then call screen update
        # update all the variables and zero out the ones that need
        # to e reset and then reset all the flags

        self.my_switch_new_value = False
     
        # Disable interrupts for a short time to read shared variable
        self.irq_state = machine.disable_irq()
        if self.my_switch.new_value_available:
            self.my_switch_value = self.my_switch.value
            self.my_switch_new_value = True
            self.my_switch.new_value_available = False
        machine.enable_irq(self.irq_state)
 
        # If my switch had a new value, print the new state
        if self.my_switch_new_value:
            if self.my_switch_value:
                print("add one")
            else:
                pass




        if self.calc_projected_stroke == True:
            self.output_projected_strokes = self.stroke_count * 6.0
            self.calc_projected_stroke = False
            self.output_actual_strokes += self.stroke_count
            self.stroke_count = 0

        if self.calc_timed_stroke == True:
            self.output_minute_strokes = self.output_actual_strokes / 2
            self.output_actual_strokes = 0
            self.calc_timed_stroke = False

        self.screen_update(self.output_projected_strokes,
                     self.output_minute_strokes)


# making waves below the surface
# ------------------------------

my_rower = rower()

while True:
    my_rower.update()
    pyb.delay(500)