import math
import scipy as sp
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import sqlite3

path = input('Enter the path of new data: ')

df = pd.read_csv(path)
conn = sqlite3.connect('database.db')

df.to_sql('my_table', conn, if_exists='replace', index=False)

conn.close()

