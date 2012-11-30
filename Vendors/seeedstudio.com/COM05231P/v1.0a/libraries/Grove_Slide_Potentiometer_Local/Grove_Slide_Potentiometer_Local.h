// Generated file: only edit in designated area!

#ifndef GROVE_SLIDE_POTENTIOMETER_LOCAL_H
#define GROVE_SLIDE_POTENTIOMETER_LOCAL_H

#include <MB7.h>

  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

class Grove_Slide_Potentiometer : public Maker_Bus_Module {
  public:
    // Constructor
    Grove_Slide_Potentiometer();

    // LED duty cycle
    UByte duty_cycle_get();
    void duty_cycle_set(UByte duty_cycle);

    // LED refresh frequency
    UShort frequency_get();
    void frequency_set(UShort frequency);

    // Return Potentiometer Value
    UShort value_get();

  //////// Edit begins here: PRIVATE
  private:
    UShort _duty_cycle;
    UShort _frequency;
  //////// Edit ends here: PRIVATE
};

#endif // GROVE_SLIDE_POTENTIOMETER_LOCAL_H
