% Create the Polar Histogram
p = polarhistogram(thetamax, 30);

% Professional Styling
p.FaceColor = [0, 0.4470, 0.7410]; % Academic blue
p.FaceAlpha = 0.6; 
p.EdgeColor = 'w'; % White edges help separate the bins visually

% Title - Include the Frequency units here for clarity
title({'Directional Distribution of Dosage Slopes (\theta_{max})', ...
       'Radial Axis: Frequency (UDS Events)'}, ...
      'FontSize', 13, 'FontWeight', 'bold');

% Format the Polar Axes
ax = gca;
ax.ThetaDir = 'clockwise'; 
ax.ThetaZeroLocation = 'top'; 
ax.FontSize = 10;
ax.GridAlpha = 0.3; % Subtle grid lines

% Alternative: Add a manual label to the radial axis
% This places the word "Frequency" along the 90-degree line
max_r = ax.RLim(2);
text(deg2rad(95), max_r * 0.7, 'Frequency', ...
    'FontSize', 10, 'FontWeight', 'bold', 'Rotation', -90);
shg