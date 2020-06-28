clear all
clc

load('Rastrigin-PSO-2.mat')
PSO=ave_per_fit;
load('Rastrigin-LDIWPSO-2.mat')
LDIWPSO=ave_per_fit;
load('Rastrigin-APSO-2.mat')
APSO=ave_per_fit;
load('Rastrigin-BreedPSO-2.mat')
BreedPSO=ave_per_fit;
load('Rastrigin-BBPSO-2.mat')
BBPSO=ave_per_fit;
load('Rastrigin-CLPSO-2.mat')
CLPSO=ave_per_fit;

figure()
t=1:99:1000;
semilogy(t,PSO(t),'-o');
hold on;
semilogy(t,LDIWPSO(t),'-*');
hold on;
semilogy(t,APSO(t),'-+');
hold on;
semilogy(t,BreedPSO(t),'-x');
hold on;
semilogy(t,BBPSO(t),'-s');
hold on;
semilogy(t,CLPSO(t),'-d');
hold on;
legend('PSO','LDIW-PSO','APSO','Breed-PSO','BBPSO','CLPSO')

%title('Ackley函数收敛结果对比(N=20，D=10)');
grid on
xlabel('Interation');
ylabel('Fitness');

