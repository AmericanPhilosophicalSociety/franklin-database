# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 10:09:08 2022

@author: dnelson
"""

import os

path = 'static\js'
f = []
for (dirpath, dirnames, filenames) in os.walk(path):
    f += [os.path.join(dirpath, file) for file in filenames]

print(f)
