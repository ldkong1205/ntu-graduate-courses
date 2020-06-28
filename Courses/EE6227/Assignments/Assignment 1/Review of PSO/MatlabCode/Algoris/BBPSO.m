
%仿真
%%参数初始化
format long;
clc;
clear all;
maxg=1000;    %进化次数

%alter
sizepop=80;  %种群规模-------------------N=20/80
D=30;        %维度-----------------------D=10/30
popmax=1;    %种群上下边界值-------------------------------------------------------★

%  32      5.21       600       10      100     30          10      
%  Ackley  Rastrigin  Griewank  Alpine  Sphere  Rosenbrock  Schwefel
%
%  1
%  Sum_of_Different_Power
popmin=-popmax;
Vmax=0.15*popmax;
Vmin=0.15*popmin;

wmax=0.9;
wmin=0.4;

%重复50次
for t=1:50
    %%初始化种群
    for i=1:sizepop
        pop(i,:)=popmax.*rands(1,D);    %初始位置
        %V(i,:)=Vmax.*rands(1,D);        %初始速度
        fitness(i)=Sum_of_Different_Power(pop(i,:));%适应度-----------------------------------------★
    end
    
    %寻找最优个体
    pBest=pop;                  %个体最佳
    [bestfitness bestindex]=min(fitness);
    gBest=pop(bestindex,:);     %全局最佳
    
    fitnesspbest=fitness;       %个体最佳适应度
    fitnessgbest=bestfitness;   %全局最佳适应度
    
    %%迭代寻优
    for i=1:maxg
        for j=1:sizepop            
            %种群更新
            %pop(j,:)=pop(j,:)+V(j,:);
            MU=0.5*(pBest(j,:)+gBest);
            SIGMA=abs(pBest(j,:)-gBest);
            pop(j,:)=normrnd(MU,SIGMA,[1,D]);
            pop(j,find(pop(j,:)>popmax))=popmax;
            pop(j,find(pop(j,:)<popmin))=popmin;

            %%适应度值
            fitness(j)=Sum_of_Different_Power(pop(j,:));%---------------------------------------------★
            
            %个体最优更新
            if fitness(j)<fitnesspbest(j)
                pBest(j,:)=pop(j,:);
                fitnesspbest(j)=fitness(j);
            end
            
            %群体最优更新
            if fitness(j)<fitnessgbest
                gBest=pop(j,:);
                fitnessgbest=fitness(j);
            end
        end
        result(i)=fitnessgbest;
    end
    time(t)=result(maxg);
end















