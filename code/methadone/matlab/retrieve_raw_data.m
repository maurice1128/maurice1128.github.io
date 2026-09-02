clear all
clc
close all


%% read cell
data = []


C = readcell("/Users/mauricewang/Desktop/mesodon_code/2018-2022美沙冬每日劑量.xlsx","Sheet","2018-2020美沙冬","Range","A2:E1009075");
data = C(:,[2,3,5]);
data = cell2mat(data);
date = [C{:,1}];
date = date';
[B,I]=sort(data(:,1));
data_sort = data(I,:);
date_sort = date(I,:);
startpoint = 1;
date_all = date_sort;
data_all = data_sort;

%% 找出驗尿結果
C = readcell("/Users/mauricewang/Desktop/mesodon_code/2018-2022驗尿結果.xlsx","Sheet","驗尿結果","Range","A2:D56704");
date = cell2mat(C(:,2));
date = num2str(date);
data = C(:,[1,3,4]);
data = cell2mat(data);
a = find(data(:,2)==-1|data(:,3)==-1)
data(a,:) = [];
date(a,:) = [];

date_convert = {}
for i = 1:length(date)
year = date(i,1:3);
year =str2num(year)+1911;
month = str2num(date(i,4:5));
day = str2num(date(i,6:7));
date_convert = [date_convert;datetime(year,month,day)];
end

temp = []
parfor i = 1:length(data)
    i
    a =find(date_all==date_convert(i) & data_all(:,1)==data(i,1))
if isempty(a)==1
    temp = [temp,-1];
else
    temp = [temp,find(date_all==date_convert(i) & data_all(:,1)==data(i,1))];
end

end
data_urt = data;
date_urt = date_convert;
[B,I]=sort(data_urt (:,1));
data_urt   = data_urt(I,:);
date_urt  = date_urt(I,:);
a = find(data_urt(:,2)==0);
data_urt_amph = data_urt(a,:);
data_urt_amph(:,2) = [];
date_urt_amph = date_urt(a,:);
a = find(data_urt(:,2)==1);
data_urt_morph= data_urt(a,:);
data_urt_morph(:,2) = [];
date_urt_morph = date_urt(a,:);


%% 轉成cell，排序好，計算freq
clearvars -except data_all date_all data_urt_amph date_urt_amph data_urt_morph date_urt_morph
start = 1;
data = {};
namelist_All = [];
count = 1;
for i = 1:length(data_all)-1
    i
    if data_all(i,1)~=data_all(i+1,1)
        temp_data = data_all(start:i,:);
        temp_date = date_all(start:i,:);
        [B,I]=sort(temp_date);
        temp_date = temp_date(I);
        temp_data = temp_data(I,:);
%         freq = [];
%         freq(1:7) = -1;
%         for k = 8:length(temp_date)
%         freq = [freq,days(temp_date(k)-temp_date(k-7))/7];
%         end
%        
%         temp_data(:,end+1) = freq;
        data(count) = {{temp_data,temp_date}};
        count = count+1;   
        start = i+1;
        namelist_All = [namelist_All;temp_data(1,1)];
    end
end

data_all = data;
start = 1;
data = {};
count = 1;
namelist_amph = [];
for i = 1:length(data_urt_amph)-1
    if data_urt_amph(i,1)~=data_urt_amph(i+1,1)
        temp_data = data_urt_amph(start:i,:);
        temp_date = date_urt_amph(start:i,:);
        [B,I]=sort(temp_date);
        temp_date = temp_date(I);
        temp_data = temp_data(I,:);
%         freq = [];
%         freq(1:7) = -1;
%         for k = 8:length(temp_date)
%         freq = [freq,days(temp_date(k)-temp_date(k-7))/7];
%         end
%        
%         temp_data(:,end+1) = freq;
        data(count) = {{temp_data,temp_date}};
        count = count+1; 
        start = i+1;
        namelist_amph = [namelist_amph;temp_data(1,1)];
    end

end
data_urt_amph = data;

start = 1;
data = {};
count = 1;
namelist_morph = [];
for i = 1:length(data_urt_morph)-1
    if data_urt_morph(i,1)~=data_urt_morph(i+1,1)
        temp_data = data_urt_morph(start:i,:);
        temp_date = date_urt_morph(start:i,:);
        [B,I]=sort(temp_date);
        temp_date = temp_date(I);
        temp_data = temp_data(I,:);
%         freq = [];
%         freq(1:7) = -1;
%         for k = 8:length(temp_date)
%         freq = [freq,days(temp_date(k)-temp_date(k-7))/7];
%         end
%        
%         temp_data(:,end+1) = freq;
        data(count) = {{temp_data,temp_date}};
        count = count+1;  
        start = i+1
        namelist_morph = [namelist_morph;temp_data(1,1)];
    end

end
data_urt_morph = data;
clearvars -except data_urt_morph data_urt_amph data_all namelist_amph namelist_morph namelist_All
%% 找出目標病患
C = readcell("/Users/mauricewang/Desktop/mesodon_code/2年以上維持治療者_599人.xlsx","Sheet","名單","Range","A2:A600");

a = C(:,1);
datadouble = cell2mat(a);

list = {};
count = 0;
location = [];
for i = 1:length(C)
    location = [location , find(datadouble(i) == namelist_All)];
    
end

namelist_2y = namelist_All(location);
data_2y = data_all(location);

%%  畫圖
% patient_num = data()%病歷號碼
% doctor_say = %處方劑量
% patient_drink = %服用劑量
try
Folder_dir_PNG = '<LOCAL_DATA_PATH>'
Folder_dir_FIG = '<LOCAL_DATA_PATH>'
freq_days = 7;
for i = 1: length(data_2y)
    y_freq = [];
    patient_name = namelist_2y(i);
    x_all = data_2y{i}{2};
    y_ds = data_2y{i}{1}(:,2);
    y_pd = data_2y{i}{1}(:,3).*10;
    location = find(namelist_amph ==patient_name);
    x_freq = x_all(1):x_all(end);
    
    if length(x_freq)>6
    for k = 1:length(x_freq)-freq_days+1
        count_f=0
        for u = 0:freq_days-1
    if isempty(find(x_all==x_freq(k+u)))==0
count_f = count_f+1;
    end
    
        end
        y_freq = [y_freq,(count_f)];
    end


    x_freq(1:6) = [];
    
    else
        y_freq = zeros(1,length(x_freq))

    end

    if isempty(location)~=1
    x_amph = data_urt_amph{location}{2}
    y_amph = data_urt_amph{location}{1}(:,2)
    a = find(y_amph==1);
    positive_amph = x_amph(a);
    a = find(y_amph==0);
    negative_amph = x_amph(a)
    else 
        positive_amph = [];
        negative_amph = [];
    end


    location = find(namelist_morph ==patient_name);
    if isempty(location)~=1
    x_morph = data_urt_morph{location}{2}%紀錄驗尿時間
    y_morph = data_urt_morph{location}{1}(:,2)%紀錄驗尿是否為陰或陽性
    a = find(y_morph==1);
    positive_morph = x_morph(a);
    a = find(y_morph==0);
    negative_morph = x_morph(a);

    else 
        x_morph = [];
        y_morph = [];
        positive_morph = [];
        negative_morph = [];
    end

    a = [positive_amph;positive_morph]
    positive_all = unique(a);
    a = [negative_amph;negative_morph]
    negative_all = unique(a);
    [au,ia] = unique(a,'stable');
Same = ones(size(a));
Same(ia) = 0;

location = find(Same~=0)
negative_all = a(location)
% plot7,14,28 days
for pn_candidate = 1:length(x_morph)
    close all
    count_plot = 0
for date_plot_num = [7,14,28]
    count_plot = count_plot+1;

    x_all_temp = [];
    x_freq_temp= [] ;
    y_pd_temp=[];
    y_ds_temp=[];
    y_freq_temp=[];
    
    for z = -date_plot_num:-1
    location = find(x_all==x_morph(pn_candidate)+z);
    if isempty(location)~=1
    x_all_temp = [x_all_temp,x_all(location)];
    y_pd_temp=[y_pd_temp,y_pd(location)];
    y_ds_temp=[y_ds_temp,y_ds(location)];
    end
    location = find(x_freq == x_morph(pn_candidate)+z);
    if isempty(location)~=1;
    x_freq_temp = [x_freq_temp,x_freq(location)];
    y_freq_temp=[y_freq_temp,y_freq(location)];
    end
    

    end


for z = 0:date_plot_num
    location = find(x_all==x_morph(pn_candidate)+z);
    if isempty(location)~=1
    x_all_temp = [x_all_temp,x_all(location)];
    y_pd_temp=[y_pd_temp,y_pd(location)];
    y_ds_temp=[y_ds_temp,y_ds(location)];
    end
    location = find(x_freq == x_morph(pn_candidate)+z);
    if isempty(location)~=1
    x_freq_temp = [x_freq_temp,x_freq(location)];
    y_freq_temp=[y_freq_temp,y_freq(location)];
    end

end

if count_plot == 1
figure('units','normalized','outerposition',[0 0 1 1])
end

 subplot(3,1,count_plot)
    if isempty(x_all_temp) ~=1
    plot(x_all_temp,y_pd_temp,'-o','LineWidth',2,'Color',"#0072BD")
    hold on
    plot(x_all_temp,y_ds_temp,'--','LineWidth',2,'Color',"#D95319")
    ylim([0,max(y_ds_temp)*1.35])
    xlim([x_morph(pn_candidate)-date_plot_num ,x_morph(pn_candidate)+date_plot_num ])

    yyaxis right
    plot(x_freq_temp,y_freq_temp,'LineWidth',2,'Color',"#EDB120")
    ylim([-30,10])
    
    hold on
    end

grid on
if y_morph(pn_candidate)==1
    Morph_state = 1
xline(positive_morph,'-k',{'Morphine Postive'},'LineWidth',1.2)
else
    Morph_state = 0
    xline(negative_morph,':',{'Morphine Negative'},'LineWidth',1.5)
end
legend({'服藥劑量(cc*10)','處方劑量(mg)','服用頻率/7天'},'FontSize',12,'Location','northeastoutside')

title(['Patient ' num2str(patient_name) ' Morphine Result No.' num2str(pn_candidate) ' in ' num2str(date_plot_num*2+1) ' days'],'FontSize',20)

end
differencial = 0;
for dif = 1:length(y_pd_temp)-1
differencial  = differencial + abs(y_pd_temp(dif+1)-y_pd_temp(dif));
end
differencial = differencial/date_plot_num;
% Dosage->Difference plot
if max(y_pd_temp)>=100
    if Morph_state ==1
saveas(gcf,[Folder_dir_PNG '/Dosage_Differnece/Positive/' 'Dosage_High_Variation_' num2str(differencial) '_Patient_' num2str(patient_name) '_Result_' num2str(pn_candidate) '.png'] ,'png')
saveas(gcf,[Folder_dir_PNG '/Doseage_Patient_Difference/Positive/' 'Dosage_High_Patient_' num2str(patient_name) '_Variation_' num2str(differencial) '_Result_' num2str(pn_candidate) '.png' ] ,'png')
saveas(gcf,[Folder_dir_FIG '/Dosage_Differnece/Positive/' 'Dosage_High_Variation_' num2str(differencial) '_Patient_' num2str(patient_name) '_Result_' num2str(pn_candidate) '.fig'] ,'fig')
saveas(gcf,[Folder_dir_FIG '/Doseage_Patient_Difference/Positive/' 'Dosage_High_Patient_' num2str(patient_name) '_Variation_' num2str(differencial) '_Result_' num2str(pn_candidate) '.fig' ] ,'fig')

    elseif Morph_state ==0
        saveas(gcf,[Folder_dir_PNG '/Dosage_Differnece/Negative/' 'Dosage_High_Variation_' num2str(differencial) '_Patient_'  num2str(patient_name) '_Result_' num2str(pn_candidate) '.png'] ,'png')
    saveas(gcf,[Folder_dir_PNG '/Doseage_Patient_Difference/Negative/' 'Dosage_High_Patient_' num2str(patient_name) '_Variation_' num2str(differencial) '_Result_' num2str(pn_candidate) '.png'] ,'png')
saveas(gcf,[Folder_dir_FIG '/Dosage_Differnece/Negative/' 'Dosage_High_Variation_' num2str(differencial) '_Patient_'  num2str(patient_name) '_Result_' num2str(pn_candidate) '.fig'] ,'fig')
    saveas(gcf,[Folder_dir_FIG '/Doseage_Patient_Difference/Negative/' 'Dosage_High_Patient_' num2str(patient_name) '_Variation_' num2str(differencial) '_Result_' num2str(pn_candidate) '.fig'] ,'fig')

    end
else
    if Morph_state ==1
saveas(gcf,[Folder_dir_PNG '/Dosage_Differnece/Positive/' 'Dosage_Low_Variation_' num2str(differencial) '_Patient_'  num2str(patient_name) '_Result_' num2str(pn_candidate) '.png'] ,'png')
    saveas(gcf,[Folder_dir_PNG '/Doseage_Patient_Difference/Positive/' 'Dosage_Low_Patient_' num2str(patient_name) '_Variation_' num2str(differencial) '_Result_' num2str(pn_candidate) '.png'] ,'png')
saveas(gcf,[Folder_dir_FIG '/Dosage_Differnece/Positive/' 'Dosage_Low_Variation_' num2str(differencial) '_Patient_'  num2str(patient_name) '_Result_' num2str(pn_candidate) '.fig'] ,'fig')
    saveas(gcf,[Folder_dir_FIG '/Doseage_Patient_Difference/Positive/' 'Dosage_Low_Patient_' num2str(patient_name) '_Variation_' num2str(differencial) '_Result_' num2str(pn_candidate) '.fig'] ,'fig')

    elseif Morph_state ==0
        saveas(gcf,[Folder_dir_PNG '/Dosage_Differnece/Negative/' 'Dosage_Low_Variation_' num2str(differencial) '_Patient_'  num2str(patient_name) '_Result_' num2str(pn_candidate) '.png'] ,'png')
        saveas(gcf,[Folder_dir_PNG '/Doseage_Patient_Difference/Negative/' 'Dosage_Low_Patient_' num2str(patient_name) '_Variation_' num2str(differencial) '_Result_' num2str(pn_candidate) '.png'] ,'png')
saveas(gcf,[Folder_dir_FIG '/Dosage_Differnece/Negative/' 'Dosage_Low_Variation_' num2str(differencial) '_Patient_'  num2str(patient_name) '_Result_' num2str(pn_candidate) '.fig'] ,'fig')
        saveas(gcf,[Folder_dir_FIG '/Doseage_Patient_Difference/Negative/' 'Dosage_Low_Patient_' num2str(patient_name) '_Variation_' num2str(differencial) '_Result_' num2str(pn_candidate) '.fig'] ,'fig')

end
end
% Difference plot and patient->Difference plot
if Morph_state == 1
saveas(gcf,[Folder_dir_PNG '/Differnece/Positive/' 'Variation_' num2str(differencial) '_Patient_' num2str(patient_name) '_Result_' num2str(pn_candidate) '.png'] ,'png')
saveas(gcf,[Folder_dir_PNG '/Patient_Difference/Positive/' 'Patient_' num2str(patient_name) '_Variation_' num2str(differencial) '_Result_' num2str(pn_candidate) '.png'] ,'png')
saveas(gcf,[Folder_dir_FIG '/Differnece/Positive/' 'Variation_' num2str(differencial) '_Patient_' num2str(patient_name) '_Result_' num2str(pn_candidate) '.fig'] ,'fig')
saveas(gcf,[Folder_dir_FIG '/Patient_Difference/Positive/' 'Patient_' num2str(patient_name) '_Variation_' num2str(differencial) '_Result_' num2str(pn_candidate) '.fig'] ,'fig')

else
saveas(gcf,[Folder_dir_PNG '/Differnece/Negative/' 'Variation_' num2str(differencial) '_Patient_' num2str(patient_name) '_Result_' num2str(pn_candidate) '.png'] ,'png')
saveas(gcf,[Folder_dir_PNG '/Patient_Difference/Negative/' 'Patient_' num2str(patient_name) '_Variation_' num2str(differencial) '_Result_' num2str(pn_candidate) '.png'] ,'png')
saveas(gcf,[Folder_dir_FIG '/Differnece/Negative/' 'Variation_' num2str(differencial) '_Patient_' num2str(patient_name) '_Result_' num2str(pn_candidate) '.fig'] ,'fig')
saveas(gcf,[Folder_dir_FIG '/Patient_Difference/Negative/' 'Patient_' num2str(patient_name) '_Variation_' num2str(differencial) '_Result_' num2str(pn_candidate) '.fig'] ,'fig')

end



end


%%
% 
%     close all
%     figure('units','normalized','outerposition',[0 0 1 1])
%     plot(x_all,y_pd,'-o','LineWidth',2,'Color',"#0072BD")
%     hold on
%     plot(x_all,y_ds,'--','LineWidth',2,'Color',"#D95319")
%     ylim([0,max(y_ds)*1.35])
% 
%     yyaxis right
%     plot(x_freq,y_freq,'LineWidth',2,'Color',"#EDB120")
%     ylim([-30,10])
% 
% 
% 
%     if isempty(positive_morph)~=1
%     xline(positive_morph,'-k',{'Morphine Postive'},'LineWidth',1.2)
%     end
%     if isempty(negative_morph)~=1
%     xline(negative_morph,':',{'Morphine Negative'},'LineWidth',1.5)
%     end
%     title(['Patient ' num2str(patient_name) ' Morphine Result'],'FontSize',20)
%     hold on
% legend({'服藥劑量(cc*10)','處方劑量(mg)','服用頻率/7天'},'FontSize',15)
% grid on
% %savefig(['<LOCAL_DATA_PATH>' num2str(patient_name) '.fig'])
% saveas(gcf,['<LOCAL_DATA_PATH>' num2str(patient_name)],'png')
% 
%     close all
%     figure('units','normalized','outerposition',[0 0 1 1])
%     plot(x_all,y_pd,'-o','LineWidth',2,'Color',"#0072BD")
%     hold on
%     plot(x_all,y_ds,'--','LineWidth',2,'Color',"#D95319")
%     ylim([0,max(y_ds)*1.35])
% 
%     yyaxis right
%     plot(x_freq,y_freq,'LineWidth',2,'Color',"#EDB120")
%     ylim([-30,10])
%     if isempty(positive_amph)~=1
%     xline(positive_amph,'-',{'Amphetamine Postive'},'LineWidth',2)
%     end
%      if isempty(negative_amph)~=1
%     xline(negative_amph,':',{'Amphetamine Negative'})
%      end
%     title(['Patient ' num2str(patient_name) ' Amphetamine Result'],'FontSize',20)
%     hold on
% legend({'服藥劑量(cc*10)','處方劑量(mg)','服用頻率/7天'},'FontSize',15)
% grid on
% %savefig(['<LOCAL_DATA_PATH>' num2str(patient_name) '.fig'])
% saveas(gcf,['<LOCAL_DATA_PATH>' num2str(patient_name)] ,'png')
% 
% 
% 
%     close all
%     figure('units','normalized','outerposition',[0 0 1 1])
%     plot(x_all,y_pd,'-o','LineWidth',2,'Color',"#0072BD")
%     hold on
%     plot(x_all,y_ds,'--','LineWidth',2,'Color',"#D95319")
%     ylim([0,max(y_ds)*1.35])
% 
%     yyaxis right
%     plot(x_freq,y_freq,'LineWidth',2,'Color',"#EDB120")
%     ylim([-30,10])
%     if isempty(positive_all)~=1
%     xline(positive_all,'-',{'Either Postive'},'LineWidth',2)
%     end
%     if isempty(negative_all)~=1
%     xline(negative_all,':',{'All Negative'})
%     end
%     title(['Patient ' num2str(patient_name) ' All Result'],'FontSize',20)
%     hold on
%     grid on
% legend({'服藥劑量(cc*10)','處方劑量(mg)','服用頻率/7天'},'FontSize',15)
% %savefig(['<LOCAL_DATA_PATH>' num2str(patient_name) '.fig'])
% saveas(gcf,['<LOCAL_DATA_PATH>' num2str(patient_name)  ],'png')



end
gmail.send_mail_from_maurice_nycu ('mauricewang1128@gmail.com' ,'mesodone_finished', 'yeah~')

catch ME
    
     gmail.send_mail_from_maurice_nycu ('mauricewang1128@gmail.com' ,'error4mesodone', 'error_occur')
    rethrow(ME)
end





%% create value for analysis

C = readcell("/Users/mauricewang/Desktop/mesodon_code/Excel/2年以上維持治療者_599人.xlsx","Sheet","名單","Range","A2:A600");

a = C(:,1);
datadouble = cell2mat(a);

list = {};
count = 0;
location = [];
for i = 1:length(C)
    location = [location , find(datadouble(i) == namelist_All)];
    
end

namelist_2y = namelist_All(location);
data_2y = data_all(location);

freq_days = 7;

 positive_ds= [];
 positive_pd = [];
 negative_ds= [];
 negative_pd = [];
 positive_header = [];
 negative_header = [];
 positive_date=[];
 negative_date = [];
for i = 1: length(data_2y)
    i
    y_freq = [];
    patient_name = namelist_2y(i);
    x_all = data_2y{i}{2};
    y_ds = data_2y{i}{1}(:,2);
    y_pd = data_2y{i}{1}(:,3).*10;
    location = find(namelist_amph ==patient_name);
    x_freq = x_all(1):x_all(end);
    
    if length(x_freq)>6
    for k = 1:length(x_freq)-freq_days+1
        count_f=0;
        for u = 0:freq_days-1;
    if isempty(find(x_all==x_freq(k+u)))==0
count_f = count_f+1;
    end
    
        end
        y_freq = [y_freq,(count_f)];
    end


    x_freq(1:6) = [];
    
    else
        y_freq = zeros(1,length(x_freq));

    end

    if isempty(location)~=1
    x_amph = data_urt_amph{location}{2};
    y_amph = data_urt_amph{location}{1}(:,2);
    a = find(y_amph==1);
    positive_amph = x_amph(a);
    a = find(y_amph==0);
    negative_amph = x_amph(a);
    else 
        positive_amph = [];
        negative_amph = [];
    end


    location = find(namelist_morph ==patient_name);
    if isempty(location)~=1
    x_morph = data_urt_morph{location}{2};%紀錄驗尿時間;
    y_morph = data_urt_morph{location}{1}(:,2);%紀錄驗尿是否為陰或陽性;
    a = find(y_morph==1);
    positive_morph = x_morph(a);
    a = find(y_morph==0);
    negative_morph = x_morph(a);

    else 
        x_morph = [];
        y_morph = [];
        positive_morph = [];
        negative_morph = [];
    end

    a = [positive_amph;positive_morph];
    positive_all = unique(a);
    a = [negative_amph;negative_morph];
    negative_all = unique(a);
    [au,ia] = unique(a,'stable');
Same = ones(size(a));
Same(ia) = 0;

location = find(Same~=0);
negative_all = a(location);
% plot7,14,28 days
for pn_candidate = 1:length(x_morph)
    close all
    count_plot = 0;
    date_record = [];
for date_plot_num = [7,14,28]
    count_plot = count_plot+1;

    x_all_temp = [];
    x_freq_temp= [] ;
    y_pd_temp=[];
    y_ds_temp=[];
    y_freq_temp=[];
    
    for z = -date_plot_num:-1
    location = find(x_all==x_morph(pn_candidate)+z);
    if isempty(location)~=1
    x_all_temp = [x_all_temp,x_all(location)];
    y_pd_temp=[y_pd_temp,y_pd(location)];
    y_ds_temp=[y_ds_temp,y_ds(location)];
    end
      if date_plot_num ==28 & isempty(location)~=1
        date_record = [date_record,1];
    elseif date_plot_num ==28 & isempty(location)==1
        date_record = [date_record,-1];
    end
    location = find(x_freq == x_morph(pn_candidate)+z);
    if isempty(location)~=1;
    x_freq_temp = [x_freq_temp,x_freq(location)];
    y_freq_temp=[y_freq_temp,y_freq(location)];
    end
    

    end


for z = 0:date_plot_num
    location = find(x_all==x_morph(pn_candidate)+z);
    if isempty(location)~=1
    x_all_temp = [x_all_temp,x_all(location)];
    y_pd_temp=[y_pd_temp,y_pd(location)];
    y_ds_temp=[y_ds_temp,y_ds(location)];
    end
     if date_plot_num ==28 & isempty(location)~=1
        date_record = [date_record,1];
    elseif date_plot_num ==28 & isempty(location)==1
        date_record = [date_record,-1];
    end
    location = find(x_freq == x_morph(pn_candidate)+z);
    if isempty(location)~=1
    x_freq_temp = [x_freq_temp,x_freq(location)];
    y_freq_temp=[y_freq_temp,y_freq(location)];
    end

   
end

end
pd = [];
ds = [];
count = 0;
for special = 1:57
    
    if date_record(special) == -1
        pd=[pd,-1];
        ds = [ds,-1];
    else
        count = count+1;
        pd = [pd,y_pd_temp(count)];
        ds = [ds,y_ds_temp(count)];
    end
end


if y_morph(pn_candidate)==1
    
    positive_pd = [positive_pd;pd];
    positive_ds = [positive_ds;ds];
    positive_header = [positive_header;patient_name,pn_candidate];
    positive_date = [positive_date;x_morph(pn_candidate)];
else
    negative_pd = [negative_pd;pd];
    negative_ds = [negative_ds;ds];
    negative_header = [negative_header;patient_name,pn_candidate];
    negative_date = [negative_date ;x_morph(pn_candidate)];
end

end
end
%save('aim.mat','negative_pd','negative_ds','negative_header','positive_date','negative_date','-append')
save('aim2.mat','All_fill_date','-append')
%% put in order
list_sorted = {};


for i = 1:length(list)
    a = [];
    for date = 1:length(list{i}(:,1))
    a = [a,list{i}{date,1}];
    end

    [B,I] = sort(a);
    list_sorted{i} = list{i}(I,:);

end




save('list_sorted.mat','list_sorted')



