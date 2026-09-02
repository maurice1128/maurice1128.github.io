%% Clustering 37_28_b_cat6
clear all
close all
clc
load('aim2.mat')

%% 3b7b_28b
temp  = All_fill_norm{1}(:,22:36);
temp_s = diff(temp');
temp_s = sum(abs(temp_s))

location = find(temp_s==0)';
location_check = setdiff([1:3401],location)
X = [slope_burst_min_7db{1};slope_burst_max_7db{1}]'
[theta,rho] = cart2pol(X(:,1),X(:,2))
thetamin = theta;
polarhistogram(thetamin(location_check),30)
theta_d = [];
theta_min_d= rad2deg(theta(location_check))
for i = 1:length(theta(location_check))
    if theta_min_d(i)<0
        theta_min_d(i) = theta_min_d(i)+360;
    end

end
scatter(theta,rho)
X = [theta,rho]
h = histogram(theta)

X = [slope_burst_min_3db{1};slope_burst_max_3db{1}]'

%X = [slope_burst_min_7da{1}(location);slope_burst_min_7db{1}(location)]'
scatter(X(:,1),X(:,2))
[theta,rho] = cart2pol(X(:,1),X(:,2))
scatter(theta,rho)
thetamax = theta;
%polarhistogram(thetamin(location_check))
theta_d = [];
polarhistogram(thetamax(location_check),30)
theta_max_d= rad2deg(theta(location_check))
for i = 1:length(theta(location_check))
    if theta_max_d(i)<0
        theta_max_d(i) = theta_max_d(i)+360;
    end

end
hist3([thetamax(location_check),thetamin(location_check)],'CDataMode','auto','FaceColor','interp','Nbins',[50,50])
colorbar

x = [0,150,150,270]
y = [0,150,150,270]
count  = 0
for k = 1:2:3
    for q = 1:2:3
             
             count  = count+length(find(theta_min_d>x(k) & theta_min_d<=x(k+1) & theta_max_d>y(q) & theta_max_d<=y(q+1)))
xy{q,k} = location_check(find(theta_min_d>x(k) & theta_min_d<=x(k+1) & theta_max_d>y(q) & theta_max_d<=y(q+1)))

       
    end
end


% hist3([thetamax,thetamin],'CDataMode','auto','FaceColor','interp','Nbins',[50,50])
% colorbar


X = [All_fill_norm{1}((location),1:28),All_fill_norm{2}((location),1:28)]
[coeff,score,latent,tsquared,explained] = pca(X);

explained
%[location1(location)',xy{1,1}]
scatter(score(:,1),score(:,2),'.')
% [theta,rho] = cart2pol(score(:,1)-0.024,score(:,2)-0.039)
[theta,rho] = cart2pol(score(:,1)-0.0165,score(:,2)+0.007)
scatter(theta,rho)
[x,centers] = hist(theta,70)
bar(centers,x)
hold on
[curvefit, goodness, output, convmsg] = fit(centers',x','gauss4');
plot(curvefit)
close all
polarhistogram(theta)
polarhistogram(theta)
theta_d = [];
theta_d= rad2deg(theta)
pca_1 = location(find(theta_d>30&theta_d<=60))
pca_2 = location(find(theta_d>90&theta_d<=210))
pca_3 = location(find(theta_d>330|theta_d<=30))


%% Plot
aim_option = {pca_1;pca_2;pca_3;xy{1,1}';xy{1,3}';xy{3,1}';xy{3,3}'}
name = {'pca 1';'pca 2';'pca 3';'73d 1';'73d 2';'73d 3';'73d 4'}
num = 0
for special = 1:7
aim =aim_option{special}
for i = 1:length(aim )
    temp  = aim (i)
    if special >3
plot(All_fill_norm{1}(temp,22:29),'--','LineWidth',1)

    elseif special <=3
        subplot(2,1,1)
        plot(All_fill_norm{1}(temp,1:29),'--','LineWidth',1)
        hold on
       
        subplot(2,1,2)
         plot(All_fill_norm{2}(temp,1:29),'--','LineWidth',1)
        
    
    end
hold on
end
std(All_fill_norm{1}(aim,22:29))
if special>3
    plot(mean(All_fill_norm{1}(aim,22:29)),'LineWidth',2)
    %errorbar([1:15],mean(All_fill_norm{1}(aim,22:36)),std(All_fill_norm{1}(aim,22:36)),'LineWidth',2)
    xline(8);
elseif special <=3
    subplot(2,1,1)
    plot([mean(All_fill_norm{1}(aim,1:29))],'LineWidth',2)
    %errorbar([1:57],[mean(All_fill_norm{1}(aim,:))],[std(All_fill_norm{1}(aim,:))],'LineWidth',2)
xline(29);
subplot(2,1,2)
 plot([mean(All_fill_norm{2}(aim,1:29))],'LineWidth',2)
 %errorbar([1:57],[mean(All_fill_norm{2}(aim,:))],[std(All_fill_norm{2}(aim,:))],'LineWidth',2)

end
title([name{special} ' Percentage : '  num2str(100*length(aim)/3401) '%'])
saveas(gcf,['/Users/mauricewang/Desktop/mesodon_code/Picture/cluster_28_37_b_ver1/' name{special} ' '  num2str(100*length(aim)/3401) '%_s.png'])
close all
num = num+100*length(aim)/3401
end
