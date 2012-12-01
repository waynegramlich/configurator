// Generated file: only edit in designated area!

#ifndef LCD1602_LOCAL_H
#define LCD1602_LOCAL_H

#include <MB7.h>

  //////// Edit begins here: TOP_LEVEL
  #include <LiquidCrystal.h>
  #include <LCDKeypad.h>
  //////// Edit ends here: TOP_LEVEL

class LCD1602 : public Maker_Bus_Module, public LCDKeypad  {
  public:
    // Constructor
    LCD1602(UByte address);

    // Enable or Disable the display.
    Logical display_get();
    void display_set(Logical display);

    // Enable or disable blinking cursor.
    Logical blink_get();
    void blink_set(Logical blink);

    // Enable or disable cursor visibility.
    Logical cursor_get();
    void cursor_set(Logical cursor);

    // Specify cursor direction as left to right or right to left.
    Logical direction_get();
    void direction_set(Logical direction);

    // Enable or disable automatic scrolling.
    Logical autoscroll_get();
    void autoscroll_set(Logical autoscroll);

    // Clear the display.
    void clear();

    // Cause cursor to move to upper left.
    void home();

    // Move the cursor to (*column*, *row*).
    void cursor_move(UByte column, UByte row);

    // Return the *button* value.
    UByte button();

    // Send *character* to display.
    void character_send(Character character);

    // Shift entire display left by one character.
    void display_shift_left();

    // Shift entire display left by one character.
    void display_shift_right();

  //////// Edit begins here: PRIVATE
  private:
    Logical _autoscroll;
    Logical _blink;
    Logical _cursor;
    Logical _display;
    Logical _direction;
  //////// Edit ends here: PRIVATE
};

#endif // LCD1602_LOCAL_H
