function acc = ComputeAcc(Y,ProbScores)

Class_dist = zeros(size(Y));

for i=1:length(ProbScores)
  Dist_temp = ProbScores{i,1};  
  Class_dist = Class_dist + Dist_temp;
end
    
AvgProbScores = Class_dist./length(ProbScores);                                               
[MaxProb,indx] = max(AvgProbScores,[],2);
[~, Ind_corrClass] = max(Y,[],2);
acc = mean(indx == Ind_corrClass);

end