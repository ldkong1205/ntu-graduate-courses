 
clear;
clc;

%Read Images.
imgL = imread('L.jpg'); 
imgR = imread('R.jpg'); 

%Convert RGB image to grayscale
grayL=rgb2gray(imgL);
grayR=rgb2gray(imgR);

% Detect FAST features
ptThresh = 0.3;
pointsL = detectFASTFeatures(grayL, 'MinContrast', ptThresh);
pointsR = detectFASTFeatures(grayR, 'MinContrast', ptThresh);

% Display FAST Features found in images L and R.
fL=figure(1);
set(fL,'name','imgL','Numbertitle','off');
imshow(imgL);hold on;
plot(pointsL);
title('imgL');
saveas(fL,strcat('./','L_Fast','.jpg'));
fR=figure(2);
set(fR,'name','imgR','Numbertitle','off');
imshow(imgR);hold on;
plot(pointsR);
title('imgR');
saveas(fR,strcat('./','R_Fast','.jpg'));

%Extract features
[featuresL, pointsL] = extractFeatures(grayL, pointsL);
[featuresR, pointsR] = extractFeatures(grayR, pointsR);

%Match features.
indexPairs = matchFeatures(featuresL, featuresR);
% indexPairs(89,:)=[];%删除一行
% indexPairs(12,:)=[];%删除一行
pointsL = pointsL(indexPairs(:, 1), :);
pointsR = pointsR(indexPairs(:, 2), :);

%Visualize candidate matches.
fM=figure(3); 
set(fM,'name','Match','Numbertitle','off');
showMatchedFeatures(imgL, imgR, pointsL, pointsR);
legend('L', 'R');
saveas(fM,strcat('./','Match','.jpg'));

%Compute the fundamental matrix.
F = estimateFundamentalMatrix(pointsL.Location,pointsR.Location);

index = 12;
PL=[pointsL.Location(index,1),pointsL.Location(index,2)];
PR=[pointsR.Location(index,1),pointsR.Location(index,2)];

% [isIn_L,epipole_L] = isEpipoleInImage(F,[3024 4032]);
% [isIn_R,epipole_R] = isEpipoleInImage(F',[3024 4032]);
lines = epipolarLine(F,PL);

% Display FAST Features found in images L and R.
fEpipole_L=figure(4);
axis on;
set(fEpipole_L,'name','Epipole_L','Numbertitle','off');
imshow(imgL);hold on;
plot(PL(1),PL(2),'r*','linewidth',30);hold on;
% title('Epipole_L');
saveas(fEpipole_L,strcat('./','Epipole_L','.jpg'));

fEpipole_R=figure(5);
set(fEpipole_R,'name','Epipole_R','Numbertitle','off');
imshow(imgR);hold on;
% p=polyfit([PR(1),epipole_R(1)],[PR(2),epipole_R(2)],1);
x=[0,4032];
y = (-lines(3)-lines(1)*x)/lines(2);
plot(x,y,'g','linewidth',20);hold on;
plot(PR(1),PR(2),'r*','linewidth',30);hold on;
% title('fEpipole_R');
saveas(fEpipole_R,strcat('./','Epipole_R','.jpg'));

clear imgL imgR grayL grayR fEpipole_L fEpipole_R fL fM fR;
save(mfilename);












