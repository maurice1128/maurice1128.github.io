%% Clustering 7_3_28_ab_cat19
clear all
close all
clc
load('aim2.mat')
%save('variable.mat','All_fill_norm','All_raw_fix','Scattering_All','slope_All','slope_15d_All','freq_All','gap_All','dosage_All','slope_burst_max_All','slope_burst_min_All','slope_burst_max_15d','slope_burst_min_15d','slope_burst_sum_15d', 'gap_diff_All','freq_gap_summation','slope_burst_max_7da' ,'slope_burst_max_7db','slope_burst_min_7da','slope_burst_min_7db','slope_burst_sum_7da','slope_burst_sum_7db','freq_All_3', ...
%    'dosage_All_15d_MPD','dosage_All_15d_MDS','slope_15d_All','slope_burst_max_7da' , ...
%   'slope_burst_max_7db','slope_burst_min_7da', 'slope_burst_min_7db','slope_burst_sum_7da','slope_burst_sum_7db', ...
 %   'slope_burst_max_3da', 'slope_burst_max_3db' ,'slope_burst_min_3da' , 'slope_burst_min_3db','slope_burst_sum_3da','slope_burst_sum_3db' )


%% Analysis

X = [slope_burst_min_7da{1};slope_burst_min_7db{1};dosage_All{1}]'
[theta,rho,z] = cart2pol(X(:,1),X(:,2),X(:,3))
scatter(X(:,1),X(:,2))
scatter(theta,rho)
X = [theta,rho]
h = histogram(theta,30)
polarhistogram(theta)
location1 = find (theta<-2.3 & theta>-2.4);
subtype1_1 = find (theta<-3);
subtype1_2 = find (theta>-3&theta<-2.4)
subtype1_3 = find  (theta>-2.3 & theta<-1.7)
subtype1_4 = find  (theta>-1.7 & theta<-1.4)
X = [slope_burst_max_7da{1}(location1);slope_burst_max_7db{1}(location1)]'

%X = [slope_burst_min_7da{1}(location);slope_burst_min_7db{1}(location)]'
scatter(X(:,1),X(:,2))
[theta,rho] = cart2pol(X(:,1),X(:,2))
scatter(theta,rho)



h = histogram(theta,'NumBins',40)
location = find(theta<-1);
subtype2_1 = location1(find (theta>-1&theta<0.26));
subtype2_2 = location1(find (theta>0.26&theta<1.44));
subtype2_3 = location1(find  (theta>1.44));

X = [All_fill_norm{1}(location1(location),:),All_fill_norm{2}(location1(location),:)]
[coeff,score,latent,tsquared,explained] = pca(X);

explained
%[location1(location)',xy{1,1}]
scatter(score(:,1),score(:,2),'.')
% [theta,rho] = cart2pol(score(:,1)-0.024,score(:,2)-0.039)
[theta,rho] = cart2pol(score(:,1)+0.0088,score(:,2)-0.037)
scatter(theta,rho)
[x,centers] = hist(theta,70)
bar(centers,x)
hold on
[curvefit, goodness, output, convmsg] = fit(centers',x','gauss4');
plot(curvefit)
%histogram(theta)
subtype3_1 = location1(location(find(theta<-2.108)))
subtype3_2 = location1(location(find(theta>-2.108&theta<-0.410)))
subtype3_3 = location1(location(find(theta>-0.410&theta<1.197)))
subtype3_4 = location1(location(find(theta>1.197)))



a = setdiff([1:3401],location1(location)')
% a = [1:3401]
X = [slope_burst_min_7da{1}(a);slope_burst_min_7db{1}(a);dosage_All{1}(a)]'
[theta,rho,z] = cart2pol(X(:,1),X(:,2),X(:,3))
thetamin = theta;
scatter(theta,rho)
X = [theta,rho]
h = histogram(theta)
subtype1_1 = find (theta<-3);
subtype1_2 = find (theta>-3&theta<-2.4)
subtype1_3 = find  (theta>-2.3 & theta<-1.7)
subtype1_4 = find  (theta>-1.7 & theta<-1.4)
X = [slope_burst_max_7da{1}(a);slope_burst_max_7db{1}(a)]'

%X = [slope_burst_min_7da{1}(location);slope_burst_min_7db{1}(location)]'
scatter(X(:,1),X(:,2))
[theta,rho] = cart2pol(X(:,1),X(:,2))
scatter(theta,rho)
thetamax = theta;
scatter3(thetamax,thetamin,freq_All{1}(a),'.')
hist3([thetamax,thetamin],'CDataMode','auto','FaceColor','interp','Nbins',[50,50])
colorbar

scatter(thetamax,thetamin)
x = [-2.4349,-2.3171,-0.0795,0.0383,0.7446,0.8624,1.5692,1.6868]
y = [-1.5402,-1.6634,-2.2795,-2.4024,-3,-3.2]

for k = 1:2:7
    for q = 1:2:5
        q
xy{q,k} = a(find(thetamax>x(k) & thetamax<x(k+1) & thetamin<=y(q) & thetamin>=y(q+1)))
    end
end
location_record = [location1(location)',xy{1,1},xy{1,3},xy{1,5},xy{1,7},xy{3,1},xy{3,3},xy{3,5},xy{3,7},xy{5,1},xy{5,3},xy{5,5},xy{5,7}]
%location_record = [xy{1,1},xy{1,3},xy{1,5},xy{1,7},xy{3,1},xy{3,3},xy{3,5},xy{3,7},xy{5,1},xy{5,3},xy{5,5},xy{5,7}]

 b = setdiff([1:3401],location_record')


X = [slope_burst_min_3da{1}(b);slope_burst_max_3da{1}(b)]';
[theta,rho] = cart2pol(X(:,1),X(:,2))
scatter(X(:,1),X(:,2))
scatter(theta,rho)
histogram(theta,50)
thetamin_3 = theta

X = [slope_burst_min_3db{1}(b);slope_burst_max_3db{1}(b)]';
[theta,rho] = cart2pol(X(:,1),X(:,2))
scatter(X(:,1),X(:,2))
scatter(theta,rho)
histogram(theta,50)
thetamax_3 = theta

hist3([thetamax_3,thetamin_3],'CDataMode','auto','FaceColor','interp','Nbins',[50,50])
colorbar
scatter(thetamax_3,thetamin_3,'.')
T1 = clusterdata([thetamax_3,thetamin_3],'maxclust',4)
scatter3(thetamax_3,thetamin_3,[ones(882,1)],100,T1,'filled')
subtype4_1 = b(find(T1 == 1))
subtype4_2 = b(find(T1 == 2))
subtype4_3 = b(find(T1 == 3))
subtype4_4 = b(find(T1 == 4))

%% Plot
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


