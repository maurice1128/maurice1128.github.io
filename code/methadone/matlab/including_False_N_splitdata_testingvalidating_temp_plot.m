%% Optimized Plotting for Academic Publication
aim_option = {pca_1;pca_2;pca_3;pca_4;pca_5;xy{1,1}';xy{1,3}';xy{1,5}';xy{3,1}';xy{3,3}';xy{3,5}';xy{5,1}';xy{5,3}';xy{5,5}';xy{7,1}';xy{7,3}';xy{7,5}'};
name = {'pca 1';'pca 2';'pca 3';'pca 4';'pca 5';'7d 1';'7d 2';'7d 3';'7d 4';'7d 5';'7d 6';'7d 7';'7d 8';'7d 9';'7d 10';'7d 11';'7d 12'};

All_fill_norm_truen_pd = All_fill_norm{3}(:,:);
All_fill_norm_truen_ds = All_fill_norm{4}(:,:);

for special = 1:17
    figure('Color', 'w'); % 設定背景為白色
    aim = aim_option{special};
    
    if isempty(aim), continue; end % 防止空群組報錯

    % --- 繪製個別路徑 (灰色, 降低顯著度) ---
    if special > 5
        % 7天窗口數據 (Day 22-36)
        plot(All_fill_norm_truen_pd(aim, 22:36)', 'Color', [0.8 0.8 0.8], 'LineWidth', 0.5, 'LineStyle', '-');
        hold on;
    else
        % 28天 PCA 窗口數據 (Day 1-57)
        subplot(2,1,1);
        plot(All_fill_norm_truen_pd(aim, 1:57)', 'Color', [0.8 0.8 0.8], 'LineWidth', 0.5);
        hold on;
        
        subplot(2,1,2);
        plot(All_fill_norm_truen_ds(aim, 1:57)', 'Color', [0.8 0.8 0.8], 'LineWidth', 0.5);
        hold on;
    end

    % --- 繪製平均線 (加粗, 鮮艷顏色) ---
    if special > 5
        % 繪製 7-day 平均線
        m_pd = mean(All_fill_norm_truen_pd(aim, 22:36), 1);
        plot(m_pd, 'Color', '#d62728', 'LineWidth', 3); % 使用專業紅色
        xline(8, '--k', 'UDS Event', 'LabelVerticalAlignment', 'bottom'); % 標註驗尿當天
        
        % 固定 Y 軸 (建議根據資料分佈調整，例如 0 到 3)
        ylim([0 2]); 
        ylabel('Normalized Intake Ratio');
        xlabel('Days (Centered at UDS)');
    else
        % 繪製 28-day PCA 平均線
        subplot(2,1,1);
        m_pd_long = mean(All_fill_norm_truen_pd(aim, :), 1);
        plot(m_pd_long, 'Color', '#1f77b4', 'LineWidth', 3); % 使用專業藍色
        xline(29, '--k', 'UDS Event');
        ylim([0 2]); % 固定 Y 軸
        ylabel('Intake Ratio');
        
        subplot(2,1,2);
        m_ds_long = mean(All_fill_norm_truen_ds(aim, :), 1);
        plot(m_ds_long, 'Color', '#2ca02c', 'LineWidth', 3); % 使用專業綠色
        ylim([0 2]); % 固定 Y 軸
        ylabel('Prescription Ratio');
        xlabel('Days (-28 to +28)');
    end

    % --- 圖表裝飾 ---
    sgtitle([name{special} ' (Distribution: ' num2str(100*length(aim)/length_negative, '%.2f') '%)'], 'FontSize', 14, 'FontWeight', 'bold');
    
    % 存檔 (選擇高解析度格式)
    saveas(gcf, [name{special} '_optimized.png']);
    close all;
end