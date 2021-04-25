from machine import Pin, Timer
from pyb import delay


class rower():

    def __init__(self):

        self.stroke_count = 0
        self.total_strokes = 0
        self.button = Pin('X17', Pin.IN, Pin.PULL_UP)
        self.my_switch = Switch(self.button)

   
    def add_stroke(self, timer):
        self.stroke_count +=1 
        self.total_strokes +=0.5

    def clear(self):
        print("\x1B\x5B2J", end="")
        print("\x1B\x5BH", end="")

    def screen_update(self):
        self.clear()
        print(str(self.stroke_count))


    def update(self):
        # print("screen update")
        self.screen_update()

        self.my_switch_new_value = False

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
                self.stroke_count += 1

            else:
                pass

my_rower = rower()

while True:
    my_rower.update()
    delay(500)