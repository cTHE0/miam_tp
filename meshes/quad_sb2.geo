a = 1.; // Width
b = 1.; // Height
R = .7; // Internal disc radius
c = .02; // Nozzle length
L = .02; // Nozzle width
r = .01; // Small radius
d = .1; // Refining zone size

lc0 = .05; // Default mesh size
lc1 = .0025; // Refined mesh size


//Internal disc
Point(1) = {0,0,0,lc0};
Point(2) = {R,0,0,lc0};
Point(3) = {0,R,0,lc0};
Point(4) = {-R,0,0,lc0};
Point(5) = {0,-R,0,lc0};

Circle(1) = {2,1,3};
Circle(2) = {3,1,4};
Circle(3) = {4,1,5};
Circle(4) = {5,1,2};

Line Loop(1) = {1,2,3,4};


// External shit
Point(100) = {-a,-b+d,0,lc0};
Point(101) = {-a,-b-c,0,lc1};
Point(102) = {L-a,-b-c,0,lc1};
Point(103) = {L-a,-b-r,0,lc1};
Point(104) = {L+r-a,-b,0,lc1};
Point(105) = {L-a+r+d,-b,0,lc0};
Point(1001) = {L-a+r,-b-r,0,lc1};

Point(106) = {-L+a-r-d,-b,0,lc0};
Point(107) = {-L-r+a,-b,0,lc1};
Point(108) = {-L+a,-b-r,0,lc1};
Point(109) = {-L+a,-b-c,0,lc1};
Point(110) = {a,-b-c,0,lc1};
Point(111) = {a,-b+d,0,lc0};
Point(1002) = {-L+a-r,-b-r,0,lc1};

Point(112) = {a,b-d,0,lc0};
Point(113) = {a,b+c,0,lc1};
Point(114) = {-L+a,b+c,0,lc1};
Point(115) = {-L+a,b+r,0,lc1};
Point(116) = {-L-r+a,b,0,lc1};
Point(117) = {-L+a-r-d,b,0,lc0};
Point(1003) = {-L+a-r,b+r,0,lc1};

Point(118) = {L-a+r+d,b,0,lc0};
Point(119) = {L+r-a,b,0,lc1};
Point(120) = {L-a,b+r,0,lc1};
Point(121) = {L-a,b+c,0,lc1};
Point(122) = {-a,b+c,0,lc1};
Point(123) = {-a,b-d,0,lc0};
Point(1004) = {L-a+r,b+r,0,lc1};

Line(100) = {100,101};
Line(101) = {101,102};
Line(102) = {102,103};
Circle(103) = {103,1001,104};
Line(104) = {104,105};
Line(105) = {105,106};
Line(106) = {106,107};
Circle(107) = {107,1002,108};
Line(108) = {108,109};
Line(109) = {109,110};
Line(110) = {110,111};
Line(111) = {111,112};
Line(112) = {112,113};
Line(113) = {113,114};
Line(114) = {114,115};
Circle(115) = {115,1003,116};
Line(116) = {116,117};
Line(117) = {117,118};
Line(118) = {118,119};
Circle(119) = {119,1004,120};
Line(120) = {120,121};
Line(121) = {121,122};
Line(122) = {122,123};
Line(123) = {123,100};

Line Loop(2) = {100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123};

Plane Surface(1) = {2,-1};
Plane Surface(2) = {1};

Physical Line(1) = {101};
Physical Line(2) = {109};
Physical Line(3) = {113};
Physical Line(4) = {121};
Physical Line(5) = {100,102,103,104,105,106,107,108,110,111,112,114,115,116,117,118,119,120,122,123};

Physical Surface(1) = {1};
Physical Surface(2) = {2};

