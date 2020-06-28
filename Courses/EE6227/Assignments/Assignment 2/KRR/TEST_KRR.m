clc;
clear;

% Load datasets (The string inside the load function is the path to the
% .mat file)
train_set = load('../MatDataset/abalone/abalone_Train.mat');
test_set = load('../MatDataset/abalone/abalone_Test.mat');

% Parameters
ModelParameters.kernel = 'RBF_kernel';       % Kernel ['RBF_kernel','lin_kernel','poly_kernel','wav_kernel','Chi_square']
ModelParameters.kernel_param = 1;            % Kernel Parameters (See README)
ModelParameters.lambda = 1;                  % Regularisation Parameter

% Collect training/testing dataset
trainX = train_set.Data;
trainY = train_set.Label;
testX = test_set.Data;
testY = test_set.Label;

%% Tuning
% Parameters to tune (You can also experiment with different values)
gamma_range = 2.^(-15:2:3);
lambda_range = 2.^(-5:1:14);

best_acc = 0;   % Initialisation

% Requried for consistency
s = RandStream('mcg16807','Seed',0);
RandStream.setGlobalStream(s);

cv_part = cvpartition(trainY,'KFold',4);    % Create indices for training/validation subsets

% Test every configuration
for p1 = 1:numel(gamma_range)
    for p2 = 1:numel(lambda_range)
        TestModelParameters = ModelParameters;
        TestModelParameters.kernel_param = gamma_range(p1);
        TestModelParameters.lambda = lambda_range(p2);
        
        val_acc = zeros(4,1);   % Initialisation
        for k = 1:4
            % Collect training/validation sets
            val_trainX = trainX(cv_part.training(k),:);
            val_trainY = trainY(cv_part.training(k),:);
            val_testX = trainX(cv_part.test(k),:);
            val_testY = trainY(cv_part.test(k),:);

            % Data Normalisation
            mean_X = mean(val_trainX,1);
            std_X = std(val_trainX);
            std_X(std_X==0) = 1e-4;                 % For numerical stability
            val_trainX = bsxfun(@rdivide,val_trainX-repmat(mean_X,size(val_trainX,1),1),std_X);
            val_testX = bsxfun(@rdivide,val_testX-repmat(mean_X,size(val_testX,1),1),std_X);
            
            % Training and Testing
            val_acc(k) = KRR_RBF(val_trainX,val_trainY,val_testX,val_testY,TestModelParameters);

        end
        
        % Average the validation accuracy
        ValAcc = mean(val_acc);
        
        % Check if current configuration is the best
        if ValAcc > best_acc
            best_acc = ValAcc;
            best_gamma = gamma_range(p1);
            best_lambda = lambda_range(p2);
        end
    end
end

% Use the best settings
ModelParameters.kernel_param = best_gamma;
ModelParameters.lambda = best_lambda;


%% Evaluation
% Data Normalisation
mean_X = mean(trainX,1);
std_X = std(trainX);
std_X(std_X==0) = 1;                 % For numerical stability
trainX = bsxfun(@rdivide,trainX-repmat(mean_X,size(trainX,1),1),std_X);
testX = bsxfun(@rdivide,testX-repmat(mean_X,size(testX,1),1),std_X);

[TestAcc,TrainingTime,TestingTime] = KRR_RBF(trainX,trainY,testX,testY,ModelParameters);


