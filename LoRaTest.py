import spidev
import RPi.GPIO as GPIO
import time

# Disable GPIO warnings
GPIO.setwarnings(False)

# Pin definitions based on the image
RESET_PIN = 18    # RST
BUSY_PIN = 20     # BUSY
DIO1_PIN = 16     # DIO1
NSS_PIN = 21      # CS
MOSI_PIN = 10     # MOSI
MISO_PIN = 9      # MISO
CLK_PIN = 11      # CLK
DIO4_PIN = 6      # DIO4 (transmit enable)

print("Setting up GPIO pins...")
# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RESET_PIN, GPIO.OUT)
GPIO.setup(BUSY_PIN, GPIO.IN)
GPIO.setup(DIO1_PIN, GPIO.IN)
GPIO.setup(NSS_PIN, GPIO.OUT)
GPIO.setup(DIO4_PIN, GPIO.OUT)

# Initial pin states
GPIO.output(RESET_PIN, GPIO.HIGH)
GPIO.output(NSS_PIN, GPIO.HIGH)
GPIO.output(DIO4_PIN, GPIO.LOW)  # Start with transmit disabled

print("Initializing SPI...")
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000  # Reduced to 1 MHz for testing
spi.mode = 0
spi.bits_per_word = 8
spi.lsbfirst = False

def reset_device():
    print("Starting thorough reset sequence...")
    GPIO.output(NSS_PIN, GPIO.HIGH)
    GPIO.output(RESET_PIN, GPIO.LOW)
    time.sleep(0.2)  # Longer reset pulse
    GPIO.output(RESET_PIN, GPIO.HIGH)
    time.sleep(0.2)  # Longer wait after reset
    print(f"BUSY pin state immediately after reset: {GPIO.input(BUSY_PIN)}")

def wait_on_busy():
    print(f"Checking BUSY pin state: {GPIO.input(BUSY_PIN)}")
    retry_count = 0
    while GPIO.input(BUSY_PIN) and retry_count < 50:
        time.sleep(0.1)
        retry_count += 1
        if retry_count % 10 == 0:
            print(f"BUSY pin still high after {retry_count/10} seconds")
    
    if GPIO.input(BUSY_PIN):
        print("ERROR: Device stuck in busy state")
        return False
    return True

def write_command(command, data=None):
    if not wait_on_busy():
        return False
        
    try:
        print(f"Attempting to write command: 0x{command:02X}")
        GPIO.output(NSS_PIN, GPIO.LOW)
        time.sleep(0.001)
        resp = spi.xfer([command])
        print(f"Command write response: {resp}")
        
        if data:
            time.sleep(0.001)
            resp = spi.xfer(data)
            print(f"Data write response: {resp}")
        
        time.sleep(0.001)
        GPIO.output(NSS_PIN, GPIO.HIGH)
        time.sleep(0.001)
        
        return True
    except Exception as e:
        print(f"Error during SPI transfer: {e}")
        return False

try:
    print("\nStarting SX1262 test sequence...")
    print(f"Initial BUSY pin state: {GPIO.input(BUSY_PIN)}")
    print(f"Initial DIO1 pin state: {GPIO.input(DIO1_PIN)}")
    
    # Full reset sequence
    reset_device()
    
    # Try reading chip version (GetStatus command)
    print("\nAttempting to read device status...")
    if write_command(0xC0):  # GetStatus command
        print("Status command sent successfully")
    else:
        print("Failed to send status command")

except KeyboardInterrupt:
    print("\nProgram stopped by user")
except Exception as e:
    print(f"\nUnexpected error: {e}")
finally:
    print("\nCleaning up...")
    GPIO.output(NSS_PIN, GPIO.HIGH)
    GPIO.output(RESET_PIN, GPIO.HIGH)
    GPIO.output(DIO4_PIN, GPIO.LOW)
    spi.close()
    GPIO.cleanup()
    print("Cleanup complete")