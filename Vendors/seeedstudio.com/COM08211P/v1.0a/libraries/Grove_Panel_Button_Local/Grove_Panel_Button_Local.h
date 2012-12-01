// Generated file: only edit in designated area!

#ifndef GROVE_PANEL_BUTTON_LOCAL_H
#define GROVE_PANEL_BUTTON_LOCAL_H

#include <MB7.h>

  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

class Grove_Panel_Button : public Maker_Bus_Module {
  public:
    // Constructor
    Grove_Panel_Button(UByte address);

    // Return whether or not button is pressed
    Logical is_pressed();

  //////// Edit begins here: PRIVATE
  private:
    UByte _pin;
  //////// Edit ends here: PRIVATE
};

#endif // GROVE_PANEL_BUTTON_LOCAL_H
