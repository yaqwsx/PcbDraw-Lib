#!/usr/bin/env python3

from pcbdraw import pcbdraw
from pcbnewTransition import pcbnew
import click
import os
from pathlib import Path

from lxml import etree
from pcbdraw.pcbdraw import ki2mm, ki2svg, mm2ki

def loadFootprint(footprintPath):
    lib, foot = os.path.split(footprintPath)
    foot, _ = os.path.splitext(foot)
    return pcbnew.FootprintLoad(lib, foot)

def buildFootprintBoard(footprintPath):
    """
    Given a path to kicad_mod file, build a single board with the component on
    0,0 in the default orientation.
    """
    footprint = loadFootprint(footprintPath)

    board = pcbnew.BOARD()
    footprint.SetPosition(pcbnew.wxPoint(0, 0))
    footprint.Reference().SetVisible(False)
    footprint.Value().SetVisible(False)
    board.Add(footprint)
    return board

def buildFootprintBoardF(footprint):
    """
    Given a footprint file, build a single board with the component on
    0,0 in the default orientation.
    """
    # print(footprint)
    try:
        newFootprint = footprint.Duplicate()
    except TypeError: # Footprint has overridden the method, cannot be called directly
        print("Here")
        newFootprint = pcbnew.Cast_to_BOARD_ITEM(footprint).Duplicate()
    board = pcbnew.BOARD()
    if footprint.GetLayerName() == pcbnew.B_Cu:
        footprint.Flip(pcbnew.wxPoint(0, 0), True)
    footprint.SetPosition(pcbnew.wxPoint(0, 0))
    # footprint.Reference().SetVisible(False)
    # footprint.Value().SetVisible(False)
    board.Add(footprint)
    return board

def plotTopLayers(board):
    """
    Given a board, plot top layers for the template
    """
    process = pcbdraw.process_board_substrate_layer
    colors = {
        "copper": "#666666",
        "crt": "#000000",
        "fab": "#000000",
        "cmt": "#000000",
        "edge": "#000000",
        "silk": "#61caff"
    }
    plotPlan = [
            ("copper", [pcbnew.F_Cu], process),
            ("crt", [pcbnew.F_CrtYd], process),
            ("fab", [pcbnew.F_Fab], process),
            ("cmt", [pcbnew.Cmts_User], process),
            ("edge", [pcbnew.Edge_Cuts], process),
            ("silk", [pcbnew.F_SilkS], process)]
    elements = pcbdraw.get_layers(board, colors, {}, plotPlan)
    elements.attrib["id"] = "KiCAD footprint top"
    return elements

def plotBottomLayers(board):
    """
    Given a board, plot bottom layers for the template
    """
    process = pcbdraw.process_board_substrate_layer
    colors = {
        "copper": "#666666",
        "crt": "#000000",
        "fab": "#000000",
        "cmt": "#000000",
        "edge": "#000000",
        "silk": "#61caff"
    }
    plotPlan = [
            ("copper", [pcbnew.B_Cu], process),
            ("crt", [pcbnew.B_CrtYd], process),
            ("fab", [pcbnew.B_Fab], process),
            ("cmt", [pcbnew.Cmts_User], process),
            ("edge", [pcbnew.Edge_Cuts], process),
            ("silk", [pcbnew.B_SilkS], process)]
    elements = pcbdraw.get_layers(board, colors, {}, plotPlan)
    elements.attrib["id"] = "KiCAD footprint bottom"
    return elements

def addOrigin(document):
    """
    Add PcbDraw footprint origin to the module
    """
    origin = etree.Element("rect")
    origin.attrib["id"] = "origin"
    origin.attrib["fill"] = "red"
    origin.attrib["width"] = str(ki2svg(mm2ki(1)))
    origin.attrib["height"] = str(ki2svg(mm2ki(1)))
    origin.attrib["x"] = "0"
    origin.attrib["y"] = "0"

    document.getroot().append(origin)


@click.command("footprint")
@click.argument("footprint", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument("output", type=click.File(mode="wb"))
@click.option("--front", "front", flag_value=True,
    help="Render front size of the footprint")
@click.option("--back", "front", flag_value=False,
    help="Render back size of the footprint")
@click.option("--shrink", type=bool, default=False,
    help="Shrink template to size")
def run_footprint(footprint, output, front, shrink):
    """
    Create a template for footprint based on the KiCAD footprint file.
    """
    board = buildFootprintBoard(footprint)
    bb = board.ComputeBoundingBox()
    document = pcbdraw.empty_svg(
            width=f"{ki2mm(bb.GetWidth())}mm",
            height=f"{ki2mm(bb.GetHeight())}mm",
            viewBox=f"{ki2svg(bb.GetX())} {ki2svg(bb.GetY())} {ki2svg(bb.GetWidth())} {ki2svg(bb.GetHeight())}")
    if front:
        document.getroot().append(plotTopLayers(board))
    else:
        g = plotBottomLayers(board)
        g.attrib["transform"] = "scale(-1 1)"
        document.getroot().append(g)

    addOrigin(document)
    document.write(output)

    if shrink:
        path = output.name
        output.close()
        pcbdraw.shrink_svg(path, 0)

@click.command("board")
@click.argument("board", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument("output", type=click.Path(exists=False, file_okay=False, dir_okay=True))
@click.option("--shrink", type=bool, default=False,
    help="Shrink template to size")
def run_board(board, output, shrink):
    """
    Create a whole library of templates for footprints on given board
    """
    board = pcbnew.LoadBoard(board)
    outdir = Path(output)
    outdir.mkdir(parents=True, exist_ok=True)
    footprints = {
        (str(f.GetFPID().GetLibNickname()), str(f.GetFPID().GetLibItemName())): f
        for f in board.GetFootprints()}
    for (lib, name), f in footprints.items():
        print(f"Plotting: {lib}:{name}")
        fBoard = buildFootprintBoardF(f)
        bb = fBoard.ComputeBoundingBox()
        outFile = outdir / lib / (name + ".svg")
        document = pcbdraw.empty_svg(
            width=f"{ki2mm(bb.GetWidth())}mm",
            height=f"{ki2mm(bb.GetHeight())}mm",
            viewBox=f"{ki2svg(bb.GetX())} {ki2svg(bb.GetY())} {ki2svg(bb.GetWidth())} {ki2svg(bb.GetHeight())}")
        g = plotBottomLayers(fBoard)
        document.getroot().append(g)
        addOrigin(document)
        with open(outFile, "wb") as f:
            document.write(f)
        if shrink:
            path = output.name
            output.close()
            pcbdraw.shrink_svg(path, 0)

        outFile = outdir / lib / (name + ".back.svg")
        document = pcbdraw.empty_svg(
            width=f"{ki2mm(bb.GetWidth())}mm",
            height=f"{ki2mm(bb.GetHeight())}mm",
            viewBox=f"{ki2svg(bb.GetX())} {ki2svg(bb.GetY())} {ki2svg(bb.GetWidth())} {ki2svg(bb.GetHeight())}")
        g = plotBottomLayers(fBoard)
        g.attrib["transform"] = "scale(-1 1)"
        document.getroot().append(g)
        addOrigin(document)
        with open(outFile, "wb") as f:
            document.write(f)
        if shrink:
            path = output.name
            output.close()
            pcbdraw.shrink_svg(path, 0)


@click.group()
def cli():
    """
    Create footprint templates
    """
    pass

cli.add_command(run_footprint)
cli.add_command(run_board)

if __name__ ==  "__main__":
    cli()
