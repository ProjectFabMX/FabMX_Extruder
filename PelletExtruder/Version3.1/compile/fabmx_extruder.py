import cadscript as cad
import helper

# use log or print, depending if use inside CQ-editor or standalone
try:
    echo = log
except NameError:
    echo = print

# z is up

# origin at
# xy: center of screw
# z: upper edge of barrel

inner_dim_xy = 58  # size of cage (inside)
inner_dim_z = 146  # from origin to upper edge of cage

front_w = 70                # with of front plate
front_z1 = -8               # lower edge of front plate
front_z2 = front_z1 + 164   # upper edge of front plate
side_w = inner_dim_xy       # width of side plate
side_z1 = front_z1          # lower edge of side plate
side_z2 = side_z1 + 155     # upper edge of front plate

hole_dia = 5.2              # diameter of mounting holes
hole_dia_inlet = 7          # diameter of mounting holes in inlet
hole_dist_x = 52            # horizontal distance of mounting holes
hole_dist_y = 67            # vertical distance of mounting holes
hole_pos = 14               # z position of lower mounting holes

hole_insert_dist = 5        # distance of holes for inlet mounting from housing

plate_thickness = 3

teeth_length_hor = 8        # length of teeth
teeth_dist_hor = 10         # space between teeth
tooth_count_hor = 3         # number of teeth horizontal

teeth_length_vert = 9       # length of teeth
teeth_dist_vert = 14        # space between teeth
teeth_start_vert = -2       # z position where first tooth starts
tooth_count_vert = 8        # number of teeth vertical
tooth_plate3_length = 30    # length of single tooth in plate 3

teeth_gap = 0.1             # extra space for teeth cutouts

tooth_coutout_type = "CornerCircles"  # how the cutouts should look like: "Simple" or "CornerCircles"
CornerCircleDia = 1.1       # diameter of corner circles

addLogo = True              # cut out FabMX logo in front plate?

long_screws_dist = 32       # central screws are arranged in square, this is the side length
long_screws_hole_dia = 5.2  # hole for M5 screws

plate1_centerhole_dia = 14  # hole for inlet
plate2_centerhole_dia = 34.2  # hole for gear box shaft
plate3_centerhole_dia = 56.6  # hole for gear box

plate_pos_1 = 0             # z position of plate 1
plate_pos_2 = 86            # z position of plate 2
plate_pos_3 = 137           # z position of plate 2

window_w = 42               # width of cutout in front and right plate
window_bottom = 28          # z pos of lower edge of cutout
window_top = 76             # z pos of upper edge of cutout

window_inlet_w = 42         # width of cutout in side plate for inlet
window_inlet_bottom = 23    # z pos of lower edge of cutout
window_inlet_top = 78       # z pos of upper edge of cutout

u_cutout_w = 40             # width of u shaped cutout at the bottom of side plate
u_cutout_h = 5.5            # height of u shaped cutout at the bottom of side plate


# calculated values

hole_positions = cad.pattern_rect(hole_dist_x, (hole_pos, hole_pos + hole_dist_y))

vertical_teeth = helper.pattern_teeth(tooth_count_vert, teeth_length_vert, teeth_dist_vert, startPos=teeth_start_vert)
horizontal_teeth_std = helper.pattern_teeth(tooth_count_hor, teeth_length_hor, teeth_dist_hor, center=True)
horizontal_teeth_3 = helper.pattern_teeth(1, tooth_plate3_length, 0, center=True)

teeth_horizontal_pos1 = (-inner_dim_xy / 2 - plate_thickness, -inner_dim_xy / 2)
teeth_horizontal_pos2 = (inner_dim_xy / 2, inner_dim_xy / 2 + plate_thickness)



# helper methods

def teethCutoutVertical(sketch: cad.Sketch, posList, posVertical, type="hole"):
    insideCorners = None
    if type == "hole":
        addGap = False
        cutInverse = False
    elif type == "openLeft":
        addGap = True
        cutInverse = True
        insideCorners = ["RB", "RT"]
    elif type == "openRight":
        addGap = True
        cutInverse = True
        insideCorners = ["LB", "LT"]

    positions = helper.invert_tooth_list(posList) if cutInverse else posList
    for pos in positions:
        toothCutout(sketch, posVertical, pos, addGap, insideCorners)


def teethCutoutHorizontal(sketch: cad.Sketch, posList, posHorizontal, type="hole"):
    insideCorners = None
    if type == "hole":
        addGap = False
        cutInverse = False
    elif type == "openTop":
        addGap = True
        cutInverse = True
        insideCorners = ["LB", "RB"]
    elif type == "openBottom":
        addGap = True
        cutInverse = True
        insideCorners = ["LT", "RT"]

    positions = helper.invert_tooth_list(posList) if cutInverse else posList
    for pos in positions:
        toothCutout(sketch, pos, posHorizontal, addGap, insideCorners)


def toothCutout(sketch: cad.Sketch, dimx, dimy, addGap, insideCorners):
    if not insideCorners:
        insideCorners = ["LB", "RB", "LT", "RT"]
    if addGap:
        dimx = (dimx[0] - teeth_gap, dimx[1] + teeth_gap)
        dimy = (dimy[0] - teeth_gap, dimy[1] + teeth_gap)
    sketch.cut_rect(dimx, dimy)
    if tooth_coutout_type == "CornerCircles":
        if "LB" in insideCorners:
            sketch.cut_circle(d=CornerCircleDia, pos=(dimx[0], dimy[0]))
        if "RB" in insideCorners:
            sketch.cut_circle(d=CornerCircleDia, pos=(dimx[1], dimy[0]))
        if "LT" in insideCorners:
            sketch.cut_circle(d=CornerCircleDia, pos=(dimx[0], dimy[1]))
        if "RT" in insideCorners:
            sketch.cut_circle(d=CornerCircleDia, pos=(dimx[1], dimy[1]))
    return sketch


# sketches

def sketchForPlateFrontBack(isFront):
    sketch = cad.make_sketch()
    sketch.add_rect(front_w, (front_z1, front_z2))
    sketch.fillet("ALL", 4)

    # mounting holes
    sketch.cut_circle(r=hole_dia / 2, positions=hole_positions)

    # cutouts
    teethCutoutVertical(sketch, vertical_teeth, teeth_horizontal_pos1)
    teethCutoutVertical(sketch, vertical_teeth, teeth_horizontal_pos2)

    # teeth
    teethCutoutHorizontal(sketch, horizontal_teeth_std, (plate_pos_1, plate_pos_1 + plate_thickness))
    teethCutoutHorizontal(sketch, horizontal_teeth_std, (plate_pos_2, plate_pos_2 + plate_thickness))
    teethCutoutHorizontal(sketch, horizontal_teeth_3, (plate_pos_3, plate_pos_3 + plate_thickness))

    # window and logo at front
    if isFront:
        sketch.cut_rect(window_w, (window_bottom, window_top))
        if addLogo:
            sketch.cut_import_dxf("source/fabmax_logo.dxf", pos=(0, 96))

    return sketch


def sketchForPlateSide(isLeft):
    sketch = cad.make_sketch()
    sketch.add_rect(side_w + plate_thickness * 2, (side_z1, side_z2))

    # cutouts
    widthWitoutRoundinng = u_cutout_w - 2 * u_cutout_h
    sketch.cut_slot(width=widthWitoutRoundinng, height=u_cutout_h * 2, pos=(0, front_z1))

    # teeth vertical
    teethCutoutVertical(sketch, vertical_teeth, teeth_horizontal_pos1, type="openLeft")
    teethCutoutVertical(sketch, vertical_teeth, teeth_horizontal_pos2, type="openRight")

    # teeth horizontal
    teethCutoutHorizontal(sketch, horizontal_teeth_std, (plate_pos_1, plate_pos_1 + plate_thickness))
    teethCutoutHorizontal(sketch, horizontal_teeth_std, (plate_pos_2, plate_pos_2 + plate_thickness))
    teethCutoutHorizontal(sketch, horizontal_teeth_3, (plate_pos_3, plate_pos_3 + plate_thickness))

    if isLeft:
        # inlet side
        sketch.cut_rect(window_inlet_w, (window_inlet_bottom, window_inlet_top))
    else:
        # window
        sketch.cut_rect(window_w, (window_bottom, window_top))

    return sketch


# horizonatal plate, lowest

def sketchForPlate1():
    sketch = cad.make_sketch()
    sketch.add_rect(inner_dim_xy + plate_thickness * 2, inner_dim_xy + plate_thickness * 2)

    # holes for inlet, mouting holes
    sketch.cut_circle(d=plate1_centerhole_dia)
    sketch.cut_circle(d=long_screws_hole_dia, positions=cad.pattern_rect(long_screws_dist, long_screws_dist))
    sketch.cut_circle(d=helper.M3.diaHole, positions=cad.pattern_rect(
        inner_dim_xy - 2 * hole_insert_dist, inner_dim_xy - 2 * hole_insert_dist))

    # slit for cables at back
    # sketch.cutRect(8, u_cutout_h*2, pos=(0,inner_dim_xy/2))

    # teeth
    teethCutoutHorizontal(sketch, horizontal_teeth_std, teeth_horizontal_pos1, type="openBottom")
    teethCutoutHorizontal(sketch, horizontal_teeth_std, teeth_horizontal_pos2, type="openTop")
    teethCutoutVertical(sketch, horizontal_teeth_std, teeth_horizontal_pos1, type="openLeft")
    teethCutoutVertical(sketch, horizontal_teeth_std, teeth_horizontal_pos2, type="openRight")

    return sketch


# horizonatal plate, mid

def sketchForPlate2():
    sketch = cad.make_sketch()
    sketch.add_rect(inner_dim_xy + plate_thickness * 2, inner_dim_xy + plate_thickness * 2)

    # holes for shaft, mouting holes
    sketch.cut_circle(d=plate2_centerhole_dia)
    sketch.cut_circle(d=long_screws_hole_dia, positions=cad.pattern_rect(long_screws_dist, long_screws_dist))

    # teeth
    teethCutoutHorizontal(sketch, horizontal_teeth_std, teeth_horizontal_pos1, type="openBottom")
    teethCutoutHorizontal(sketch, horizontal_teeth_std, teeth_horizontal_pos2, type="openTop")
    teethCutoutVertical(sketch, horizontal_teeth_std, teeth_horizontal_pos1, type="openLeft")
    teethCutoutVertical(sketch, horizontal_teeth_std, teeth_horizontal_pos2, type="openRight")

    return sketch

# horizonatal plate, top


def sketchForPlate3():
    sketch = cad.make_sketch()
    sketch.add_rect(inner_dim_xy + plate_thickness * 2, inner_dim_xy + plate_thickness * 2)

    # holes mouting holes
    sketch.cut_circle(d=plate3_centerhole_dia)

    # teeth
    teethCutoutHorizontal(sketch, horizontal_teeth_3, teeth_horizontal_pos1, type="openBottom")
    teethCutoutHorizontal(sketch, horizontal_teeth_3, teeth_horizontal_pos2, type="openTop")
    teethCutoutVertical(sketch, horizontal_teeth_3, teeth_horizontal_pos1, type="openLeft")
    teethCutoutVertical(sketch, horizontal_teeth_3, teeth_horizontal_pos2, type="openRight")

    return sketch


def createInlet():
    # load step, move to correct position
    inlet = cad.import_step("source/PelletInlet v13.step")
    inlet.move((0, 0, plate_thickness))

    # add holes for long screws
    sketch = cad.make_sketch()
    sketch.add_circle(d=long_screws_hole_dia, positions=cad.pattern_rect(long_screws_dist, long_screws_dist))
    inlet.cut_extrude("<Z", sketch, -9999)

    # add holes for mounting screws
    sketch = cad.make_sketch()
    sketch.add_circle(d=hole_dia_inlet, positions=[(-hole_dist_x / 2, hole_pos), (hole_dist_x / 2, hole_pos)])
    inlet.cut_extrude("<Y", sketch, -9999)

    # add holes for M3 inserts
    sketch = cad.make_sketch()
    sketch.add_circle(d=helper.M3.diaThreadInsert,
                      positions=cad.pattern_rect(inner_dim_xy - 2 * hole_insert_dist, inner_dim_xy - 2 * hole_insert_dist))
    inlet.cut_extrude("<Z", sketch, -7)

    return inlet


def createFunnel():
    barrel = cad.import_step("source/Funnel v13.step")
    return barrel


def createBarrel():
    barrel = cad.import_step("source/Barrel v2.step")
    return barrel


# generate the components

innerBox = cad.make_box(inner_dim_xy, inner_dim_xy, (0, front_z2))

sketchFront = sketchForPlateFrontBack(isFront=True)
plateFront = innerBox.make_extrude("<Y", sketchFront, plate_thickness)
sketchBack = sketchForPlateFrontBack(isFront=False)
plateBack = innerBox.make_extrude(">Y", sketchBack, plate_thickness)
sketchLeft = sketchForPlateSide(isLeft=True)
plateLeft = innerBox.make_extrude("<X", sketchLeft, plate_thickness)
sketchRight = sketchForPlateSide(isLeft=False)
plateRight = innerBox.make_extrude(">X", sketchRight, plate_thickness)

sketch1 = sketchForPlate1()
plate1 = cad.make_extrude_z(sketch1, (plate_pos_1, plate_pos_1 + plate_thickness))

sketch2 = sketchForPlate2()
plate2 = cad.make_extrude_z(sketch2, (plate_pos_2, plate_pos_2 + plate_thickness))

sketch3 = sketchForPlate3()
plate3 = cad.make_extrude_z(sketch3, (plate_pos_3, plate_pos_3 + plate_thickness))

inlet = createInlet()
funnel = createFunnel()
barrel = createBarrel()

echo("Exporting STEPs and STLs")

inlet.export_stl("output/inlet.stl")
inlet.export_step("output/inlet.step")

funnel.export_stl("output/funnel.stl")
funnel.export_step("output/funnel.step")

barrel.export_stl("output/barrel.stl")
barrel.export_step("output/barrel.step")

echo("Exporting DXFs")

sketchFront.export_dxf("output/laser_front.dxf")
sketchBack.export_dxf("output/laser_back.dxf")
sketchLeft.export_dxf("output/laser_left.dxf")
sketchRight.export_dxf("output/laser_right.dxf")
sketch1.export_dxf("output/laser_plate1.dxf")
sketch2.export_dxf("output/laser_plate2.dxf")
sketch3.export_dxf("output/laser_plate3.dxf")



assy = cad.Assembly()
assy.add(plateFront)
assy.add(plateBack)
assy.add(plateLeft)
assy.add(plateRight)
assy.add(plate1)
assy.add(plate2)
assy.add(plate3)
assy.add(inlet)
# assy.add(funnel)
assy.add(barrel)

assy.cq().save("output/assembly.step", "STEP")

a = (
    assy.cq().toCompound()
    .rotate((0, 0, 0), (1, 0, 0), -90)  # z should be up
    .rotate((0, 0, 0), (0, 1, 0), 20)  # rotate a bit around up axis for better view
)
helper.export_svg(a, "output/render_3d.svg", width=600, height=800, strokeWidth=0.6)
a = (
    assy.cq().toCompound()
    .rotate((0, 0, 0), (1, 0, 0), -90)  # z should be up
)
helper.export_svg(a, "output/render_front.svg", width=600, height=800, strokeWidth=0.4, projectionDir=(0, 0, 1))


# for display in CQ-editor
resultFront = plateFront.cq()
resultBack = plateBack.cq()
resultLeft = plateLeft.cq()
resultRight = plateRight.cq()
plate1 = plate1.cq()
plate2 = plate2.cq()
plate3 = plate3.cq()
inlet = inlet.cq()
# funnel = funnel.cq()
barrel = barrel.cq()


echo("done")
