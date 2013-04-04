#!/usr/bin/env python

from time import sleep
from maker_bus import *
from billbot import *

class Robot:

  def __init__(self):

    maker_bus_base = Maker_Bus_Base(None)
    self.maker_bus_base = maker_bus_base
    self.project = Project(maker_bus_base)

  def run(self):
    project = self.project
    motor3_left = project.motor3_left
    motor3_right = project.motor3_right

    sleep(2.0)
    motor3_left.speed_set(55)
    motor3_right.speed_set(55)
    sleep(2.0)

    while True:
      motor3_left.speed_set(55)
      motor3_right.speed_set(55)
      sleep(1.0)
      motor3_left.speed_set(0)
      motor3_right.speed_set(0)
      sleep(1.0)


robot = Robot()
robot.run()
