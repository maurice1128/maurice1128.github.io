%% Academic Panel Generation: Manual Positioning with Left-Aligned Titles
% Data Source: Taiwan NHI Database (n=4,084 UDS Events) 

% 1. Mapping Configuration
cat_to_idx = zeros(17,1);
cat_to_idx(13:17) = 1:5; % PCA 1-5 maps to Cat 13-17
cat_to_idx(1:12) = 6:17; % 7d 1-12 maps to Cat 1-12 
% 2. Updated P/N Ratios
% Order: Cat 1 to Cat 17
pn_ratios = [1.3327, 1.7932, 1.7018, 1.5524, 1.1347, 1.0585, 0.5783, ...
             0.4447, 0.5893, 1.3449, 1.3589, 1.2916, 0.8033, ...
             0.5405, 0.7854, 1.1938, 1.5353];

%% Corrected Risk Stratification: Moving Significant Clusters out of Neutral
% Data Source: Updated N = 8,540 total UDS events

% Panel A: High Risk (Significant and P/N > 1.1)
% Moving Cat 1, Cat 10, Cat 11, and Cat 12 here because they all passed p-value tests.
high_risk_cats = [2, 3, 4, 17, 10, 11, 1, 12]; 

% Panel B: Safe Patterns (Significant and P/N < 0.9)
% Adding Cat 13 and Cat 15 here because they passed the p-value test with low P/N ratios.
safe_pattern_cats = [8, 14, 7, 9, 13, 15];        

% Panel C: Neutral / Non-Significant (p > 0.05)
% These categories failed to reach statistical significance regardless of P/N ratio.
neutral_cats = [5, 6, 16];

plot_groups = {high_risk_cats, safe_pattern_cats, neutral_cats};
panel_names = {'Panel A High Risk', 'Panel B Safe', 'Panel C Appendix'};
colors = {'#d62728', '#2ca02c', '#7f7f7f'}; 

% 3. Generation Loop
for g = 1:length(plot_groups)
    current_cats = plot_groups{g};
    num_plots = length(current_cats);
    cols = 2;
    rows = ceil(num_plots / cols);
    
    fig = figure('Color', 'w', 'Units', 'normalized', 'Position', [0.05 0.05 0.6 0.9]);
    
    for i = 1:num_plots
        cat_num = current_cats(i);
        special_idx = cat_to_idx(cat_num); 
        aim = aim_option{special_idx};
        if isempty(aim), continue; end
        
        r = ceil(i/cols); c = mod(i-1, cols) + 1;
        w = 0.4; h = 0.8 / rows;
        x_pos = 0.08 + (c-1) * 0.48;
        y_pos = 0.9 - r * h;
        
        if special_idx <= 5 % --- PCA Categories (Cat 13-17): Subplots ---
            % Intake Subplot
            ax1 = axes('Position', [x_pos, y_pos + h*0.5, w, h*0.4]);
            plot(ax1, All_fill_norm_truen_pd(aim, 1:57)', 'Color', [0.85 0.85 0.85], 'LineWidth', 0.4);
            hold(ax1, 'on');
            plot(ax1, mean(All_fill_norm_truen_pd(aim, :), 1), 'Color', colors{g}, 'LineWidth', 2.5);
            xline(ax1, 29, '--k');
            ylim(ax1, [0.5 1.5]); grid(ax1, 'on'); set(ax1, 'FontSize', 8); ylabel(ax1, 'Intake');
            
            % LEFT-ALIGNED TITLE for PCA Intake
            t1 = title(ax1, ['Cat ' num2str(cat_num) ' Intake (P/N: ' num2str(pn_ratios(cat_num)) ')'], ...
                 'FontSize', 9, 'FontWeight', 'bold');
            t1.HorizontalAlignment = 'left';
            t1.Units = 'normalized';
            t1.Position = [0, 1.05, 0]; % Aligns with X=0 (left edge of axes)

            % Prescription Subplot
            ax2 = axes('Position', [x_pos, y_pos, w, h*0.4]);
            plot(ax2, All_fill_norm_truen_ds(aim, 1:57)', 'Color', [0.85 0.85 0.85], 'LineWidth', 0.4);
            hold(ax2, 'on');
            plot(ax2, mean(All_fill_norm_truen_ds(aim, :), 1), 'Color', '#7f7f7f', 'LineWidth', 2);
            xline(ax2, 29, '--k');
            ylim(ax2, [0.5 1.5]); grid(ax2, 'on'); set(ax2, 'FontSize', 8);
            ylabel(ax2, 'Rx'); xlabel(ax2, '28-Day Window');
            
        else % --- 7-Day Window Categories (Cat 1-12) ---
            ax = axes('Position', [x_pos, y_pos + h*0.1, w, h*0.8]);
            plot(ax, All_fill_norm_truen_pd(aim, 22:36)', 'Color', [0.85 0.85 0.85], 'LineWidth', 0.5);
            hold(ax, 'on');
            m_line = mean(All_fill_norm_truen_pd(aim, 22:36), 1);
            plot(ax, m_line, 'Color', colors{g}, 'LineWidth', 2.5);
            xline(ax, 8, '--k', 'UDS', 'LabelVerticalAlignment', 'bottom', 'FontSize', 8);
            ylim(ax, [0.5 1.5]); grid(ax, 'on'); set(ax, 'FontSize', 9);
            ylabel(ax, 'Intake Ratio'); xlabel(ax, '7-Day Window');
            
            % LEFT-ALIGNED TITLE for 7-Day
            t = title(ax, ['Cat ' num2str(cat_num) ' (P/N: ' num2str(pn_ratios(cat_num)) ')'], ...
                'FontSize', 11, 'FontWeight', 'bold');
            t.HorizontalAlignment = 'left';
            t.Units = 'normalized';
            t.Position = [0, 1.02, 0];
        end
    end
    
    % Panel Header
    annotation('textbox', [0, 0.92, 1, 0.08], 'String', panel_names{g}, ...
        'EdgeColor', 'none', 'HorizontalAlignment', 'center', 'FontSize', 20, 'FontWeight', 'bold');
    
    % Save high-resolution file
    exportgraphics(fig, [panel_names{g} '.png'], 'Resolution', 300);
end