function [bestCutVar, bestCutValue] = axis_parallel_cut(Labels,Data,minleaf)

Labels_temp=unique(Labels);
num_labels=length(Labels_temp);

diff_labels = zeros(1,num_labels);
M = length(Labels);
for i=1:M
    temp=Labels(i);
    index=find(Labels_temp==temp);
    diff_labels(index)=diff_labels(index)+1;
end

pre_gini=0;
for i=1:num_labels
    pre_gini=pre_gini+diff_labels(i)*diff_labels(i);
end
pre_gini=1-pre_gini/(M*M);

[~,n]=size(Data);
cut_value=zeros(1,n);
impurity=zeros(1,n);
for i=1:n
    [cut_value(i), impurity(i)]=gini_impurity(Labels, Data(:,i),minleaf);
end
[~,min_index]=min(impurity);
min_impurity=impurity(min_index);
bestCutValue=cut_value(min_index);
if min_impurity<pre_gini
    bestCutVar=min_index;
else
    bestCutVar=-1;
end
if bestCutValue==max(Data(:,min_index))||bestCutValue==min(Data(:,min_index))
    bestCutVar=-1;
end

end
