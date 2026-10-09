import pandas as pd
import reverse_geocoder as rg

# Load datasets; Global McDonalds Locations; County Health Outcomes from CDC
mcdonalds = pd.read_csv("C:/Users/xhers/OneDrive/Desktop/Personal-Python-Projects/Personal-Python-Projects/FastFoodHealth/data/McDonalds.csv")
health = pd.read_csv("C:/Users/xhers/OneDrive/Desktop/Personal-Python-Projects/Personal-Python-Projects/FastFoodHealth/data/CountyHealth.csv")

mcdonaldsUS = mcdonalds[mcdonalds['country'] == "United States"]

# get coordinates as (latitude, longitude) tuples to assign to county
coords = list(zip(mcdonaldsUS["latitude"], mcdonaldsUS["longitude"]))

# Perform reverse geocoding using tuples
results = rg.search(coords)

# Extract county/administrative region (admin2 usually corresponds to county)
mcdonaldsUS["county"] = [res["admin2"] for res in results]

#rename and clean columns for easier analysis
mcdonaldsUS.rename(columns={"subdivision":"state"}, inplace=True)
health['TotalPopulation'] = pd.to_numeric(
                            health['TotalPopulation'].str.replace(
                                ',',''),
                            errors = 'coerce' #population not necessarily vital, just quality of life
                            )
health['TotalPop18plus'] = pd.to_numeric(
                            health['TotalPop18plus'].str.replace(
                                ',',''),
                            errors = 'coerce' #population not necessarily vital, just quality of life
                            )


#Dropping entirely NaN columns
health = health.drop(columns={'Data_Value_Footnote','Data_Value_Footnote_Symbol','Geolocation'})
#Dropping useless columns in health data
health = health.drop(columns={'Short_Question_Text','Data_Value_Unit'})
#Dropping Nation Wide Data Rows, and rows with missing data
health = health[health['StateAbbr']!='US']
health.dropna(inplace=True)

#Making percentage columns a decimal (x/100)
health[['Data_Value','Low_Confidence_Limit','High_Confidence_Limit']] = (health[['Data_Value','Low_Confidence_Limit','High_Confidence_Limit']] / 100)

#noting columns kept in pivoted dataset
columns_kept = ["LocationName", "StateAbbr","Data_Value_Type",'TotalPopulation', 'TotalPop18plus']
#pivoting to combine all counties into one row
health_pivot = health.pivot_table(
    index=columns_kept, 
    columns="MeasureId",  
    values="Data_Value"
).reset_index()


health_age =  health_pivot[health_pivot['Data_Value_Type'].str.contains('Age')]
health_crude = health_pivot[health_pivot['Data_Value_Type'].str.contains('Crude')]

#remove " County" added by geocoder
mcdonaldsUS['county'] = mcdonaldsUS['county'].str.replace(' County','')
mcdonaldsUS['county'] = mcdonaldsUS['county'].str.replace(' Parish','')



#merging both age based health statistics and crude health statistics with Mcdonalds locations

fastFoodHealth_age = pd.merge(mcdonaldsUS, 
                          health_age, 
                          left_on=['county','state'], 
                          right_on=['LocationName','StateAbbr'],
                                    how='outer')

fastFoodHealth_crude =  pd.merge(mcdonaldsUS, 
                          health_crude, 
                          left_on=['county','state'], 
                          right_on=['LocationName','StateAbbr'],
                                    how='outer')


#saving to new csvs
save_directory = "C:/Users/xhers/OneDrive/Desktop/Personal-Python-Projects/Personal-Python-Projects/FastFoodHealth/new_csvs/"
fastFoodHealth_crude.to_csv(f'{save_directory}fastFoodHealth_crude.csv')
fastFoodHealth_age.to_csv(f'{save_directory}fastFoodHealth_age.csv')
mcdonaldsUS.to_csv(f'{save_directory}mcdonaldsUS.csv')
health_age.to_csv(f'{save_directory}health_age.csv')
health_crude.to_csv(f'{save_directory}health_crude.csv')
health_pivot.to_csv(f'{save_directory}health.csv')