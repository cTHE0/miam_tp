a   = 2.;
b   = 2.;
L   = .2;
R   = .05;
lc1 = .07;
lc2 = .02;
lc3 = .15;

Point(1)  = {0,a,0,lc1};
Point(2)  = {L-2*R,a,0,lc1};
Point(3)  = {L-R,a,0,lc2};
Point(4)  = {L,a-R,0,lc2};
Point(5)  = {L,a-2*R,0,lc1};
Point(6)  = {L,0,0,lc3};
Point(7)  = {b+L,0,0,lc3};
Point(8)  = {b+L,2*a+L,0,lc3};
Point(9)  = {L,2*a+L,0,lc3};
Point(10) = {L,a+L+2*R,0,lc1};
Point(11) = {L,a+L+R,0,lc2};
Point(12) = {L-R,a+L,0,lc2};
Point(13) = {L-2*R,a+L,0,lc1};
Point(14) = {0,a+L,0,lc1};

Point(101) = {L-R,a-R,0,lc1};
Point(102) = {L-R,a+L+R,0,lc1};

Line(1)    = {1,2};
Line(2)    = {2,3};
Circle(3)  = {3,101,4};
Line(4)    = {4,5};
Line(5)    = {5,6};
Line(6)    = {6,7};
Line(7)    = {7,8};
Line(8)    = {8,9};
Line(9)    = {9,10};
Line(10)   = {10,11};
Circle(11) = {11,102,12};
Line(12)   = {12,13};
Line(13)   = {13,14};
Line(14)   = {14,1};

Line Loop(11) = {1,2,3,4,5,6,7,8,9,10,11,12,13,14};

Plane Surface(1) = {11};

Physical Line(1) = {14};
Physical Line(2) = {7};
Physical Line(3) = {1,2,3,4,5,6,8,9,10,11,12,13};

Physical Surface(1) = {1};
