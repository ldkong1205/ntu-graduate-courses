 function[ACC_CV_mean,ACC_CV_var]=bias_link_scale_f(dataset_name)

run(strcat('./',dataset_name,'/',dataset_name,'_R','.m'));

data=data(:,2:end);
dataX=data(:,1:end-1);

% do normalization for each feature
mean_X=mean(dataX,1);
dataX=dataX-repmat(mean_X,size(dataX,1),1);
norm_X=sum(dataX.^2,1);
norm_X=sqrt(norm_X);
norm_X=repmat(norm_X,size(dataX,1),1);
dataX=dataX./norm_X;
dataY=data(:,end);

% for datasets where training-testing partition is available, paramter tuning is based on this file.
run(strcat('./',dataset_name,'/',dataset_name,'_conxuntos','.m'));
trainX=dataX(index1,:); 
trainY=dataY(index1,:);
testX=dataX(index2,:);
testY=dataY(index2,:);

% Linearly scale the random features before feedinto the nonlinear activation function. 
S=-5:0.5:5;

MAX_acc1=zeros(length(S),1);
Best_N1=zeros(length(S),1);
Best_C1=zeros(length(S),1);
Best_S1=zeros(length(S),1);
MAX_acc2=zeros(length(S),1);
Best_N2=zeros(length(S),1);
Best_C2=zeros(length(S),1);
Best_S2=zeros(length(S),1);
MAX_acc3=zeros(length(S),1);
Best_N3=zeros(length(S),1);
Best_C3=zeros(length(S),1);
Best_S3=zeros(length(S),1);
MAX_acc4=zeros(length(S),1);
Best_N4=zeros(length(S),1);
Best_C4=zeros(length(S),1);
Best_S4=zeros(length(S),1);

scale=zeros(length(S),1);

for s=1:numel(S)
     
%     the number of hidden neurons
    for N=3:20:203
   
%       in ridge regression
        for C=-5:14 
    
        Scale=2^S(s);

%         RVFL without bias and without direct link.
        option1.N=N;
        option1.C=2^C;
        option1.Scale=Scale;
        option1.Scalemode=3;
        option1.bias=0;
        option1.link=0;
        
%         RVFL with bias and without direct link.
        option2.N=N;
        option2.C=2^C;
        option2.Scale=Scale;
        option2.Scalemode=3;
        option2.bias=1;
        option2.link=0;
       
%         RVFL without bias and with direct link.
        option3.N=N;
        option3.C=2^C;
        option3.Scale=Scale;
        option3.Scalemode=3;
        option3.bias=0;
        option3.link=1;
        
%         RVFL with bias and with direct link
        option4.N=N;
        option4.C=2^C;
        option4.Scale=Scale;
        option4.Scalemode=3;
        option4.bias=1;
        option4.link=1;
        
         [train_accuracy1,test_accuracy1]=RVFL_train_val(trainX,trainY,testX,testY,option1);
         [train_accuracy2,test_accuracy2]=RVFL_train_val(trainX,trainY,testX,testY,option2);  
         [train_accuracy3,test_accuracy3]=RVFL_train_val(trainX,trainY,testX,testY,option3);
         [train_accuracy4,test_accuracy4]=RVFL_train_val(trainX,trainY,testX,testY,option4);  

        if test_accuracy1>MAX_acc1(s); % paramater tuning: we prefer the parameter which lead to better accuracy on the test data.
          MAX_acc1(s)=test_accuracy1;
          Best_N1(s)=N;
          Best_C1(s)=C;
          Best_S1(s)=Scale;
       end

         if test_accuracy2>MAX_acc2(s);% paramater tuning: we prefer the parameter which lead to better accuracy on the test data.
          MAX_acc2(s)=test_accuracy2;
          Best_N2(s)=N;
          Best_C2(s)=C;
          Best_S2(s)=Scale;
         end

         if test_accuracy3>MAX_acc3(s);% paramater tuning: we prefer the parameter which lead to better accuracy on the test data.
          MAX_acc3(s)=test_accuracy3;
          Best_N3(s)=N;
          Best_C3(s)=C;
          Best_S3(s)=Scale;
        end

         if test_accuracy4>MAX_acc4(s);% paramater tuning: we prefer the parameter which lead to better accuracy on the test data.
          MAX_acc4(s)=test_accuracy4;
          Best_N4(s)=N;
          Best_C4(s)=C;
          Best_S4(s)=Scale;
         end
   
        end
    end
    scale(s)=Scale;
end

%for datasets where training-testing partition is not available, performance vealuation is based on cross-validation.
run(strcat('./',dataset_name,'/',dataset_name,'_conxuntos_kfold','.m'));

ACC_CV_1 = zeros(4,1);
ACC_CV_2 = zeros(4,1);
ACC_CV_3 = zeros(4,1);
ACC_CV_4 = zeros(4,1);
ACC_CV_5 = zeros(4,1);
ACC_CV_6 = zeros(4,1);
ACC_CV_mean = zeros(6,1);
ACC_CV_var = zeros(6,1);
for i=1:4
    
    trainX=dataX(index{2*i-1},:);
    trainY=dataY(index{2*i-1},:);
    testX=dataX(index{2*i},:);
    testY=dataY(index{2*i},:);
    
        option1.N=Best_N(1);
        option1.C=2^Best_C(1);
        option1.Scale=Best_S(1);
        option1.Scalemode=3;
        option1.bias=0;
        option1.link=0;
       
        option2.N=Best_N(2);
        option2.C=2^Best_C(2);
        option2.Scale=Best_S(2);
        option2.Scalemode=3;
        option2.bias=1;
        option2.link=0;
       
        option3.N=Best_N(3);
        option3.C=2^Best_C(3);
        option3.Scale=Best_S(3);
        option3.Scalemode=3;
        option3.bias=0;
        option3.link=1;
        
        option4.N=Best_N(4);
        option4.C=2^Best_C(4);
        option4.Scale=Best_S(4);
        option4.Scalemode=3;
        option4.bias=1;
        option4.link=1;
        
        % ACC_CV each row is the accuracy for one RVFL configuration. Each column is a single trial for evaluation.
        [train_accuracy1,ACC_CV_1(i)]=RVFL_train_val(trainX,trainY,testX,testY,option1);
        [train_accuracy2,ACC_CV_2(i)]=RVFL_train_val(trainX,trainY,testX,testY,option2);
        [train_accuracy3,ACC_CV_3(i)]=RVFL_train_val(trainX,trainY,testX,testY,option3);
        [train_accuracy4,ACC_CV_4(i)]=RVFL_train_val(trainX,trainY,testX,testY,option4);
   
end

ACC_CV_mean=[mean(ACC_CV_1),mean(ACC_CV_2),mean(ACC_CV_3),mean(ACC_CV_4)];
ACC_CV_var=[var(ACC_CV_1),var(ACC_CV_2),var(ACC_CV_3),var(ACC_CV_4)];

save(strcat(mfilename,'_',dataset_name));

f=figure();
set(f,'name',filename,'Numbertitle','off');
subplot(221);
yyaxis left;
scatter(S,MAX_acc1,'bs','LineWidth',2);hold on;
plot(S,MAX_acc1,'b','LineWidth',1);
ylabel('Accuracy');
yyaxis right;
scatter(S,Best_N1,'r*','LineWidth',2);hold on;
plot(S,Best_N1,'r','LineWidth',1);
ylabel('N');
xlabel('log2S');
title('without bias, without direct link');

subplot(222);
yyaxis left;
scatter(S,MAX_acc2,'bs','LineWidth',2);hold on;
plot(S,MAX_acc2,'b','LineWidth',1);hold on;
ylabel('Accuracy');
yyaxis right;
scatter(S,Best_N2,'r*','LineWidth',2);hold on;
plot(S,Best_N2,'r','LineWidth',1);hold on;
ylabel('N');
xlabel('log2S');
title('with bias, without direct link');

subplot(223);
yyaxis left;
scatter(S,MAX_acc3,'bs','LineWidth',2);hold on;
plot(S,MAX_acc3,'b','LineWidth',1);hold on;
ylabel('Accuracy');
yyaxis right;
scatter(S,Best_N3,'r*','LineWidth',2);hold on;
plot(S,Best_N3,'r','LineWidth',1);hold on;
ylabel('N');
xlabel('log2S');
title('without bias, with direct link');

subplot(224);
yyaxis left;
scatter(S,MAX_acc4,'bs','LineWidth',2);hold on;
plot(S,MAX_acc4,'b','LineWidth',1);hold on;
ylabel('Accuracy');
yyaxis right;
scatter(S,Best_N4,'r*','LineWidth',2);hold on;
plot(S,Best_N4,'r','LineWidth',1);hold on;
ylabel('N');
xlabel('log2S');
title('with bias, with direct link');

axes( 'Position', [0, 0.95, 1, 0.05] ) ;
set( gca, 'Color', 'None', 'XColor', 'None', 'YColor', 'None' ) ;
text( 0.5, 0, filename, 'FontSize', 14', 'FontWeight', 'Bold', ...
  'HorizontalAlignment', 'Center', 'VerticalAlignment', 'Bottom' ) ;

saveas(f,strcat(mfilename,'_',dataset_name,'.jpg'));
