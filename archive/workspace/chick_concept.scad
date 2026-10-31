// Chick robot: 100 mm appearance and packaging study, NOT a validated walker.
// Rounded soles and a single geared DC hip motor are the proposed starting point.
// Fastener patterns, bearing fits, motor SKU and gait remain to be engineered.
show_shell=true;
$fn=64;
yellow="#f5cd39"; orange="#ee8b25";
module rod(a,b,r=2){hull(){translate(a)sphere(r);translate(b)sphere(r);}}
module along_y(d,h){rotate([90,0,0])cylinder(d=d,h=h,center=true);}
module egg(p,s,wall=.8){translate(p)difference(){scale(s)sphere(1);scale(s-[wall,wall,wall])sphere(1);}}
module sole(){intersection(){translate([0,0,45])sphere(45);translate([0,0,4])cube([36,24,8],center=true);}}
for(side=[-1,1]){
 color(orange)translate([0,side*14,0])sole();
 // Toe details stay on the top of the sole, above the intended contact surface.
 for(y=[-6,0,6])color("#f4a331")rod([6,side*14+y,6],[17,side*14+y,6],1.5);
 color("#d6a345")rod([0,side*14,8],[0,side*14,50],2.5);
 color("#485d63")translate([0,side*14,48])cube([18,2,14],center=true);
 color("silver")translate([0,side*14,50])along_y(8,4);
}
// Single N20 motor envelope, held by the left hip plate and a small cradle.
color("#a4adb2")translate([0,-2,50])cube([12,25,10],center=true);
color("#c5b17d")translate([0,8,50])cube([12,8,10],center=true);
color("silver")translate([0,13,50])along_y(3,10);
color("#485d63")translate([0,-8,43])cube([16,12,3],center=true);
// Battery and controller are low, one on each side; both are bought-part envelopes.
color("#7894a5")translate([1,-14,17])cube([25,14,5],center=true);
for(x=[-9,11])color("#46545e")translate([x,-14,20])cube([2,16,1],center=true);
color("#33765d")translate([0,14,16])cube([18,12,2],center=true);
color("#222d34")translate([0,14,18])cube([7,7,2],center=true);
if(show_shell){
 color(yellow)egg([2,0,55],[19,19,20]);
 color(yellow)egg([6,0,76],[23,20,23]);
 for(side=[-1,1]){
  color("#ffe785")translate([-2,side*19,56])scale([11,2,15])sphere(1);
  color("#171d22")translate([20,side*12,83])sphere(3.4);
  color("white")translate([22,side*12,84])sphere(.9);
 }
 color(orange)hull(){translate([27,0,75])scale([1,7,4])sphere(1);translate([36,0,73])sphere(.7);}
 color("#ffe785")rod([2,0,96],[5,0,99],1);
}
