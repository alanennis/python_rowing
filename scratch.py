

timer to calcualte the actual number of strokes after 60
        seconds has passed
        self.timed_stroke_timer = Timer(-1)
        initialise it
        self.timed_stroke_timer.init(mode=Timer.PERIODIC, period=60000,
                                     callback=self.timed_stroke_enable)

