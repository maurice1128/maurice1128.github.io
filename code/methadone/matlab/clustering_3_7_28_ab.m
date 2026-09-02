%% Clustering 3_7_28_ab
clear all
close all
clc
load('aim2.mat')

%% 3ab_28b
% 
X = [slope_burst_min_3db{1};slope_burst_max_3db{1}]'
[theta,rho] = cart2pol(X(:,1),X(:,2))
thetamin = theta;
scatter(theta,rho)
X = [theta,rho]
h = histogram(thetamin)

X = [slope_burst_min_3da{1};slope_burst_max_3da{1}]'

%X = [slope_burst_min_7da{1}(location);slope_burst_min_7db{1}(location)]'
scatter(X(:,1),X(:,2))
[theta,rho] = cart2pol(X(:,1),X(:,2))
scatter(theta,rho)
thetamax = theta;
histogram(thetamax)
%polarhistogram(thetamin(location_check))
location = find(thetamax<-2.1&thetamax>-2.4& thetamin>-2.4&thetamin<-2.1)
location_check = setdiff([1:3401],location)
hist3([thetamax(location_check),thetamin(location_check)],'CDataMode','auto','FaceColor','interp','Nbins',[50,50])
colorbar
polarhistogram(thetamax(location_check))
polarhistogram(thetamin(location_check))
% hist3([thetamax,thetamin],'CDataMode','auto','FaceColor','interp','Nbins',[50,50])
% colorbar


X = [All_fill_norm{1}((location),1:28),All_fill_norm{2}((location),1:28)]
[coeff,score,latent,tsquared,explained] = pca(X);

explained
%[location1(location)',xy{1,1}]
scatter(score(:,1),score(:,2),'.')
% [theta,rho] = cart2pol(score(:,1)-0.024,score(:,2)-0.039)
[theta,rho] = cart2pol(score(:,1)-0.00537,score(:,2)-0.00803)
scatter(theta,rho)
[x,centers] = hist(theta,70)
bar(centers,x)
hold on
[curvefit, goodness, output, convmsg] = fit(centers',x','gauss4');
plot(curvefit)
polarhistogram(theta,50)

%% plot 
aim_option = {xy{1,1};xy{1,3};xy{1,5};xy{1,7};xy{3,1};xy{3,3};xy{3,5};xy{3,7};xy{5,1};xy{5,3};xy{5,5};xy{5,7};subtype3_1;subtype3_2;subtype3_3;subtype3_4;subtype4_1;subtype4_2;subtype4_3;subtype4_4}
name = {'subtype1 1s';'subtype2 1s';'subtype3 1s';'subtype4 1s';'subtype1 2s';'subtype2 2s';'subtype3 2s';'subtype4 2s';'subtype1 3s';'subtype2 3s';'subtype3 3s';'subtype4 3s';'subtype5 1';'subtype5 2';'subtype5 3';'subtype5 4';'subtype6 1';'subtype6 2';'subtype6 3';'subtype6 4';}
num = 0
for special = 13:16
aim =aim_option{special}
for i = 1:length(aim )
    temp  = aim (i)
    if special <13
plot(All_fill_norm{1}(temp,22:36),'--','LineWidth',1)

    elseif special <17& special>=13
        subplot(2,1,1)
        plot(All_fill_norm{1}(temp,1:57),'--','LineWidth',1)
        hold on
       
        subplot(2,1,2)
         plot(All_fill_norm{2}(temp,1:57),'--','LineWidth',1)
        
    else
        plot(All_fill_norm{1}(temp,26:32),'--','LineWidth',1)
    end
hold on
end
std(All_fill_norm{1}(aim,22:36))
if special<13
    plot(mean(All_fill_norm{1}(aim,22:36)),'LineWidth',2)
    %errorbar([1:15],mean(All_fill_norm{1}(aim,22:36)),std(All_fill_norm{1}(aim,22:36)),'LineWidth',2)
    xline(8);
elseif special <17& special>=13
    subplot(2,1,1)
    %plot([mean(All_fill_norm{1}(aim,:))],'LineWidth',2)
    errorbar([1:57],[mean(All_fill_norm{1}(aim,:))],[std(All_fill_norm{1}(aim,:))],'LineWidth',2)
xline(29);
subplot(2,1,2)
 %plot([mean(All_fill_norm{2}(aim,:))],'LineWidth',2)
 errorbar([1:57],[mean(All_fill_norm{2}(aim,:))],[std(All_fill_norm{2}(aim,:))],'LineWidth',2)
else
    plot(mean(All_fill_norm{1}(aim,26:32)),'LineWidth',2)
    %errorbar([1:15],mean(All_fill_norm{1}(aim,22:36)),std(All_fill_norm{1}(aim,22:36)),'LineWidth',2)
    xline(4);

end
title([name{special} ' Percentage : '  num2str(100*length(aim)/3401) '%'])
saveas(gcf,['/Users/mauricewang/Desktop/mesodon_code/Picture/clustering_ver2/' name{special} ' '  num2str(100*length(aim)/3401) '%_s.png'])
close all
num = num+100*length(aim)/3401
end




