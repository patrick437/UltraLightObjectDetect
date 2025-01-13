import spidev
import RPi.GPIO as GPIO
import time

# Pin definitions for SX1262
RESET_PIN = 22
BUSY_PIN = 23
DIO1_PIN = 24
NSS_PIN = 8  # Chip select

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RESET_PIN, GPIO.OUT)
GPIO.setup(BUSY_PIN, GPIO.IN)
GPIO.setup(DIO1_PIN, GPIO.IN)
GPIO.setup(NSS_PIN, GPIO.OUT)
GPIO.output(NSS_PIN, GPIO.HIGH)  # Chip select inactive by default

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
    GPIO.output(RESET_PIN, GPIO.LOW)
    time.sleep(0.01)  # 10ms
    GPIO.output(RESET_PIN, GPIO.HIGH)
    time.sleep(0.01)  # Wait for device to start

def wait_on_busy():
    while GPIO.input(BUSY_PIN):
        pass

def write_command(command, data=None):
    GPIO.output(NSS_PIN, GPIO.LOW)
    spi.xfer([command])
    if data:
        spi.xfer(data)
    GPIO.output(NSS_PIN, GPIO.HIGH)
    wait_on_busy()

def setup_lora():
    # Reset device
    reset_device()
    
    # Set to standby mode
    write_command(CMD_SET_STANDBY, [0x00])  # STDBY_RC mode
    
    # Set packet type to LoRa
    write_command(CMD_SET_PACKET_TYPE, [0x01])  # 0x01 = LoRa
    
    # Set frequency to 868.1 MHz (EU868)
    freq = int(868100000 / 32768)  # Convert frequency to register value
    freq_bytes = [(freq >> 24) & 0xFF, (freq >> 16) & 0xFF, 
                 (freq >> 8) & 0xFF, freq & 0xFF]
    write_command(CMD_SET_RF_FREQUENCY, freq_bytes)
    
    # Set TX parameters (power = 14dBm, ramp time = 200us)
    write_command(CMD_SET_TX_PARAMS, [14, 0x04])
    
    # Set modulation parameters (SF=7, BW=125kHz, CR=4/5)
    write_command(CMD_SET_MODULATION_PARAMS, [0x07, 0x04, 0x01])
    
    # Set packet parameters (preamble=8, variable length, payload=10, CRC on)
    write_command(CMD_SET_PACKET_PARAMS, [0x00, 0x08, 0x00, 0x0A, 0x01, 0x00])

def send_test_packet():
    # Prepare test packet
    test_data = [0x48, 0x65, 0x6C, 0x6C, 0x6F]  # "Hello" in ASCII
    write_command(CMD_SET_TX, test_data)
    time.sleep(1)  # Wait for transmission

try:
    print("Initializing SX1262...")
    setup_lora()
    
    print("Starting test transmission...")
    while True:
        print("Sending test packet...")
        send_test_packet()
        time.sleep(10)  # Wait 10 seconds between transmissions

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    spi.close()
    GPIO.cleanup()