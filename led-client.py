import requests
import time
import json
import gpiozero
import rpi_ws281x

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
LED_COUNT = 10      # Number of LED pixels
LED_PIN = 21        # GPIO pin connected to the pixels
LED_FREQ_HZ = 800000  # LED signal frequency in hertz
LED_DMA = 10        # DMA channel to use for generating signal
LED_BRIGHTNESS = 255 # Set to 0 for darkest and 255 for brightest
LED_INVERT = False   # True to invert the signal
LED_CHANNEL = 0      # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Initialize GPIO
gpio_leds = {led_id: gpiozero.LED(pin) for led_id, pin in LED_PINS.items()}

# Initialize addressable LEDs
strip = rpi_ws281x.PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def update_leds():
    try:
        headers = {"api-key": API_KEY}
        response = requests.get(f"{API_URL}", headers=headers)
        response.raise_for_status()
        led_states = response.json()
        
        for led_id, state in led_states.items():
            if led_id in gpio_leds:
                # Standard GPIO control
                gpio_leds[led_id].on() if state["on"] else gpio_leds[led_id].off()
            
            # Addressable LED control (WS2812B)
            if led_id.isdigit() and int(led_id) <= LED_COUNT:
                led_index = int(led_id) - 1
                if state["on"]:
                    r, g, b = hex_to_rgb(state["color"])
                    strip.setPixelColor(led_index, Color(r, g, b))
                else:
                    strip.setPixelColor(led_index, Color(0, 0, 0))
        
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