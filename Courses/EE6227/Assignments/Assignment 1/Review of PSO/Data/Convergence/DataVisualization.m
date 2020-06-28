clear all
clc

load('SDP-PSO-2.mat')
PSO=ave_per_fit;
load('SDP-LDIWPSO-2.mat')
LDIWPSO=ave_per_fit;
load('SDP-APSO-2.mat')
APSO=ave_per_fit;
load('SDP-BreedPSO-2.mat')
BreedPSO=ave_per_fit;
load('SDP-BBPSO-2.mat')
BBPSO=ave_per_fit;
load('SDP-CLPSO-2.mat')
CLPSO=ave_per_fit;

figure(1)
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

load('Rosenbrock-CLPSO-10000.mat')
CLPSO=result;
figure(2)
t=1:499:10000;
semilogy(t,CLPSO(t),'-s');
%hold on;
%semilogy(t,BBPSO(t),'-d')
grid on;
