# Readme

Hi,

#### Dataset Statement

There are 28 UCI datasets, the number of instances is in range of $[1000,5000)$. You can choose any 10 of them for your assignment. Each datasets contains 2 `.mat` files, which are training set  and test set namely. The size ratio between the training set and the test set is 4:1. 

#### How to Import Dataset

We suggest you use MATLAB for your assignment.

Just run  `load(dataset_name)` , for example `load('abalone_Train.mat')` , then you can get the raw data and the corresponding labels as `Data` and `Label` namely on your MATLAB Workspace as the `homogeneous array`. Of course you can assign a variable name as `f=load('abalone_Train.mat')`, `f` will be a `Structures` variable, you can call `f.Data` or `f.Label` to access the data you need. Or even you can just double click the files and there will be an Import Wizard of MATLAB helping you.

#### Don't Forget Using K-fold

We need to use k fold when tuning the parameters. Assuming now you have loaded the training set as `f_train` , we can get the stratified 4-fold dataset by calling `c = cvpartition(f_train.Label,'KFold',4)`.  The partition indices of each fold can be get from `c.training(i)` and `c.test(i)` where `i` is the fold number.  For each fold, you can use a `for` loop like following:

```matlab
for i = 1:c.NumTestSets
    trIdx = c.training(i);
    teIdx = c.test(i);
	... ...
end
```

You can also refer to this website for more information about stratified k-fold: [MathWork-CVPartition][cvpartition class]



##### Hope you have fun with them.



[cvpartition class]: https://ww2.mathworks.cn/help/stats/cvpartition-class.html

