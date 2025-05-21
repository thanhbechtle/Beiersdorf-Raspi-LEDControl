import requests
import time
import json
import gpiozero
from rpi_ws281x import PixelStrip, Color

# Configuration
API_URL = "https://beiersdorfraspi-eeefbrfsf2cadcb9.westeurope-01.azurewebsites.net/api/leds"
API_KEY = "your-api-key"
POLL_INTERVAL = 2  # seconds

# GPIO Setup (adjust pins as needed)
LED_PINS = {
    "1": 17, "2": 18, "3": 22, "4": 23, "5": 24,
    "6": 25, "7": 5, "8": 6, "9": 13, "10": 19
}

# For addressable LEDs (WS2812B)
LED_COLS = 17
LED_ROWS = 6
LED_COUNT = LED_COLS * LED_ROWS  # 102     # Number of LED pixels
LED_PIN = 21        # GPIO pin connected to the pixels
LED_FREQ_HZ = 800000  # LED signal frequency in hertz
LED_DMA = 10        # DMA channel to use for generating signal
LED_BRIGHTNESS = 255 # Set to 0 for darkest and 255 for brightest
LED_INVERT = False   # True to invert the signal
LED_CHANNEL = 0      # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Initialize GPIO
gpio_leds = {led_id: gpiozero.LED(pin) for led_id, pin in LED_PINS.items() if led_id not in ["1", "2"]}

# Permanently turn on LED 1 and 2
led1 = gpiozero.LED(17)
led2 = gpiozero.LED(18)
led1.on()
led2.on()
print("LED 1 and LED 2 permanently ON")

# Initialize addressable LEDs
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def get_snake_index(x, y, cols):
    if y % 2 == 0:
        return y * cols + x
    else:
        return y * cols + (cols - 1 - x)

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Track previous LED states
previous_led_states = {}

def update_leds():
    global previous_led_states
    try:
        headers = {"api-key": API_KEY}
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        led_states = response.json()

        for led_id, state in led_states.items():
            # --- Handle GPIO LEDs (e.g., keys like "1", "2", ...)
            # if led_id in gpio_leds:
            #     previous_state = previous_led_states.get(led_id, {"on": None})
            #     if state["on"] != previous_state["on"]:
            #         if state["on"]:
            #             gpio_leds[led_id].on()
            #             print(f"GPIO LED {led_id} turned ON")
            #         else:
            #             gpio_leds[led_id].off()
            #             print(f"GPIO LED {led_id} turned OFF")
            #     previous_led_states[led_id] = state
            #     continue  # skip to next LED

            # --- Handle matrix LEDs using "x,y" notation
            if ',' in led_id:
                try:
                    x_str, y_str = led_id.split(',')
                    x, y = int(x_str), int(y_str)

                    if 0 <= x < LED_COLS and 0 <= y < LED_ROWS:
                        led_index = get_snake_index(x, y, LED_COLS)
                        previous_state = previous_led_states.get(led_id, {"on": None, "color": None})

                        if state["on"] != previous_state["on"] or state.get("color") != previous_state.get("color"):
                            if state["on"]:
                                r, g, b = hex_to_rgb(state["color"])
                                strip.setPixelColor(led_index, Color(r, g, b))
                                print(f"Matrix LED {led_id} set to color ({r}, {g}, {b})")
                            else:
                                strip.setPixelColor(led_index, Color(0, 0, 0))
                                print(f"Matrix LED {led_id} turned OFF")

                        previous_led_states[led_id] = state
                except ValueError:
                    print(f"Invalid matrix LED id format: {led_id}")
                    continue

        strip.show()

    except requests.RequestException as e:
        print(f"Error fetching LED states: {e}")
        
if __name__ == "__main__":
    print("Starting LED controller client...")
    try:
        while True:
            update_leds()
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("Stopping LED controller")