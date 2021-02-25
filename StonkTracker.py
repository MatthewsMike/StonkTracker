# Imports and Defines for Display
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT
NUMBER_OF_DISPLAY_MODULES = 4
message = ""

# Imports and Defines for BitCoin
import requests
CRYPTO_API_URL="https://production.api.coindesk.com/v2/price/ticker/sparkline?assets="
crypto_list = ["BTC", "DOGE", "ETH"]
crypto_index = 0
crypto_choice_changed = False
crypto_last_updated = None
MAX_TIME_IN_SECONDS_BETWEEN_UPDATES = 5 * 60


# Imports and Defines for Servo
import RPi.GPIO as GPIO
from time import sleep
SERVO_PWM_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PWM_PIN, GPIO.OUT)
pwm=GPIO.PWM(SERVO_PWM_PIN, 50) #PWM at 50Hz frequency
pwm.start(2.5)

# Imports and Defines for Button
CYCLE_BUTTON_PIN = 12
GPIO.setup(CYCLE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
def cycle_button_callback(channel):
    global crypto_choice_changed
    crypto_choice_changed = True
    
GPIO.add_event_detect(CYCLE_BUTTON_PIN, GPIO.RISING, callback=cycle_button_callback)


from datetime import datetime


def output_message(message):
    serial = spi(port=0, device =0, gpio=noop())
    device = max7219(serial,
                    8 * NUMBER_OF_DISPLAY_MODULES,
                    block_orientation= 90,
                    rotate = 0, 
                    blocks_arranged_in_reverse_order = True)
    show_message(device, message, fill="white", font=proportional(SINCLAIR_FONT), scroll_delay=0.04)

def get_crypto_value(crypto = "BTC"):
    while True:
        try:
            response = requests.get(CRYPTO_API_URL + crypto)
            response_json = response.json()
            value = response_json['data'][crypto]['sparkline'][-1]
            prev_value = response_json['data'][crypto]['sparkline'][0]
            percent_change = value[1] / prev_value[1] - 1
            return value[1], percent_change
        except:
            output_message("Waiting For Internet...")
            sleep(3)
            pass

def set_servo_angle(angle):
    duty = angle / 18.0 + 2
    pwm.ChangeDutyCycle(duty)
    sleep(0.5)
    pwm.ChangeDutyCycle(0) #Turn off to prevent twitching


def rotate_rocket(percent_change):
    """ We convert the Percentage change 0.069 (for 6.9%)
    to an angle on the rocket ship on the servo basically:
    90 degrees = 0% Change
    180 degrees = >+10% Change
    0 degrees = <-10% Change
    """
    angle = percent_change * 1000 + 90
    set_servo_angle(angle)

def update():
    global crypto_last_updated
    print("Updating Prices")
    crypto_last_updated = datetime.now()
    global message, crypto_list, crypto_index
    price, change = get_crypto_value(crypto_list[crypto_index])
    rotate_rocket(change)
    if price >= 1:
        message = crypto_list[crypto_index] + ": " + '{:,.2f}'.format(price) + ' ({:,.1f}%)'.format(change*100)
    else:
        message = crypto_list[crypto_index] + ": " + '{:,.4f}'.format(price) + ' ({:,.1f}%)'.format(change*100)

if __name__ == "__main__":
    output_message("Hello")
    set_servo_angle(0)
    output_message("Min")
    sleep(1)
    set_servo_angle(90)
    output_message("Zero")
    sleep(1)
    set_servo_angle(180)
    output_message("Max")
    sleep(1)
    update()
    try:
        while True:
            if crypto_choice_changed == True:
                crypto_choice_changed = False
                crypto_index = (crypto_index + 1 ) % len(crypto_list)
                output_message(crypto_list[crypto_index])
                update()
            if (datetime.now() - crypto_last_updated).seconds > MAX_TIME_IN_SECONDS_BETWEEN_UPDATES:
                update()
            output_message(message)
    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup()