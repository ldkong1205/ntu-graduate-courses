function [acc,trainingtime,testingtime,model1]  = RF(trainX,trainY,testX,testY,options)

% Requried for consistency
s = RandStream('mcg16807','Seed',0);
RandStream.setGlobalStream(s);

% Generate bag indices
nTree = options.nTree;
B_indx = cell(nTree,1);

for i = 1:nTree
    B_indx{i} = randsample(size(trainX,1),size(trainX,1),true);
end

% Training
[model1,trainingtime] = RF_train(trainX,trainY,B_indx,options);

% Testing
[Y1,~,testingtime,~] = RF_predict(testX,model1);

acc = length(find(Y1==testY))/size(testY,1);

end




