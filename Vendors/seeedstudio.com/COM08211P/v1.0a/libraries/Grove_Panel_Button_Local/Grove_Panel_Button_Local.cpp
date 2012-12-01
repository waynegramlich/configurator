// Generated file: only edit in designated areas!
#include <Grove_Panel_Button_Local.h>
#include <MB7.h>

// Put top level includes, typedef's here:
  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

// Constructor
Grove_Panel_Button::Grove_Panel_Button(UByte address) {
  //////// Edit begins here: CONSTRUCTOR
  _pin = address;
  pinMode(_pin, INPUT);
  //////// Edit ends here: CONSTRUCTOR
}

// is_pressed: Return whether or not button is pressed
Logical Grove_Panel_Button::is_pressed() {
  Logical button_value;
  //////// Edit begins here: IS_PRESSED
  button_value = (Logical)digitalRead(_pin);
  //////// Edit ends here: IS_PRESSED
  return button_value;
}

