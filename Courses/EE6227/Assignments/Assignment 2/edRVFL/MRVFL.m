function [Model,TrainAcc,TestAcc,TrainingTime,TestingTime]  = MRVFL(trainX,trainY,testX,testY,option)

% Requried for consistency
s = RandStream('mcg16807','Seed',0);
RandStream.setGlobalStream(s);

% Train RVFL
[Model,TrainAcc,TrainingTime] = MRVFLtrain(trainX,trainY,option);

% Using trained model, predict the testing data
[TestAcc,TestingTime] = MRVFLpredict(testX,testY,Model);

end
%EOF