'''
To test model and scaler saving
Ridge model is a placeholder for now; needs to be replaced by final model
'''

import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib

df = pd.read_csv('../datasets/final_dataset.csv')
df['Sale Date'] = pd.to_datetime(df['Sale Date'])
df = pd.concat([df, pd.get_dummies(df.pop('Property Type'))], axis=1)
#df['Time Period'] = df['Sale Date'].apply(lambda x: (x.year - df['Sale Date'][0].year)*12 + (x.month - df['Sale Date'][0].month))
df.drop(columns=['BLK_NO',
                 'BUILDING',
                 'POSTAL',
                 'Planning Area',
                 'Planning Region',
                 'Postal Code',
                 'ROAD_NAME',
                 'Sale Date',
                 'Transacted Price ($)',
                 'Police Centre',
                 'num_stations_1km',
                 'Number of Primary Schools'], inplace=True)
df.drop_duplicates(inplace=True)
df.reset_index(drop=True, inplace=True)
df.drop(columns=['Age Sold',
                 'Woodlands',
                 'Condominium'], inplace=True)

print(df.shape)
print(df.head(3))

X = df.drop(columns = ['Unit Price ($ PSM)'])
y = df['Unit Price ($ PSM)']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle = False, random_state = None)


standardScale_vars = ['Area (SQM)',
                      'Floor Number',
                      'PPI',
                      'Average Cases Per Year',
                      'Nearest Primary School',
                      'nearest_station_distance']
minMax_vars = ['Remaining Lease']

s_scaler = StandardScaler()
mm_scaler = MinMaxScaler()

X_train_std = s_scaler.fit_transform(X_train.loc[:, standardScale_vars].copy())
X_train_mm = mm_scaler.fit_transform(X_train.loc[:, minMax_vars].copy())
X_test_std = s_scaler.transform(X_test.loc[:, standardScale_vars].copy())
X_test_mm = mm_scaler.transform(X_test.loc[:, minMax_vars].copy())

X_train_df = pd.concat([pd.DataFrame(X_train_std, columns=standardScale_vars),
                       pd.DataFrame(X_train_mm, columns = minMax_vars),
                       X_train.loc[:, 'Ang Mo Kio':'Executive Condominium'].copy()], axis = 1)
X_test_df = pd.concat([pd.DataFrame(X_test_std, columns=standardScale_vars),
                       pd.DataFrame(X_test_mm, columns = minMax_vars),
                       X_test.loc[:, 'Ang Mo Kio':'Executive Condominium'].copy()], axis = 1)

regressor = Ridge(alpha = 1.10, fit_intercept = True)
regressor.fit(X_train_df, y_train)

joblib.dump(regressor, 'model_test.pkl')
joblib.dump(s_scaler, 'standard_scaler.bin')
joblib.dump(mm_scaler, 'mm_scaler.bin')
'''

# Load the model and scalers from the file
model_from_joblib = joblib.load('C:/Users/User/Desktop/NOTES/Notes_Y4S2/BT4222/HDB Project/Modelling/model_test.pkl')
sc_ = joblib.load('C:/Users/User/Desktop/NOTES/Notes_Y4S2/BT4222/HDB Project/Modelling/standard_scaler.bin')
mm_ = joblib.load('C:/Users/User/Desktop/NOTES/Notes_Y4S2/BT4222/HDB Project/Modelling/mm_scaler.bin')


s_scaled = pd.DataFrame(s_scaler.fit_transform(df.loc[:, standardScale_vars].copy()), columns=standardScale_vars)
mm_scaled = pd.DataFrame(mm_scaler.fit_transform(df.loc[:, minMax_vars].copy()), columns=minMax_vars)

df = pd.concat([df.loc[:,['Unit Price ($ PSM)'].copy()],
                s_scaled,
                mm_scaled,
                df.loc[:,'Ang Mo Kio':'Executive Condominium'].copy()], axis=1)

os.chdir('C:/Users/User/Desktop/NOTES/Notes_Y4S2/BT4222/HDB Project/Modelling/')
df = pd.read_csv('modelling_dataset.csv')

X = df.drop(columns = ['Unit Price ($ PSM)'])
y = df['Unit Price ($ PSM)']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle = False, random_state = None)
regressor = Ridge(alpha = 1.10, fit_intercept = True)
regressor.fit(X_train, y_train)

import joblib

# Save the model as a pickle in a file
joblib.dump(regressor, 'C:/Users/User/Desktop/NOTES/Notes_Y4S2/BT4222/HDB Project/Modelling/model_test.pkl')
joblib.dump(s_scaler, 'C:/Users/User/Desktop/NOTES/Notes_Y4S2/BT4222/HDB Project/Modelling/standard_scaler.bin')
joblib.dump(mm_scaler, 'C:/Users/User/Desktop/NOTES/Notes_Y4S2/BT4222/HDB Project/Modelling/mm_scaler.bin')
# Load the model from the file
model_from_joblib = joblib.load('C:/Users/User/Desktop/NOTES/Notes_Y4S2/BT4222/HDB Project/Modelling/model_test.pkl')

# Use the loaded model to make predictions
print(model_from_joblib.predict(X_test[:1]))
'''