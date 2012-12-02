// Generated file: only edit in designated areas!
#include <TinkerKit_Linear_Potentiometer_Local.h>
#include <MB7.h>

// Put top level includes, typedef's here:
  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

// Constructor
TinkerKit_Linear_Potentiometer::TinkerKit_Linear_Potentiometer(UByte address) {
  //////// Edit begins here: CONSTRUCTOR
    _pin = address;
  //////// Edit ends here: CONSTRUCTOR
}

// value_get: Return Potentiometer Value
UShort TinkerKit_Linear_Potentiometer::value_get() {
  UShort value;
  //////// Edit begins here: VALUE_GET
  value = (UShort)analogRead(_pin);
  //////// Edit ends here: VALUE_GET
  return value;
}

