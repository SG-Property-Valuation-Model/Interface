'''
To test model and scaler saving
XGBoost model for now; needs to be replaced by final model
'''

import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib

df = pd.read_csv('../datasets/modelling_dataset.csv')

X = df.drop(["Unit Price ($ PSM)"], axis=1)
y = df['Unit Price ($ PSM)']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, shuffle=True)

all_features = list(X_train.columns)
print(all_features)
standardScale_vars = ['Area (SQM)',
                      'Floor Number',
                      'PPI',
                      'Average Cases Per Year',
                      'Nearest Primary School',
                      'nearest_station_distance']

minMax_vars = ['Remaining Lease']

remaining_features = [x for x in all_features if x not in standardScale_vars and x not in minMax_vars]
s_scaler = StandardScaler()
mm_scaler = MinMaxScaler()

s_scaled = pd.DataFrame(s_scaler.fit_transform(X_train.loc[:, standardScale_vars].copy()), columns=standardScale_vars, index=X_train.index)
mm_scaled = pd.DataFrame(mm_scaler.fit_transform(X_train.loc[:, minMax_vars].copy()), columns=minMax_vars, index=X_train.index)

X_train = pd.concat([s_scaled,
                     mm_scaled,
                     X_train.loc[:, remaining_features].copy()], axis=1)

s_scaled_test = pd.DataFrame(s_scaler.transform(X_test.loc[:, standardScale_vars].copy()), columns=standardScale_vars, index=X_test.index)
mm_scaled_test = pd.DataFrame(mm_scaler.transform(X_test.loc[:, minMax_vars].copy()), columns=minMax_vars, index=X_test.index)

X_test = pd.concat([s_scaled_test,
                     mm_scaled_test,
                     X_test.loc[:, remaining_features].copy()], axis=1)


# Split training set into train and eval sets
X_train, X_eval, y_train, y_eval = train_test_split(X_train, y_train, test_size=0.2, random_state=42, shuffle=True)

# Best model parameters
model = XGBRegressor(colsample_bytree=0.7,
                     gamma=5,
                     learning_rate=0.07,
                     max_depth=7,
                     min_child_weight=5,
                     n_estimators=4675,
                     reg_linear=0.6,
                     reg_lambda=0.4,
                     subsample=0.7,
                     seed=42)


model.fit(X_train, y_train, eval_set=[(X_eval, y_eval)], early_stopping_rounds=50)

joblib.dump(model, 'model_test.pkl')
joblib.dump(s_scaler, 'standard_scaler.bin')
joblib.dump(mm_scaler, 'mm_scaler.bin')

# Load the model and scalers from the file
model_from_joblib = joblib.load('model_test.pkl')
s_scaler = joblib.load('standard_scaler.bin')
mm_scaler = joblib.load('mm_scaler.bin')

s_scaled = pd.DataFrame(s_scaler.transform(X_test[:1].loc[:, standardScale_vars].copy()),
                        columns=standardScale_vars)
mm_scaled = pd.DataFrame(mm_scaler.transform(X_test[:1].loc[:, minMax_vars].copy()), columns=minMax_vars)

property_df_scaled = pd.concat([s_scaled,
                                mm_scaled,
                                X_test[:1].loc[:, 'Ang Mo Kio':'Executive Condominium'].copy()], axis=1)

prediction = model_from_joblib.predict(property_df_scaled)[0]

'''
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