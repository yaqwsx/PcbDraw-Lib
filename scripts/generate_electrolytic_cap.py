#!/usr/bin/env python

"""
  This program generates SMD passives (resistors, capacitors, etc).

  This uses the base model found in base/passives.svg

  This assumes that the part's origin is in the center of the part
"""
import sys
import os
from lxml import etree
from copy import deepcopy
import argparse
import math

def to_mm(i):
  return i * 25.4

def replace_keyvalue_value(svg_str, key, new_val):
  n = svg_str.split(";")
  n = [i.split(":") for i in n]
  for i in n:
    if i[0] == key:
      i[1] = str(new_val)
      break
  n = [":".join(i) for i in n]
  n = ";".join(n)
  return n

cap_sizes= [
    {'d': 4.0, 'p': 1.5},
    {'d': 4.0, 'p': 2.0},
    {'d': 5.0, 'p': 2.0},
    {'d': 5.0, 'p': 2.5},
    {'d': 6.3, 'p': 2.5},
    {'d': 7.5, 'p': 2.5},
    {'d': 8.0, 'p': 2.5},
    {'d': 8.0, 'p': 3.5},
    {'d': 8.0, 'p': 3.8},
    {'d': 8.0, 'p': 5.0},
    {'d': 10.0, 'p': 2.5},
    {'d': 10.0, 'p': 3.5},
    {'d': 10.0, 'p': 3.8},
    {'d': 10.0, 'p': 5.0},
    {'d': 10.0, 'p': 7.5},
    {'d': 12.5, 'p': 2.5},
    {'d': 12.5, 'p': 5.0},
    {'d': 12.5, 'p': 7.5},
    {'d': 13.0, 'p': 2.5},
    {'d': 13.0, 'p': 5.0},
    {'d': 13.0, 'p': 7.5},
    {'d': 14.0, 'p': 5.0},
    {'d': 14.0, 'p': 7.5},
    {'d': 16.0, 'p': 7.5},
    {'d': 17.0, 'p': 7.5},
    {'d': 18.0, 'p': 7.5},
]

cap_cathode_angle = math.radians(20)

if __name__ == "__main__":

  for size in cap_sizes:
    document = etree.parse("base/ECapBase.svg")
    root = document.getroot()

    # Delete all inkscape grids and crap
    p = root.find("{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}namedview")
    root.remove(p)

    # Remove the origin to add later. This is to place them above the pins
    origin = root.find(".//*[@id='origin']")
    root.remove(origin)

    circle_fill = root.find(".//*[@id='blue_c']")
    circle_cathode = root.find(".//*[@id='cathode_m']")
    circle_white = root.find(".//*[@id='inner_white_c']")
    circle_outline = root.find(".//*[@id='outline_c']")

    # Set the circle sizes based off the size that we want
    var_c_x_center = size['p']/2    # The center x location is in between the pins
    var_radius = size['d'] / 2

    circle_fill.attrib["r"] = "{}".format(var_radius)
    circle_fill.attrib["cx"] = "{}".format(var_c_x_center)

    circle_outline.attrib["r"] = "{}".format(var_radius)
    circle_outline.attrib["cx"] = "{}".format(var_c_x_center)

    circle_white.attrib["r"] = "{}".format(var_radius/1.5)
    circle_white.attrib["cx"] = "{}".format(var_c_x_center)

    circle_cathode.attrib["d"] = "M {},{} A {},{} 0 0 1 {},{} L {},0 Z".format(var_radius*math.cos(cap_cathode_angle)+var_c_x_center, -var_radius*math.sin(cap_cathode_angle), var_radius, var_radius, var_radius*math.cos(cap_cathode_angle)+var_c_x_center, var_radius*math.sin(cap_cathode_angle), var_c_x_center)

    root.append(origin)
    # Save
    sn = "export/CP_Radial_D{:.1f}mm_P{:.2f}mm.svg".format(size['d'], size['p'])
    if not os.path.isdir("export"):
      os.mkdir("export")
    document.write(sn)
    os.system(f"inkscape {sn} -D -o {sn} ;")
