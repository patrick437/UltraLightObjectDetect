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
GPIO.output(NSS_PIN, GPIO.HIGH)
GPIO.output(DIO4_PIN, GPIO.HIGH)  # Enable transmit

print("Initializing SPI...")
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 5000000  # 5 MHz
spi.mode = 0

def reset_device():
    print("Resetting device...")
    GPIO.output(RESET_PIN, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(RESET_PIN, GPIO.HIGH)
    time.sleep(0.1)
    print("Reset complete")

def wait_on_busy():
    print("Waiting for device to be ready...")
    print(f"Initial BUSY pin state: {GPIO.input(BUSY_PIN)}")
    timeout = 100
    count = 0
    while GPIO.input(BUSY_PIN):
        time.sleep(0.1)
        count += 1
        if count % 10 == 0:
            print(f"Still waiting... BUSY pin state: {GPIO.input(BUSY_PIN)}")
        if count >= timeout:
            print("ERROR: Device busy timeout!")
            return False
    print("Device ready")
    return True

def write_command(command, data=None):
    try:
        print(f"Writing command: 0x{command:02X}")
        GPIO.output(NSS_PIN, GPIO.LOW)
        time.sleep(0.001)
        spi.xfer([command])
        if data:
            print(f"Writing data: {[hex(x) for x in data]}")
            spi.xfer(data)
        time.sleep(0.001)
        GPIO.output(NSS_PIN, GPIO.HIGH)
        return wait_on_busy()
    except Exception as e:
        print(f"Error writing command: {e}")
        return False

try:
    print("Starting SX1262 test program...")
    print("\nTesting BUSY pin state...")
    print(f"Current BUSY pin state: {GPIO.input(BUSY_PIN)}")
    
    reset_device()
    time.sleep(1)
    
    print(f"BUSY pin state after reset: {GPIO.input(BUSY_PIN)}")
    
    if write_command(0x80, [0x00]):  # Simple standby command
        print("Initial command successful!")
    else:
        print("Initial command failed!")

except KeyboardInterrupt:
    print("\nProgram stopped by user")
except Exception as e:
    print(f"\nUnexpected error: {e}")
finally:
    print("Cleaning up...")
    spi.close()
    GPIO.cleanup()
    print("Cleanup complete")