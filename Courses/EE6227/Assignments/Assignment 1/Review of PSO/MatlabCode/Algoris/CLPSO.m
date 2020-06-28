%function [ fhistory1 fGbest1 ] = clpso( )
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here

%  Estimate parameter
%  Optimization.
%  Written by Xu Xia
%  2013. 5. 24

clc; clear all; close all;

%% Predefine some variables for PSO
sz = 80;                                                                   % swarm size of pso
dim = 30;                                                                  % dimension of particle's
fname ='Sum_of_Different_Power';
xmax=1;
xmin=-xmax;

%  32      5.21       600       10      100     30          10      
%  Ackley  Rastrigin  Griewank  Alpine  Sphere  Rosenbrock  Schwefel
%
%  1
%  Sum_of_Different_Power

X=zeros(sz,dim);                                                           % position of particles
V=zeros(sz,dim);                                                           % velocity of particles

Pbest = zeros(sz, dim);                                                    % individual's best position
fPbest = zeros(sz, 1);

Gbest = zeros(1, dim);                                                     % global best position
fGbest = 0;

fhistory = [ ];                                                            % the best fitness of history
Xhistory = [ ];                                                            % the best position of history

f = zeros(sz, 1);
for k=1:50
    %% Initialization for pso variables
    % upper and lower limit of particle's position
    
    X = rand(sz, dim);
    for i = 1 : dim
        X(:, i)  = repmat(xmin, sz, 1) + (xmax - xmin)*X(:, i);
    end
    
    v_min = -4; v_max = 4;
    V = v_min + (v_max - v_min)*rand(sz, dim);
    c1= 2; c2 = 2;
    w_max = 0.9; w_min = 0.4;
    iter_max = 1000;                                                          % maximum number of iteration
    m = 7;
    %delay=0.02;                                                               %延迟时间
    %% calculate fitness
    for s=1:1:sz
        tempval = feval(fname,X(s,:));
        f(s)=tempval;
    end
    %% update global best and individual best
    [fmin, ind] = min(f);
    fGbest = fmin;
    Gbest = X(ind, :);
    
    Pbest = X;
    fPbest = f;
    
    fhistory = [fhistory; fGbest];
    Xhistory = [ Xhistory; [0,Gbest] ];
    
    iter = 0;
    %% pso main loop
    mask_min = repmat(xmin, 1, dim);
    mask_max = repmat(xmax, 1, dim);
    for i = 1:sz
        PC(i) = 0.05 + 0.45 * (exp(10*(i-1)/(sz-1))-1)/(exp(10)-1);
    end
    flag = zeros(sz,1);
    %figure;
    %hold on;
    %plot(X(:,1),X(:,2),'r.');
    %title('0','fontname','Times New Roman','Color','b','FontSize',16);
    
    while iter<iter_max
        %pause(delay);
        %cla;
        
        %CLPSO
        for i=1:sz
            if mod(flag(i),m)==0;
                for j= 1:dim
                    r = rand;
                    if r < PC(i)
                        a=randperm(sz);
                        b=a(1:2);
                        fchrows = fPbest(b(1)) < fPbest(b(2));
                        if fchrows == 1
                            Pbest(i,j) = Pbest(b(1),j);
                        else
                            Pbest(i,j) = Pbest(b(2),j);
                        end
                    end
                end
                flag(i)=0;
            end
        end
        
        w = w_max - iter*(w_max - w_min)/iter_max;
        V = w*V + c2*rand(sz, dim).*(Pbest - X);
        % check if V is out range of [v_min v_max]
        chrows1 = V > v_max;
        V(find(chrows1)) = v_max;                                             %[row,col V] = find(X, ...)  查询满足一定条件的元素的行和列
        chrows2 = V < v_min;
        V(find(chrows2)) = v_min;
        
        X = X +V;
        
        for s=1:1:sz
            tempval = feval(fname,X(s,:));
            f(s)=tempval;
        end
        
        % check if X is out range of xrange
        for i = 1:sz
            min_throw = X(i,:) < mask_min;
            max_throw = X(i,:) > mask_max;
            mi = sum(sum(min_throw.*min_throw));
            ma = sum(sum(max_throw.*min_throw));
            mm = mi + ma;
            if mm==0
                if f(i) < fPbest(i)
                    fPbest(i) = f(i);
                    Pbest(i,:) = X(i,:);
                else
                    flag(i) = flag(i) + 1;
                end
            end
        end
        % check if X is out range of xrange
        %min_throw = X <= mask_min;
        %min_keep = X > mask_min;
        %max_throw = X >= mask_max;
        %max_keep = X < mask_max;
        %X = ( min_throw.*mask_min ) + ( min_keep.*X );
        %X = ( max_throw.*mask_max ) + ( max_keep.*X );
        
        % update individual's best
        %chrows = f < fPbest;
        %fPbest(find(chrows)) = f(find(chrows));
        %Pbest(find(chrows), :) = X(find(chrows), :);
        
        % update global best
        [fmin, ind] = min(fPbest);
        if fmin < fGbest
            fGbest = fmin;
            Gbest = Pbest(ind, :);
        end
        
        
        %plot(X(:,1),X(:,2),'r.');
        %title(iter,'fontname','Times New Roman','Color','b','FontSize',16);
        
        fhistory = [fhistory; fGbest];
        Xhistory = [ Xhistory; [iter,Gbest]];
        
        iter = iter +1;
    end
    % End of loop
    fhistory1 = fhistory;
    fGbest1 = fGbest;
    %% output the final result
%     figure;
%     plot(fhistory);
%     title('最优个体适应度','fontsize',12);
%     xlabel('进化代数','fontsize',12);
%     ylabel('适应度','fontsize',12);
    time(k)=fhistory(end);
end