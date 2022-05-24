# -*- coding: utf-8 -*-
"""
Created on Sun May 22 19:06:11 2022

@author: Jesus Lizana

Diagnostic analytics to audit the passive building performance. It involves three indicators: 
    
    1. Heat resilience is characterised by an overheating index (BSOI, %);
    
    2. Indoor environment is diagnosed through a heat balance map that divides building performance into four thermal stages 
    related to the positive or negative influence of total heat flux and the ventilation and infiltration load; 
    
    3. Air change rates (ACHs) per thermal stage are calculated using the CO2-based decay method.   

        
Python version and libraries: 
    
    Python 3.9.7 
    Libraries: 
        pandas
        numpy
        matplotlib
        os
        scipy
        
VERSIONS: 
v1_2022.05.23_First version




INPUT DATA REQUIRED:
    Examples of data are provided in the folder: /data
    
    Columns: datetime,indoor_CO2,indoor_Temp,indoor_RH,outdoor_Temp
    
    Time resolution: 1-hour resolution - for lower resolution some functions need modifications

OUTPUT DATA: 
    
 
    

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats import sem

#%%

# get current location of script
cwd = os.path.dirname(__file__) 

#Introduce folder of input data
folder = "\data"
os.chdir(cwd+folder)

print(os.listdir())

#%%

#Read input data
df_home = pd.read_csv('home3.csv', index_col = "datetime", parse_dates=True) 


#%%

##############################################################################

# 1 - Analysis of the overheating situation - BSOI (%, from 0 to 100%) 

##############################################################################

#Function to calculate overheating indicator: BSOI - building seasonal overheating index, %

def BSOI(data):
    
    df = data.copy()   
    df['Tout_Tint']=df['outdoor_Temp']-df['indoor_Temp']
    
    print("Numerator" , abs(df.loc[df['Tout_Tint'] < 0, 'Tout_Tint'].sum()))
    print("Denominator", df["Tout_Tint"].abs().sum()/2)
    
    BSOI =(((abs(df.loc[df['Tout_Tint'] < 0, 'Tout_Tint'].sum())) / (df["Tout_Tint"].abs().sum()/2)) - 1)*100
    BSOI = round(BSOI,2)
    
    return BSOI
    

#%%

#Result of BSOI: 
    
home2_BSOI = BSOI(df_home)


#%%

##############################################################################

# 2 - Analysis of building thermal stages

##############################################################################

#Function to calculate required parameters to define thermal stages of building 

def thermal_stages(data):   

    df = data.copy()
    
    df['grad']=-df['indoor_Temp'].diff(periods=-1)
    df['Tout_Tint']=df['outdoor_Temp']-df['indoor_Temp']
    
    df=df[:-1] #eliminate last value
       
    return df

#Function to calculate the percentage of time in which the building is operating in each thermal stage

def thermal_stages_summary(data):
    
    #Dimensionality of the stages
    stage_1=data[(data.grad<0)&(data.Tout_Tint>0)].shape[0]
    stage_2=data[(data.grad>0)&(data.Tout_Tint>0)].shape[0]
    stage_3=data[(data.grad>0)&(data.Tout_Tint<0)].shape[0]
    stage_4=data[(data.grad<0)&(data.Tout_Tint<0)].shape[0]
    total=stage_1+stage_2+stage_3+stage_4
    
    stage1_p = round(stage_1/total*100,2)
    stage2_p = round(stage_2/total*100,2)
    stage3_p = round(stage_3/total*100,2)
    stage4_p = round(stage_4/total*100,2)
    
    
    df = {"Stages":["Stage 1","Stage 2","Stage 3","Stage 4"],
            "Percentage_%":[stage1_p,stage2_p,stage3_p,stage4_p],
            }

    result = pd.DataFrame(df,columns=["Stages","Percentage_%"])
    result = result.set_index("Stages")
    
    return result

  
#%%

#Result of thermal stages analysis: 

df_home_1 = thermal_stages(df_home)
  
home2_thermalstages_summary = thermal_stages_summary(df_home_1)


#%%

##############################################################################

# 3 - Analysis of ACH through CO2-based decay method

##############################################################################



#Function to calculate ACH based on the CO2-based decay method

#add limit and slope as input parameters

def ACH(data):
    
    df = data.copy()
    
    #if CO2 concentration < 500 = null - baseline for calculation
    df.indoor_CO2[(df['indoor_CO2']<=500)]=500
    
    #Thermal stages
    df['grad']=-df['indoor_Temp'].diff(periods=-1)
    df['Tout_Tint']=df['outdoor_Temp']-df['indoor_Temp']
    
    #CO2 gradient
    df['grad_co2']=-df['indoor_CO2'].diff(periods=-1)  
    df=df[:-1] #eliminate last value
    
    #Fillna by 0 (to avoid errors)
    df['grad_co2']=df['grad_co2'].fillna(0)
    
    
    #calculate ACH
    df=df.reset_index()
    
    ACH_total=np.zeros(0)
    Cext=400
    
    for i in df.index:
        if i==0:
            ACH_i=0
            ACH_total=np.append(ACH_total,ACH_i)
        
        else:
            
            if  df.loc[i,'grad_co2']>=-100 or df.loc[i,'indoor_CO2']<1000:
                ACH_i=0
                ACH_total=np.append(ACH_total,ACH_i)
            
            else:              
                          
                A=df[df.index==i].indoor_CO2
                B=df[df.index==i+1].indoor_CO2
                ACH_i= np.log((int(A)-Cext)/(int(B)-Cext))        
        
                ACH_total=np.append(ACH_total,ACH_i)
            
    df['ACH']=ACH_total
    df=df.set_index('datetime')
    
    #clean 0 values
    df.loc[df.grad_co2>-100,'ACH']=np.nan
    df.loc[df.ACH<=0, 'ACH']=np.nan
    
    return df


#Function to calculate the mean ACH (and number of points and std) per thermal stage

def ACH_summary(data):
    
    #mean ACH value per stage
    stage1_mean=round(np.nanmean(data.loc[(data.Tout_Tint>0)&(data.grad<0), 'ACH']),2)
    stage2_mean=round(np.nanmean(data.loc[(data.Tout_Tint>0)&(data.grad>0), 'ACH']),2)
    stage3_mean=round(np.nanmean(data.loc[(data.Tout_Tint<0)&(data.grad>0), 'ACH']),2)
    stage4_mean=round(np.nanmean(data.loc[(data.Tout_Tint<0)&(data.grad<0), 'ACH']),2)
    
    #standard deviation
    stage1_std=round(float(sem(data.loc[(data.Tout_Tint>0)&(data.grad<0), 'ACH'], nan_policy='omit')),2)
    stage2_std=round(float(sem(data.loc[(data.Tout_Tint>0)&(data.grad>0), 'ACH'], nan_policy='omit')),2)
    stage3_std=round(float(sem(data.loc[(data.Tout_Tint<0)&(data.grad>0), 'ACH'], nan_policy='omit')),2)
    stage4_std=round(float(sem(data.loc[(data.Tout_Tint<0)&(data.grad<0), 'ACH'], nan_policy='omit')),2)
    
    #Number of points per stage
    stage1_shape=data[(data.grad<0)&(data.Tout_Tint>0)].shape[0]-(data.loc[(data.Tout_Tint>0)&(data.grad<0), 'ACH'].isna().sum())
    stage2_shape=data[(data.grad>0)&(data.Tout_Tint>0)].shape[0]-(data.loc[(data.Tout_Tint>0)&(data.grad>0), 'ACH'].isna().sum())
    stage3_shape=data[(data.grad>0)&(data.Tout_Tint<0)].shape[0]-(data.loc[(data.Tout_Tint<0)&(data.grad>0), 'ACH'].isna().sum())
    stage4_shape=data[(data.grad<0)&(data.Tout_Tint<0)].shape[0]-(data.loc[(data.Tout_Tint<0)&(data.grad<0), 'ACH'].isna().sum())
    
    df = {"Stages":["Stage 1","Stage 2","Stage 3","Stage 4"],
            "ACH_mean":[stage1_mean,stage2_mean,stage3_mean,stage4_mean],
            "ACH_std":[stage1_std,stage2_std,stage3_std,stage4_std],
            "ACH_points":[stage1_shape,stage2_shape,stage3_shape,stage4_shape],
            }

    result = pd.DataFrame(df,columns=["Stages","ACH_mean","ACH_std","ACH_points"])
    result = result.set_index("Stages")
    
    return result


#%%

#Result of ACH analysis: 
    
df_home_2 = ACH(df_home)

home_ACH_summary = ACH_summary(df_home_2)



#%%


##############################################################################

# SUMMARY OF INDICATORS TO CHARACTERISE THE PASSIVE PERFORMANCE OF BUILDINGS

##############################################################################


summary = pd.concat([home2_thermalstages_summary,home_ACH_summary],axis=1)



#%%


##############################################################################

# FIGURES 

##############################################################################


#Figure 1. Heat balance map to audit passive building performance through four stages, including all calculated indicators per thermal stage

#Building overheating
BSOI_value= "Building seasonal overheating index: " +str(home2_BSOI)+" %"

#Stage 1: heat modulation. 
stage1= "Stage 1: " +str(home2_thermalstages_summary["Percentage_%"].iloc[0])+" %"
ACH_1= "Mean ACH: " +str(home_ACH_summary["ACH_mean"].iloc[0])+" $h^{-1}$"
#Stage 2: solar and heat gains (1/2); 
stage2= "Stage 2: " +str(home2_thermalstages_summary["Percentage_%"].iloc[1])+" %"
ACH_2= "Mean ACH: " +str(home_ACH_summary["ACH_mean"].iloc[1])+" $h^{-1}$"
#stage 3: solar and heat gains (2/2); 
stage3= "Stage 3: " +str(home2_thermalstages_summary["Percentage_%"].iloc[2])+" %"
ACH_3= "Mean ACH: " +str(home_ACH_summary["ACH_mean"].iloc[2])+" $h^{-1}$"
#stage 4: heat dissipation.
stage4= "Stage 4: " +str(home2_thermalstages_summary["Percentage_%"].iloc[3])+" %"
ACH_4= "Mean ACH: " +str(home_ACH_summary["ACH_mean"].iloc[3])+" $h^{-1}$"


fig = plt.figure(figsize=(10,6))
plt.style.use('ggplot') #'seaborn-notebook'



plt.title('Diagnostic analytics to audit the passive builing performance',y=1.08,loc="left",fontsize=17, pad=15)
plt.suptitle(BSOI_value, y=0.945, x=0.357,fontsize=15)

plt.plot(df_home_1['grad'],df_home_1['Tout_Tint'],'o', alpha=0.2,color="royalblue")
ax = plt.gca()
ax.spines['left'].set_position('zero')
ax.spines['right'].set_color('none')
ax.spines['bottom'].set_position('zero')
ax.spines['top'].set_color('none')
plt.xlabel('Indoor temperature gradient', loc='right',fontsize=11)
plt.ylabel('Tout - Tind', loc='bottom',rotation=0, fontsize=12,  labelpad=70)
plt.yticks(np.arange(-20,25,5))
plt.xticks(np.arange(-7,8,1))


plt.text(-6, 13, stage1 ,fontsize=15)
plt.text(-6, 11, "Heat modulation" ,fontsize=13)
plt.text(-6, 9, ACH_1 ,fontsize=13)

plt.text(2.5, 13, stage2 ,fontsize=15)
plt.text(2.5, 11, "Solar and heat gains (1/2)" ,fontsize=13)
plt.text(2.5, 9, ACH_2 ,fontsize=13)

plt.text(2.5, -13, stage3 ,fontsize=15)
plt.text(2.5, -15, "Solar and heat gains (2/2)" ,fontsize=13)
plt.text(2.5, -17, ACH_3 ,fontsize=13)


plt.text(-6, -13, stage4 ,fontsize=15)
plt.text(-6, -15, "Heat dissipation" ,fontsize=13)
plt.text(-6, -17, ACH_4 ,fontsize=13)



#ax.set_facecolor((0.95, 0.95, 0.95))
#plt.margins(x=0.1)

plt.show()



#%%


# Figure 2. Violin plot of ACH rates


plt.rcParams["figure.figsize"] = (4,6)
data_violin=[df_home_2['ACH'].dropna()]
labels=['Home']

fig = plt.figure()
plt.style.use('default') #'seaborn-notebook'
# Create an axes instance
ax = fig.add_axes([0,0,1,1])

# Create the boxplot
bp = ax.violinplot(data_violin,showmedians=True)
ax.set_xticks(np.arange(1, len(labels) + 1))
ax.set_xticklabels(labels)
ax.set_ylabel('ACH (h-1)')
ax.set_title('Air Change Rate')
plt.yticks(np.arange(0,3,0.5))
plt.show()



#%%

# Figure 3. Comparison of ACH points with CO2 concentrations throughout the monitored period

df_home_3 = df_home_2.truncate(before='2021-06-11', after='2021-06-12')

fig, ax = plt.subplots(figsize =(10, 4))
ax.set_title('Air Change Rate')

ax = df_home_3['ACH'].plot(marker='D', markersize=8,color="royalblue",markeredgecolor="none",linestyle = 'None',lw=5,zorder=0)
ax.set_ylim(0,3)
ax.set_ylabel('ACH (h-1)')

ax1 = df_home_3['indoor_CO2'].plot(secondary_y=True, color='gray',linestyle="--",linewidth=1,zorder=50)
ax1.set_ylabel("CO2 concentration (ppm)")
ax1.set_ylim(500,2000)

ax.set_xlabel('datetime')
plt.margins(x=0.01)
plt.show()



