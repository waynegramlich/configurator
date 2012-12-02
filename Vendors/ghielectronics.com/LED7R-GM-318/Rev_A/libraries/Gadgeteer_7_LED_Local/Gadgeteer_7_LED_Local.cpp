// Generated file: only edit in designated areas!
#include <Gadgeteer_7_LED_Local.h>
#include <MB7.h>

// Put top level includes, typedef's here:
  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

// Constructor
Gadgeteer_7_LED::Gadgeteer_7_LED(UByte address) {
  //////// Edit begins here: CONSTRUCTOR
  _mask = (UByte)0;
  _d1_pin = D3;
  _d2_pin = D4;
  _d3_pin = D5;
  _d4_pin = D6;
  _d5_pin = D7;
  _d6_pin = D8;
  _d7_pin = D9;
  pinMode(_d1_pin, OUTPUT);
  pinMode(_d2_pin, OUTPUT);
  pinMode(_d3_pin, OUTPUT);
  pinMode(_d4_pin, OUTPUT);
  pinMode(_d5_pin, OUTPUT);
  pinMode(_d6_pin, OUTPUT);
  pinMode(_d7_pin, OUTPUT);
  LED_Bits_set(_mask);
  //////// Edit ends here: CONSTRUCTOR
}

// LED_Bits_get: LED duty cycle
UByte Gadgeteer_7_LED::LED_Bits_get() {
  //////// Edit begins here: LED_BITS_GET
  return _mask;
  //////// Edit ends here: LED_BITS_GET
}

// LED_Bits_set: LED duty cycle
void Gadgeteer_7_LED::LED_Bits_set(UByte LED_Bits) {
  //////// Edit begins here: LED_BITS_SET
  _mask = LED_Bits;
  digitalWrite(_d1_pin, (_mask >> 0) & 1);  
  digitalWrite(_d2_pin, (_mask >> 1) & 1);  
  digitalWrite(_d3_pin, (_mask >> 2) & 1);  
  digitalWrite(_d4_pin, (_mask >> 3) & 1);  
  digitalWrite(_d5_pin, (_mask >> 4) & 1);  
  digitalWrite(_d6_pin, (_mask >> 5) & 1);  
  digitalWrite(_d7_pin, (_mask >> 6) & 1);  
  //////// Edit ends here: LED_BITS_SET
}

