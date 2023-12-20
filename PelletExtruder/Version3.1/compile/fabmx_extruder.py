import cadscript as cad
import importlib 
importlib.reload(cad) 
from itertools import product, chain
from cadquery import exporters

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
plate2_centerhole_dia = 34.2 # hole for gear box shaft
plate3_centerhole_dia = 56.6 # hole for gear box

plate_pos_1 = 0             # z position of plate 1
plate_pos_2 = 86            # z position of plate 2
plate_pos_3 = 137           # z position of plate 2

window_w = 42               # width of cutout in front and right plate
window_bottom = 28          # z pos of lower edge of cutout
window_top = 76             # z pos of upper edge of cutout

window_inlet_w = 42         # width of cutout in side plate for inlet
window_inlet_bottom = 23    # z pos of lower edge of cutout
window_inlet_top = 78       # z pos of upper edge of cutout

u_cutout_w  = 40            # width of u shaped cutout at the bottom of side plate 
u_cutout_h  = 5.5           # height of u shaped cutout at the bottom of side plate 


### calculated values

hole_positions = cad.PatternRect(hole_dist_x, (hole_pos, hole_pos+hole_dist_y))

vertical_teeth = cad.PatternTeeth(tooth_count_vert, teeth_length_vert, teeth_dist_vert, startPos=teeth_start_vert)
horizontal_teeth_std = cad.PatternTeeth(tooth_count_hor, teeth_length_hor, teeth_dist_hor, center=True)
horizontal_teeth_3 = cad.PatternTeeth(1, tooth_plate3_length, 0, center=True)

teeth_horizontal_pos1 = (-inner_dim_xy/2-plate_thickness,-inner_dim_xy/2)
teeth_horizontal_pos2 = (inner_dim_xy/2, inner_dim_xy/2+plate_thickness)




### helper methods

def invertToothList(posList):
    newList = list(chain([-999999], *posList, [999999])) # flatten, add new limits
    return zip(newList[0::2], newList[1::2]) # turn into tuples again

def teethCutoutVertical(sketch, posList, posVertical, type="hole"):
  insideCorners = None
  if type=="hole":
      addGap = False
      cutInverse = False
  elif type=="openLeft":
      addGap = True
      cutInverse = True
      insideCorners = ["RB", "RT"]
  elif type=="openRight":
      addGap = True
      cutInverse = True
      insideCorners = ["LB", "LT"]
  
  positions = invertToothList(posList) if cutInverse else posList
  for pos in positions:
    toothCutout(sketch, posVertical, pos, addGap, insideCorners)

def teethCutoutHorizontal(sketch, posList, posHorizontal, type="hole"):
  insideCorners = None
  if type=="hole":
      addGap = False
      cutInverse = False
  elif type=="openTop":
      addGap = True
      cutInverse = True
      insideCorners = ["LB", "RB"]
  elif type=="openBottom":
      addGap = True
      cutInverse = True
      insideCorners = ["LT", "RT"]

  positions = invertToothList(posList) if cutInverse else posList
  for pos in positions:
    toothCutout(sketch, pos, posHorizontal, addGap, insideCorners)

def toothCutout(sketch, dimx, dimy, addGap, insideCorners):
  if not insideCorners:
    insideCorners = ["LB","RB","LT","RT"]
  if addGap:
    dimx = (dimx[0]-teeth_gap, dimx[1]+teeth_gap)
    dimy = (dimy[0]-teeth_gap, dimy[1]+teeth_gap)
  sketch.cutRect(dimx, dimy)
  if tooth_coutout_type == "CornerCircles":
    if "LB" in insideCorners:
      sketch.cutCircle(r=CornerCircleDia/2, positions=[(dimx[0],dimy[0])])
    if "RB" in insideCorners:
      sketch.cutCircle(r=CornerCircleDia/2, positions=[(dimx[1],dimy[0])])
    if "LT" in insideCorners:
      sketch.cutCircle(r=CornerCircleDia/2, positions=[(dimx[0],dimy[1])])
    if "RT" in insideCorners:
      sketch.cutCircle(r=CornerCircleDia/2, positions=[(dimx[1],dimy[1])])
  return sketch
  

def sketchForPlateFrontBack(isFront):
  sketch = cad.makeSketch()
  sketch.addRect(front_w, (front_z1, front_z2))
  sketch.fillet("ALL", 4)

  # mounting holes
  sketch.cutCircle(r=hole_dia/2, positions=hole_positions)

  # cutouts
  teethCutoutVertical(sketch, vertical_teeth, teeth_horizontal_pos1)
  teethCutoutVertical(sketch, vertical_teeth, teeth_horizontal_pos2)

  # teeth
  teethCutoutHorizontal(sketch, horizontal_teeth_std, (plate_pos_1, plate_pos_1+plate_thickness))
  teethCutoutHorizontal(sketch, horizontal_teeth_std, (plate_pos_2, plate_pos_2+plate_thickness))
  teethCutoutHorizontal(sketch, horizontal_teeth_3, (plate_pos_3, plate_pos_3+plate_thickness))
  
  # window and logo at front
  if isFront:
    sketch.cutRect(window_w, (window_bottom, window_top))
    if addLogo:
        sketch.cutImportDxf("source/fabmax_logo.dxf",[(0,-70)])

  sketch.finalize()
  return sketch



def sketchForPlateSide(isLeft):
  sketch = cad.makeSketch()
  sketch.addRect(side_w+plate_thickness*2, (side_z1, side_z2))

  # cutouts
  widthWitoutRoundinng = u_cutout_w-2*u_cutout_h
  sketch.cutSlot(widthWitoutRoundinng, u_cutout_h*2, positions=[(0,front_z1)])

  # teeth vertical
  teethCutoutVertical(sketch, vertical_teeth, teeth_horizontal_pos1, type="openLeft")
  teethCutoutVertical(sketch, vertical_teeth, teeth_horizontal_pos2, type="openRight")

  # teeth horizontal
  teethCutoutHorizontal(sketch, horizontal_teeth_std, (plate_pos_1, plate_pos_1+plate_thickness))
  teethCutoutHorizontal(sketch, horizontal_teeth_std, (plate_pos_2, plate_pos_2+plate_thickness))
  teethCutoutHorizontal(sketch, horizontal_teeth_3, (plate_pos_3, plate_pos_3+plate_thickness))

  if isLeft:
    # inlet side
    sketch.cutRect(window_inlet_w, (window_inlet_bottom, window_inlet_top))
  else:
    # window
    sketch.cutRect(window_w, (window_bottom, window_top))

  sketch.finalize()
  return sketch

# horizonatal plate, lowest
def sketchForPlate1():
  sketch = cad.makeSketch()
  sketch.addRect(inner_dim_xy+plate_thickness*2, inner_dim_xy+plate_thickness*2)

  # holes for inlet, mouting holes
  sketch.cutCircle(plate1_centerhole_dia/2)
  sketch.cutCircle(long_screws_hole_dia/2, cad.PatternRect(long_screws_dist, long_screws_dist))
  sketch.cutCircle(cad.M3.rHole, cad.PatternRect(inner_dim_xy-2*hole_insert_dist, inner_dim_xy-2*hole_insert_dist))

  # slit for cables at back
  #sketch.cutRect(8, u_cutout_h*2, positions=[(0,inner_dim_xy/2)])

  # teeth
  teethCutoutHorizontal(sketch, horizontal_teeth_std, teeth_horizontal_pos1, type="openBottom")
  teethCutoutHorizontal(sketch, horizontal_teeth_std, teeth_horizontal_pos2, type="openTop")
  teethCutoutVertical(sketch, horizontal_teeth_std, teeth_horizontal_pos1, type="openLeft")
  teethCutoutVertical(sketch, horizontal_teeth_std, teeth_horizontal_pos2, type="openRight")

  sketch.finalize()
  return sketch

# horizonatal plate, mid
def sketchForPlate2():
  sketch = cad.makeSketch()
  sketch.addRect(inner_dim_xy+plate_thickness*2, inner_dim_xy+plate_thickness*2)

  # holes for shaft, mouting holes
  sketch.cutCircle(plate2_centerhole_dia/2)
  sketch.cutCircle(long_screws_hole_dia/2, cad.PatternRect(long_screws_dist, long_screws_dist))
  
  # teeth
  teethCutoutHorizontal(sketch, horizontal_teeth_std, teeth_horizontal_pos1, type="openBottom")
  teethCutoutHorizontal(sketch, horizontal_teeth_std, teeth_horizontal_pos2, type="openTop")
  teethCutoutVertical(sketch, horizontal_teeth_std, teeth_horizontal_pos1, type="openLeft")
  teethCutoutVertical(sketch, horizontal_teeth_std, teeth_horizontal_pos2, type="openRight")

  sketch.finalize()
  return sketch

# horizonatal plate, top
def sketchForPlate3():
  sketch = cad.makeSketch()
  sketch.addRect(inner_dim_xy+plate_thickness*2, inner_dim_xy+plate_thickness*2)

  # holes mouting holes
  sketch.cutCircle(plate3_centerhole_dia/2)
  
  # teeth
  teethCutoutHorizontal(sketch, horizontal_teeth_3, teeth_horizontal_pos1, type="openBottom")
  teethCutoutHorizontal(sketch, horizontal_teeth_3, teeth_horizontal_pos2, type="openTop")
  teethCutoutVertical(sketch, horizontal_teeth_3, teeth_horizontal_pos1, type="openLeft")
  teethCutoutVertical(sketch, horizontal_teeth_3, teeth_horizontal_pos2, type="openRight")

  sketch.finalize()
  return sketch


def inlet():
  #load step, move to correct position
  inlet = cad.importStep("source/PelletInlet v13.step")
  inlet.move((0,0,plate_thickness))
  
  # add holes for long screws
  sketch = cad.makeSketch()
  sketch.addCircle(long_screws_hole_dia/2, cad.PatternRect(long_screws_dist, long_screws_dist))
  sketch.finalize()
  inlet.cutExtrude("<Z", sketch, -9999)

  # add holes for mounting screws
  sketch = cad.makeSketch()
  sketch.addCircle(hole_dia_inlet/2, positions=[(-hole_dist_x/2, hole_pos), (hole_dist_x/2, hole_pos)])
  sketch.finalize()
  inlet.cutExtrude("<Y", sketch, -9999)

  # add holes for M3 inserts
  sketch = cad.makeSketch()
  sketch.addCircle(cad.M3.rThreadInsert, cad.PatternRect(inner_dim_xy-2*hole_insert_dist, inner_dim_xy-2*hole_insert_dist))
  sketch.finalize()
  inlet.cutExtrude("<Z", sketch, -7) 

  return inlet

def funnel():
  barrel = cad.importStep("source/Funnel v13.step")
  return barrel

def barrel():
  barrel = cad.importStep("source/Barrel v2.step")
  return barrel


### generate the components

innerBox = cad.makeBox(inner_dim_xy, inner_dim_xy, (0,front_z2))

sketchFront = sketchForPlateFrontBack(isFront=True)
plateFront = innerBox.makeExtrude("<Y", sketchFront, plate_thickness)
sketchBack = sketchForPlateFrontBack(isFront=False)
plateBack = innerBox.makeExtrude(">Y",sketchBack , plate_thickness)
sketchLeft = sketchForPlateSide(isLeft=True)
plateLeft = innerBox.makeExtrude("<X", sketchLeft, plate_thickness)
sketchRight = sketchForPlateSide(isLeft=False)
plateRight = innerBox.makeExtrude(">X", sketchRight, plate_thickness)

plane1 = cad.makeWorkplane("XY", offset=plate_pos_1)
sketch1 = sketchForPlate1()
plate1 = cad.makeExtrude(sketch1, plate_thickness, workplane=plane1)

plane2 = cad.makeWorkplane("XY", offset=plate_pos_2)
sketch2 = sketchForPlate2()
plate2 = cad.makeExtrude(sketch2, plate_thickness, workplane=plane2)

plane3 = cad.makeWorkplane("XY", offset=plate_pos_3)
sketch3 = sketchForPlate3()
plate3 = cad.makeExtrude(sketch3, plate_thickness, workplane=plane3)

inlet = inlet()
funnel = funnel()
barrel = barrel()

echo("Exporting STEPs and STLs")

inlet.exportStl("output/inlet.stl")
inlet.exportStep("output/inlet.step")

funnel.exportStl("output/funnel.stl")
funnel.exportStep("output/funnel.step")

barrel.exportStl("output/barrel.stl")
barrel.exportStep("output/barrel.step")

echo("Exporting DXFs")

sketchFront.exportDxf("output/laser_front.dxf")
sketchBack.exportDxf("output/laser_back.dxf")
sketchLeft.exportDxf("output/laser_left.dxf")
sketchRight.exportDxf("output/laser_right.dxf")
sketch1.exportDxf("output/laser_plate1.dxf")
sketch2.exportDxf("output/laser_plate2.dxf")
sketch3.exportDxf("output/laser_plate3.dxf")



assy = cad.Assembly()
assy.add(plateFront)
assy.add(plateBack)
assy.add(plateLeft)
assy.add(plateRight)
assy.add(plate1)
assy.add(plate2)
assy.add(plate3)
assy.add(inlet)
#assy.add(funnel)
assy.add(barrel)

assy.cq().save("output/assembly.step","STEP")

a = (
    assy.cq().toCompound()
    .rotate((0,0,0), (1,0,0), -90) # z should be up
    .rotate((0,0,0), (0,1,0), 20) # rotate a bit around up axis for better view
  )
cad.export_svg(a, "output/render_3d.svg", width=600, height=800, strokeWidth=0.6)
a = (
    assy.cq().toCompound()
    .rotate((0,0,0), (1,0,0), -90) # z should be up
  )
cad.export_svg(a, "output/render_front.svg", width=600, height=800, strokeWidth=0.4, projectionDir=(0,0,1))

echo(cad.debugtxt)

resultFront = plateFront.cq()
resultBack = plateBack.cq()
resultLeft = plateLeft.cq()
resultRight = plateRight.cq()
plate1 = plate1.cq()
plate2 = plate2.cq()
plate3 = plate3.cq()
inlet = inlet.cq()
#funnel = funnel.cq()
barrel = barrel.cq()


echo("done")
