// Generated file: only edit in designated area!

#ifndef GADGETEER_JOYSTICK_LOCAL_H
#define GADGETEER_JOYSTICK_LOCAL_H

#include <MB7.h>

  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

class Gadgeteer_Joystick : public Maker_Bus_Module {
  public:
    // Constructor
    Gadgeteer_Joystick(UByte address);

    // Return the Left/Right Joystick value
    UShort left_right_get();

    // Return the Left/Right Joystick value
    UShort up_down_get();

    // Return *True* if joystick is depressed
    Logical is_pressed();

  //////// Edit begins here: PRIVATE
  private:
    UByte _button_pin;
    UByte _left_right_pin;
    UByte _up_down_pin;
  //////// Edit ends here: PRIVATE
};

#endif // GADGETEER_JOYSTICK_LOCAL_H
