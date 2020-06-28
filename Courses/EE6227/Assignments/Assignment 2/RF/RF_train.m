function [Random_Forest,Trainningtime]= RF_train(Data,Labels,B_indx,options)
                      

Trainningtime=0;
nTrees = options.mtry; %number of trees in Random Forest
method = 'c';
M = 1:numel(Labels);

for i = 1 : nTrees
  
   %for parameter tuning
   %TDindx = randsample(M,numel(Labels),true);
   
   
   TDindx = B_indx{i}; %use the indices in the bags. Random sampling with replacement
     
   tic            %starts the clock
   
    Random_ForestT = cartree_train(Data(TDindx,:),Labels(TDindx),TDindx,options.mtry);
    
    Trainingtime_temp=toc;
    Trainningtime=Trainningtime+Trainingtime_temp;

   
    Random_ForestT.method = method;

    Random_ForestT.oobe = 1;
  
    Random_Forest(i) = Random_ForestT; 
end
