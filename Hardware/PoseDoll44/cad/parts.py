"""H1 fit coupons and serviceable single-axis clutch study; all dimensions mm."""
import cadquery as cq
import math
from fits import FITS, clearance
def box(x,y,z,at=(0,0,0)):
    return cq.Workplane("XY").box(x,y,z).translate(at).val()
def cyl(r,h,z=0,xy=(0,0)):
    return cq.Workplane("XY").circle(r).extrude(h).translate((xy[0],xy[1],z)).val()
def ring(ro,ri,h,z=0):return cyl(ro,h,z).cut(cyl(ri,h+2,z-1))
def drill(s,xy,d,z,h):return s.cut(cyl(d/2,h,z,xy))
def clipped_coupon(x,y,z,revision_clip=3):
    s=box(x,y,z,(0,0,z/2))
    s=s.cut(cq.Workplane("XY").polyline([(-x/2,-y/2),(-x/2+6,-y/2),(-x/2,-y/2+6)]).close().extrude(z+2).val())
    # A second, smaller clipped corner distinguishes Rev B from the old four-row coupon.
    return s.cut(cq.Workplane("XY").polyline([(x/2,y/2),(x/2-revision_clip,y/2),(x/2,y/2-revision_clip)]).close().extrude(z+2).val())
def fit_coupon():
    spec=FITS["coupon"]
    s=clipped_coupon(*spec["size_mm"],revision_clip=spec["top_right_revision_clip_mm"])
    for row in spec["rows_bottom_to_top"]:
        for col,d in enumerate(row["diameters_mm"]):
            s=drill(s,(-44+col*22,row["y_mm"]),d,-1,8)
    return s
def nut_coupon():
    s=clipped_coupon(86,40,8)
    nut=FITS["nut_M3"]; magnet=FITS["magnet"]
    for i,af in enumerate(nut["coupon_af_mm"]):
        p=cq.Workplane("XY").polygon(6,af/math.cos(math.pi/6)).extrude(nut["pocket_depth_mm"]).translate((-30+i*20,8,8-nut["pocket_depth_mm"])).val()
        s=s.cut(p);s=drill(s,(-30+i*20,8),clearance("M3"),-1,10)
    for i,d in enumerate(magnet["coupon_d_mm"]):
        s=s.cut(cyl(d/2,magnet["seat_depth_mm"],8-magnet["seat_depth_mm"],(-30+i*20,-10)))
    return s
def sensor_fixture():
    s=box(54,56,4,(0,0,2)).cut(box(14,20,10,(0,0,2)))
    for x in (-22,22):
        for y in (-21,21):
            s=s.cut(cq.Workplane("XY").slot2D(6,clearance("M3"),0).extrude(6).translate((x,y,-1)).val())
    # Mounting for our actual 32x32 Rev A board: 26 mm hole pitch. Chip faces down.
    for x in (-13,13):
        for y in (-13,13):s=drill(s,(x,y),clearance("M2"),-1,6)
    return s
def edge_clamp():
    s=box(15,8,4,(0,0,2)).cut(box(10,4,1.8,(-2.5,-2,0.9)))
    return drill(s,(4,0),clearance("M3"),-1,6)
def gap_gauge():
    s=box(58,8,3,(0,-12,1.5))
    for i,h in enumerate((1.0,1.5,2.0,2.5,3.0)):s=s.fuse(box(8,22,h,(-24+i*12,2,h/2)))
    return s
def base():
    s=box(112,66,6,(-16,0,-3))
    for x,y in ((-62,-24),(-62,24),(20,-24),(20,24)):s=drill(s,(x,y),clearance("M4"),-7,8)
    s=drill(s,(0,0),clearance("M6"),-7,8)
    a=math.degrees(math.asin(11/35))
    for ang in (-a,145+a):s=drill(s,(35*math.cos(math.radians(ang)),35*math.sin(math.radians(ang))),clearance("M3"),-7,8)
    for y in (-5,5):s=drill(s,(-49,y),clearance("M3",aligned_frame=True),-7,8)
    return s
def spine():
    s=box(12,20,76,(-49,0,38)).cut(box(14,16.4,5.4,(-49,0,33.5))).cut(box(14,16.4,5.4,(-49,0,73.5)))
    for y in (-5,5):s=drill(s,(-49,y),clearance("M3",aligned_frame=True),-1,78)
    return s
def upper_fork():
    s=cyl(21,5,31).fuse(box(55,16,5,(-27.5,0,33.5)))
    s=drill(s,(0,0),clearance("M6"),30,8)
    for a in (30,150,270):
        xy=(14*math.cos(math.radians(a)),14*math.sin(math.radians(a)))
        s=drill(s,xy,clearance("M3"),30,8)
        pocket=cq.Workplane("XY").polygon(6,FITS["nut_M3"]["pocket_af_mm"]/math.cos(math.pi/6)).extrude(FITS["nut_M3"]["pocket_depth_mm"]).translate((*xy,31)).val()
        s=s.cut(pocket)
    for y in (-5,5):s=drill(s,(-49,y),clearance("M3",aligned_frame=True),30,8)
    return s
def rotor():
    s=ring(16,FITS["bushing"]["housing_d_mm"]/2,19,6).fuse(box(91,12,6,(53.5,0,16)))
    s=drill(s,(95,0),clearance("M4"),12,9)
    for x in (27,35):s=drill(s,(x,0),clearance("M3"),12,9)
    return s
def magnet_bridge():
    s=box(16,12,5,(31,0,21.5)).fuse(box(8,12,35,(31,0,41.5)))
    s=s.fuse(box(35,12,5,(15.5,0,59.5))).fuse(cyl(9,5,57))
    s=s.cut(cyl(FITS["magnet"]["seat_d_mm"]/2,FITS["magnet"]["seat_depth_mm"],62-FITS["magnet"]["seat_depth_mm"]))
    for x in (27,35):s=drill(s,(x,0),clearance("M3"),18,8)
    for y in (-5,5):s=drill(s,(0,y),clearance("M2"),56,8)
    return s
def magnet_cover():
    s=cyl(8.5,.8,62)
    for y in (-5,5):s=drill(s,(0,y),clearance("M2"),61,4)
    return s
def sensor_arm():
    s=box(76,16,5,(-16,0,73.5))
    for y in (-5,5):s=drill(s,(-49,y),clearance("M3",aligned_frame=True),70,8)
    for x in (-22,22):
        s=s.fuse(box(10,50,5,(x,0,73.5)))
        for y in (-21,21):s=drill(s,(x,y),clearance("M3"),70,8)
    return s
def all_parts():
    return {
    "H1-001_fit_coupon":(fit_coupon(),"fit_test"),
    "H1-002_nut_magnet_coupon":(nut_coupon(),"fit_test"),
    "H1-003_gap_gauge":(gap_gauge(),"fit_test"),
    "H1-010_base":(base(),"draft_mechanism"),
    "H1-011_spine":(spine(),"draft_mechanism"),
    "H1-012_upper_fork":(upper_fork(),"draft_mechanism"),
    "H1-013_rotor_lever":(rotor(),"draft_mechanism"),
    "H1-014_magnet_bridge":(magnet_bridge(),"draft_mechanism"),
    "H1-015_magnet_cover":(magnet_cover(),"draft_mechanism"),
    "H1-016_sensor_arm":(sensor_arm(),"draft_mechanism"),
    "H1-017_sensor_carrier":(sensor_fixture().translate((0,0,66)),"draft_mechanism"),
    "H1-018_edge_clamp":(edge_clamp(),"draft_mechanism"),"H1-019_stop":(stop(),"draft_mechanism")
    }

def stop():
    return drill(cyl(5,20),(0,0),clearance("M3"),-1,22)
def hardware_reference():
    items=[]
    # Purchased/machined-to-drawing components, NOT printed parts.
    items.append(("M6_stationary_sleeve_OD8_ID6p4_L31",ring(4,3.2,31),(.72,.64,.25)))
    for z in (6,19):items.append(("POM_bushing_"+str(z),ring(5,4.025,6,z),(.88,.9,.86)))
    for z,h in ((0,3),(3,1.5),(26.5,1.5),(28,3)):items.append(("steel_thrust_"+str(z),ring(16,5.2,h,z),(.58,.6,.62)))
    for z in (4.5,25):items.append(("friction_fibre_"+str(z),ring(16,5.2,1.5,z),(.52,.31,.22)))
    a=math.degrees(math.asin(11/35))
    for j,ang in enumerate((-a,145+a)):
        pos=(35*math.cos(math.radians(ang)),35*math.sin(math.radians(ang)),0)
        items.append(("printed_stop_"+str(j),stop().translate(pos),(.7,.3,.18)))
    items.append(("magnet_6x2p5",cyl(3,2.5,59.4),(.7,.15,.18)))
    board=box(32,32,1.6,(0,0,65.2))
    for x in (-13,13):
        for y in (-13,13):board=drill(board,(x,y),2.2,63,5)
    items.append(("sensor_revA_PCB",board,(.08,.4,.25)))
    items.append(("AS5048A_package_envelope",box(5,6.4,1.2,(0,0,63.8)),(.12,.14,.17)))
    items.append(("M6x55_screw_envelope",cyl(3,55,-6).fuse(cyl(5,6,-12)),(.54,.55,.56)))
    items.append(("M6_nut_envelope",ring(5.7,3.1,5,36.8),(.54,.55,.56)))
    for y in (-5,5):
        items.append(("M3x90_frame_"+str(y),cyl(1.5,90,-6,(-49,y)),(.54,.55,.56)))
    for x in (-22,22):
        for y in (-21,21):items.append(("M3x14_carrier_"+str(x)+"_"+str(y),cyl(1.5,14,62.5,(x,y)),(.54,.55,.56)))
    # Connector sticks sideways from the board edge; exact housing envelope for review.
    items.append(("sensor_connector_envelope",box(10,5,4,(0,-12,62.4)),(.86,.88,.84)))
    return items
