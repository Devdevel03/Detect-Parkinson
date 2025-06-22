import numpy as np
import pandas as pd
import os, sys
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

#DataFlair - Read the data
df=pd.read_csv('./parkinsons.data.csv')
df.head()

#DataFlair - Get the features and labels
features = df.loc[:,df.columns!='status'].values[:,1:]
labels = df.loc[:,'status'].values
#DataFlair - Get the count of each label(0and1) in labels
print(labels[labels==1].shape[0], labels[labels==0].shape[0])

#DataFlair - Scale the features to between -1 and 1
scaler = MinMaxScaler((-1, 1))
x=scaler.fit_transform(features)
y=labels

#DataFlair - Split the dataset
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=7)

#DataFlair - Train the model
model=XGBClassifier()
model.fit(x_train,y_train)

XGBClassifier(base_score=0.5, booster='gbtree', colsample_bylevel=1,
              colsample_bynode=1, colsample_bytree=1, gamma=0,
              learning_rate=0.1, max_delta_step=0, max_depth=3,
              min_child_weight=1, missing=None, n_estimators=100, n_jobs=1,
              nthread=None, objective='binary:logistic', random_state=0,
              reg_alpha=0, reg_lambda=1, scale_pos_weight=1, seed=None,
              silent=None, subsample=1)

#DataFlair - Calculate the accuracy
y_pred = model.predict(x_test)
print("Accuracy: ", accuracy_score(y_test, y_pred)*100)

# Add this to the end of your training script
import joblib

# File names for the saved model and scaler
model_filename = 'parkinsons_model.joblib'
scaler_filename = 'parkinsons_scaler.joblib'

# Save the trained model
joblib.dump(model, model_filename)

# Save the fitted scaler
joblib.dump(scaler, scaler_filename)

print(f"Model saved to {model_filename}")
print(f"Scaler saved to {scaler_filename}")