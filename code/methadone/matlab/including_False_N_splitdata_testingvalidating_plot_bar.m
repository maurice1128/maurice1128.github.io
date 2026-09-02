%% Updated Data Input based on Final Statistical Analysis (2025-12-31)
% Data Source: Taiwan NHI Database (N = 8,540 total UDS events)

categories = {'Cat 1', 'Cat 2', 'Cat 3', 'Cat 4', 'Cat 5', 'Cat 6', 'Cat 7', ...
              'Cat 8', 'Cat 9', 'Cat 10', 'Cat 11', 'Cat 12', 'Cat 13', ...
              'Cat 14', 'Cat 15', 'Cat 16', 'Cat 17', 'Attendance'};

% Updated P/N Ratios
pn_ratios = [1.3327, 1.7932, 1.7018, 1.5524, 1.1347, 1.0585, 0.5783, ...
             0.4447, 0.5893, 1.3449, 1.3589, 1.2916, 0.8033, ...
             0.5405, 0.7854, 1.1938, 1.5353, 0.7217];
         
% Updated P-values
p_values = [0.0352, 0.0001, 0.0001, 0.0007, 0.1895, 0.6395, 0.0001, ...
            0.0001, 0.0001, 0.0024, 0.0001, 0.0225, 0.0001, ...
            0.0001, 0.0092, 0.0864, 0.0022, 0.0001];


%% Sorting Logic (for academic clarity)
[sorted_ratios, idx] = sort(pn_ratios, 'ascend');
sorted_cats = categories(idx);
sorted_p = p_values(idx);

%% Define Professional Colors
colors = zeros(length(sorted_ratios), 3);
for i = 1:length(sorted_ratios)
    if sorted_p(i) < 0.05
        if sorted_ratios(i) > 1.0
            colors(i, :) = [0.85, 0.33, 0.10]; % Red (High Risk)
        else
            colors(i, :) = [0.47, 0.67, 0.19]; % Green (Safe)
        end
    else
        colors(i, :) = [0.70, 0.70, 0.70]; % Grey (Non-Significant)
    end
end

%% Plotting
figure('Color', 'w', 'Position', [100 100 900 600]);
b = barh(sorted_ratios, 'FaceColor', 'flat');
b.CData = colors;

% Add baseline at 1.0
xline(1.0, '--k', 'LineWidth', 1.5, 'Alpha', 0.5);
text(1.02, length(sorted_ratios), 'Neutral Baseline', 'FontWeight', 'bold');

% Formatting
set(gca, 'YTick', 1:length(sorted_cats), 'YTickLabel', sorted_cats, 'FontSize', 11);
xlabel('Positive/Negative (P/N) Ratio', 'FontSize', 13, 'FontWeight', 'bold');
ylabel('Behavioral Usage Category', 'FontSize', 13, 'FontWeight', 'bold');
title('Primary Risk Analysis: Morphine Relapse Predictive Value by Cluster', 'FontSize', 15);
grid on; ax = gca; ax.XGrid = 'on'; ax.YGrid = 'off';

%% Add Significance Markers (Stars)
for i = 1:length(sorted_ratios)
    if sorted_p(i) <= 0.0001, txt = '****';
    elseif sorted_p(i) < 0.001, txt = '***';
    elseif sorted_p(i) < 0.01, txt = '**';
    elseif sorted_p(i) < 0.05, txt = '*';
    else, txt = 'ns'; end
    text(sorted_ratios(i) + 0.03, i, txt, 'VerticalAlignment', 'middle', 'FontSize', 10);
end

% Save figure for publication
% exportgraphics(gcf, 'MMT_Primary_Risk_Graph.png', 'Resolution', 300);