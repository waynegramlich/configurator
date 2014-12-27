// Generated file: only edit in designated area!

#ifndef BUS_BRIDGE_ENCODERS_SONAR_LOCAL_H
#define BUS_BRIDGE_ENCODERS_SONAR_LOCAL_H

#include <Bus.h>

  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

class Bus_Bridge_Encoders_Sonar : public Bus_Module {
  public:
    // Constructor
    Bus_Bridge_Encoders_Sonar(UByte address);

    // LED to control
    Logical led_get();
    void led_set(Logical led);

    // Encoder 1
    Integer encoder1_get();
    void encoder1_set(Integer encoder1);

    // Encoder 2
    Integer encoder2_get();
    void encoder2_set(Integer encoder2);

    // Motor 1
    Byte motor1_get();
    void motor1_set(Byte motor1);

    // Motor 1
    Byte motor2_get();
    void motor2_set(Byte motor2);

    // Toggle motor direction.
    Logical motor1_reverse_get();
    void motor1_reverse_set(Logical motor1_reverse);

    // Toggle motor direction.
    Logical motor2_reverse_get();
    void motor2_reverse_set(Logical motor2_reverse);

    // Reset both encoders to zero.
    void encoders_reset();

    // Cause both encoder values to be latched.
    void encoders_latch();

  //////// Edit begins here: PRIVATE
  //private:
    Logical _led;
    Integer _encoder1;
    Integer _encoder2;
    Integer _encoder2_latched;
    Byte _motor1;
    Byte _motor2;
    Logical _motor1_reverse;
    Logical _motor2_reverse;
  //////// Edit ends here: PRIVATE
};

#endif // BUS_BRIDGE_ENCODERS_SONAR_LOCAL_H
