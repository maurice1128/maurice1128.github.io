clear all
close all
clc
load('aim2.mat')
All_fill_fix_positive = [All_raw_fix{1}(index_record{2,1},:)]
All_fill_fix_negative =[All_raw_fix{3}(index_record{2,3},:)]
positive_rate = zeros(1,2721)
negative_rate  = zeros(1,5819)
positive_rate(find(min(All_fill_fix_positive(:,22:29)')==-1)) = 1;
attending_rate_postitive = (2721-sum(positive_rate))/2721
negative_rate(find(min(All_fill_fix_negative(:,22:29)')==-1)) = 1;
attending_rate_negative = (5819-sum(negative_rate))/5819



positive_rate(find(positive_rate==1)) = 2
positive_rate(find(positive_rate==0)) = 1
positive_rate(find(positive_rate==2)) = 0
positive_rate = positive_rate'
negative_rate(find(negative_rate==1)) = 2
negative_rate(find(negative_rate==0)) = 1
negative_rate(find(negative_rate==2)) = 0
negative_rate = negative_rate'