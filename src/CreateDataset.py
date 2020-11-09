#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 22:12:48 2020

@author: Dani
"""

import pandas as pd
import numpy as np
import path 

file_path = path.Path(__file__).parent / "../data/test.csv"
with file_path.open() as dataset_file:
    df = pd.read_csv(dataset_file) 