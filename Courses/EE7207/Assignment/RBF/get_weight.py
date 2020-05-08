import numpy as np 
import h5py

f = h5py.File('my_model_weights.h5','r')
weights = f['dense_1']['dense_1/kernel:0'].value
print(weights)