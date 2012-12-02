// Generated file: only edit in designated areas!
#include <Gadgeteer_Joystick_Local.h>
#include <MB7.h>

// Put top level includes, typedef's here:
  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

// Constructor
Gadgeteer_Joystick::Gadgeteer_Joystick(UByte address) {
  //////// Edit begins here: CONSTRUCTOR
  _button_pin = A0;
  _up_down_pin = A1;
  _left_right_pin = A2;
  pinMode(_button_pin, INPUT);
  //////// Edit ends here: CONSTRUCTOR
}

// left_right_get: Return the Left/Right Joystick value
UShort Gadgeteer_Joystick::left_right_get() {
  UShort left_right_value;
  //////// Edit begins here: LEFT_RIGHT_GET
  left_right_value = (UShort)analogRead(_left_right_pin);
  //////// Edit ends here: LEFT_RIGHT_GET
  return left_right_value;
}

// up_down_get: Return the Left/Right Joystick value
UShort Gadgeteer_Joystick::up_down_get() {
  UShort up_down_value;
  //////// Edit begins here: UP_DOWN_GET
  up_down_value = (UShort)analogRead(_up_down_pin);
  //////// Edit ends here: UP_DOWN_GET
  return up_down_value;
}

// is_pressed: Return *True* if joystick is depressed
Logical Gadgeteer_Joystick::is_pressed() {
  Logical depressed_value;
  //////// Edit begins here: IS_PRESSED
  depressed_value = (Logical)(digitalRead(_button_pin) == 0);
  //////// Edit ends here: IS_PRESSED
  return depressed_value;
}

