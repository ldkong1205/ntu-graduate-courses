function y = Sum_of_Different_Power(x)
[row,col]=size(x);
y=0;
for i=1:col
    y=y+abs(x(i))^(i+1);
end

