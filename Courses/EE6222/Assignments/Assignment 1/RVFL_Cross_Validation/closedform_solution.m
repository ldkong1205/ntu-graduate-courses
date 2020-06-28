
clear;
clc;

dataset_name = {'abalone','car','ecoli','magic','nursery','pageblocks','semeion','wine','yeast','zoo'};

ACC_CV_mean = {};
ACC_CV_var = {};
for i=1:numel(dataset_name)
   [ACC_CV_mean{i},ACC_CV_var{i}]= closedform_solution_f(dataset_name{i});
end

save(mfilename);
