clc;
clear;

% Load datasets (The string inside the load function is the path to the
% .mat file)
train_set = load('../MatDataset/abalone/abalone_Train.mat');
test_set = load('../MatDataset/abalone/abalone_Test.mat');

% Parameters
ModelParameters.L = 10;                 % Number of layers [int]
ModelParameters.N = 100;                % Number of neurons [int]
ModelParameters.C = 0.1;                % Regularisation Parameter [float]
ModelParameters.scale = 1;              % Scaling parameter [float]
ModelParameters.Activation = "relu";    % Activation function ['relu','sigmoid']

% Collect training/testing dataset
trainX = train_set.Data;
trainY = train_set.Label;
testX = test_set.Data;
testY = test_set.Label;

% Encode the label
[trainYT,classes] = OneVAllEncode(trainY);
testYT = OneVAllEncode(testY,classes);

%% Tuning
% Parameters to tune (You can also experiment with different values)
N_range = 3:20:303;
C_range = 2.^(-5:1:14);

best_acc = 0;   % Initialisation

% Requried for consistency
s = RandStream('mcg16807','Seed',0);
RandStream.setGlobalStream(s);

cv_part = cvpartition(trainY,'KFold',4);    % Create indices for training/validation subsets

% Test every configuration
for p1 = 1:numel(N_range)
    for p2 = 1:numel(C_range)
        TestModelParameters = ModelParameters;
        TestModelParameters.N = N_range(p1);
        TestModelParameters.C = C_range(p2);
        
        val_acc = zeros(4,1);   % Initialisation
        for k = 1:4
            % Collect training/validation sets
            val_trainX = trainX(cv_part.training(k),:);
            val_trainY = trainYT(cv_part.training(k),:);
            val_testX = trainX(cv_part.test(k),:);
            val_testY = trainYT(cv_part.test(k),:);
            
            % Data Normalisation
            mean_X = mean(val_trainX,1);
            std_X = std(val_trainX);
            std_X(std_X==0) = 1e-4;                 % For numerical stability
            val_trainX = bsxfun(@rdivide,val_trainX-repmat(mean_X,size(val_trainX,1),1),std_X);
            val_testX = bsxfun(@rdivide,val_testX-repmat(mean_X,size(val_testX,1),1),std_X);

            % Training and Testing
            [~,~,val_acc(k),~,~] = MRVFL(val_trainX,val_trainY,val_testX,val_testY,TestModelParameters);

        end
        
        % Average the validation accuracy
        ValAcc = mean(val_acc);
        
        % Check if current configuration is the best
        if ValAcc > best_acc
            best_acc = ValAcc;
            best_N = N_range(p1);
            best_C = C_range(p2);
        end
    end
end

% Use the best settings
ModelParameters.N = best_N;
ModelParameters.C = best_C;


%% Evaluation
% Data Normalisation
mean_X = mean(trainX,1);
std_X = std(trainX);
std_X(std_X==0) = 1;                 % For numerical stability
trainX = bsxfun(@rdivide,trainX-repmat(mean_X,size(trainX,1),1),std_X);
testX = bsxfun(@rdivide,testX-repmat(mean_X,size(testX,1),1),std_X);
            
[Model,TrainAcc,TestAcc,TrainingTime,TestingTime] = MRVFL(trainX,trainYT,testX,testYT,ModelParameters);


