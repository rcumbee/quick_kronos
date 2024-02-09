import sys
import os
import pandas as pd
from matplotlib import pyplot as plt
from functools import reduce

def result_file_dir(ion, ioniz, neutral,method, Energy):
	dir = f"./Results/{ion}{ioniz}+{neutral}/{method}/{Energy}"
	if not os.path.exists(dir):
		print ('Does not exist')
	print (dir)
	return dir

dir = "./cxdatabase-master/Projectile_Ions/O/Charge/6/Targets/H/"

f1 = "table2.dat"
df1_head = ['(eV/u)','Total','n=4','n=5','4s','4p','4d','4f','5s','5p','5d','5f','5g']

f2 = "table3.dat"
df2_head = ['(eV/u)','Total','n=4','n=5','4s','4p','4d','4f','5s','5p','5d','5f','5g']

f3 = "table4.dat"
df3_head = ['(eV/u)','4s','4p','4d','4f']

total_columns = ['n=2','n=3','n=4','n=5','n=6','n=7','total']


df1 = pd.read_csv(f1, sep='\s+',names = df1_head)
df1 = df1.apply(pd.to_numeric)
# df1 = df1.drop(total_columns,axis = 1)
df2 = pd.read_csv(f2, sep='\s+',names = df2_head)
df2 = df2.apply(pd.to_numeric)
df3 = pd.read_csv(f3, sep='\s+',names = df3_head)
df3 = df3.apply(pd.to_numeric)

print (df1,df2,df3)
# df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['(eV/u)'],
#                                             how='outer'), data_frames).fillna('0.0')

# df_merged["E(eV/u)"] = pd.to_numeric(df_merged["E(eV/u)"])
# df_merged = df_merged.apply(pd.to_numeric)
# df_merged=df_merged.sort_values(by=['E(eV/u)'], ascending=True)
# total_columns = ['n=2','n=3','n=4','n=5','n=6','n=7','total']
# df_merged = df_merged.drop(total_columns,axis = 1)
# # df_merged['Total'] = df_merged.drop(['E(eV/u)'], axis=1).sum(axis=1)

# print(df_merged)
# print(df_merged.columns)

# Header_lst = list(df_merged.columns)
# print (Header_lst)
# Header = '#'
# for i in Header_lst:
#     print (i)
#     Header = Header + ' ' + i +'(2' + i[-1].capitalize() + ')'
# citation = "Y. Wu et al 2012 J. Phys. B: At. Mol. Opt. Phys. 45 235201"

# txt = "# Prepared by R. Cumbee, 6/2021 \n# Single electron capture cross \
# sections, nl state-selective \n# O^6+ + H -> O^5+ + H^+ \n\
# # Method=MOCC/CTMC/AOCC \n" + '# ' + citation + '\n' + \
# "# ------------------------------------------------------------------------- \
# --- \n# Energy		Cross sections (10^-16 cm^2) \n" + Header

# print (txt)
# path = 'out.cs'
# path_2 = 'o8+h_sec_mocc.cs'
# df_merged.to_csv(path,index=False, header = False, sep ='\t')

# f = open(path,'r')
# newf = open(path_2,'w')
# lines = f.readlines() # read old content
# newf.write(txt) # write new content at the beginning
# for line in lines: # write old content after new
#     newf.write(line)
# newf.close()
# f.close()

