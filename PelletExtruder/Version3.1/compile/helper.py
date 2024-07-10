from itertools import chain
import cadquery as cq



def pattern_teeth(toothCount, toothLength, toothGap, startPos=None, center=None):
    if startPos and center:
        raise ValueError("cannot set both startPos and center")
    if center:
        startPos = 0
    toothList = []
    last_pos = 0
    for i in range(toothCount):
        pos = startPos + (toothGap + toothLength) * i
        toothList.append((pos, pos + toothLength))
        last_pos = pos + toothLength
    if center:
        offset = -last_pos / 2

        def addoffset(x):
            x1, x2 = x
            return (x1 + offset, x2 + offset)
        toothList = list(map(addoffset, toothList))
    return toothList


def invert_tooth_list(posList):
    newList = list(chain([-999999], *posList, [999999]))  # flatten, add new limits
    return zip(newList[0::2], newList[1::2])  # turn into tuples again


def export_svg(part, filename, width=300, height=300, strokeWidth=0.6, projectionDir=(1, 1, 1)):
    cq.exporters.export(part,
                        filename,
                        opt={
                            "width": width,
                            "height": height,
                            "marginLeft": 5,
                            "marginTop": 5,
                            "showAxes": False,
                            "projectionDir": projectionDir,
                            "strokeWidth": strokeWidth,
                            "strokeColor": (0, 0, 0),
                            "hiddenColor": (0, 0, 255),
                            "showHidden": False,
                        },)




class M3Helper:

    dia = 3
    diaHole = 3.2
    diaCoreHole = 2.5
    diaThreadInsert = 3.9

    r = dia / 2
    rHole = diaHole / 2
    rCoreHole = diaCoreHole / 2
    rThreadInsert = diaThreadInsert / 2


M3 = M3Helper()
