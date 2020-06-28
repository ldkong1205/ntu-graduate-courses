function out=RVFLtest(input, net)
% RVFLtest: Random Vector Functional Link
% (Test)
%
%
%Output Parameters
%        out: actul output
%
%Input Parameters
%         input: input data (each row represent different observations)
%         outputlayerweights: output weights that connect both enhancement
%         and direct inputs nodes to output (calculated after training)
%         hiddenlayerweights: hiddenlayer weights that connect inputs nodes
%         to enhancement nodes (calculated after training)
%
% Example Usage
%         input=rand(3,5);
%         target=rand(3,1);
%         enhancementnodesneuronnumber=5
%         net=RVFLtrain(input, target, enhancementnodesneuronnumber)
%         out=RVFLtest(input, net)
%        % check target and y values
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %                           TEST                               %
% %      Random Vector Functional Link with Modified BP          %
% %                                                              %
% %                    Apdullah Yay?k, 2019                      %
% %                    apdullahyayik@gmail.com                   %
% %                                                              %
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

input=normDadapt(input, net.normparameters.minn, net.normparameters.maxx);
enhancementnodesoutput=logsig(input*net.hiddenlayerweights);
hiddenlayerout=[input, enhancementnodesoutput]; % concatanation
y=hiddenlayerout*net.outputlayerweights;
out=outCreate(y);
end



function out=outCreate(y)
% create output

outtemp=[];
for p=1:size(y,1)
    outtemp=[outtemp; y(p,:)==max(y(p,:))];
end
clear y

out=zeros(size(outtemp,1), 1);
for pp=1:size(outtemp,2)
    out=out+outtemp(:,pp)*pp;
end
end

function X=normDadapt(X, minn, maxx)
% adapt norm

sizeX=size(X);
for ii=1:sizeX(1)
    for j=1:sizeX(2)
        X(ii,j)=(((X(ii,j)-minn(j))/(maxx(j)-minn(j))))*2-1;
    end
end
end



