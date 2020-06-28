clear;clc;
img1=imread('1.jpg');
img2=imread('2.jpg');

img1G=rgb2gray(img1);
img2G=rgb2gray(img2);

C1=corner(img1G,200);
C2=corner(img2G,200);

figure,subplot(1,2,1)
imshow(img1G),title('leftCorner'),
hold on
plot(C1(:,1), C1(:,2), 'r*');
hold off

subplot(1,2,2)
imshow(img2G),title('rightCorner'),
hold on
plot(C2(:,1),C2(:,2),'r*');
hold off

lpoints=zeros(8,2);
rpoints=zeros(8,2);
A=zeros(8,9);
lpoints(1,1)=287;lpoints(1,2)=374;
lpoints(2,1)=254;lpoints(2,2)=193;
lpoints(3,1)=466;lpoints(3,2)=29;
lpoints(4,1)=616;lpoints(4,2)=89;
lpoints(5,1)=596;lpoints(5,2)=374;
lpoints(6,1)=677;lpoints(6,2)=372;
lpoints(7,1)=403;lpoints(7,2)=380;
lpoints(8,1)=520;lpoints(8,2)=396;


rpoints(1,1)=405;rpoints(1,2)=468;
rpoints(2,1)=389;rpoints(2,2)=293;
rpoints(3,1)=623;rpoints(3,2)=112;
rpoints(4,1)=784;rpoints(4,2)=153;    
rpoints(5,1)=763;rpoints(5,2)=473;
rpoints(6,1)=857;rpoints(6,2)=474;
rpoints(7,1)=513;rpoints(7,2)=477;
rpoints(8,1)=643;rpoints(8,2)=496;

for m=1:8
    A(m,1)=lpoints(m,1)*rpoints(m,1);
    A(m,2)=lpoints(m,1)*rpoints(m,2);
    A(m,3)=lpoints(m,1);    
    A(m,4)=lpoints(m,2)*rpoints(m,1);
    A(m,5)=lpoints(m,2)*rpoints(m,2);
    A(m,6)=lpoints(m,2);
    A(m,7)=rpoints(m,1);
    A(m,8)=rpoints(m,2);
    A(m,9)=1;
end

[U,S,V]=svd(A);
V
F=[-0.0662 0.7634 0.0058;
    -0.6421 -0.0236 -0.0011;
    0.0070 0.0009 0.0000;];
[U2,S2,V2]=svd(F);
S2
S2=[0.7685 0 0;0 0.6399 0;0 0 0;];
F_f = U2*S2*V2';

%%

for i=1:8
     test_x=lpoints(i,1);test_y=lpoints(i,2);
     T=[test_x,test_y,1]*F_f;
     line_x=1:4032;
     line_y(i,:)=round((-T(1,3)-T(1,1)*line_x)/T(1,2));
end

figure
imshow(img2G),title('test'),
hold on
for i=1:6

    plot(line_x(:), line_y(i,:), 'b');
    plot(rpoints(i,1),rpoints(i,2),'r*');
end
hold off

test_x=443;test_y=396;
T=[test_x,test_y,1]*F_f;
line_x=1:4032;
line_y=round((-T(1,3)-T(1,1)*line_x)/T(1,2));

figure,subplot(1,2,1)
imshow(img1G),title('test')
hold on 
plot(443,396,'r*')
hold off

subplot(1,2,2)
imshow(img2G),title('test'),
hold on
plot(line_x(:), line_y(:), 'b');
plot(562,494,'r*');
hold off