import spidev
import RPi.GPIO as GPIO
import time

# Pin setup
NSS = 8
RST = 22
DIO0 = 4  # optional (not used for interrupt)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(NSS, GPIO.OUT)
GPIO.setup(RST, GPIO.OUT)
GPIO.setup(DIO0, GPIO.IN)

# SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, CE0 (GPIO8)
spi.max_speed_hz = 5000000

# LoRa registers
REG_OP_MODE = 0x01
REG_FIFO = 0x00
REG_FIFO_RX_CURRENT_ADDR = 0x10
REG_RX_NB_BYTES = 0x13
REG_IRQ_FLAGS = 0x12

# Modes
MODE_LONG_RANGE = 0x80
MODE_SLEEP = 0x00
MODE_STDBY = 0x01
MODE_RX_CONT = 0x05

def write_reg(addr, value):
    spi.xfer2([addr | 0x80, value])

def read_reg(addr):
    return spi.xfer2([addr & 0x7F, 0x00])[1]

def reset_lora():
    GPIO.output(RST, GPIO.LOW)
    time.sleep(0.01)
    GPIO.output(RST, GPIO.HIGH)
    time.sleep(0.01)

def lora_init():
    reset_lora()
    write_reg(REG_OP_MODE, MODE_LONG_RANGE | MODE_SLEEP)
    time.sleep(0.1)

    write_reg(REG_OP_MODE, MODE_LONG_RANGE | MODE_STDBY)

    # Set frequency = 434 MHz
    frf = int((434e6 / 32000000.0) * (1 << 19))
    write_reg(0x06, (frf >> 16) & 0xFF)
    write_reg(0x07, (frf >> 8) & 0xFF)
    write_reg(0x08, frf & 0xFF)

    write_reg(REG_OP_MODE, MODE_LONG_RANGE | MODE_RX_CONT)

def receive():
    irq_flags = read_reg(REG_IRQ_FLAGS)

    if irq_flags & 0x40:  # RxDone
        write_reg(REG_IRQ_FLAGS, 0xFF)

        length = read_reg(REG_RX_NB_BYTES)
        addr = read_reg(REG_FIFO_RX_CURRENT_ADDR)
        write_reg(0x0D, addr)

        payload = []
        for _ in range(length):
            payload.append(read_reg(REG_FIFO))

        try:
            print("Received:", bytes(payload).decode())
        except:
            print("Raw:", payload)

# MAIN
try:
    print("Starting LoRa Receiver...")
    lora_init()

    while True:
        receive()
        time.sleep(0.2)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    spi.close()
    GPIO.cleanup()
