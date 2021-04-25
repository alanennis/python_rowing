import pyb

def wait_pin_change(pin):
    print("hello")
    print(pin.value())
    # wait for pin to change value
    # it needs to be stable for a continuous 20ms
    cur_value = pin.value()
    active = 0
    while active < 20:
        if pin.value() != cur_value:
            # print(pin.value)
            active += 1
        else:
            active = 0
        pyb.delay(1)





pin_x1 = pyb.Pin('X17', pyb.Pin.IN, pyb.Pin.PULL_DOWN)
while True:
    wait_pin_change(pin_x1)
    pyb.LED(1).toggle()
    pyb.delay(5)