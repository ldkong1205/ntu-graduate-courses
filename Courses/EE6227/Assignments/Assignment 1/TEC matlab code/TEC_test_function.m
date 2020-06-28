function f=TEC_test_function(x,fun,VRmin,VRmax,gbias,norm_flag,shift_flag)
global orthm %best_f best_keep initial_flag

[ps,D]=size(x);

if norm_flag==1
x=VRmin(1,:)+(VRmax(1,:)-VRmin(1,:)).*x;
end

if shift_flag==1
x=x-repmat(gbias,ps,1);
end

greal=[0 1 0 0 0 0 4.209687462275036e+002 0 0 0 0 0 0 0 0];
x=x-greal(fun);
x=x*orthm;
x=x+greal(fun);

if fun==1
    %sphere with noise
%     f=sum(x.^2,2).*(1+0.1.*normrnd(0,1,ps,1));
    f=sum(x.^2,2);

elseif fun==2
    %rosenbrock
    f=sum(100.*(x(:,1:D-1).^2-x(:,2:D)).^2+(x(:,1:D-1)-1).^2,2);
    
    
elseif fun==3
    %ackley
    f=sum(x.^2,2);
    f=20-20.*exp(-0.2.*sqrt(f./D))-exp(sum(cos(2.*pi.*x),2)./D)+exp(1);
    
elseif fun==4
    %griewank
    f=1;
    for i=1:D
        f=f.*cos(x(:,i)./sqrt(i));
    end
    f=sum(x.^2,2)./4000-f+1;

elseif fun==5
    %rastrigin
    f=sum(x.^2-10.*cos(2.*pi.*x)+10,2);
    
elseif fun==6
    %rastrigin_noncont
    x=(abs(x)<0.5).*x+(abs(x)>=0.5).*(round(x.*2)./2);
    f=sum(x.^2-10.*cos(2.*pi.*x)+10,2);
    
elseif fun==7
    %schewfel
    f=0;
    for i=1:D
        f=f-(abs(x(:,i))<=500).*(x(:,i).*sin(sqrt(abs(x(:,i)))))+(abs(x(:,i))>500).*0.001.*(500-abs(x(:,i))).^2;
    end
    f=4.189828872724338e+002*D+f;
    
%     for i=1:ps
%         q=(abs(x(i,:))>500).*(500-abs(x(i,:)).^2);
%         q=sum(q);
%     if (sum(abs(x(i,:))>500))>0
%     f(i)=0.001*q;%abs(f(i))+q;
%     end  
%     end
    
    
elseif fun==8
    %weierstrass
    x=x+0.5;
    a = 0.5;
    b = 3;
    kmax = 20;
    c1(1:kmax+1) = a.^(0:kmax);
    c2(1:kmax+1) = 2*pi*b.^(0:kmax);
    f=0;
    c=-w(0.5,c1,c2);
    for i=1:D
    f=f+w(x(:,i)',c1,c2);
    end
    f=f+c*D;
    
elseif fun==9
    %EF8F2
    f=0;
    for i=1:(D-1)
        f=f+F8F2(x(:,[i,i+1]));
    end
    f=f+F8F2(x(:,[D,1]));
    
elseif fun==10
    %E_ScafferF6
    fhd=str2func('ScafferF6');
    f=0;
    for i=1:(D-1)
        f=f+feval(fhd,(x(:,i:i+1)));
    end
    f=f+feval(fhd,x(:,[D,1]));
    
elseif fun==11
    f=0;
    for i=1:D
        f=f+abs(x(:,i)).^(i+1);
    end

elseif fun==12
    f=schwefel_213(x);

elseif fun==13
    f=com_func1(x);   

elseif fun==14
    f=hybrid_func1(x);
    
elseif fun==15
    f=hybrid_func2(x);

end

% if f<best_f
%     best_f=f;
% end
% best_keep=[best_keep,best_f];



function y = w(x,c1,c2)
y = zeros(length(x),1);
for k = 1:length(x)
	y(k) = sum(c1 .* cos(c2.*x(:,k)));
end

function f=F8F2(x)
f2=100.*(x(:,1).^2-x(:,2)).^2+(1-x(:,1)).^2;
f=1+f2.^2./4000-cos(f2);

function f=ScafferF6(x)
f=0.5+(sin(sqrt(x(:,1).^2+x(:,2).^2)).^2-0.5)./(1+0.001*(x(:,1).^2+x(:,2).^2)).^2;

    % 	12.Schwefel's Problem 2.13
function f=schwefel_213(x)%after Fletcher and Powell
global initial_flag
persistent a b A alpha
[ps,D]=size(x);
if initial_flag==0
    initial_flag=1;
    load schwefel_213_data
    if length(alpha)>=D
        alpha=alpha(1:D);a=a(1:D,1:D);b=b(1:D,1:D);
    else
        alpha=-3+6*rand(1,D);
        a=round(-100+200.*rand(D,D));
        b=round(-100+200.*rand(D,D));
    end
    alpha=repmat(alpha,D,1);
    A=sum(a.*sin(alpha)+b.*cos(alpha),2);
end

for i=1:ps
    xx=repmat(x(i,:),D,1);
    B=sum(a.*sin(xx)+b.*cos(xx),2);
    f(i,1)=sum((A-B).^2,1);
end

%---------------------------------------------------
%   1.com Composition Function 1
function fit=com_func1(x)
global initial_flag
persistent  fun_num func o sigma lamda bias M
if initial_flag==0
    [ps,D]=size(x);
    initial_flag=1;
    fun_num=10;
    load com_func1_data % saved the predefined optima
    if length(o(1,:))>=D
         o=o(:,1:D);
    else
         o=-5+10*rand(fun_num,D);
    end
    o(10,:)=zeros(1,D);
    func.f1=str2func('fsphere');
    func.f2=str2func('fsphere');
    func.f3=str2func('fsphere');
    func.f4=str2func('fsphere');
    func.f5=str2func('fsphere');
    func.f6=str2func('fsphere');
    func.f7=str2func('fsphere');
    func.f8=str2func('fsphere');
    func.f9=str2func('fsphere');
    func.f10=str2func('fsphere');
    bias=((1:fun_num)-1).*100;
    sigma=ones(1,fun_num);
    lamda=5/100.*ones(fun_num,1);
    lamda=repmat(lamda,1,D);
    for i=1:fun_num
        eval(['M.M' int2str(i) '=diag(ones(1,D));']);
    end
end
fit=hybrid_composition_func(x,fun_num,func,o,sigma,lamda,bias,M);

%---------------------------------------------------
%   2.com Composition Function 2
function fit=com_func2(x)
global initial_flag
persistent  fun_num func o sigma lamda bias M
if initial_flag==0
    [ps,D]=size(x);
    initial_flag=1;
    fun_num=10;
    load com_func2_data % saved the predefined optima
    if length(o(1,:))>=D
         o=o(:,1:D);
    else
         o=-5+10*rand(fun_num,D);
    end
    o(10,:)=zeros(1,D);
    func.f1=str2func('fgriewank');
    func.f2=str2func('fgriewank');
    func.f3=str2func('fgriewank');
    func.f4=str2func('fgriewank');
    func.f5=str2func('fgriewank');
    func.f6=str2func('fgriewank');
    func.f7=str2func('fgriewank');
    func.f8=str2func('fgriewank');
    func.f9=str2func('fgriewank');
    func.f10=str2func('fgriewank');
    bias=((1:fun_num)-1).*100;
    sigma=ones(1,fun_num);
    lamda=5/100.*ones(fun_num,1);
    lamda=repmat(lamda,1,D);
    if D==10
    load com_func2_M_D10,
    elseif D==30
    load com_func2_M_D30,
    else
        for i=1:fun_num
            eval(['M.M' int2str(i) '=orthm_generator(D);']);
        end
    end
end
fit=hybrid_composition_func(x,fun_num,func,o,sigma,lamda,bias,M);
    
%---------------------------------------------------
%   3.com Composition Function 3
function fit=com_func3(x)
global initial_flag
persistent  fun_num func o sigma lamda bias M
if initial_flag==0
    [ps,D]=size(x);
    initial_flag=1;
    fun_num=10;
    load com_func3_data % saved the predefined optima
    if length(o(1,:))>=D
         o=o(:,1:D);
    else
         o=-5+10*rand(fun_num,D);
    end
    o(10,:)=zeros(1,D);
    func.f1=str2func('frastrigin');
    func.f2=str2func('frastrigin');
    func.f3=str2func('frastrigin');
    func.f4=str2func('frastrigin');
    func.f5=str2func('frastrigin');
    func.f6=str2func('frastrigin');
    func.f7=str2func('frastrigin');
    func.f8=str2func('frastrigin');
    func.f9=str2func('frastrigin');
    func.f10=str2func('frastrigin');
    bias=((1:fun_num)-1).*100;
    sigma=ones(1,fun_num);
    lamda=ones(fun_num,1);
    lamda=repmat(lamda,1,D);
    if D==10
    load com_func3_M_D10,
    elseif D==30
    load com_func3_M_D30,
    else
        for i=1:fun_num
            eval(['M.M' int2str(i) '=orthm_generator(D);']);
        end
    end
end
fit=hybrid_composition_func(x,fun_num,func,o,sigma,lamda,bias,M);


%----------------------------------------------------------------
%   4.	Rotated Hybrid Composition Function 1
function fit=hybrid_func1(x)
global initial_flag
persistent  fun_num func o sigma lamda bias M
if initial_flag==0
    [ps,D]=size(x);
    initial_flag=1;
    fun_num=10;
    load hybrid_func1_data % saved the predefined optima
    if length(o(1,:))>=D
         o=o(:,1:D);
    else
         o=-5+10*rand(fun_num,D);
    end
    o(10,:)=0;
    func.f1=str2func('fackley');
    func.f2=str2func('fackley');
    func.f3=str2func('frastrigin');
    func.f4=str2func('frastrigin');
    func.f5=str2func('fweierstrass');
    func.f6=str2func('fweierstrass');
    func.f7=str2func('fgriewank');
    func.f8=str2func('fgriewank');
    func.f9=str2func('fsphere');
    func.f10=str2func('fsphere');
    bias=((1:fun_num)-1).*100;
    sigma=ones(1,fun_num);
    lamda=[5/32; 5/32; 1; 1; 10; 10; 5/100; 5/100;  5/100; 5/100];
    lamda=repmat(lamda,1,D);
    if D==10
    load hybrid_func1_M_D10,
    elseif D==30
    load hybrid_func1_M_D30,
    else
        for i=1:fun_num
            eval(['M.M' int2str(i) '=orthm_generator(D);']);
        end
    end
end
fit=hybrid_composition_func(x,fun_num,func,o,sigma,lamda,bias,M);
%----------------------------------------------------------------
%   5.Rotated Hybrid Composition Function 2	
function fit=hybrid_func2(x)
global initial_flag
persistent  fun_num func o sigma lamda bias M
if initial_flag==0
    [ps,D]=size(x);
    initial_flag=1;
    fun_num=10;
    load hybrid_func2_data % saved the predefined optima
    if length(o(1,:))>=D
         o=o(:,1:D);
    else
         o=-5+10*rand(fun_num,D);
    end
    o(10,:)=zeros(1,D);
    func.f1=str2func('frastrigin');
    func.f2=str2func('frastrigin');
    func.f3=str2func('fweierstrass');
    func.f4=str2func('fweierstrass');
    func.f5=str2func('fgriewank');
    func.f6=str2func('fgriewank');
    func.f7=str2func('fackley');
    func.f8=str2func('fackley');
    func.f9=str2func('fsphere');
    func.f10=str2func('fsphere');
    bias=((1:fun_num)-1).*100;
    sigma=ones(1,fun_num); 
    lamda=[1/5;1/5;10;10;5/100;5/100;5/32;5/32;5/100;5/100];
    lamda=repmat(lamda,1,D);
    if D==10
    load hybrid_func2_M_D10,
    elseif D==30
    load hybrid_func2_M_D30,
    else
        for i=1:fun_num
            eval(['M.M' int2str(i) '=orthm_generator(D);']);
        end
    end
    end
fit=hybrid_composition_func(x,fun_num,func,o,sigma,lamda,bias,M);
%---------------------------------------------------------------------
%   6.	Rotated Hybrid Composition Function 3
function fit=hybrid_func3(x)
global initial_flag
persistent  fun_num func o sigma lamda bias M
if initial_flag==0
    [ps,D]=size(x);
    initial_flag=1;
    fun_num=10;
    load hybrid_func2_data % saved the predefined optima
    if length(o(1,:))>=D
         o=o(:,1:D);
    else
         o=-5+10*rand(fun_num,D);
    end
    o(10,:)=0;
    func.f1=str2func('frastrigin');
    func.f2=str2func('frastrigin');
    func.f3=str2func('fweierstrass');
    func.f4=str2func('fweierstrass');
    func.f5=str2func('fgriewank');
    func.f6=str2func('fgriewank');
    func.f7=str2func('fackley');
    func.f8=str2func('fackley');
    func.f9=str2func('fsphere');
    func.f10=str2func('fsphere');
    bias=((1:fun_num)-1).*100;
    sigma=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1];
    lamda=[1/5;1/5;10;10;5/100;5/100;5/32;5/32;5/100;5/100];lamda=lamda.*sigma';
    lamda=repmat(lamda,1,D);
    if D==10
    load hybrid_func2_M_D10,
    elseif D==30
    load hybrid_func2_M_D30,
    else
        for i=1:fun_num
            eval(['M.M' int2str(i) '=orthm_generator(D);']);
        end
    end
end
fit=hybrid_composition_func(x,fun_num,func,o,sigma,lamda,bias,M);
%----------------------------------
function fit=hybrid_composition_func(x,fun_num,func,o,sigma,lamda,bias,M)
[ps,D]=size(x);
for i=1:fun_num
    oo=repmat(o(i,:),ps,1);
    weight(:,i)=exp(-sum((x-oo).^2,2)./2./(D*sigma(i)^2));
end

[tmp,tmpid]=sort(weight,2);
for i=1:ps
    weight(i,:)=(weight(i,:)==tmp(i,fun_num)).*weight(i,:)+(weight(i,:)~=tmp(i,fun_num)).*(weight(i,:).*(1-tmp(i,fun_num).^10));
end
weight=weight./repmat(sum(weight,2),1,fun_num);

fit=0;
for i=1:fun_num
    oo=repmat(o(i,:),ps,1);
    eval(['f=feval(func.f' int2str(i) ',((x-oo)./repmat(lamda(i,:),ps,1))*M.M' int2str(i) ');']);
    x1=5*ones(1,D);
    eval(['f1=feval(func.f' int2str(i) ',(x1./lamda(i,:))*M.M' int2str(i) ');']);
    fit1=2000.*f./f1;
    fit=fit+weight(:,i).*(fit1+bias(i));
end
%-------------------------------------------------
%basic functions

function f=fsphere(x)
%Please notice there is no use to rotate a sphere function, with rotation
%here just for a similar structure as other functions and easy programming
[ps,D]=size(x);
f=sum(x.^2,2);
%--------------------------------
function f=fsphere_noise(x)
[ps,D]=size(x);
f=sum(x.^2,2).*(1+0.1.*normrnd(0,1,ps,1));
%--------------------------------
function f=fgriewank(x)
[ps,D]=size(x);
f=1;
for i=1:D
    f=f.*cos(x(:,i)./sqrt(i));
end
f=sum(x.^2,2)./4000-f+1;
%--------------------------------
function f=fackley(x)
[ps,D]=size(x);
f=sum(x.^2,2);
f=20-20.*exp(-0.2.*sqrt(f./D))-exp(sum(cos(2.*pi.*x),2)./D)+exp(1);
%--------------------------------
function f=frastrigin(x)
[ps,D]=size(x);
f=sum(x.^2-10.*cos(2.*pi.*x)+10,2);
%--------------------------------
function f=frastrigin_noncont(x)
[ps,D]=size(x);
x=(abs(x)<0.5).*x+(abs(x)>=0.5).*(round(x.*2)./2);
f=sum(x.^2-10.*cos(2.*pi.*x)+10,2);
%--------------------------------
function [f]=fweierstrass(x)
[ps,D]=size(x);
x=x+0.5;
a = 0.5;
b = 3;
kmax = 20;
c1(1:kmax+1) = a.^(0:kmax);
c2(1:kmax+1) = 2*pi*b.^(0:kmax);
f=0;
c=-w(0.5,c1,c2);
for i=1:D
f=f+w(x(:,i)',c1,c2);
end
f=f+c*D;

function y = w(x,c1,c2)
y = zeros(length(x),1);
for k = 1:length(x)
	y(k) = sum(c1 .* cos(c2.*x(:,k)));
end
%--------------------------------
function f=fE_ScafferF6(x)
fhd=str2func('ScafferF6');
[ps,D]=size(x);

f=0;
for i=1:(D-1)
    f=f+feval(fhd,(x(:,i:i+1)));
end
    f=f+feval(fhd,x(:,[D,1]));
%--------------------------------    
function f=fE_ScafferF6_noncont(x)
fhd=str2func('ScafferF6');
[ps,D]=size(x);
x=(abs(x)<0.5).*x+(abs(x)>=0.5).*(round(x.*2)./2);
f=0;
for i=1:(D-1)
    f=f+feval(fhd,(x(:,i:i+1)));
end
    f=f+feval(fhd,x(:,[D,1]));
%------------------------------
function f=fEF8F2(x)
[ps,D]=size(x);
f=0;
for i=1:(D-1)
    f=f+F8F2(x(:,[i,i+1]));
end
    f=f+F8F2(x(:,[D,1]));

%--------------------------------
function f=fschwefel_102(x)
[ps,D]=size(x);
f=0;
for i=1:D
    f=f+sum(x(:,1:i),2).^2;
end
%--------------------------------
function f=felliptic(x)
[ps,D]=size(x);
a=1e+6;
f=0;
for i=1:D
f=f+a.^((i-1)/(D-1)).*x(:,i).^2;
end
%--------------------------------

% classical Gram Schmid 
 function [q,r] = cGram_Schmidt (A)
% computes the QR factorization of $A$ via
% classical Gram Schmid 
% 
 [n,m] = size(A); 
 q = A;    
 for j=1:m
     for i=1:j-1 
         r(i,j) = q(:,j)'*q(:,i);
     end
     for i=1:j-1   
       q(:,j) = q(:,j) -  r(i,j)*q(:,i);
     end
     t =  norm(q(:,j),2 ) ;
     q(:,j) = q(:,j) / t ;
     r(j,j) = t  ;
 end 
 
function M=rot_matrix(D,c)
A=normrnd(0,1,D,D);
P=cGram_Schmidt(A);
A=normrnd(0,1,D,D);
Q=cGram_Schmidt(A);
u=rand(1,D);
D=c.^((u-min(u))./(max(u)-min(u)));
D=diag(D);
M=P*D*Q;