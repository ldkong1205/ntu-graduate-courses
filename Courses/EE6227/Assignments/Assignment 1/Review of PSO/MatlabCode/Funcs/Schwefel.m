function y = Schwefel(x)
[row,col]=size(x);

y1=0;
for i=1:col
    y1=y1+abs(x(i));
end
%y1=sum(abs(x));

y2=1;
for h=1:col
    y2=y2*abs(x(h));
end
    
y=y1+y2;
end

