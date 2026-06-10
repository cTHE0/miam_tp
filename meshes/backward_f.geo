a   = 1.;
b   = 5.;
c   = 2.5;
R   = .2;
lc1 = .15;
lc2 = .05;

Point(1)  = {0,0,0,lc1};
Point(2)  = {b,0,0,lc1};
Point(3)  = {b,c,0,lc1};
Point(4)  = {0,c,0,lc1};
Point(5)  = {0,c-a,0,lc1};
Point(16) = {b-a-2*R,c-a,0,lc1};
Point(6)  = {b-a-R,c-a,0,lc2};
Point(7)  = {b-a,c-a-R,0,lc2};
//Point(17) = {b-a,c-a-2*R,0,lc1};
//Point(18) = {b-a,a+2*R,0,lc1};
Point(8)  = {b-a,a+R,0,lc2};
Point(9)  = {b-a-R,a,0,lc2};
Point(19) = {b-a-2*R,a,0,lc1};
Point(10) = {0,a,0,lc1};

Point(101) = {b-a-R,c-a-R,0,lc1};
Point(102) = {b-a-R,a+R,0,lc1};

Line(1)    = {1,2};
Line(2)    = {2,3};
Line(3)    = {3,4};
Line(4)    = {4,5};
Line(5)    = {5,16};
Line(6)    = {16,6};
Circle(7)  = {6,101,7};
Line(8)    = {7,8};
Circle(10) = {8,102,9};
Line(11)   = {9,19};
Line(12)   = {19,10};
Line(13)   = {10,1};

Line Loop(11) = {1,2,3,4,5,6,7,8,10,11,12,13};

Plane Surface(1) = {11};

Physical Line(1) = {4};
Physical Line(2) = {13};
Physical Line(3) = {1,2,3,5,6,7,8,10,11,12};

Physical Surface(1) = {1};
