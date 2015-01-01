// Generated file: only edit in designated areas!
#include <Bus_Bridge_Encoders_Sonar_Local.h>
#include <Bus.h>

// Put top level includes, typedef's here:
  //////// Edit begins here: TOP_LEVEL
  //////// Edit ends here: TOP_LEVEL

// Constructor
Bus_Bridge_Encoders_Sonar::Bus_Bridge_Encoders_Sonar(UByte address) {
  //////// Edit begins here: CONSTRUCTOR
  led_set(1);
  encoder1_set(0);
  encoder2_set(0);
  encoder1_reverse_set((Logical)1);
  encoder2_reverse_set((Logical)1);
  motor1_set(0);
  motor2_set(0);
  motor1_reverse_set((Logical)0);
  motor2_reverse_set((Logical)0);
  motors_encoders_swap_set((Logical)1);
  //////// Edit ends here: CONSTRUCTOR
}

// led_get: LED to control
Logical Bus_Bridge_Encoders_Sonar::led_get() {
  //////// Edit begins here: LED_GET
  return _led;
  //////// Edit ends here: LED_GET
}

// led_set: LED to control
void Bus_Bridge_Encoders_Sonar::led_set(Logical led) {
  //////// Edit begins here: LED_SET
  _led = led;
  digitalWrite(13, led);
  //////// Edit ends here: LED_SET
}

// encoder1_get: Encoder 1
Integer Bus_Bridge_Encoders_Sonar::encoder1_get() {
  //////// Edit begins here: ENCODER1_GET
  Integer encoder = _motors_encoders_swap ? _encoder2 :_encoder1;
  if (_encoder1_reverse) {
    encoder = -encoder;
  }
  return encoder;
  //////// Edit ends here: ENCODER1_GET
}

// encoder1_set: Encoder 1
void Bus_Bridge_Encoders_Sonar::encoder1_set(Integer encoder1) {
  //////// Edit begins here: ENCODER1_SET
  if (_encoder1_reverse) {
    encoder1 = -encoder1;
  }
  if (_motors_encoders_swap) {
    _encoder2 = encoder1;
  } else {
    _encoder1 = encoder1;
  }
  //////// Edit ends here: ENCODER1_SET
}

// encoder2_get: Encoder 2
Integer Bus_Bridge_Encoders_Sonar::encoder2_get() {
  //////// Edit begins here: ENCODER2_GET
  Integer encoder = _motors_encoders_swap ? _encoder1 :_encoder2;
  if (_encoder2_reverse) {
    encoder = -encoder;
  }
  return encoder;
  //////// Edit ends here: ENCODER2_GET
}

// encoder2_set: Encoder 2
void Bus_Bridge_Encoders_Sonar::encoder2_set(Integer encoder2) {
  //////// Edit begins here: ENCODER2_SET
  if (_encoder2_reverse) {
    encoder2 = -encoder2;
  }
  if (_motors_encoders_swap) {
    _encoder1 = encoder2;
  } else {
    _encoder2 = encoder2;
  }
  //////// Edit ends here: ENCODER2_SET
}

// motor1_get: Motor 1
Byte Bus_Bridge_Encoders_Sonar::motor1_get() {
  //////// Edit begins here: MOTOR1_GET
  return _motor1;
  //////// Edit ends here: MOTOR1_GET
}

// motor1_set: Motor 1
void Bus_Bridge_Encoders_Sonar::motor1_set(Byte motor1) {
  //////// Edit begins here: MOTOR1_SET

  // Save *motor1* for future reads:
  _motor1 = motor1;

  // Set the direction pins:
  Logical pin1 = (Logical)0;
  Logical pin2 = (Logical)1;
  if ((motor1 > 0 && _motor1_reverse) || (motor1 < 0 && !_motor1_reverse)) {
    // Reverse the motor direction:
    pin1 = (Logical)1;
    pin2 = (Logical)0;
  } else if ((motor1 & 0x7f) == 0) {
    // Put the motor into "brake" mode:
    pin2 = (Logical)0;
  } // else leave the motor in the forward direction:

  // Compute *pwm* (Pulse Width Modulation) value from *motor1*:
  if (motor1 < 0) {
    motor1 = -motor1;
  }
  UByte pwm = ((UByte)motor1 & 0x7f) << 1;
  if (motor1 == 0x80) {
    // A speed of 0x80 (== (Byte)-128), is full brake mode:
    pwm = 0xff;
  }
  if (_motors_encoders_swap) {
    digitalWrite(_direction_3a_pin, pin1);
    digitalWrite(_direction_4a_pin, pin2);
    analogWrite(_direction_enable_34_pin, pwm);
  } else {
    digitalWrite(_direction_1a_pin, pin1);
    digitalWrite(_direction_2a_pin, pin2);
    analogWrite(_direction_enable_12_pin, pwm);
  }
  //////// Edit ends here: MOTOR1_SET
}

// motor2_get: Motor 2
Byte Bus_Bridge_Encoders_Sonar::motor2_get() {
  //////// Edit begins here: MOTOR2_GET
  return _motor2;
  //////// Edit ends here: MOTOR2_GET
}

// motor2_set: Motor 2
void Bus_Bridge_Encoders_Sonar::motor2_set(Byte motor2) {
  //////// Edit begins here: MOTOR2_SET

  // Save *motor2* for future reads:
  _motor2 = motor2;

  // Set the direction pins:
  Logical pin1 = (Logical)0;
  Logical pin2 = (Logical)1;
  if ((motor2 > 0 && _motor2_reverse) || (motor2 < 0 && !_motor2_reverse)) {
    // Reverse the motor direction:
    pin1 = (Logical)1;
    pin2 = (Logical)0;
  } else if ((motor2 & 0x7f) == 0) {
    // Put the motor into "brake" mode:
    pin2 = (Logical)0;
  } // else leave the motor in the forward direction:

  // Compute *pwm* (Pulse Width Modulation) value from *motor2*:
  if (motor2 < 0) {
    motor2 = -motor2;
  }
  UByte pwm = ((UByte)motor2 & 0x7f) << 1;
  if (motor2 == 0x80) {
    // A speed of 0x80 (== (Byte)-128), is full brake mode:
    pwm = 0xff;
  }
  if (_motors_encoders_swap) {
    analogWrite(_direction_enable_12_pin, pwm);
    digitalWrite(_direction_1a_pin, pin1);
    digitalWrite(_direction_2a_pin, pin2);
  } else {
    analogWrite(_direction_enable_34_pin, pwm);
    digitalWrite(_direction_3a_pin, pin1);
    digitalWrite(_direction_4a_pin, pin2);
  }
  //////// Edit ends here: MOTOR2_SET
}

// motor1_reverse_get: Toggle motor direction.
Logical Bus_Bridge_Encoders_Sonar::motor1_reverse_get() {
  //////// Edit begins here: MOTOR1_REVERSE_GET
  return _motor1_reverse;
  //////// Edit ends here: MOTOR1_REVERSE_GET
}

// motor1_reverse_set: Toggle motor direction.
void Bus_Bridge_Encoders_Sonar::motor1_reverse_set(Logical motor1_reverse) {
  //////// Edit begins here: MOTOR1_REVERSE_SET
  _motor1_reverse = motor1_reverse;
  //////// Edit ends here: MOTOR1_REVERSE_SET
}

// motor2_reverse_get: Toggle motor direction.
Logical Bus_Bridge_Encoders_Sonar::motor2_reverse_get() {
  //////// Edit begins here: MOTOR2_REVERSE_GET
  return _motor2_reverse;
  //////// Edit ends here: MOTOR2_REVERSE_GET
}

// motor2_reverse_set: Toggle motor direction.
void Bus_Bridge_Encoders_Sonar::motor2_reverse_set(Logical motor2_reverse) {
  //////// Edit begins here: MOTOR2_REVERSE_SET
  _motor2_reverse = motor2_reverse;
  //////// Edit ends here: MOTOR2_REVERSE_SET
}

// encoder1_reverse_get: Toggle encoder direction.
Logical Bus_Bridge_Encoders_Sonar::encoder1_reverse_get() {
  //////// Edit begins here: ENCODER1_REVERSE_GET
  return _encoder1_reverse;
  //////// Edit ends here: ENCODER1_REVERSE_GET
}

// encoder1_reverse_set: Toggle encoder direction.
void Bus_Bridge_Encoders_Sonar::encoder1_reverse_set(Logical encoder1_reverse) {
  //////// Edit begins here: ENCODER1_REVERSE_SET
  _encoder1_reverse = encoder1_reverse;
  //////// Edit ends here: ENCODER1_REVERSE_SET
}

// encoder2_reverse_get: Toggle encoder direction.
Logical Bus_Bridge_Encoders_Sonar::encoder2_reverse_get() {
  //////// Edit begins here: ENCODER2_REVERSE_GET
  return _encoder2_reverse;
  //////// Edit ends here: ENCODER2_REVERSE_GET
}

// encoder2_reverse_set: Toggle encoder direction.
void Bus_Bridge_Encoders_Sonar::encoder2_reverse_set(Logical encoder2_reverse) {
  //////// Edit begins here: ENCODER2_REVERSE_SET
  _encoder2_reverse = encoder2_reverse;
  //////// Edit ends here: ENCODER2_REVERSE_SET
}

// motors_encoders_swap_get: Toggle encoder direction.
Logical Bus_Bridge_Encoders_Sonar::motors_encoders_swap_get() {
  //////// Edit begins here: MOTORS_ENCODERS_SWAP_GET
  return _motors_encoders_swap;
  //////// Edit ends here: MOTORS_ENCODERS_SWAP_GET
}

// motors_encoders_swap_set: Toggle encoder direction.
void Bus_Bridge_Encoders_Sonar::motors_encoders_swap_set(Logical motors_encoders_swap) {
  //////// Edit begins here: MOTORS_ENCODERS_SWAP_SET
  _motors_encoders_swap = motors_encoders_swap;
  //////// Edit ends here: MOTORS_ENCODERS_SWAP_SET
}

// encoders_reset: Reset both encoders to zero.
void Bus_Bridge_Encoders_Sonar::encoders_reset() {
  //////// Edit begins here: ENCODERS_RESET
  _encoder1 = 0;
  _encoder2 = 0;
  //////// Edit ends here: ENCODERS_RESET
}

// encoders_latch: Cause both encoder values to be latched.
void Bus_Bridge_Encoders_Sonar::encoders_latch() {
  //////// Edit begins here: ENCODERS_LATCH
  //////// Edit ends here: ENCODERS_LATCH
}

