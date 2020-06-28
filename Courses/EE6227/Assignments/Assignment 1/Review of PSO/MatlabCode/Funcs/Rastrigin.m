function y= Rastrigin(x)
[row,col]=size(x);
if row>1
    error('输入的参数错误');
end
y=sum(x.^2-10*cos(2*pi*x)+10);
y=y;



