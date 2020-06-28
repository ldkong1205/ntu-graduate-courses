%test_frame
clear all
% close all
global orthm best_f best_keep initial_flag
rand('state',sum(100*clock));
warning off
fhd=str2func('TEC_test_function');%fun,VRmin,VRmax,gbias,norm_flag,shift_flag

me=3000;
ps=10;
Max_FES=ps*me;
D=10;
norm_flag=0;
shift_flag=0;


orthm=diag(ones(1,D));

VRmin=[-100,-2.048,-32.768,-600,-5.12,-5.12,-500,-0.5,-2.048,-100,-1,-5,-5,-5,-5];
VRmax=-VRmin;
if norm_flag==1;
    VRminn=zeros(1,D);
    VRmaxn=ones(1,D)
else
    VRminn=VRmin;VRmaxn=VRmax;
end
% funchoose=[1,2,3,4,5,6,7,8,10];
funchoose=[1,2,3,4,5,6,7,8,13,15];
for funnum=1:10
fun=funchoose(funnum);
initial_flag=0;
for jjj=1:30

if shift_flag==1
    gbias=0.8.*(VRmin(fun)+(VRmax(fun)-VRmin(fun)).*rand(1,D));
    if fun==2
        gbias=-1+(1+1).*rand(1,D);
    end
    if fun==7
        gbias=-500+(0+500).*rand(1,D);
    end
else
    gbias=zeros(1,D);
end
fun,jjj
% best_keep=[];best_f=1e+30;
[CLPSO_new_gbest,CLPSO_new_gbestval,CLPSO_new_fitcount]= CLPSO_new_func(fhd,me,Max_FES,ps,D,VRminn(fun),VRmaxn(fun),fun,VRmin(fun),VRmax(fun),gbias,norm_flag,shift_flag); 
CLPSO_new_gbestval

CLPSO_new_fitcount_res(fun,jjj)=CLPSO_new_fitcount;CLPSO_new_gbestval_res(fun,jjj)=CLPSO_new_gbestval;CLPSO_new_gbest_res(fun,jjj,:)=CLPSO_new_gbest;

end

end

mean(CLPSO_new_gbestval_res')

