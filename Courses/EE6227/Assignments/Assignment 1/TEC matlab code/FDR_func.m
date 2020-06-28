function [gbest,gbestval,fitcount]= FDR_func(fhd,Max_Gen,Max_FES,Particle_Number,Dimension,VRmin,VRmax,varargin)
%[gbest,gbestval,fitcount]= PSO_func('f8',3500,200000,30,30,-5.12,5.12)
rand('state',sum(100*clock));
me=Max_Gen;
ps=Particle_Number;
D=Dimension;
fii=[1 1 2];
iwt=0.9-(1:me).*(0.5./me);
if length(VRmin)==1
    VRmin=repmat(VRmin,1,D);
    VRmax=repmat(VRmax,1,D);
end
mv=0.2*(VRmax-VRmin);
VRmin=repmat(VRmin,ps,1);
VRmax=repmat(VRmax,ps,1);
Vmin=repmat(-mv,ps,1);
Vmax=-Vmin;
pos=VRmin+(VRmax-VRmin).*rand(ps,D);

for i=1:ps;
e(i,1)=feval(fhd,pos(i,:),varargin{:});
end

fitcount=ps;
vel=Vmin+2.*Vmax.*rand(ps,D);%initialize the velocity of the particles
pbest=pos;
pbestval=e; %initialize the pbest and the pbest's fitness value
[gbestval,gbestid]=min(pbestval);
gbest=pbest(gbestid,:);%initialize the gbest and the gbest's fitness value
gbestrep=repmat(gbest,ps,1);

for i=2:me

    for k=1:ps
    dis=abs(repmat(pbest(k,:),ps,1)-pbest(1:ps,:));
    fiterr=repmat(pbestval(k),ps,1)-pbestval(1:ps);
    fiterr=repmat(fiterr,1,D);
    fiterr=fiterr-(dis==zeros(ps,D)).*fiterr;
    dis=dis+(dis==zeros(ps,D));
    FDR=fiterr./dis;
    [fdr,Fid]=max(FDR);
    for dimcnt=1:D
        Pnd(k,dimcnt)=pbest(Fid(dimcnt),dimcnt);
    end
    aa(k,:)=fii(1).*rand(1,D).*(pbest(k,:)-pos(k,:))+fii(2).*rand(1,D).*(gbestrep(k,:)-pos(k,:))+fii(3).*rand(1,D).*(Pnd(k,:)-pos(k,:));

    vel(k,:)=iwt(i).*vel(k,:)+aa(k,:); 
    vel(k,:)=(vel(k,:)>mv).*mv+(vel(k,:)<=mv).*vel(k,:); 
    vel(k,:)=(vel(k,:)<(-mv)).*(-mv)+(vel(k,:)>=(-mv)).*vel(k,:);
    pos(k,:)=pos(k,:)+vel(k,:); 
    
    if (sum(pos(k,:)>VRmax(k,:))+sum(pos(k,:)<VRmin(k,:)))==0;
    e(k,1)=feval(fhd,pos(k,:),varargin{:});
    fitcount=fitcount+1;
    tmp=(pbestval(k)<e(k));
    temp=repmat(tmp,1,D);
    pbest(k,:)=temp.*pbest(k,:)+(1-temp).*pos(k,:);
    pbestval(k)=tmp.*pbestval(k)+(1-tmp).*e(k);%update the pbest
    if pbestval(k)<gbestval
    gbest=pbest(k,:);
    gbestval=pbestval(k);
    gbestrep=repmat(gbest,ps,1);%update the gbest
    end
    end
    
    end

if fitcount>=Max_FES
    break;
end
end


