import pandas as pd
import numpy as np

fallecidos=pd.read_excel(r"Titulares Fallecidos_EF_Final.xlsx",sheet_name="FALLECIDOS")
pagosds02=pd.read_csv(r"REBAJA DIVIDENDO 012026.txt",sep=";",header=None)
pagosds12=pd.read_csv(r"ARCHIVO1.txt",sep=";",header=None)
pagosds51=pd.read_csv(r"ARCHIVO2.txt",sep=";",header=None)

#print(fallecidos.head())
#print(pagosds02.head())
#print(pagosds12.head())
#print(pagosds51.head())

# ASIGNAR COLUMNAS A UN TXT
#pagosds02.columns ["EF","RUT","COL3","COL4","COL5","COL6","COL7","COL8","COL9","COL10"]
#pagosds12.columns ["EF","RUT","COL3","COL4","COL5","COL6","COL7","COL8","COL9","COL10"]
#pagosds51.columns ["EF","RUT","COL3","COL4","COL5","COL6","COL7","COL8","COL9","COL10"]


fallecidos["RUT"]= fallecidos["RUT"].astype(str)
pagosds02[1]=pagosds02[1].astype(str)
pagosds12[1]=pagosds12[1].astype(str)
pagosds51[1]=pagosds51[1].astype(str)


merge_testP02 =pagosds02.merge(fallecidos["RUT"],left_on=1,right_on="RUT",how="left",indicator=True)
merge_testP12 =pagosds12.merge(fallecidos["RUT"],left_on=1,right_on="RUT",how="left",indicator=True)
merge_testP51 =pagosds51.merge(fallecidos["RUT"],left_on=1,right_on="RUT",how="left",indicator=True)

coincidenciasP02 =merge_testP02[merge_testP02["_merge"]=="both"]
coincidenciasP12 =merge_testP12[merge_testP12["_merge"]=="both"]
coincidenciasP51 =merge_testP51[merge_testP51["_merge"]=="both"]

print(coincidenciasP02)
print(coincidenciasP12)
print(coincidenciasP51)
#print(fallecidos.head())
#print(pagosds02.head())
#print(pagosds12.head())
#print(pagosds51.head())



