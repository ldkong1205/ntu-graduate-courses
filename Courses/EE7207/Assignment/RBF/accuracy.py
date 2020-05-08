import numpy as np 

y = np.load('y.npy')
y_pred = np.load('y_pred.npy')
print('accurcy:', np.mean(np.around(np.squeeze(y_pred)) == y))