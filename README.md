# Indicators to assess the heat resilience of buildings - 🌞

Novel diagnostic analytics to assess the indoor overheating of buildings using real long-term monitoring data obtained through indoor and outdoor IoT sensors.

## Overview

The diagnostic analytics are based on three methods. 

First, the overheating situation of the indoor environment is characterised by a seasonal building overheating index (SBOI) ranging from 0% to 100%. 

Second, the indoor environment is diagnosed through a heat balance map that divides building performance into four thermal stages related to the positive or negative influence of total heat flux and the ventilation and infiltration load. Third, the air changes (ACH), associated with ventilation and infiltration per thermal stage, are calculated using the CO2-based decay method.

Third, the air changes (ACH), associated with ventilation and infiltration per thermal stage, are calculated using the CO2-based decay method. 


#### Install dependencies (use Python3)

```python

pip install -r requirements.txt

```

## How to use these **diagnostic analytics**?

First, collect required data for the analysis: 

-Indoor: temperature, CO2 concentrations
-Outoor: temperature

Second, prepare the data: 

-See example in folder /data. 

Third, diagnostic analysis. 

### 1. Analysis of the overheating situation - Seasonal building overheating index (SBOI): 

In a well-designed building scenario, SBOI should be closer to 0% (Fig. a).

In an overheated indoor environment, SBOI shows the different situations (Fig. b): 

	• SBOI >10%: slightly overheated indoor environment.
	• SBOI >25% for an overheated scenario.
	• SBOI >50% for an extremely overheated indoor environment. 
	• SBOI ≈100% for a tremendously overheated scenario, where the indoor temperature is always higher than outside. 

  
![CSV example](https://github.com/lizanafj/Indicators-to-assess-the-heat-resilience-of-buildings/blob/master/resources/1_SBOI.jpg )


### 2. Analysis of building thermal stages - Heat balance map

The passive thermal performance of building is analysed through four thermal stages related to the positive or negative influence of total heat flux and the ventilation and infiltration load.
These stages can be labelled according to the three main action groups for the passive conditioning of buildings:

	• Stage 1. Heat modulation. This shows cooling periods due to building thermal mass (or sporadic AC operation)
	• Stage 2. Solar and heat gains 1/2. This stage illustrates temperature increasing as a result of solar and heat gains.
	• Stage 3. Solar and heat gains 2/2. Stage 3 illustrates temperature increasing despite the lower outdoor temperature. In this stage, heat fluxes from the building surface and internal heat gains are predominant. 
	• Stage 4. Heat dissipation. This stage 4 is associated with cooling periods mainly due to ventilative cooling (or sporadic AC operation)


![CSV example](https://github.com/lizanafj/Indicators-to-assess-the-heat-resilience-of-buildings/blob/master/resources/2_Thermalbuildingstages.jpg )


### 3. Analysis of ACH through CO2-based decay method

This method uses monitored data related to indoor CO2 concentrations in the indoor environment to calculate air change rate (ACH, h-1) related to ventilation and air infiltration.

![CSV example](https://github.com/lizanafj/Indicators-to-assess-the-heat-resilience-of-buildings/blob/master/resources/3_ACHmethod.png )


### FINAL OUTPUT OF THE SCRIPT 

![CSV example](https://github.com/lizanafj/Indicators-to-assess-the-heat-resilience-of-buildings/blob/master/resources/4_scriptresults.png )





