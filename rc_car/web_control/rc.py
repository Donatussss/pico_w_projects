from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep

sleep(5)
onst = Pin('LED', Pin.OUT)
onst.off()
sleep(0.5)
onst.on()
 
@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_prog():
    pull(noblock) .side(0)
    mov(x, osr) # Keep most recent pull data stashed in X, for recycling by noblock
    mov(y, isr) # ISR must be preloaded with PWM count max
    label("pwmloop")
    jmp(x_not_y, "skip")
    nop() .side(1)
    label("skip")
    jmp(y_dec, "pwmloop")


class PIOPWM:
    def __init__(self, sm_id, pin, max_count, count_freq):
        self._sm = StateMachine(sm_id, pwm_prog, freq=2 * count_freq, sideset_base=Pin(pin))
        # Use exec() to load max count into ISR
        self._sm.put(max_count)
        self._sm.exec("pull()")
        self._sm.exec("mov(isr, osr)")
        self._sm.active(1)
        self._max_count = max_count

    def set(self, value):
        # Minimum value is -1 (completely turn off), 0 actually still produces narrow pulse
        value = max(value, -1)
        value = min(value, self._max_count)
        self._sm.put(value)



in1 = Pin(1, Pin.OUT)
in2 = Pin(2, Pin.OUT)
in3 = Pin(4, Pin.OUT)
in4 = Pin(5, Pin.OUT)

in2.off()
in1.on()
in4.off()
in3.on()

en1 = PIOPWM(0, 0, max_count=(1 << 16) - 1, count_freq=400_000)
en2 = PIOPWM(1, 3, max_count=(1 << 16) - 1, count_freq=400_000)
en1.set(0)
en2.set(0)
sleep(1)

while True:
    for i in range(65500, 256**2):
        en1.set(i)
        en2.set(i)
        print(i)
        sleep(0.0001)

    en1.set(0)
    en2.set(0)
    in1.toggle()
    in2.toggle()
    in3.toggle()
    in4.toggle()
    sleep(1)