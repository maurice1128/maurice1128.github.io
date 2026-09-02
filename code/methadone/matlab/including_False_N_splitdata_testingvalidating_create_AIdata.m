clear all
close all
clc
load('aim2.mat')
training_all = []
validation_all = []
length_negative = 5819
%% PCA check
% find no change in 14 days
temp  = All_fill_norm_training{1}(:,22:36);
temp_s = diff(temp');
temp_s = sum(abs(temp_s))

location = find(temp_s==0)';
location_check = setdiff([1:2721],location)
location_p = location;
temp(location,:)
X = [All_fill_norm_training{1}(location,:),All_fill_norm_training{2}(location,:)]
[coeff,score,latent,tsquared,explained,mu]  = pca(X);
%[location1(location)',xy{1,1}]
scatter(score(:,1),score(:,2),'.')
% [theta,rho] = cart2pol(score(:,1)-0.024,score(:,2)-0.039)
[theta,rho] = cart2pol(score(:,1)+0.04,score(:,2)-0.0256)

data = X;
% Weight and Mean:
wt = 1./var(data);
mu = mean(data);
% PCA, W is coefficient and Y is the score
[W,Y,latent,tsquared,explained,mu]=pca(data);
% First observation of the centered data and its score


%% 57 days preparation
data =  [[All_fill_norm_training{1}(:,:),All_fill_norm_training{2}(:,:)];[All_fill_norm_training{3}(:,:),All_fill_norm_training{4}(:,:)]]
x1 = data-mu;
% According to the reconstruction rule, we should have x1=y1*W'
% therefore, y1 = x1/W'
y = x1/W'
[theta,rho] = cart2pol(y(:,1)+0.04,y(:,2)-0.0270)
training_all = [theta,rho]

data =  [[All_fill_norm_validation{1}(:,:),All_fill_norm_validation{2}(:,:)];[All_fill_norm_validation{3}(:,:),All_fill_norm_validation{4}(:,:)]]
x1 = data-mu;
% According to the reconstruction rule, we should have x1=y1*W'
% therefore, y1 = x1/W'
y = x1/W'
[theta,rho] = cart2pol(y(:,1)+0.04,y(:,2)-0.0270)
validation_all = [theta,rho]
%% 14 days preparation min
X = [[slope_burst_min_7da_training{1}(:)',slope_burst_min_7da_training{3}(:)'];[slope_burst_min_7db_training{1}(:)',slope_burst_min_7db_training{3}(:)']]'
[theta,rho] = cart2pol(X(:,1),X(:,2))
training_all = [training_all,[theta,rho]]

X = [[slope_burst_min_7da_validation{1}(:)',slope_burst_min_7da_validation{3}(:)'];[slope_burst_min_7db_validation{1}(:)',slope_burst_min_7db_validation{3}(:)']]'
[theta,rho] = cart2pol(X(:,1),X(:,2))
validation_all = [validation_all,[theta,rho]]
%% 14 days preparation max
X = [[slope_burst_max_7da_training{1}(:)',slope_burst_max_7da_training{3}(:)'];[slope_burst_max_7db_training{1}(:)',slope_burst_max_7db_training{3}(:)']]'
[theta,rho] = cart2pol(X(:,1),X(:,2))
training_all = [training_all,[theta,rho]]


X = [[slope_burst_max_7da_validation{1}(:)',slope_burst_max_7da_validation{3}(:)'];[slope_burst_max_7db_validation{1}(:)',slope_burst_max_7db_validation{3}(:)']]'
[theta,rho] = cart2pol(X(:,1),X(:,2))
validation_all = [validation_all,[theta,rho]]
%% Attending rate preparation
All_fill_fix_train = [All_raw_fix{1}(index_record{2,1},:);All_raw_fix{3}(index_record{2,3},:)]
list_training_attending_rate = zeros(1,8540)
list_training_attending_rate(find(min(All_fill_fix_train(:,22:29)')==-1)) = 1
training_all = [training_all,list_training_attending_rate']



All_fill_fix_val = [All_raw_fix{1}(index_record{2,2},:);All_raw_fix{3}(index_record{2,4},:)]
list_validation_attending_rate = zeros(1,1360)
list_validation_attending_rate(find(min(All_fill_fix_val(:,22:29)')==-1)) = 1
validation_all = [validation_all,list_validation_attending_rate']
%% All data preparation
All_fill_fix_train = [[All_raw_fix{1}(index_record{2,1},:),All_raw_fix{2}(index_record{2,1},:)];[All_raw_fix{3}(index_record{2,3},:),All_raw_fix{4}(index_record{2,3},:)]]
All_fill_norm_train = [[All_raw_norm{1}(index_record{2,1},:),All_raw_norm{2}(index_record{2,1},:)];[All_raw_norm{3}(index_record{2,3},:),All_raw_norm{4}(index_record{2,3},:)]]
find(All_fill_fix_train==-1)
All_fill_norm_train(find(All_fill_fix_train==-1))= -1

training_all = [training_all,All_fill_norm_train]

All_fill_fix_val = [[All_raw_fix{1}(index_record{2,2},:),All_raw_fix{2}(index_record{2,2},:)];[All_raw_fix{3}(index_record{2,4},:),All_raw_fix{4}(index_record{2,4},:)]]
All_fill_norm_val = [[All_raw_norm{1}(index_record{2,2},:),All_raw_norm{2}(index_record{2,2},:)];[All_raw_norm{3}(index_record{2,4},:),All_raw_norm{4}(index_record{2,4},:)]]
find(All_fill_fix_val==-1)
All_fill_norm_val(find(All_fill_fix_val==-1))= -1

validation_all = [validation_all,All_fill_norm_val]


y_train =  [[zeros(4270,1),ones(4270,1)];[ones(4270,1),zeros(4270,1)]]
y_val = [[zeros(680,1),ones(680,1)];[ones(680,1),zeros(680,1)]]

% save('AI_dataset.mat','training_all','validation_all','y_train','y_val')
