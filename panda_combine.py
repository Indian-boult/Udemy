#!/usr/bin/env python

import pandas as pd
import glob

all_files = glob.glob('./out'+ "/*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)

frame = pd.concat(li, axis=0, ignore_index=True)





