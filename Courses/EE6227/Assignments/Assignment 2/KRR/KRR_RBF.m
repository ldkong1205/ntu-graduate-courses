function [acc,Trainningtime,Testingtime] = KRR_RBF(TrainX,TrainY,TestX,TestY,option)

kernel = option.kernel;
kernel_param = option.kernel_param;
lambda = option.lambda;

Ulabel = unique(TrainY);

%% train
Trainningtime = 0;

tic
trainY_temp = oneVrestCoding(TrainY,Ulabel);

K = kernel_matrix(TrainX,kernel,kernel_param);
c = pinv(K+lambda*eye(size(K,1)))*trainY_temp;


Trainingtime_temp = toc;
Trainningtime = Trainningtime + Trainingtime_temp;

%% test
Ntest = size(TestX,1);
Testingtime = 0;

tic
Kt = kernel_matrix(TrainX,kernel,kernel_param,TestX);
Yt = Kt'*c;

Y = oneVrestDecoding(Yt,Ulabel);

Testingtime_temp = toc;
Testingtime = Testingtime + Testingtime_temp;


acc = length(find(Y==TestY))/Ntest;

end

