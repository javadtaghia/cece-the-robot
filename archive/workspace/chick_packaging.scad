// Generated compact two-AA packaging study, mm. Not print-ready.
$fn=48;
module shell_box(){difference(){translate([0,0,67])cube([64,48,64],center=true);translate([0,0,67])cube([60,44,60],center=true);}}
color([1,.78,.15,.2])shell_box();
color([1,.83,.25,.2])translate([6,0,119])difference(){scale([25,22,23])sphere(1);scale([23,20,21])sphere(1);}
color([1,.4,.05])translate([33,0,111])scale([12,7,4])sphere(1);
// AA_holder: estimated 5 g
color([0.2,0.23,0.26,0.22])translate([-16,0,65.5])cube([18,34,55],center=true);
// AA_left: estimated 24 g
color([0.65,0.7,0.75,1])translate([-16,-8,65.5])cube([14.5,14.5,50.5],center=true);
// AA_right: estimated 24 g
color([0.65,0.7,0.75,1])translate([-16,8,65.5])cube([14.5,14.5,50.5],center=true);
// SuperMini: estimated 4 g
color([0.1,0.6,0.3,1])translate([17,-3,78])cube([23,18,8],center=true);
// motor_driver_reserve: estimated 2 g
color([0.1,0.6,0.3,1])translate([17,-13,53])cube([20,14,6],center=true);
// regulator_reserve: estimated 3 g
color([0.2,0.4,0.8,1])translate([17,9,53])cube([20,16,8],center=true);
// audio_amp_reserve: estimated 2 g
color([0.1,0.6,0.3,1])translate([17,4,65])cube([20,18,6],center=true);
// speaker: estimated 6 g
color([0.15,0.17,0.2,1])translate([6,4,118])cube([30,5,20],center=true);
// mic_board_reserve: estimated 1 g
color([0.1,0.6,0.3,1])translate([14,-6,122])cube([16.5,4,12.7],center=true);
// N20_motor_reserve: estimated 10 g
color([0.6,0.65,0.7,1])translate([0,0,28])cube([12,26,10],center=true);
color("orange")translate([0,-18,0])intersection(){translate([0,0,45])sphere(45);translate([0,0,4])cube([36,24,8],center=true);}
color("goldenrod")hull(){translate([0,-18,8])sphere(2.5);translate([0,-18,28])sphere(2.5);}
color("orange")translate([0,18,0])intersection(){translate([0,0,45])sphere(45);translate([0,0,4])cube([36,24,8],center=true);}
color("goldenrod")hull(){translate([0,18,8])sphere(2.5);translate([0,18,28])sphere(2.5);}