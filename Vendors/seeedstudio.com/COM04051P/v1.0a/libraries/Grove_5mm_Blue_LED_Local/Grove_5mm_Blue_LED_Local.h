// Generated file: only edit in designated area!

#ifndef GROVE_5MM_BLUE_LED_LOCAL_H
#define GROVE_5MM_BLUE_LED_LOCAL_H

#include <MB7.h>

  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

class Grove_5mm_Blue_LED : public Maker_Bus_Module {
  public:
    // Constructor
    Grove_5mm_Blue_LED(UByte address);

    // LED duty cycle
    UByte duty_cycle_get();
    void duty_cycle_set(UByte duty_cycle);

    // LED refresh frequency
    UShort frequency_get();
    void frequency_set(UShort frequency);

  //////// Edit begins here: PRIVATE
  private:
    UByte _pin;
    UShort _duty_cycle;
    UShort _frequency;
  //////// Edit ends here: PRIVATE
};

#endif // GROVE_5MM_BLUE_LED_LOCAL_H
