function [cut_value, impurity]=gini_impurity(Labels, Data,minleaf)

cut_value=0;
impurity=100; 
if length(unique(Data))~=1
Labels_temp=unique(Labels);
num_labels=length(Labels_temp);
diff_labels_l = zeros(1,num_labels);
diff_labels_r = zeros(1,num_labels);
diff_labels = zeros(1,num_labels);
M=length(Labels);
      for i=1:M 
          temp=Labels(i);
          index=find(Labels_temp==temp);
          diff_labels(index)=diff_labels(index)+1;
      end
      
 pre_gini=0;
  for i=1:num_labels
     pre_gini=pre_gini+diff_labels(i)* diff_labels(i);
  end
  pre_gini=1-pre_gini/(M*M);
  
 

for nl=1:num_labels
    diff_labels_r(nl)=diff_labels(nl);
    
end

[sort_value,sort_index]=sort(Data,'ascend');
sort_labels=Labels(sort_index);
%calculate gini after a node

j=minleaf;

while(j<=M-minleaf)

index_temp=find(sort_value(j:end)==sort_value(j));
sort_labels_temp=sort_labels(j:end);
temp=sort_labels_temp(index_temp);
temp_label1=unique(temp);
 NO_temp_label=length(temp_label1);
    for i=1:NO_temp_label
        NO_temp=length(find(temp==temp_label1(i)));
        cl=find(Labels_temp==temp_label1(i));
%         Labels_temp
%         temp_label1
        diff_labels_l(cl)= diff_labels_l(cl)+NO_temp;
        diff_labels_r(cl)=diff_labels_r(cl)-NO_temp;
    end
    gr=0;
    gl=0;
    
  for nl=1:num_labels
      gl=gl+diff_labels_l(nl)*diff_labels_l(nl);
      gr=gr+diff_labels_r(nl)*diff_labels_r(nl);
               
  end
  j=j+length(index_temp);
%      if j-1~=M
%     gl=1-gl/((j-1)*(j-1));
%     gr=1-gr/((M-j+1)*(M-j+1));
%     post_gini=(j-1)*gl/M+(M-j+1)*gr/M;
     if j<=M-minleaf
    gl=1-gl/((j-1)*(j-1));
    gr=1-gr/((M-j+1)*(M-j+1));
     post_gini=(j-1)*gl/M+(M-j+1)*gr/M; %what is this?
     else
         post_gini=pre_gini+1;
     end
%         diff_labels_l
%         diff_labels_r
    if post_gini<pre_gini
        pre_gini=post_gini;
        cut_value=0.5*(sort_value(j)+sort_value(j-1)); %taking the average of sorted matrix for splitting value
       
        impurity=post_gini;
    
    end
     
    
end
% L1=length(find(sort_value<=cut_value));
% L2=length(find(sort_value>cut_value));
% if L1<minleaf && L1~=0
%     L1
%     Labels
%     Data
% end
% if L2<minleaf && L2~=0
%     L2
%     Labels
%     Data
% end 
else
   impurity=1000; 
end

end
