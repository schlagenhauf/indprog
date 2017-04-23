function [inPortSpecs, outPortSpecs, paramSpecs] = matlabTemplate(inFds, outFds, params)

if nargin == 0
  inPortSpecs = {'in1','in2'};
  outPortSpecs = {'out1', 'out2'};
  paramSpecs = {'param1', 'param2'};
  return
end

inFds
outFds
%fileID = cell2mat(inFds(1))
%str = fread(fileID)
%fprint('Matlab received %s', str);
%fwrite(outFds(1), str);

pause(10)


end
