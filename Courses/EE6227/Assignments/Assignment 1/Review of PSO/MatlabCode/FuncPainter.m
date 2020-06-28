%Griewank 函数
clc;
clear;

%绘制Griewank函数图形
x=[-600:12:600];
y=x;
[X,Y]=meshgrid(x,y);
[row,col]=size(X);
for l =1:col
    for h=1:row
        z(h,l)=Griewank([X(h,l),Y(h,l)]);
    end
end
surf(X,Y,z);
view([-15.5 30]);
shading faceted
