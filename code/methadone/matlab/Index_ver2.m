%% Index Ver2
clear all
close all
clc
load('aim2.mat')

%% -1 data
All = {positive_pd,positive_ds,negative_pd,negative_ds};

All_h = {positive_header,positive_header,negative_header,negative_header};
All_fill = {};
All_date_ur = {positive_date,positive_date,negative_date,negative_date};
for special = 1:4
    long = All{special};
    header = All_h{special};
    date_ur = All_date_ur{special};
temp = [];
temp_header = [];
temp_date = [];
temp_raw = [];
for i = 1:length(long)
    i
aim = long(i,:);
aim_raw = long(i,:);
location = find(aim == -1);
for k = 1:length(location)
    light = 1;
    count =-1;
    while light ==1
        if location(k)+count~=0;
        if aim(location(k)+count)==-1
            count = count-1;
        else  
            light = 0;
            left_count = count;
            left = aim(location(k)+count);
        end
        else
            light = 0;
            left_count = count;
            left = -1;
        end
    end
    light = 1;
    count =1;
    while light ==1
        if location(k)+count~=58;
        if aim(location(k)+count)==-1;
            count = count+1;
        else
            light = 0;
            right_count = count;
            right = aim(location(k)+count);
        end
        else
            light = 0;
            right_count = count;
            right = -1;
        end

    end
    if left==-1&right==-1
    aim(location(k)) = -1;
    elseif left==-1|right==-1
aim(location(k)) = max(left,right);
    else

    aim(location(k)) = ((right-left)/(abs(right_count)+abs(left_count)))*abs(left_count)+left;


    end


end
if aim~=-1
temp = [temp;aim];
temp_header = [temp_header,header(i)];
temp_date = [temp_date,date_ur(i)];
temp_raw =[temp_raw;aim_raw ];
end
end
All_fill(special) ={temp};
All_raw_fix(special) = {temp_raw};
All_fill_header(special) ={temp_header};
All_fill_date(special) = {temp_date};
end

%% normalization base on day 7 center from 29
All_fill_norm = {};
for special = 1:4
    long = All_fill{special};
    aim_temp = [];
    for i = 1:length(long)
        i
        aim = long(i,:);
        temp = [];
        for k = 1:57
       temp =[temp,aim(k)/aim(22)];
        end
        aim_temp = [aim_temp;temp];

    end
    All_fill_norm(special) = {aim_temp};
    temp = find(All_raw_fix{special}==-1)
   
    aim_temp_raw = aim_temp;
    aim_temp_raw(temp) = -1;
    raw=All_raw_fix{special};
    All_raw_norm(special) = {aim_temp}

end






%% Index
ds_n_gap = All_fill{4};
ds_p_gap = All_fill{2};
for special = 1:4
    long = All_fill{special};
    long_raw = All_raw_fix{special};
    long_norm = All_fill_norm{special};
    R_temp = [];
    p_temp = [];
    freq_temp = [];
    gap = [];
    gap_diff = [];
    dosage = [];
    dosage_15d_MDS = [];
    dosage_15d_MPD = [];
    p_temp_b = [];
    p_temp_b_m = [];
    p_temp_b_s = [];
    p_temp_b_m_15d  = [];
    p_temp_b_s_15d  = [];
    p_temp_b_sum_15d=[];
    p_temp_b_m_7da = [];
    p_temp_b_s_7da = [];
    p_temp_b_sum_7da = [];
   p_temp_b_m_7db= [];
   p_temp_b_s_7db = [];
    p_temp_b_sum_7db = [];
    temp_gap_summation = [];
    low_dose_location = [];
    high_dose_location = [];
p_temp_b_m_3da = [];
p_temp_b_s_3da = [];
p_temp_b_sum_3da = [];
p_temp_b_m_3db = [];
p_temp_b_s_3db = [];
p_temp_b_sum_3db = [];
freq_temp_3 = [];
    for i = 1:length(long)
        i
        aim = long(i,:);
        aim_raw = long_raw(i,:);
        aim_norm = long_norm(i,:);
 

%% trend ->norm data in  57days
[p,S] = polyfit(1:57,aim_norm,1); 
p_temp = [p_temp,p(1)];


%% burst trend -> norm data in 15 days
[p,S] = polyfit(1:15,aim_norm(22:36),1); 
p_temp_b = [p_temp_b,p(1)];
%%  scattering->norm data in 57 days
[p,S] = polyfit(1:57,aim_norm,1); 
f = polyval(p,1:57);
R = corrcoef(aim_norm,f);
if isnan(R(2,1))
    R(2,1) = 1;
else
    R(2,1)  = abs(R(2,1));
end

R_temp = [R_temp,R(2,1)];
    
%% Dosage Gap -> fill data norm by mean of ds
if special == 1
    aim_ds = ds_p_gap(i,:);
    gap = [gap,mean((aim_ds-aim)/mean(aim_ds))];
end

if special == 3
    aim_ds = ds_n_gap(i,:);
    gap = [gap,mean((aim_ds-aim)/mean(aim_ds))];
end

%% Max Dosage Gap Difference in 15d
if special == 1
    aim_ds = ds_p_gap(i,:);
    gap_diff = [gap_diff,(max(aim_ds-aim)-min(aim_ds-aim))/max(aim_raw)];
end

if special == 3
    aim_ds = ds_n_gap(i,:);
    gap_diff = [gap_diff,(max(aim_ds-aim)-min(aim_ds-aim))/max(aim_raw)];
end
%% Come Frequency-> 0 = 都沒來 , 1 = 都有來
location = find(aim_raw==-1);
location= location-21;
location_1 = find(location<=7 & location>0);
Freq = length(location_1);
freq_temp = [freq_temp,(7-Freq)/7];

%% Come Frequency in  3 Day-> 0 = 都沒來 , 1 = 都有來
location = find(aim_raw==-1);
location= location-25;
location_1 = find(location<=3 & location>0);
Freq = length(location_1);
freq_temp_3 = [freq_temp_3,(3-Freq)/3];
%% Dosage
dosage = [dosage,max(aim_raw)];
%% 15d Dosage Median in DS
if special == 2|4
dosage_15d_MDS =[dosage_15d_MDS,median(aim(22:36))];
end

%% 15d Dosage Median in PD
if special == 1|3
dosage_15d_MPD =[dosage_15d_MPD,median(aim(22:36))];
end
%% maxBurst trend -> 3 days max&min slope 
p_find = [];
for trend_burst = 1:54
[p,S] = polyfit(1:3,aim_norm(1,trend_burst:trend_burst+2),1); 
p_find = [p_find,p(1)];
end

p_temp_b_m = [p_temp_b_m,max(p_find)];
p_temp_b_s = [p_temp_b_s,min(p_find)];
%% maxBurst trend -> 3 days max&min slope->in 15 days
p_find = [];
for trend_burst = 22:36
[p,S] = polyfit(1:3,aim_norm(1,trend_burst:trend_burst+2),1); 
p_find = [p_find,p(1)];
end

p_temp_b_m_15d = [p_temp_b_m_15d,max(p_find)];
p_temp_b_s_15d = [p_temp_b_s_15d,min(p_find)];
p_temp_b_sum_15d = [p_temp_b_sum_15d,abs(min(p_find))+max(p_find)];

%% maxBurst trend -> 3 days max&min slope->in 7+ days
p_find = [];
for trend_burst = 29:34
[p,S] = polyfit(1:3,aim_norm(1,trend_burst:trend_burst+2),1); 
p_find = [p_find,p(1)];
end

p_temp_b_m_7da = [p_temp_b_m_7da,max(p_find)];
p_temp_b_s_7da = [p_temp_b_s_7da,min(p_find)];
p_temp_b_sum_7da = [p_temp_b_sum_7da,abs(min(p_find))+max(p_find)];

%% maxBurst trend -> 3 days max&min slope->in 7- days
p_find = [];
for trend_burst = 22:27
[p,S] = polyfit(1:3,aim_norm(1,trend_burst:trend_burst+2),1); 
p_find = [p_find,p(1)];
end

p_temp_b_m_7db = [p_temp_b_m_7db,max(p_find)];
p_temp_b_s_7db = [p_temp_b_s_7db,min(p_find)];
p_temp_b_sum_7db = [p_temp_b_sum_7db,abs(min(p_find))+max(p_find)];

%% maxBurst trend -> 3 days max&min slope->in 3+ days
p_find = [];
for trend_burst = 29:30
[p,S] = polyfit(1:3,aim_norm(1,trend_burst:trend_burst+2),1); 
p_find = [p_find,p(1)];
end

p_temp_b_m_3da = [p_temp_b_m_3da,max(p_find)];
p_temp_b_s_3da = [p_temp_b_s_3da,min(p_find)];
p_temp_b_sum_3da = [p_temp_b_sum_3da,abs(min(p_find))+max(p_find)];

%% maxBurst trend -> 3 days max&min slope->in 3- days
p_find = [];
for trend_burst = 26:27
[p,S] = polyfit(1:3,aim_norm(1,trend_burst:trend_burst+2),1); 
p_find = [p_find,p(1)];
end

p_temp_b_m_3db = [p_temp_b_m_3db,max(p_find)];
p_temp_b_s_3db = [p_temp_b_s_3db,min(p_find)];
p_temp_b_sum_3db = [p_temp_b_sum_3db,abs(min(p_find))+max(p_find)];

%% gap summation for freq 
temp_g =0;
if special == 1
    aim_ds = ds_p_gap(i,:);
    for gap_s = 22:29
        if aim_raw(gap_s) == -1
            temp_g = temp_g+aim_ds(gap_s);
        else
            temp_g = temp_g+aim_ds(gap_s)-aim_raw(gap_s);
        end
    end
end


if special == 3
    aim_ds = ds_n_gap(i,:);
    for gap_s = 22:29
        if aim_raw(gap_s) == -1
            temp_g = temp_g+aim_ds(gap_s);
        else
            temp_g = temp_g+aim_ds(gap_s)-aim_raw(gap_s);
        end
end
end

temp_gap_summation = [temp_gap_summation , temp_g];

%% record high low dose
threshold = 100;
if max(aim_raw) >=threshold
    high_dose_location = [high_dose_location,i];
else
    low_dose_location = [low_dose_location,i];
end

    end


   Scattering_All(special) = {R_temp} ;
   slope_All(special) = {p_temp};
   slope_15d_All(special) = {p_temp_b};
   slope_burst_max_All(special) = {p_temp_b_m};
   slope_burst_min_All(special) = {p_temp_b_s};
   slope_burst_max_15d(special) = {p_temp_b_m_15d};
   slope_burst_min_15d(special) = {p_temp_b_s_15d};
   slope_burst_sum_15d(special) = {p_temp_b_sum_15d};
   freq_All(special) = {freq_temp};
   freq_All_3(special) = {freq_temp_3};
   gap_All(special) = {gap};
   gap_diff_All(special) = {gap_diff};
   dosage_All(special) = {dosage};
   freq_gap_summation(special) = {temp_gap_summation};
   slope_burst_max_7da(special) = {p_temp_b_m_7da};
   slope_burst_max_7db(special) = {p_temp_b_m_7db};
   slope_burst_min_7da(special) = {p_temp_b_s_7da};
   slope_burst_min_7db(special) = {p_temp_b_s_7db};
   slope_burst_sum_7da(special) = {p_temp_b_sum_7da};
   slope_burst_sum_7db(special) = {p_temp_b_sum_7db};
   location_high(special) = {high_dose_location};
   location_low(special) = {low_dose_location};
   dosage_All_15d_MPD(special) = {dosage_15d_MPD};
   dosage_All_15d_MDS(special) = {dosage_15d_MDS};
   slope_burst_max_3da(special) = {p_temp_b_m_3da};
   slope_burst_max_3db(special) = {p_temp_b_m_3db};
   slope_burst_min_3da(special) = {p_temp_b_s_3da};
   slope_burst_min_3db(special) = {p_temp_b_s_3db};
   slope_burst_sum_3da(special) = {p_temp_b_sum_3da};
   slope_burst_sum_3db(special) = {p_temp_b_sum_3db};

   
end

save('aim2.mat')


%% 2D Clustering
%input
% imgdir = '/Users/mauricewang/Desktop/mesodon_code/Picture/2D_clustering'
% positive_index_all = { Scattering_All{1},slope_All{1},slope_15d_All{1}, freq_All{1},gap_All{1},dosage_All{1},slope_burst_max_All{1},slope_burst_min_All{1},slope_burst_max_15d{1},slope_burst_min_15d{1},slope_burst_sum_15d{1},gap_diff_All{1}};
% negative_index_all = {Scattering_All{3},slope_All{3},slope_15d_All{3}, freq_All{3},gap_All{3},dosage_All{3},slope_burst_max_All{3},slope_burst_min_All{3},slope_burst_max_15d{3},slope_burst_min_15d{3},slope_burst_sum_15d{3},gap_diff_All{3}};
% label = {'Scattering All';'slope All';'slope 15d All';'freq All';'gap All';'dosage All';'slope Burst Max';'slope Burst Min';'slope Burst Max 15d';'slope Burst Min 15d';'slope Burst Sum 15d';'gap difference'}
%code
for a =1:length(positive_index_all)
    count = a+1
    while count<=length(positive_index_all)
for i = 1:2
    if i ==1
        z = 1
    close all
    scatter(positive_index_all{a},positive_index_all{count})
    
     xlabel(label{a});
       ylabel(label{count})
    hold on
    saveas(gcf,[imgdir '/Positive_only_' label{a} '_' label{count} '.png'])
   
    else
       scatter(negative_index_all{a},negative_index_all{count}) 
      
       legend('Positive','Negative')
        saveas(gcf,[imgdir '/Both_' label{a} '_' label{count} '.png'])

    end
end

count = count+1;
end
end

%% 3D Clustering
%input
% imgdir = '/Users/mauricewang/Desktop/mesodon_code/Picture/3D_clustering'
% positive_index_all = { 
%     Scattering_All{1},
%     slope_All{1},
%     slope_15d_All{1},
%     freq_All{1},
%     gap_All{1},
%     dosage_All{1},
%     slope_burst_max_All{1},
%     slope_burst_min_All{1},
%     slope_burst_max_15d{1},
%     slope_burst_min_15d{1},
%     slope_burst_sum_15d{1},
%     gap_diff_All{1},
%     freq_gap_summation{1},
%    slope_burst_max_7da{1} ,
%    slope_burst_max_7db{1},
%    slope_burst_min_7da{1},
%    slope_burst_min_7db{1},
%    slope_burst_sum_7da{1},
%    slope_burst_sum_7db{1},
%     };
% negative_index_all = {
%     Scattering_All{3},
%     slope_All{3},
%     slope_15d_All{3}, 
%     freq_All{3},
%     gap_All{3},
%     dosage_All{3},
%     slope_burst_max_All{3},
%     slope_burst_min_All{3},
%     slope_burst_max_15d{3},
%     slope_burst_min_15d{3},
%     slope_burst_sum_15d{3},
%     gap_diff_All{3},
%     freq_gap_summation{3},
%    slope_burst_max_7da{3} ,
%    slope_burst_max_7db{3},
%    slope_burst_min_7da{3},
%    slope_burst_min_7db{3},
%    slope_burst_sum_7da{3},
%    slope_burst_sum_7db{3},
%     };
% 
% label = {'Scattering All';
%     'slope All';
%     'slope 15d All';
%     'freq All';
%     'gap All';
%     'dosage All';
%     'slope Burst Max';
%     'slope Burst Min';
%     'slope Burst Max 15d';
%     'slope Burst Min 15d';
%     'slope Burst Sum 15d';
%     'gap difference';
%     'freq diff from gap summation';
%     'slope burst max 7da';
%    'slope burst max 7db';
%    'slope burst min 7da';
%    'slope burst min 7db';
%    'slope burst sum 7da';
%    'slope burst sum 7db';
%     }
imgdir = '/Users/mauricewang/Desktop/mesodon_code/Picture/3D_clustering_ver2'
positive_index_all = { 
    
   
    freq_All{1},
    freq_All_3{1},
     freq_gap_summation{1},
    
    dosage_All{1},
   dosage_All_15d_MPD{1},
   dosage_All_15d_MDS{1},
   
    slope_15d_All{1},
   slope_burst_max_7da{1} ,
   slope_burst_max_7db{1},
   slope_burst_min_7da{1},
   slope_burst_min_7db{1},
   slope_burst_sum_7da{1},
   slope_burst_sum_7db{1},
   slope_burst_max_3da{1} ,
   slope_burst_max_3db{1} ,
   slope_burst_min_3da{1} ,
   slope_burst_min_3db{1},
   slope_burst_sum_3da{1} ,
   slope_burst_sum_3db{1} ,
    };
negative_index_all = {
    
    
    freq_All{3},
    freq_All_3{3},
     freq_gap_summation{3},
    
    dosage_All{3},
    dosage_All_15d_MPD{3},
     dosage_All_15d_MDS{3},
    
   slope_15d_All{3}, 
   slope_burst_max_7da{3} ,
   slope_burst_max_7db{3},
   slope_burst_min_7da{3},
   slope_burst_min_7db{3},
   slope_burst_sum_7da{3},
   slope_burst_sum_7db{3},
    slope_burst_max_3da{3} ,
   slope_burst_max_3db{3} ,
   slope_burst_min_3da{3} ,
   slope_burst_min_3db{3},
   slope_burst_sum_3da{3} ,
   slope_burst_sum_3db{3} ,
    };

label = {
    
    'freq All';
    'freq All in 3 Day';
    'freq diff from gap summation';
    'dosage All maximum for Patient drink';
    'dosage All median in 15d for Patient drink';
     'dosage All median in 15d for Doctor say';

    
   
    
    'slope 15d All';
    'slope burst max 7da';
   'slope burst max 7db';
   'slope burst min 7da';
   'slope burst min 7db';
   'slope burst sum 7da';
   'slope burst sum 7db';
   'slope_burst max 3da' ;
   'slope burst max 3db' ;
   'slope burst min 3da' ;
   'slope burst min 3db';
   'slope burst sum 3da' ;
   'slope burst sum 3db' ;
    }
%code
for a =1:length(positive_index_all)
    count = a+1
    while count<=length(positive_index_all)
        count_1 = count+1
        while count_1 <=length(positive_index_all)
for i = 1:2
    if i ==1
        z = 1
    close all
    T = table(positive_index_all{a},positive_index_all{count},positive_index_all{count_1})
    T = renamevars(T,T.Properties.VariableNames{1},label{a})
    T = renamevars(T,T.Properties.VariableNames{2},label{count})
     T = renamevars(T,T.Properties.VariableNames{3},label{count_1})
    
    scatter3(T,label{a},label{count},label{count_1})
   
    
     xlabel(label{a});
       ylabel(label{count})
    hold on
    saveas(gcf,[imgdir '/Positive_only_' label{a} '_' label{count} '_' label{count_1} '.png'])
        saveas(gcf,[imgdir '/Positive_only_' label{a} '_' label{count} '_' label{count_1} '.fig'])
    
    else
        T = table(negative_index_all{a},negative_index_all{count},negative_index_all{count_1})
    T = renamevars(T,T.Properties.VariableNames{1},label{a})
    T = renamevars(T,T.Properties.VariableNames{2},label{count})
     T = renamevars(T,T.Properties.VariableNames{3},label{count_1})
         scatter3(T,label{a},label{count},label{count_1})
      
       legend('Positive','Negative')
        saveas(gcf,[imgdir '/Both_' label{a} '_' label{count} '_' label{count_1} '.png'])
           saveas(gcf,[imgdir '/Both_' label{a} '_' label{count} '_' label{count_1} '.fig'])
    end
end
count_1 = count_1+1
        end

count = count+1;
        end
    

end

%%3d plot for high low dose
imgdir = '/Users/mauricewang/Desktop/mesodon_code/Picture/3D_clustering_ver2'

positive_index_all = { 
    Scattering_All{1}(location_high{1}),
    slope_All{1}(location_high{1}),
    slope_15d_All{1}(location_high{1}),
    freq_All{1}(location_high{1}),
    gap_All{1}(location_high{1}),
    dosage_All{1}(location_high{1}),
    slope_burst_max_All{1}(location_high{1}),
    slope_burst_min_All{1}(location_high{1}),
    slope_burst_max_15d{1}(location_high{1}),
    slope_burst_min_15d{1}(location_high{1}),
    slope_burst_sum_15d{1}(location_high{1}),
    gap_diff_All{1}(location_high{1}),
    freq_gap_summation{1}(location_high{1}),
   slope_burst_max_7da{1}(location_high{1}) ,
   slope_burst_max_7db{1}(location_high{1}),
   slope_burst_min_7da{1}(location_high{1}),
   slope_burst_min_7db{1}(location_high{1}),
   slope_burst_sum_7da{1}(location_high{1}),
   slope_burst_sum_7db{1}(location_high{1}),
    };
negative_index_all = {
    Scattering_All{1}(location_low{1}),
    slope_All{1}(location_low{1}),
    slope_15d_All{1}(location_low{1}), 
    freq_All{1}(location_low{1}),
    gap_All{1}(location_low{1}),
    dosage_All{1}(location_low{1}),
    slope_burst_max_All{1}(location_low{1}),
    slope_burst_min_All{1}(location_low{1}),
    slope_burst_max_15d{1}(location_low{1}),
    slope_burst_min_15d{1}(location_low{1}),
    slope_burst_sum_15d{1}(location_low{1}),
    gap_diff_All{1}(location_low{1}),
    freq_gap_summation{1}(location_low{1}),
   slope_burst_max_7da{1}(location_low{1}) ,
   slope_burst_max_7db{1}(location_low{1}),
   slope_burst_min_7da{1}(location_low{1}),
   slope_burst_min_7db{1}(location_low{1}),
   slope_burst_sum_7da{1}(location_low{1}),
   slope_burst_sum_7db{1}(location_low{1}),
    };

label = {'Scattering All';
    'slope All';
    'slope 15d All';
    'freq All';
    'gap All';
    'dosage All';
    'slope Burst Max';
    'slope Burst Min';
    'slope Burst Max 15d';
    'slope Burst Min 15d';
    'slope Burst Sum 15d';
    'gap difference';
    'freq diff from gap summation';
    'slope burst max 7da';
   'slope burst max 7db';
   'slope burst min 7da';
   'slope burst min 7db';
   'slope burst sum 7da';
   'slope burst sum 7db';
    }
%code
for a =1:length(positive_index_all)
    count = a+1
    while count<=length(positive_index_all)
        count_1 = count+1
        while count_1 <=length(positive_index_all)
for i = 1:2
    if i ==1
        z = 1
    close all
    T = table(positive_index_all{a},positive_index_all{count},positive_index_all{count_1})
    T = renamevars(T,T.Properties.VariableNames{1},label{a})
    T = renamevars(T,T.Properties.VariableNames{2},label{count})
     T = renamevars(T,T.Properties.VariableNames{3},label{count_1})
    
    scatter3(T,label{a},label{count},label{count_1})
   
    
     xlabel(label{a});
       ylabel(label{count})
    hold on
    else
    
           T = table(negative_index_all{a},negative_index_all{count},negative_index_all{count_1})
    T = renamevars(T,T.Properties.VariableNames{1},label{a})
    T = renamevars(T,T.Properties.VariableNames{2},label{count})
     T = renamevars(T,T.Properties.VariableNames{3},label{count_1})
         scatter3(T,label{a},label{count},label{count_1})
      
       legend('High Dose','Low Dose')
        saveas(gcf,[imgdir '/Positive_only_highlow_' label{a} '_' label{count} '_' label{count_1} '.png'])
           saveas(gcf,[imgdir '/Positive_only_highlow_' label{a} '_' label{count} '_' label{count_1} '.fig'])   
    end
end
count_1 = count_1+1
        end

count = count+1;
        end
    

end
%% clustering

X = [Scattering_All{1}',freq_All{1}',gap_All{1}',slope_All{1}',dosage_All{1}',slope_15d_All{1}'];
X_temp = [Scattering_All{3}',freq_All{3}',gap_All{3}',slope_All{3}',dosage_All{3}',slope_15d_All{3}'];
X = [X;X_temp];
X = X(1:100,1:2)



T2 = clusterdata(X,30) 
final = [length(find(T2==1)),length(find(T2 == 2))]
gTruth = [ones(3401,1)',zeros(6499,1)'];
close all
scatter3(X(:,1),X(:,2),X(:,3),100,T2,'filled')
clust = kmeans(X,2,'distance','cityblock');

[silh3,h] = silhouette(X,clust,'cityblock');
xlabel('Silhouette Value')
ylabel('Cluster')
[idx ,C]= kmeans(X,2)
idx = kmeans(X,3)
%% plot
close all
temp = Scattering_All
h1 = histogram(temp{1},'Normalization','probability')
hold on
h2 = histogram(temp{3},'Normalization','probability')

h1.Normalization = 'probability';
h1.BinWidth = h2.BinWidth 
h2.Normalization = 'probability';

legend({'Positve','Negative'})


%% pca

positive_index_all = [
    zscore([Scattering_All{1},Scattering_All{3}],0,'all');
    zscore([slope_All{1},slope_All{3}],0,'all');
    zscore([slope_15d_All{1},slope_15d_All{3}],0,'all');
    zscore([freq_All{1},freq_All{3}],0,'all');
    zscore([gap_All{1},gap_All{3}],0,'all');
    zscore([dosage_All{1},dosage_All{3}],0,'all');
    zscore([slope_burst_max_All{1},slope_burst_max_All{3}],0,'all');
    zscore([slope_burst_min_All{1},slope_burst_min_All{3}],0,'all');
    zscore([slope_burst_max_15d{1},slope_burst_max_15d{3}],0,'all');
    zscore([slope_burst_min_15d{1},slope_burst_min_15d{3}],0,'all');
    zscore([slope_burst_sum_15d{1},slope_burst_sum_15d{3}],0,'all');
    zscore([gap_diff_All{1},gap_diff_All{3}],0,'all');
    zscore([freq_gap_summation{1},freq_gap_summation{3}],0,'all');
   zscore([slope_burst_max_7da{1},slope_burst_max_7da{3}],0,'all');
   zscore([slope_burst_max_7db{1},slope_burst_max_7db{3}],0,'all');
   zscore([slope_burst_min_7da{1},slope_burst_min_7da{3}],0,'all');
   zscore([slope_burst_min_7db{1},slope_burst_min_7db{3}],0,'all');
   zscore([slope_burst_sum_7da{1},slope_burst_sum_7da{3}],0,'all');
   zscore([slope_burst_sum_7db{1}, slope_burst_sum_7db{3}],0,'all');
    ]';
positive_index_all = [
    Scattering_All{1};
    slope_All{1};
    slope_15d_All{1};
    freq_All{1};
    gap_All{1};
    dosage_All{1};
    slope_burst_max_All{1};
    slope_burst_min_All{1};
    slope_burst_max_15d{1};
    slope_burst_min_15d{1};
    slope_burst_sum_15d{1};
    gap_diff_All{1};
    freq_gap_summation{1};
   slope_burst_max_7da{1};
   slope_burst_max_7db{1};
   slope_burst_min_7da{1};
   slope_burst_min_7db{1};
   slope_burst_sum_7da{1};
   slope_burst_sum_7db{1};
    ]';



positive_index_all = [All_raw_fix{:,1},All_raw_fix{:,2};All_raw_fix{:,3},All_raw_fix{:,4}];

positive_index_all = [All_raw_norm{:,1},All_raw_norm{:,2};All_raw_norm{:,3},All_raw_norm{:,4}];
positive_index_all = [
    Scattering_All{1};
    slope_All{1};
    
    freq_gap_summation{1};
   
   
    ]';
location = find(All_raw_fix{1}==-1)
location1 = find(All_raw_fix{2}==0)
[coeff,score,latent,tsquared,explained,mu] = pca(positive_index_all);
subplot(2,1,1)
scatter(score(1:3401,1),score(1:3401,2))
axis equal
xlabel('1st Principal Component')
ylabel('2nd Principal Component')
zlabel('3nd Principal Component')
subplot(2,1,2)
scatter3(positive_index_all(:,1),positive_index_all(:,2),positive_index_all(:,3))
hold on
scatter(score(3402:end,1),score(3402:end,2))
axis equal
xlabel('1st Principal Component')
ylabel('2nd Principal Component')

legend('Positive','Negative')
%% histogram in 3D
location = find(freq_All{1} ==0)
X = [slope_All{1}(location);dosage_All{1}(location)]';
hist3(X,'CDataMode','auto','FaceColor','interp','Nbins',[20,20])
colorbar
lm = mean(slope_15d_All{1}(find(dosage_All{1}<100)))
ls = std(slope_15d_All{1}(find(dosage_All{1}<100)))
hm = mean(slope_15d_All{1}(find(dosage_All{1}>100)))
hs = std(slope_15d_All{1}(find(dosage_All{1}>100)))

location = find(slope_burst_min_7da{1} <-0.01&slope_burst_min_7db{1}<-0.01)
  X = [slope_burst_min_7da{1};slope_burst_min_7db{1},dosage_All{1}]';
  scatter3(slope_burst_min_7da{1},slope_burst_min_7db{1},dosage_All{1},'.')
[idx,C] = kmeans(X,3)
figure
gscatter(X(:,1),X(:,2),idx,'bgm')
hold on
plot(C(:,1),C(:,2),'kx')
legend('Cluster 1','Cluster 2','Cluster 3','Cluster Centroid')
gscatter(X(:,1),X(:,2),idx)
hist3(X,'CDataMode','auto','FaceColor','interp','Nbins',[50,50])
 N = hist3(X,'CDataMode','auto','FaceColor','interp','Nbins',[70,30])
plot(N,'.')
temp = mean(N)
plot(linespace(1,320,30),temp)
 dosafe_All{1}


 %%
   X = [slope_burst_min_7da{1};slope_burst_min_7db{1};dosage_All{1}]';
   idx = dbscan(X,1,5); % The default distance metric is Euclidean distance

gscatter(X(:,1),X(:,2),idx);
title('DBSCAN Using Euclidean Distance Metric')
scatter3(X(:,1),X(:,2),X(:,3),'.')
 X = [slope_burst_min_7da{1};slope_burst_min_7db{1}]';
hist3(X,'CDataMode','auto','FaceColor','interp','Nbins',[100,100])
location = find(slope_burst_min_7da{1}<-0.01 & slope_burst_min_7db{1}<-0.01)
 X = [slope_burst_min_7da{1}(location);slope_burst_min_7db{1}(location)]';
hist3(X,'CDataMode','auto','FaceColor','interp','Nbins',[100,100])

%%

location = find(slope_burst_min_7da{1}<-0.01 | slope_burst_min_7db{1}<-0.01)
 X = [slope_burst_min_7da{1}(location);slope_burst_min_7db{1}(location)]';
scatter(X(:,1),X(:,2),'.')
hist3(X,'CDataMode','auto','FaceColor','interp','Nbins',[100,100])
 idx = dbscan(X,0.016,30); % The default distance metric is Euclidean distance
gscatter(X(:,1),X(:,2),idx);
minpts = 10;
kD = pdist2(X,X,'euc','Smallest',minpts);
plot(sort(kD(end,:)));
title('k-distance graph')
xlabel('Points sorted with 50th nearest distances')
ylabel('50th nearest distances')
grid
location1 = find(slope_burst_min_7da{1}>-0.01 & slope_burst_min_7db{1}>-0.01)






