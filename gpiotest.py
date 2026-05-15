import pigpio
from time import sleep

GREEN_LED = 16
RED_LED = 20
WHITE_LED = 21

LEDS = [GREEN_LED, RED_LED, WHITE_LED]

def gpio_reset(pi):
    for led in LEDS:
        pi.set_mode(led, pigpio.OUTPUT)
        pi.set_pull_up_down(led, pigpio.PUD_OFF)
        pi.write(led, 0)

def toggle_gpio(pi, gpio):
    if pi.read(gpio) == 0:
        pi.write(gpio, 1)
    else:
        pi.write(gpio, 0)


if __name__ == "__main__":
    mcu = pigpio.pi()
    try:
        gpio_reset(mcu)
        
        # one by one
        curr_led = 0
        repeats = 2
        while repeats > 0:
            toggle_gpio(mcu, LEDS[curr_led])
            sleep(1)
            toggle_gpio(mcu, LEDS[curr_led])

            curr_led += 1
            if curr_led >= len(LEDS):
                curr_led = 0

            repeats -= 1

        # faster
        repeats = 6
        while repeats > 0:
            toggle_gpio(mcu, LEDS[curr_led])
            sleep(0.333)
            toggle_gpio(mcu, LEDS[curr_led])

            curr_led += 1
            if curr_led >= len(LEDS):
                curr_led = 0

            repeats -= 1

        # at random

    except KeyboardInterrupt:
        gpio_reset(mcu)
        mcu.stop()
    except Exception as e:
        print(e)
        gpio_reset(mcu)
        mcu.stop()
