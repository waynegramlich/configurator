// Generated file: only edit in designated area!

#ifndef GROVE_THUMB_JOYSTICK_LOCAL_H
#define GROVE_THUMB_JOYSTICK_LOCAL_H

#include <MB7.h>

  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

class Grove_Thumb_Joystick : public Maker_Bus_Module {
  public:
    // Constructor
    Grove_Thumb_Joystick(UByte address);

    // Return the Left/Right Thumbstick value
    UShort left_right_get();

    // Return the Left/Right Thumbstick value
    UShort up_down_get();

    // Return *True* if thumbstick is depressed
    Logical is_pressed();

  //////// Edit begins here: PRIVATE
  private:
    UByte _left_right_pin;
    UByte _up_down_pin;
  //////// Edit ends here: PRIVATE
};

#endif // GROVE_THUMB_JOYSTICK_LOCAL_H
