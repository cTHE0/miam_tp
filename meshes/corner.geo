a   = 1.;
b   = 1.;
R   = .05;
lc1 = .07;
lc2 = .02;

Point(1)  = {0.0,0.0,0.0,lc1};
Point(2)  = {a,0.0,0.0,lc1};
Point(3)  = {a,b-R,0.0,lc2};
Point(4)  = {a+R,b,0.0,lc2};
Point(5)  = {2*a,b,0.0,lc1};
Point(6)  = {2*a,2*b,0.0,lc1};
Point(7)  = {0.0,2*b,0.0,lc1};
Point(10) = {a+R,b-R,0.0,lc2};

Point(8)  = {a,b-2*R,0.0,lc1};
Point(9)  = {a+2*R,b,0.0,lc1};

Line(1)   = {1,2};
Line(2)   = {2,8};
Line(3)   = {8,3};
Circle(4) = {3,10,4};
Line(5)   = {4,9};
Line(6)   = {9,5};
Line(7)   = {5,6};
Line(8)   = {6,7};
Line(9)   = {7,1};

Line Loop(11) = {1,2,3,4,5,6,7,8,9};

Plane Surface(1) = {11};

Physical Line(1) = {1};
Physical Line(2) = {7};
Physical Line(3) = {2,3,4,5,6,8,9};

Physical Surface(1) = {1};
