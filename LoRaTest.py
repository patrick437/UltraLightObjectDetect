import spidev
import RPi.GPIO as GPIO
import time

# Disable GPIO warnings
GPIO.setwarnings(False)

# Pin definitions for SX1262
RESET_PIN = 22
BUSY_PIN = 23
DIO1_PIN = 24
NSS_PIN = 8  # Chip select

print("Setting up GPIO pins...")
# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RESET_PIN, GPIO.OUT)
GPIO.setup(BUSY_PIN, GPIO.IN)
GPIO.setup(DIO1_PIN, GPIO.IN)
GPIO.setup(NSS_PIN, GPIO.OUT)
GPIO.output(NSS_PIN, GPIO.HIGH)  # Chip select inactive by default

print("Initializing SPI...")
# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0
spi.max_speed_hz = 10000000  # 10 MHz
spi.mode = 0

# SX1262 Commands
CMD_SET_STANDBY = 0x80
CMD_SET_PACKET_TYPE = 0x8A
CMD_SET_RF_FREQUENCY = 0x86
CMD_SET_TX_PARAMS = 0x8E
CMD_SET_MODULATION_PARAMS = 0x8B
CMD_SET_PACKET_PARAMS = 0x8C
CMD_SET_TX = 0x83

def reset_device():
    print("Resetting device...")
    GPIO.output(RESET_PIN, GPIO.LOW)
    time.sleep(0.01)  # 10ms
    GPIO.output(RESET_PIN, GPIO.HIGH)
    time.sleep(0.01)  # Wait for device to start
    print("Reset complete")

def wait_on_busy():
    print("Waiting for device to be ready...")
    timeout = 100  # 10 second timeout (100 * 0.1)
    count = 0
    while GPIO.input(BUSY_PIN):
        time.sleep(0.1)
        count += 1
        if count >= timeout:
            print("ERROR: Device busy timeout!")
            return False
    print("Device ready")
    return True

def write_command(command, data=None):
    try:
        print(f"Writing command: 0x{command:02X}")
        GPIO.output(NSS_PIN, GPIO.LOW)
        spi.xfer([command])
        if data:
            print(f"Writing data: {[hex(x) for x in data]}")
            spi.xfer(data)
        GPIO.output(NSS_PIN, GPIO.HIGH)
        if not wait_on_busy():
            print("Command failed - device busy timeout")
            return False
        print("Command successful")
        return True
    except Exception as e:
        print(f"Error writing command: {e}")
        return False

def setup_lora():
    print("\nStarting LoRa setup...")
    
    # Reset device
    reset_device()
    
    # Set to standby mode
    print("\nSetting standby mode...")
    if not write_command(CMD_SET_STANDBY, [0x00]):
        return False
    
    # Set packet type to LoRa
    print("\nSetting packet type to LoRa...")
    if not write_command(CMD_SET_PACKET_TYPE, [0x01]):
        return False
    
    # Set frequency to 868.1 MHz (EU868)
    print("\nSetting frequency...")
    freq = int(868100000 / 32768)
    freq_bytes = [(freq >> 24) & 0xFF, (freq >> 16) & 0xFF, 
                 (freq >> 8) & 0xFF, freq & 0xFF]
    if not write_command(CMD_SET_RF_FREQUENCY, freq_bytes):
        return False
    
    # Set TX parameters
    print("\nSetting TX parameters...")
    if not write_command(CMD_SET_TX_PARAMS, [14, 0x04]):
        return False
    
    # Set modulation parameters
    print("\nSetting modulation parameters...")
    if not write_command(CMD_SET_MODULATION_PARAMS, [0x07, 0x04, 0x01]):
        return False
    
    # Set packet parameters
    print("\nSetting packet parameters...")
    if not write_command(CMD_SET_PACKET_PARAMS, [0x00, 0x08, 0x00, 0x0A, 0x01, 0x00]):
        return False
    
    print("LoRa setup complete!")
    return True

def send_test_packet():
    print("\nPreparing to send test packet...")
    test_data = [0x48, 0x65, 0x6C, 0x6C, 0x6F]  # "Hello" in ASCII
    if write_command(CMD_SET_TX, test_data):
        print("Test packet sent successfully")
        return True
    else:
        print("Failed to send test packet")
        return False

try:
    print("Starting SX1262 test program...")
    if setup_lora():
        print("\nSetup successful - starting transmission loop...")
        while True:
            if not send_test_packet():
                print("Transmission failed - retrying in 10 seconds...")
            time.sleep(10)
    else:
        print("Setup failed!")

except KeyboardInterrupt:
    print("\nProgram stopped by user")
except Exception as e:
    print(f"\nUnexpected error: {e}")
finally:
    print("Cleaning up...")
    spi.close()
    GPIO.cleanup()
    print("Cleanup complete")