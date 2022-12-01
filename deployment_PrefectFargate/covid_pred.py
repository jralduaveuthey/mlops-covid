#!/usr/bin/env python
# coding: utf-8


from sklearn.metrics import mean_squared_error
import pandas as pd
import numpy as np
from datetime import timedelta, datetime, date
from pandas._libs.tslibs.timestamps import Timestamp
import mlflow
import os
from prefect import task, flow, get_run_logger
from prefect.context import get_run_context
import sys

def preprocess(df,TARGETS=["ConfirmedCases", "Fatalities"],loc_group=['Province_State', 'Country_Region']):
    df["Date"] = df["Date"].astype("datetime64[ms]")
    for col in loc_group:
        df[col].fillna("none", inplace=True) #NOTE: replace all NaN with none  
    for col in TARGETS:
        df[col] = np.log1p(df[col]) 
    for col in TARGETS:
        df["prev_{}".format(col)] = df.groupby(loc_group)[col].shift() #NOTE: the prev_ columns basically has the same than the others but delayed one day
    return df

def create_output(df, TARGETS=["ConfirmedCases", "Fatalities"]): #To have the same format as the original input
    for col in TARGETS:
        df["pred_out_{}".format(col)] = np.expm1(df["pred_{}".format(col)])
    return  df

def get_data_last_days(num_days): #gets the data from the last "num_days" days
    num_days = num_days + 2 #I do this because I get rid of the first date since it has NaNs in the columns prev_ConfirmedCases	prev_Fatalities and because of the for loop with range
    dfs = []  # empty list which will hold your dataframes
    for d in range(1, num_days): #NOTE: do the same that has been done for the first day but for the whole period
        date = datetime.now() - timedelta(days=d)
        date_str = date.strftime("%m-%d-%Y")
        source_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/' + date_str + '.csv'
        df_temp = pd.read_csv(source_url)
        df_temp.rename(columns={"Last_Update": "Date"}, inplace=True) #Renane dataframe column from "Last_Update" to "Date"
        df_temp_2 = df_temp[["Admin2", "Province_State", "Country_Region","Confirmed", "Deaths"]].copy() #TODO: consider also other columns in future versions like Recovered,Active,Combined_Key,Incident_Rate,Case_Fatality_Ratio
        df_temp_2.loc[:,"Date"] = date.strftime("%Y-%m-%d") 
        dfs.append(df_temp_2)  # append dataframe to list
    res = pd.concat(dfs, ignore_index=True)  # concatenate list of dataframes
    
    # group by Country_Region and sum Confirmed and Deaths
    df = res.groupby(['Province_State','Country_Region','Date']).agg({'Confirmed':'sum', 'Deaths':'sum'})
    df.reset_index(inplace=True)
    df.rename(columns={"Confirmed": "ConfirmedCases", "Deaths": "Fatalities"}, inplace=True)  
    df = preprocess(df)
    df = df[df["Date"] > df["Date"].min()].copy() #removes the first day since it has NaNs in the "prev" columns
    df.reset_index(inplace=True, drop=True)
    
    return df

def predict_today_Province_State(model,Province_State,df):
    y_pred = predict_today_world(model) #Predict today worldwide
    index_PS = df[df['Province_State']==Province_State].iloc[0].name
    predictions = y_pred[index_PS]
    return predictions #First the predicted Confirmed cases and second the predicted fatalities

def predict_today_world(model,features=["prev_ConfirmedCases", "prev_Fatalities"]):#Does the prediction for today
    df = get_data_last_days(1) #Get data from yesterday
    yesterday = datetime.now() - timedelta(days=1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = Timestamp(yesterday)
    y_pred = np.clip(model.predict(df.loc[df["Date"] == yesterday][features]), None, 16)#NOTE: here predicting the targets for the first day and saturating (clip) them with max=16
    return y_pred

def evaluate_yesterday():
    return evaluate_last_days(1)

def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))

def predict_past(model, num_days,TARGETS,features=["prev_ConfirmedCases", "prev_Fatalities"]):
    test_df = get_data_last_days(num_days)
    first_day = datetime.now() - timedelta(days=num_days)
    first_day = first_day.replace(hour=0, minute=0, second=0, microsecond=0)
    first_day = Timestamp(first_day)
    y_pred = np.clip(model.predict(test_df.loc[test_df["Date"] == first_day][features]), None, 16)#NOTE: here he is predicting the targets for the first day and saturating (clip) them with max=16
    for i, col in enumerate(TARGETS):
        test_df["pred_{}".format(col)] = 0
        test_df.loc[test_df["Date"] == first_day, "pred_{}".format(col)] = y_pred[:, i] #NOTE: here he sets the predicted column
    for d in range(1, num_days): #NOTE: do the same that has been done for the first day but for the whole period
        y_pred = np.clip(model.predict(y_pred), None, 16)
        date = first_day + timedelta(days=d)
        for i, col in enumerate(TARGETS):
            test_df.loc[test_df["Date"] == date, "pred_{}".format(col)] = y_pred[:, i]
            
    test_df = create_output(test_df)
    return test_df

def evaluate_last_days(model,num_days,TARGETS):
    #get data from the last "num_days" days
    df = predict_past(model,num_days)
    
    #get the rmse
    error = 0
    for col in TARGETS:
        error += rmse(df[col].values, df["pred_{}".format(col)].values) #NOTE: checks the error between the predicted columns and the target columns
    return np.round(error/len(TARGETS), 5)


def load_model(run_id,mlflow_artifacts_path):
    logged_model = f's3://{mlflow_artifacts_path}/{run_id}/artifacts/models'
    model = mlflow.pyfunc.load_model(logged_model)
    return model

@task
def apply_model_today_Province_State(run_id, output_file,Province_State, mlflow_artifacts_path): #NOTE: this sequence is only for the function predict_today_Province_State, 
                                                    #other functions not separated into "tasks" (meaning functions call each other like inside predict_past it calls get_data_last_days)
    logger = get_run_logger()
    
    logger.info(f">>>>>>>>>>>>>>>>>> Getting COVID data from yesterday from CSSE at Johns Hopkins University's Github ...") 
    df = get_data_last_days(1) #Get data from yesterday

    logger.info(f'>>>>>>>>>>>>>>>>>> Loading the model with RUN_ID={run_id}...')
    logger.info(f'>>>>>>> TODO DELETEME mlflow_artifacts_path={mlflow_artifacts_path}...')
    model = load_model(run_id,mlflow_artifacts_path)

    logger.info(f'>>>>>>>>>>>>>>>>>> Applying the model...')
    predictions = predict_today_Province_State(model,Province_State,df) #Returns first the predicted Confirmed cases and second the predicted fatalities

    logger.info(f'>>>>>>>>>>>>>>>>>> Saving the result to {output_file}...')
    df_result = pd.DataFrame()
    df_result['Province_State'] = pd.Series(Province_State)
    df_result['Date'] =  pd.Series(date.today())
    df_result['pred_out_ConfirmedCases']=pd.Series(np.expm1(predictions[0])) #TODO: instead of doing the exp here, call create_output inside the pred_today_* functions
    df_result['pred_out_Fatalities']=pd.Series(np.expm1(predictions[1])) #TODO: instead of doing the exp here, call create_output inside the pred_today_* functions
    df_result['model_version'] = run_id
    # df_result.to_parquet(output_file, index=False)
    df_result.to_csv(output_file, index=False)
    
    logger.info(f'>>>>>>>>>>>>>>>>>> Finished succesfully!')


def get_output_path(Province_State, run_id, s3_results_path):
    run_date = date.today()
    year = run_date.year
    month = run_date.month
    day = run_date.day
    logger = get_run_logger()
    output_file = f's3://{s3_results_path}/{Province_State}_predictons_{year:04d}-{month:02d}-{day:02d}/{run_id}.csv'
    return output_file


@flow
def covid_prediction(
        Prov_St: str,
        run_id: str,
        mlflow_artifacts_path: str,
        s3_results_path: str):
    
    output_file = get_output_path(Prov_St, run_id, s3_results_path)

    apply_model_today_Province_State(
        run_id=run_id,
        output_file=output_file,
        Province_State=Prov_St,
        mlflow_artifacts_path=mlflow_artifacts_path
        )
    


def run():
    ##NOTE: this variables are commented because not necessary for the batch with the task apply_model_today_Province_State
    # TARGETS = ["ConfirmedCases", "Fatalities"]
    # features = ["prev_{}".format(col) for col in TARGETS]
    # loc_group ["ConfirmedCases", "Fatalities"]
    
    Province_State = sys.argv[1] # "Madrid"
    RUN_ID = sys.argv[2] # '16082a31f2be4eadb6f368b4ded2d309'
    
    # Province_State = "Madrid"
    # RUN_ID = '16082a31f2be4eadb6f368b4ded2d309'

    # MLFLOW_TRACKING_URI = 'http://127.0.0.1:5000'
    # mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    # RUN_ID = os.getenv('RUN_ID','16082a31f2be4eadb6f368b4ded2d309') #NOTE: to use this you have to run in the terminal before <export RUN_ID='16082a31f2be4eadb6f368b4ded2d309'>, otherwise you get an error when loading the model
    # RUN_ID = '16082a31f2be4eadb6f368b4ded2d309'

    
    covid_prediction(
        Prov_St=Province_State,
        run_id=RUN_ID,
    )


if __name__ == '__main__':
    run()

