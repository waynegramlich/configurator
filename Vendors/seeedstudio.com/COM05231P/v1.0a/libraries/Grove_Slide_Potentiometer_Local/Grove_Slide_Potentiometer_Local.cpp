// Generated file: only edit in designated areas!
#include <Grove_Slide_Potentiometer_Local.h>
#include <MB7.h>

// Put top level includes, typedef's here:
  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

// Constructor
Grove_Slide_Potentiometer::Grove_Slide_Potentiometer(UByte address) {
  //////// Edit begins here: CONSTRUCTOR
  _analog_pin = address;
  _duty_cycle = 0;
  _frequency = 0;
  _led_pin = address + 1;
  pinMode(_led_pin, OUTPUT);
  //////// Edit ends here: CONSTRUCTOR
}

// duty_cycle_get: LED duty cycle
UByte Grove_Slide_Potentiometer::duty_cycle_get() {
  //////// Edit begins here: DUTY_CYCLE_GET
  return _duty_cycle;
  //////// Edit ends here: DUTY_CYCLE_GET
}

// duty_cycle_set: LED duty cycle
void Grove_Slide_Potentiometer::duty_cycle_set(UByte duty_cycle) {
  //////// Edit begins here: DUTY_CYCLE_SET
  _duty_cycle = duty_cycle;
  if (duty_cycle >= 50) {
    digitalWrite(_led_pin, HIGH);
  } else {
    digitalWrite(_led_pin, LOW);
  }
  //////// Edit ends here: DUTY_CYCLE_SET
}

// frequency_get: LED refresh frequency
UShort Grove_Slide_Potentiometer::frequency_get() {
  //////// Edit begins here: FREQUENCY_GET
  return _frequency;
  //////// Edit ends here: FREQUENCY_GET
}

// frequency_set: LED refresh frequency
void Grove_Slide_Potentiometer::frequency_set(UShort frequency) {
  //////// Edit begins here: FREQUENCY_SET
  _frequency = frequency;
  //////// Edit ends here: FREQUENCY_SET
}

// value_get: Return Potentiometer Value
UShort Grove_Slide_Potentiometer::value_get() {
  UShort value;
  //////// Edit begins here: VALUE_GET
  return (UShort)analogRead(_analog_pin);
  //////// Edit ends here: VALUE_GET
  return value;
}

