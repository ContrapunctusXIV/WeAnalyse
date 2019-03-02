import os
try:
 import numpy
 import matplotlib
 import pyecharts
 import pyecharts_snapshot
 import jieba
except ImportError as e:
    os.popen("pip install -r requirement.txt", "r")
