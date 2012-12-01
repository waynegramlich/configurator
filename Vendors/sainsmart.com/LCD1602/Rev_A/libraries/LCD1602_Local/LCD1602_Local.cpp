// Generated file: only edit in designated areas!
#include <LCD1602_Local.h>
#include <MB7.h>

// Put top level includes, typedef's here:
  //////// Edit begins here: TOP_LEVEL
  #include <LiquidCrystal.h>
  //////// Edit ends here: TOP_LEVEL

// Constructor
LCD1602::LCD1602(UByte address) {
  //////// Edit begins here: CONSTRUCTOR
  //////// Edit ends here: CONSTRUCTOR
}

// display_get: Enable or Disable the display.
Logical LCD1602::display_get() {
  //////// Edit begins here: DISPLAY_GET
  return _display;
  //////// Edit ends here: DISPLAY_GET
}

// display_set: Enable or Disable the display.
void LCD1602::display_set(Logical display) {
  //////// Edit begins here: DISPLAY_SET
  _display = display;
  if (display) {
    LiquidCrystal::display();
  } else {
    LiquidCrystal::noDisplay();
  }
  //////// Edit ends here: DISPLAY_SET
}

// blink_get: Enable or disable blinking cursor.
Logical LCD1602::blink_get() {
  //////// Edit begins here: BLINK_GET
  return _blink;
  //////// Edit ends here: BLINK_GET
}

// blink_set: Enable or disable blinking cursor.
void LCD1602::blink_set(Logical blink) {
  //////// Edit begins here: BLINK_SET
  _blink = blink;
  if (blink) {
    LiquidCrystal::blink();
  } else {
    LiquidCrystal::noBlink();
  }
  //////// Edit ends here: BLINK_SET
}

// cursor_get: Enable or disable cursor visibility.
Logical LCD1602::cursor_get() {
  //////// Edit begins here: CURSOR_GET
  return _cursor;
  //////// Edit ends here: CURSOR_GET
}

// cursor_set: Enable or disable cursor visibility.
void LCD1602::cursor_set(Logical cursor) {
  //////// Edit begins here: CURSOR_SET
  _cursor = cursor;
  if (cursor) {
    LiquidCrystal::cursor();
  } else {
    LiquidCrystal::noCursor();
  }
  //////// Edit ends here: CURSOR_SET
}

// direction_get: Specify cursor direction as left to right or right to left.
Logical LCD1602::direction_get() {
  //////// Edit begins here: DIRECTION_GET
  return _direction;
  //////// Edit ends here: DIRECTION_GET
}

// direction_set: Specify cursor direction as left to right or right to left.
void LCD1602::direction_set(Logical direction) {
  //////// Edit begins here: DIRECTION_SET
  _direction = direction;
  if (direction) {
    LiquidCrystal::leftToRight();
  } else {
    LiquidCrystal::rightToLeft();
  }
  //////// Edit ends here: DIRECTION_SET
}

// autoscroll_get: Enable or disable automatic scrolling.
Logical LCD1602::autoscroll_get() {
  //////// Edit begins here: AUTOSCROLL_GET
  return _autoscroll;
  //////// Edit ends here: AUTOSCROLL_GET
}

// autoscroll_set: Enable or disable automatic scrolling.
void LCD1602::autoscroll_set(Logical autoscroll) {
  //////// Edit begins here: AUTOSCROLL_SET
  _autoscroll = autoscroll;
  if (autoscroll) {
    LiquidCrystal::autoscroll();
  } else {
    LiquidCrystal::noAutoscroll();
  }
  //////// Edit ends here: AUTOSCROLL_SET
}

// clear: Clear the display.
void LCD1602::clear() {
  //////// Edit begins here: CLEAR
  LiquidCrystal::clear();
  //////// Edit ends here: CLEAR
}

// home: Cause cursor to move to upper left.
void LCD1602::home() {
  //////// Edit begins here: HOME
  LiquidCrystal::home();
  //////// Edit ends here: HOME
}

// cursor_move: Move the cursor to (*column*, *row*).
void LCD1602::cursor_move(UByte column, UByte row) {
  //////// Edit begins here: CURSOR_MOVE
  LiquidCrystal::setCursor(column, row);
  //////// Edit ends here: CURSOR_MOVE
}

// button: Return the *button* value.
UByte LCD1602::button() {
  UByte button;
  //////// Edit begins here: BUTTON
  button = LCDKeypad::button();
  //////// Edit ends here: BUTTON
  return button;
}

// character_send: Send *character* to display.
void LCD1602::character_send(Character character) {
  //////// Edit begins here: CHARACTER_SEND
  write(character);
  //////// Edit ends here: CHARACTER_SEND
}

// display_shift_left: Shift entire display left by one character.
void LCD1602::display_shift_left() {
  //////// Edit begins here: DISPLAY_SHIFT_LEFT
  LiquidCrystal::scrollDisplayLeft();
  //////// Edit ends here: DISPLAY_SHIFT_LEFT
}

// display_shift_right: Shift entire display left by one character.
void LCD1602::display_shift_right() {
  //////// Edit begins here: DISPLAY_SHIFT_RIGHT
  LiquidCrystal::scrollDisplayRight();
  //////// Edit ends here: DISPLAY_SHIFT_RIGHT
}

