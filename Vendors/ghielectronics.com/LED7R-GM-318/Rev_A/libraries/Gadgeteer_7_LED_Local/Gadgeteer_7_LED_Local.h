// Generated file: only edit in designated area!

#ifndef GADGETEER_7_LED_LOCAL_H
#define GADGETEER_7_LED_LOCAL_H

#include <MB7.h>

  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

class Gadgeteer_7_LED : public Maker_Bus_Module {
  public:
    // Constructor
    Gadgeteer_7_LED(UByte address);

    // LED duty cycle
    UByte LED_Bits_get();
    void LED_Bits_set(UByte LED_Bits);

  //////// Edit begins here: PRIVATE
  private:
    UByte _mask;
    UByte _d1_pin;
    UByte _d2_pin;
    UByte _d3_pin;
    UByte _d4_pin;
    UByte _d5_pin;
    UByte _d6_pin;
    UByte _d7_pin;
  //////// Edit ends here: PRIVATE
};

#endif // GADGETEER_7_LED_LOCAL_H
