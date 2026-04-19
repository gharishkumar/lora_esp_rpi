#include <SPI.h>
#include <LoRa.h>

// Define LoRa module pins
#define NSS 15    // SPI chip select pin
#define RESET 16   // Reset pin
#define DIO0 4    // Interrupt pin

void setup() {
  // Initialize serial communication for debugging
  Serial.begin(9600);
  while (!Serial);

  Serial.println("Initializing LoRa module...");

  // Initialize LoRa module
  LoRa.setPins(NSS, RESET, DIO0); // Set SPI and control pins
  if (!LoRa.begin(433E6)) {       // Initialize at 433 MHz
    Serial.println("LoRa initialization failed!");
    while (1);
  }

  Serial.println("LoRa initialized successfully!");
}

void loop() {
  // Send a test message
  Serial.println("Sending message...");
  LoRa.beginPacket();            // Start a new packet
  LoRa.print("Hello, LoRa!");    // Add data to the packet
  LoRa.endPacket();              // Send the packet

  delay(5000);                   // Wait 5 seconds before sending again
}
