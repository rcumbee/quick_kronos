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

f1 = "n=2_recommended.dat"

f2 = "n=3&4&5&total_recommended.dat"

f3 = "n=6_recommended.dat"

f4 = "n=7_recommended.dat"

df1 = pd.read_csv(dir+f1, sep='\s+')
print(df1)

df2 = pd.read_csv(dir+f2, sep='\s+')
print(df2)

df3 = pd.read_csv(dir+f3, sep='\s+')
print(df3)

df4 = pd.read_csv(dir+f4, sep='\s+')
print(df4)

data_frames = [df1,df2,df3,df4]

df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['E(eV/u)'],
                                            how='outer'), data_frames).fillna('0.0')

# df_merged["E(eV/u)"] = pd.to_numeric(df_merged["E(eV/u)"])
df_merged = df_merged.apply(pd.to_numeric)
df_merged=df_merged.sort_values(by=['E(eV/u)'], ascending=True)
total_columns = ['n=2','n=3','n=4','n=5','n=6','n=7','total']
df_merged = df_merged.drop(total_columns,axis = 1)
df_merged['Total'] = df_merged.drop(['E(eV/u)'], axis=1).sum(axis=1)

print(df_merged)
print(df_merged.columns)

Header_lst = list(df_merged.columns)
print (Header_lst)
Header = '#'
for i in Header_lst:
    print (i)
    Header = Header + ' ' + i +'(2' + i[-1].capitalize() + ')'
citation = "Y. Wu et al 2012 J. Phys. B: At. Mol. Opt. Phys. 45 235201"

txt = "# Prepared by R. Cumbee, 6/2021 \n# Single electron capture cross \
sections, nl state-selective \n# O^6+ + H -> O^5+ + H^+ \n\
# Method=MOCC/CTMC/AOCC \n" + '# ' + citation + '\n' + \
"# ------------------------------------------------------------------------- \
--- \n# Energy		Cross sections (10^-16 cm^2) \n" + Header

print (txt)
path = 'out.cs'
path_2 = 'o8+h_sec_mocc.cs'
df_merged.to_csv(path,index=False, header = False, sep ='\t')

f = open(path,'r')
newf = open(path_2,'w')
lines = f.readlines() # read old content
newf.write(txt) # write new content at the beginning
for line in lines: # write old content after new
    newf.write(line)
newf.close()
f.close()