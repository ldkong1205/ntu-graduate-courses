
%%参数初始化

    clc;
    clear all;
    c1=1.49445;
    c2=1.49445;
    bc=0.8;%杂交概率
    bs=0.1;%杂交池大小比例
    w=0.8;
    maxg=1000;     %进化次数
    %--------------------------------------------------------------------------
    sizepop=80;    %种群规模  N=20/80
    par_num=30;    %best_particle number  D=10/30
    popmax=1;      %种群上下边界值
    %  32      5.21       600       10      100     30          10      
    %  Ackley  Rastrigin  Griewank  Alpine  Sphere  Rosenbrock  Schwefel
    %
    %  1
    %  Sum_of_Different_Power
    %--------------------------------------------------------------------------
    popmin=-popmax;
    Vmax=0.15*popmax;
    Vmin=0.15*popmin;


    wmax=0.8;
    wmin=0.6;

%重复50次
for t=1:50
    %%产生初始粒子和速度
    for i=1:sizepop
        pop(i,:)=popmax.*rands(1,par_num);    %初始位置
        V(i,:)=Vmax.*rands(1,par_num);        %初始速度
        fitness(i)=Sum_of_Different_Power(pop(i,:));%适应度-----------------------------------------------------------------
    end

    %寻找最优个体
    [bestfitness bestindex]=min(fitness);
    pBest=pop;                  %个体最佳
    gBest=pop(bestindex,:);     %全局最佳
    fitnesspbest=fitness;       %个体最佳适应度
    fitnessgbest=bestfitness;   %全局最佳适应度

    %%迭代寻优
    for i=1:maxg
        for j=1:sizepop
            
            %速度更新
            V(j,:)=w*V(j,:)+c1*rand*(pBest(j,:)-pop(j,:))+c2*rand*(gBest-pop(j,:));
            V(j,find(V(j,:)>Vmax))=Vmax;
            V(j,find(V(j,:)<Vmin))=Vmin;

            %种群更新
            pop(j,:)=pop(j,:)+V(j,:);
            pop(j,find(pop(j,:)>popmax))=popmax;
            pop(j,find(pop(j,:)<popmin))=popmin;

            %适应度值
            fitness(j)=Sum_of_Different_Power(pop(j,:));%-----------------------------------------------

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
            r1=rand();
            if r1<bc
                numPool=round(bs*sizepop);
                PoolX=pop(1:numPool,:);
                PoolVX=V(1:numPool,:);
                for z=1:numPool
                    seed1=floor(rand()*(numPool-1)+1);
                    seed2=floor(rand()*(numPool-1)+1);
                    pb=rand();
                    childx1(z,:)=pb*PoolX(seed1,:)+(1-pb)*PoolX(seed2,:);
                    childv1(z,:)=(PoolVX(seed1,:)+PoolVX(seed2,:))*norm(PoolVX(seed1,:))/norm(PoolVX(seed1,:)+PoolVX(seed2,:));
                end 
            end
        end
        result(i)=fitnessgbest;
    end
time(t)=result(maxg);
end


    
    
        
        
        
        
        
        
        
        
        
    
    
    