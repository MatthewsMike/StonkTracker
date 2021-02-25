# StonkTracker
A Ticker for bitcoin with a servo controller ship to reflect the 24hr rate of change.
The data is currently pulled from coindesk.com, and is updated every 5 minutes.


# Display
The display is based on the MAX7219 Driver for daisy chained 8x8 LED matrix displays.

PI PIN | Display Pin | Purpose
--- | --- | --- 
2 | VCC | Power
6 | GND | Ground
19 | DIN | Data In 
24 | CS | Chip Select
23 | CLK | Clock

# Servo
Connect the control wire to GPIO Pin 17.  We don't power the servo between updates.
This prevents the default, and less accurate, GPIO library to be used without twitching.

# Button
A button can be connected to GPIO 12 and 3.3Volts with a resistor in line.
This will cycle through any stocks in your crypto list.