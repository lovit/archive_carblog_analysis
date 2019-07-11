import sys
sys.path.append('../')

import carblog_analyzer
print('Available carblog_analyzer == {}'.format(carblog_analyzer.__version__))

import os
carblog_dataset_path = '/mnt/sdc2/carblog_dataset/'
if os.path.exists(carblog_dataset_path):
    sys.path.append(carblog_dataset_path)
    print('Available carblog_dataset')
else:
    print('Check your carblog dataset or "git clone https://github.com/lovit/carblog_dataset.git"')
    print('After cloning, you must install the dataset. See more carblog_dataset README')

exp_name = 'demo_0'
model_dir = '/mnt/sdc2/carblog_analysis/{}/'.format(exp_name)
if not os.path.exists(model_dir):
    os.makedirs(model_dir)
