// Generated file: only edit in designated area!

#ifndef TINKERKIT_LINEAR_POTENTIOMETER_LOCAL_H
#define TINKERKIT_LINEAR_POTENTIOMETER_LOCAL_H

#include <MB7.h>

  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

class TinkerKit_Linear_Potentiometer : public Maker_Bus_Module {
  public:
    // Constructor
    TinkerKit_Linear_Potentiometer(UByte address);

    // Return Potentiometer Value
    UShort value_get();

  //////// Edit begins here: PRIVATE
  private:
    UByte _pin;
  //////// Edit ends here: PRIVATE
};

#endif // TINKERKIT_LINEAR_POTENTIOMETER_LOCAL_H
