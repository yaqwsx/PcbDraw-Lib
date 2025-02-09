#!/usr/bin/env python

"""

This script is to be ran inside KiCAD-base/Resistor_THT

The base design's resistor is 6.0 x 2.075mm, so a new resistor lenght and width must be 
scaled from this size to the desired size.
"""

from lxml import etree
from copy import deepcopy
import re
import os

res_options = [
  {'din': 'DIN0204', 'l': 3.6, 'd': 1.6, 'ps_h': [5.08, 7.62], 'ps_v': [1.90, 2.54, 5.08]},
  {'din': 'DIN0207', 'l': 6.3, 'd': 2.5, 'ps_h': [7.62, 10.16, 15.24], 'ps_v': [2.54, 5.08]},
  {'din': 'DIN0309', 'l': 9.0, 'd': 3.2, 'ps_h': [12.7, 15.24, 20.32, 25.4], 'ps_v': [2.54, 5.08]},
  {'din': 'DIN0411','l': 9.9, 'd': 3.6, 'ps_h': [12.7, 15.24, 20.32, 25.4], 'ps_v': [5.08, 7.62]},
  {'din': 'DIN0414','l': 11.9, 'd': 4.5, 'ps_h': [15.24, 20.32, 25.4], 'ps_v': [5.08, 7.62]},
  {'din': 'DIN0516','l': 15.5, 'd': 5.0, 'ps_h': [20.32, 25.4, 30.48], 'ps_v': [5.08, 7.62]},
  {'din': 'DIN0614','l': 14.3, 'd': 5.7, 'ps_h': [15.24, 20.32, 25.4], 'ps_v': [5.08, 7.62]},
  {'din': 'DIN0617','l': 17.0, 'd': 6.0, 'ps_h': [20.32, 25.4, 30.48], 'ps_v': [5.08, 7.62]},
  {'din': 'DIN0918','l': 18.0, 'd': 9.0, 'ps_h': [22.86, 25.4, 30.48], 'ps_v': [7.62]},
  {'din': 'DIN0922','l': 20.0, 'd': 9.0, 'ps_h': [25.4, 30.48], 'ps_v': [7.62]},
]

def map_scale(old_scale, new_scale):
    # Assume a zero old and new min value
    return new_scale / old_scale

def map_stroke_value(s_v, old_scale, new_scale):
    return s_v * (new_scale / old_scale)

if __name__ == "__main__":
    if not os.path.isdir("export"):
      os.mkdir("export")

    # generate all the horizonal resistors
    for r in res_options:
        for pin_len in r['ps_h']:
            # if r['l'] > 6.0:
                # document = etree.parse("base/R_Axial_Horizonal_Long_BASE.svg")
                # orig_ysize = 1.834
            # else:
            document = etree.parse("base/R_Axial_Horizonal_BASE.svg")
            orig_ysize = 2.075

            def mapX(oldX):
                v = oldX*(r['l']/6.0)
                return f"{v:.3f}"
            def mapY(oldY):
                v = oldY*(r['d']/orig_ysize)
                return f"{v:.3f}"
            def mapXY(oldX, oldY):
                return mapX(oldX) + ',' + mapY(oldY)

            root = document.getroot()
            
            # Delete all inkscape grids
            p = root.find("{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}namedview")
            for c in p.findall("{http://www.inkscape.org/namespaces/inkscape}grid"):
                p.remove(c)
            
            # Remove the origin to add later. This is to place them above the pins
            origin = root.find(".//*[@id='origin']")
            root.remove(origin)
            
            # Change the pin's lenght to the one for a particular resistor
            pin = root.find(".//*[@id='main_pin']")
            pin.attrib["d"] = pin.attrib["d"].replace("10", str(pin_len))
            
            # Find the main body, then transform it
            bean = root.find(".//*[@id='res_bean']")
            bean.attrib["transform"] = "translate({}, 0)".format((pin_len/2)-(r['l']/2))

            # set new bean path, to scale it nicely including stroke
            # from design file:
            #       "M 0,0 C 0,1 0.9,1.3 1.5,0.8 H 3 4.5 C 5.1,1.3 6,1 6,0 6,-1 5.1,-1.3 4.5,-0.8 H 3 1.5 C 0.9,-1.3 0,-1 0,0 Z"
            curveDamp = 0.0
            if r['l'] > 6.0:
                curveDamp = ((r['l']-6.0)/20.0) * -0.5

            def dampenCurve(cStartX, cStartY, cLocX, cLocY):
                deltaX = cLocX - cStartX
                deltaY = cLocY - cStartY
                deltaX *= curveDamp
                deltaY *= curveDamp
                return mapXY(cLocX+deltaX, cLocY+deltaY)


            beanPath = f"M 0,0 \
                C {mapXY(0.0,1.0)} {dampenCurve(1.5,0.8, 0.9,1.3)} {mapXY(1.5,0.8)} \
                H {mapX(3.0)} {mapX(4.5)} \
                C {dampenCurve(4.5, 0.8, 5.1,1.3)} {mapXY(6,1)} {mapXY(6,0)} \
                  {mapXY(6,-1)} {dampenCurve(4.5, -0.8, 5.1,-1.3)} {mapXY(4.5,-0.8)} \
                H {mapX(3.0)} {mapX(1.5)} \
                C {dampenCurve(1.5,-0.8, 0.9,-1.3)} {mapXY(0,-1)} 0,0\
                Z"

            bean_fill = root.find(".//*[@id='bean_fill']")
            bean_fill.attrib["d"] = beanPath
            
            bean_outline = root.find(".//*[@id='bean_outline']")
            bean_outline.attrib["style"] = re.sub(r'stroke-width:\d*\.?\d+', f'stroke-width:{map_stroke_value(0.09, 6.0, r['l']):.4f}', bean_outline.attrib["style"])
            bean_outline.attrib["d"] = beanPath

            # for each resistor band, also move the rectangle size
            resBands = [f"res_band{i+1}" for i in range(4)]
            resBands += [f"res_5band{i+1}" for i in range(5)]
            resBands += ['res_zeroband']
            for bandI in resBands:
                band = root.find(f".//*[@id='{bandI}']")
                for key in ['x', 'width']:
                    band.attrib[key] = mapX(float(band.attrib[key]))
                for key in ['y','height']:
                    band.attrib[key] = mapY(float(band.attrib[key]))
            
            # Add the origin back
            root.append(origin)
            # Save
            document.write("export/R_Axial_{:}_L{:.1f}mm_D{:.1f}mm_P{:.2f}mm_Horizontal.svg".format(r['din'], r['l'], r['d'], pin_len))

    # Generate the vertical resistors
    for r in res_options:
        for pin_len in r['ps_v']:
            document = etree.parse("base/R_Axial_Vertical_BASE.svg")
            root = document.getroot()

            # Delete all inkscape grids
            p = root.find("{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}namedview")
            for c in p.findall("{http://www.inkscape.org/namespaces/inkscape}grid"):
                p.remove(c)

            # Remove the origin to add later. This is to place them above the pins
            origin = root.find(".//*[@id='origin']")
            root.remove(origin)

            # Change the pin's lenght to the one for a particular resistor
            pin = root.find(".//*[@id='main_pin']")
            pin.attrib["d"] = pin.attrib["d"].replace("10", str(pin_len))


            # Find the main body, then transform it
            bean = root.find(".//*[@id='res_bean']")
            bean.attrib["transform"] = "scale({a}, {a})".format(a=map_scale(0.9*2, r['d']))

            bean_outline = root.find(".//*[@id='bean_outline']")
            # bean_outline.attrib["style"] = re.sub(r'stroke-width:\d*\.?\d+', f'stroke-width:{map_stroke_value(0.09, 0.9*2, r['d']):.4f}', bean_outline.attrib["style"])

            # Add the origin back
            root.append(origin)
            # Save
            document.write("export/R_Axial_{:}_L{:.1f}mm_D{:.1f}mm_P{:.2f}mm_Vertical.svg".format(r['din'], r['l'], r['d'], pin_len))
