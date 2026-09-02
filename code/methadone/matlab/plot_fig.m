% clear all
% clc
% close all
% 
% matdir = ''
% load(matdir)


patient_num = [1:538]


for i = patient_num %:length(list_sorted)
    data = cell2mat(list_sorted{i}(:,4));
    a = [];
    for date = 1:length(list_sorted{i}(:,1))
    a = [a,list_sorted{i}{date,1}];
    end

plot(a,data)
saveas(gcf,['/Users/mauricewang/Desktop/mesodon_code/patient_png_ver1/patient_' num2str(list_sorted{i}{1,2}) '.png'])
close all
i
end


