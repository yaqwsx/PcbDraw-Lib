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

def to_mm(i):
  return i * 25.4

def replace_unset_values(default_dict, newkeys_dict):
  ret_dict = default_dict.copy()
  for d in default_dict:
    if d not in newkeys_dict:
      continue
    if isinstance(default_dict[d], dict):
      ret_dict[d] = replace_unset_values(default_dict[d], newkeys_dict[d])
    else:
      ret_dict[d] = newkeys_dict[d]
  return ret_dict

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

default = {
  "color": {
    "body": {
      "fill": "#191919",
      "stroke": "#6d6d6d",
    },
    "leads": {
      "fill": "#d6dcdb",
      "stroke": "#99abb0",
    }
  },
  "save_name": "Unknown"
}
custom_componet_properties = {
  "resistor": {
    "save_name": "R"
  },
  "fuse": {
    "save_name": "Fuse"
  },
  "capacitor": {
    "color": {
      "body": {
        "fill": "#e1dc9c",
        "stroke": "#6d6d6d",
      },
    },
    "save_name": "C"
  },
  "inductor": {
    "color": {
      "body": {
        "fill": "#916f6f",
        "stroke": "#483737",
      },
    },
    "save_name": "L"
  },
}

sizes = {
  # Specify in mm
  "0603": {
    "w_total": to_mm(0.06),
    "h_total": to_mm(0.03),
    "w_lead": to_mm(0.01),
    "stroke_width": 0.05,
  },
  "0805": {
    "w_total": to_mm(0.08),
    "h_total": to_mm(0.05),
    "w_lead": to_mm(0.015),
    "stroke_width": 0.05,
  },
  "1206": {
    "w_total": to_mm(0.12),
    "h_total": to_mm(0.06),
    "w_lead": to_mm(0.02),
    "stroke_width": 0.1,
  },
  "1210": {
    "w_total": to_mm(0.12),
    "h_total": to_mm(0.10),
    "w_lead": to_mm(0.02),
    "stroke_width": 0.1,
  }
}
  


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("passive", help="The passive type")
  parser.add_argument("--size", default=None, help="The size of the component to generate");
  
  args = parser.parse_args()  

  if args.passive not in custom_componet_properties.keys():
    print("Invalid component")
    sys.exit(1)
  componet_properties = replace_unset_values(default, custom_componet_properties[args.passive])
  
  if args.size is not None:
    if args.size not in sizes.keys():
      print("Invalid size. If you want a custom size, add it to this generator")
      sys.exit(1)
    args.size = [args.size]
  else:
    args.size = sizes.keys()
  
  for size in args.size:
    document = etree.parse("base/passives.svg")
    root = document.getroot()
    
    # Delete all inkscape grids
    p = root.find("{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}namedview")
    for c in p.findall("{http://www.inkscape.org/namespaces/inkscape}grid"):
      p.remove(c)
    
    # Remove the origin to add later. This is to place them above the pins
    origin = root.find(".//*[@id='origin']")
    root.remove(origin)
    
    body = root.find(".//*[@id='main_body']")
    leads = root.find(".//*[@id='leads']")
    # Set the body and lead colors
    c = componet_properties["color"]
    s = sizes[size]
    
    body.attrib["style"] = replace_keyvalue_value(body.attrib["style"], "fill", c["body"]["fill"])
    body.attrib["style"] = replace_keyvalue_value(body.attrib["style"], "stroke", c["body"]["stroke"])
    body.attrib["style"] = replace_keyvalue_value(body.attrib["style"], "stroke-width", s["stroke_width"])
    
    leads.attrib["style"] = replace_keyvalue_value(leads.attrib["style"], "fill", c["leads"]["fill"])
    leads.attrib["style"] = replace_keyvalue_value(leads.attrib["style"], "stroke", c["leads"]["stroke"])
    leads.attrib["style"] = replace_keyvalue_value(leads.attrib["style"], "stroke-width", s["stroke_width"])
    # Set the body and lead sizes
    # M 1,1.7 V -0.8 H 2 V 1.7 Z
    
    leads.attrib["d"] = "M {},{} v {} h {} v {} z m {},{} v {} h {} v {} z".format(-s["w_total"]/2, s["h_total"]/2, -s["h_total"], s["w_lead"], s["h_total"], s["w_total"], 0, -s["h_total"], -s["w_lead"], s["h_total"])
    body.attrib["d"] = "M {},{} v {} h {} v {} z".format(-s["w_total"]/2 + s["w_lead"], s["h_total"]/2, -s["h_total"], s["w_total"]-2*s["w_lead"], s["h_total"])
    
    root.append(origin)
    # Save
    sn = "export/{}_{}.svg".format(componet_properties["save_name"], size)
    if not os.path.isdir("export"):
      os.mkdir("export")
    document.write(sn)
    os.system(f"inkscape {sn} -D -o {sn} ;")
