function net = RVFLtrain (input, target, enhancementnodesneuronnumber)
% RVFLtrain: Random Vector Functional Link 
% (Train)
% Structure of NET is described in "A comprehensive Evaluation of RVFLNs"
% Le Zhang, P.N. Suganthan, Information Sciences
% Learning system is described in "Modified BP Algorithm", Verma B.K. and
% Mulaka J.J., 1994
% These 2 approaches are married in these codes.
%
%Output Parameters
%         outputlayerweights: output weights that connect both enhancement
%         and direct inputs nodes to output
%         hiddenlayerweights: hiddenlayer weights that connect inputs nodes
%         to enhancement nodes
%
%Input Parameters
%         input: input data (each row represent different observations)
%         target: desired outputs
%         enhancementnodesneuronnumber: number of enhacement nodes (specific to RVFL nets)
%
% Example Usage
%         input=rand(3,5);
%         target=rand(3,1);
%         enhancementnodesneuronnumber=5
%         net=RVFLtrain(input, target, enhancementnodesneuronnumber)
%
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %                           TRAIN                              %
% %      Random Vector Functional Link with Modified BP          %
% %                                                              %
% %                    Apdullah Yay?k, 2019                      %
% %                    apdullahyayik@gmail.com                   %
% %                                                              %
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if isequal(size(target,1), size(input,1))==0
    error('Error: input and target sizes dismatch')
else
    target=targetCreate(target);
    [net.normparameters.minn, net.normparameters.maxx, input]=normD(input);
    inputneuronnumber=size(input, 2);
    net.hiddenlayerweights=rand(inputneuronnumber,enhancementnodesneuronnumber);
    enhancementnodesoutput=logsig(input*net.hiddenlayerweights);
    hiddenlayerout=[input, enhancementnodesoutput]; % direct and enhacement nodes
    net.outputlayerweights=pinv(hiddenlayerout)*target;
 end    
end

function target=targetCreate(trainlabel)
% creates target

 classnumber=length(unique(trainlabel));
    target=[];
    for p=1:classnumber
        target=[target trainlabel==unique(p)];
    end
end

function [minn, maxx, X]=normD(X)
% peforms linear normalization

sizeX=size(X);
minn=zeros(1, size(X,2));
maxx=zeros(1, size(X,2));
for i=1:sizeX(2)
    minn(i)=min(X(:,i));
    maxx(i)=max(X(:,i));
end
for ii=1:sizeX(1)
    for j=1:sizeX(2)
        X(ii,j)=(((X(ii,j)-minn(j))/(maxx(j)-minn(j))))*2-1;
    end
end
end
