// Generated file: only edit in designated areas!
#include <Grove_Thumb_Joystick_Local.h>
#include <MB7.h>

// Put top level includes, typedef's here:
  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

// Constructor
Grove_Thumb_Joystick::Grove_Thumb_Joystick(UByte address) {
  //////// Edit begins here: CONSTRUCTOR
    _left_right_pin = address;
    _up_down_pin = address + 1;
  //////// Edit ends here: CONSTRUCTOR
}

// left_right_get: Return the Left/Right Thumbstick value
UShort Grove_Thumb_Joystick::left_right_get() {
  UShort left_right_value;
  //////// Edit begins here: LEFT_RIGHT_GET
  left_right_value = (UShort)analogRead(_left_right_pin);
  //////// Edit ends here: LEFT_RIGHT_GET
  return left_right_value;
}

// up_down_get: Return the Left/Right Thumbstick value
UShort Grove_Thumb_Joystick::up_down_get() {
  UShort up_down_value;
  //////// Edit begins here: UP_DOWN_GET
  up_down_value = (UShort)analogRead(_up_down_pin);
  //////// Edit ends here: UP_DOWN_GET
  return up_down_value;
}

// is_pressed: Return *True* if thumbstick is depressed
Logical Grove_Thumb_Joystick::is_pressed() {
  Logical depressed_value;
  //////// Edit begins here: IS_PRESSED
  depressed_value = (Logical)(analogRead(_left_right_pin) > 1000);
  //////// Edit ends here: IS_PRESSED
  return depressed_value;
}

