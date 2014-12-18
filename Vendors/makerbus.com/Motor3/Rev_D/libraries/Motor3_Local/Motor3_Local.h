// Generated file: only edit in designated area!

#ifndef MOTOR3_LOCAL_H
#define MOTOR3_LOCAL_H

//#include <MB7.h>
#include <Maker_Bus.h>

  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

class Motor3 : public Maker_Bus_Module {
  public:
    // Constructor
    Motor3(UByte address);

    // Motor speed
    Byte speed_get();
    void speed_set(Byte speed);

    // Invert motor direction
    Logical direction_invert_get();
    void direction_invert_set(Logical direction_invert);

    // 8-bit Motor encoder
    Byte encoder8_get();
    void encoder8_set(Byte encoder8);

    // Motor encoder
    Integer encoder_get();
    void encoder_set(Integer encoder);

  //////// Edit begins here: PRIVATE
  //////// Edit ends here: PRIVATE
};

#endif // MOTOR3_LOCAL_H
