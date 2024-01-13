clc

rotx = 0.770031;
roty = 0;
rotz = -0.547733;

rotMat  = euler_rotation(rotx,roty,rotz);

camera_up_vector = rotMat * [0;1;0];
camera_target = rotMat * [0;0;-1];


fprintf("session.viewports['Viewport: 1'].view.setValues(nearPlane=0.25525, farPlane=0.409669, cameraPosition=(-3.044590, -4.635415, 5.748052), cameraUpVector=%s, cameraTarget=%s)\n", ...
                print_vector(camera_up_vector), ...
                print_vector(camera_target));
            

function str = print_vector(vector)
    str = '(';
    for i=1:numel(vector)
        str = strcat(str, sprintf('%.6f, ', vector(i)));
    end
    str = strcat(str(1:(end-2)), ')');
    fprintf("%s\n",str)
end




function R = euler_rotation(alpha, beta, gamma)
    % Input: alpha, beta, gamma are the rotation angles
%     alpha = alpha*pi/180;
%     beta = beta*pi/180;
%     gamma = gamma*pi/180;

    % Define the rotation matrices
    Rx = [1, 0, 0; 0, cos(alpha), -sin(alpha); 0, sin(alpha), cos(alpha)];
    Ry = [cos(beta), 0, sin(beta); 0, 1, 0; -sin(beta), 0, cos(beta)];
    Rz = [cos(gamma), -sin(gamma), 0; sin(gamma), cos(gamma), 0; 0, 0, 1];

    % Multiply the matrices
    R = Rz * Ry * Rx;
end

