a   = 1.;
b   = 2.;
R   = .1;
lc1 = .2;
lc2 = .1;

L = R/Cos(Pi/8);
e = R*Tan(Pi/8);

Point(1)  = {0.0,0.0,0.0,lc1};
Point(2)  = {b,0.0,0.0,lc1};

Point(3)  = {a+b-(e+R)/Sqrt(2),2*a-(e+R)/Sqrt(2),0.0,lc1};
Point(4)  = {a+b-e/Sqrt(2),2*a-e/Sqrt(2),0.0,lc2};
Point(5)  = {a+b+L*Cos(13*Pi/8),2*a,0.0,lc2};
Point(6)  = {a+b+L*Cos(13*Pi/8)+R,2*a,0.0,lc1};

Point(7)  = {2*b+a-L*Cos(13*Pi/8)-R,2*a,0.0,lc1};
Point(8)  = {2*b+a-L*Cos(13*Pi/8),2*a,0.0,lc2};
Point(9)  = {2*b+a+e/Sqrt(2),2*a-e/Sqrt(2),0.0,lc2};
Point(10) = {2*b+a+(e+R)/Sqrt(2),2*a-(e+R)/Sqrt(2),0.0,lc1};

Point(11) = {2*a+2*b,0.0,0.0,lc1};
Point(12) = {3*b+2*a,0.0,0.0,lc1};
Point(13) = {3*b+2*a,5*a,0.0,lc1};
Point(14) = {2*a+2*b,5*a,0.0,lc1};

Point(15) = {2*b+a+(e+R)/Sqrt(2),3*a+(e+R)/Sqrt(2),0.0,lc1};
Point(16) = {2*b+a+e/Sqrt(2),3*a+e/Sqrt(2),0.0,lc2};
Point(17) = {2*b+a-L*Cos(13*Pi/8),3*a,0.0,lc2};
Point(18) = {2*b+a-R-L*Cos(13*Pi/8),3*a,0.0,lc1};

Point(19) = {a+b+L*Cos(13*Pi/8)+R,3*a,0.0,lc1};
Point(20) = {a+b+L*Cos(13*Pi/8),3*a,0.0,lc2};
Point(21) = {a+b-e/Sqrt(2),3*a+e/Sqrt(2),0.0,lc2};
Point(22) = {a+b-(e+R)/Sqrt(2),3*a+(e+R)/Sqrt(2),0.0,lc1};

Point(23) = {b,5*a,0.0,lc1};
Point(24) = {0.0,5*a,0.0,lc1};

Point(101) = {a+b+L*Cos(13*Pi/8),2*a+L*Sin(13*Pi/8),0.0,lc1};
Point(102) = {2*b+a-L*Cos(13*Pi/8),2*a+L*Sin(13*Pi/8),0.0,lc1};
Point(103) = {2*b+a-L*Cos(13*Pi/8),3*a-L*Sin(13*Pi/8),0.0,lc1};
Point(104) = {a+b+L*Cos(13*Pi/8),3*a-L*Sin(13*Pi/8),0.0,lc1};

// Useless repering points
Point(1001) = {a+b,2*a,0.0,lc1};
Point(1002) = {2*b+a,2*a,0.0,lc1};
Point(1003) = {2*b+a,3*a,0.0,lc1};
Point(1004) = {a+b,3*a,0.0,lc1};

Line(1)    = {1,2};
Line(2)    = {2,3};
Line(3)    = {3,4};
Circle(4)  = {4,101,5};
Line(5)    = {5,6};
Line(6)    = {6,7};
Line(7)    = {7,8};
Circle(8)  = {8,102,9};
Line(9)    = {9,10};
Line(10)   = {10,11};
Line(11)   = {11,12};
Line(12)   = {12,13};
Line(13)   = {13,14};
Line(14)   = {14,15};
Line(15)   = {15,16};
Circle(16) = {16,103,17};
Line(17)   = {17,18};
Line(18)   = {18,19};
Line(19)   = {19,20};
Circle(20) = {20,104,21};
Line(21)   = {21,22};
Line(22)   = {22,23};
Line(23)   = {23,24};
Line(24)   = {24,1};

Line Loop(11) = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24};

Plane Surface(1) = {11};

Physical Line(1) = {24};
Physical Line(2) = {12};
Physical Line(3) = {1,2,3,4,5,6,7,8,9,10,11,13,14,15,161,7,18,19,20,21,22,23};

Physical Surface(1) = {1};
