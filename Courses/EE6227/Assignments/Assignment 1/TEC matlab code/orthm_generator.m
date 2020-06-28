function M=orthm_generator(D)
pi=3.14159;
M=diag(ones(1,D));
for j=1:D%*D
R1=diag(ones(1,D));
x=pi/2.*rand;angel=[cos(x) -sin(x);sin(x) cos(x)];
rc=randperm(D);row=rc(1:2);
R1(row(1),row(1))=angel(1,1);
R1(row(1),row(2))=angel(1,2);
R1(row(2),row(1))=angel(2,1);
R1(row(2),row(2))=angel(2,2);
M=M*R1;
end
