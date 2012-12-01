// Generated file: only edit in designated areas!
#include <Grove_5mm_Blue_LED_Local.h>
#include <MB7.h>

// Put top level includes, typedef's here:
  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

// Constructor
Grove_5mm_Blue_LED::Grove_5mm_Blue_LED(UByte address) {
  //////// Edit begins here: CONSTRUCTOR
  _pin = address;
  _duty_cycle = 0;
  _frequency = 0;
  pinMode(_pin, OUTPUT);
  //////// Edit ends here: CONSTRUCTOR
}

// duty_cycle_get: LED duty cycle
UByte Grove_5mm_Blue_LED::duty_cycle_get() {
  //////// Edit begins here: DUTY_CYCLE_GET
  return _duty_cycle;
  //////// Edit ends here: DUTY_CYCLE_GET
}

// duty_cycle_set: LED duty cycle
void Grove_5mm_Blue_LED::duty_cycle_set(UByte duty_cycle) {
  //////// Edit begins here: DUTY_CYCLE_SET
  _duty_cycle = duty_cycle;
  if (duty_cycle >= 50) {
    Serial.write("B1");
    digitalWrite(_pin, HIGH);
  } else {
    Serial.write("B0");
    digitalWrite(_pin, LOW);
  }
  //////// Edit ends here: DUTY_CYCLE_SET
}

// frequency_get: LED refresh frequency
UShort Grove_5mm_Blue_LED::frequency_get() {
  //////// Edit begins here: FREQUENCY_GET
  return _frequency;
  //////// Edit ends here: FREQUENCY_GET
}

// frequency_set: LED refresh frequency
void Grove_5mm_Blue_LED::frequency_set(UShort frequency) {
  //////// Edit begins here: FREQUENCY_SET
  _frequency = frequency;
  //////// Edit ends here: FREQUENCY_SET
}

