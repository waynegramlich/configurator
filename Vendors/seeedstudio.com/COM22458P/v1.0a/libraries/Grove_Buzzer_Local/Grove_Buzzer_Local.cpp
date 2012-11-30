// Generated file: only edit in designated areas!
#include <Grove_Buzzer_Local.h>
#include <MB7.h>

// Put top level includes, typedef's here:
  //////// Edit begins here: TOP_LEVEL
const int buzzer_pin = 6;
  //////// Edit ends here: TOP_LEVEL

// Constructor
Grove_Buzzer::Grove_Buzzer() {
  //////// Edit begins here: CONSTRUCTOR
  pinMode(buzzer_pin, OUTPUT);
  _duty_cycle = 0;
  _frequency = 0;
  //////// Edit ends here: CONSTRUCTOR
}

// duty_cycle_get: LED duty cycle
UByte Grove_Buzzer::duty_cycle_get() {
  //////// Edit begins here: DUTY_CYCLE_GET
  return _duty_cycle;
  //////// Edit ends here: DUTY_CYCLE_GET
}

// duty_cycle_set: LED duty cycle
void Grove_Buzzer::duty_cycle_set(UByte duty_cycle) {
  //////// Edit begins here: DUTY_CYCLE_SET
  _duty_cycle = duty_cycle;
  if (duty_cycle >= 50) {
    digitalWrite(buzzer_pin, HIGH);
  } else {
    digitalWrite(buzzer_pin, LOW);
  }
  //////// Edit ends here: DUTY_CYCLE_SET
}

// frequency_get: LED refresh frequency
UShort Grove_Buzzer::frequency_get() {
  //////// Edit begins here: FREQUENCY_GET
  return _frequency;
  //////// Edit ends here: FREQUENCY_GET
}

// frequency_set: LED refresh frequency
void Grove_Buzzer::frequency_set(UShort frequency) {
  //////// Edit begins here: FREQUENCY_SET
  _frequency = frequency;
  //////// Edit ends here: FREQUENCY_SET
}

