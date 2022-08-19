#!/usr/bin/env python
# coding: utf-8

from datetime import date, datetime, timedelta

import numpy as np
import mlflow
import pandas as pd
from prefect import flow, task, get_run_logger
from sklearn.metrics import mean_squared_error
from pandas._libs.tslibs.timestamps import Timestamp


def preprocess(df, TARGETS=None, loc_group=None):
    """
    Preprocess the dataframe: filling NaNs, ...
    """
    if TARGETS is None:
        TARGETS = ["ConfirmedCases", "Fatalities"]
    if loc_group is None:
        loc_group = ["Province_State", "Country_Region"]

    df["Date"] = df["Date"].astype("datetime64[ms]")
    for col in loc_group:
        df[col].fillna("none", inplace=True)  # NOTE: replace all NaN with none
    for col in TARGETS:
        df[col] = np.log1p(df[col])
    for col in TARGETS:
        df["prev_{}".format(col)] = df.groupby(loc_group)[
            col
        ].shift()  # NOTE: the prev_ columns basically has the same than the others but delayed one day
    return df


def create_output(df, TARGETS=None):  # To have the same format as the original input
    """
    Adds output columns to the dataframe with the same units as the original input
    """
    if TARGETS is None:
        TARGETS = ["ConfirmedCases", "Fatalities"]

    for col in TARGETS:
        df["pred_out_{}".format(col)] = np.expm1(df["pred_{}".format(col)])
    return df


def get_data_last_days(num_days):
    """
    Gets the data from the last "num_days" days
    """
    num_days = (
        num_days + 2
    )  # I do this because I get rid of the first date since it has NaNs in the columns prev_ConfirmedCases	prev_Fatalities and
    # because of the for loop with range
    dfs = []  # empty list which will hold your dataframes
    for d in range(
        1, num_days
    ):  # NOTE: do the same that has been done for the first day but for the whole period
        date_now = datetime.now() - timedelta(days=d)
        date_str = date_now.strftime("%m-%d-%Y")
        source_url = (
            "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"
            + date_str
            + ".csv"
        )
        df_temp = pd.read_csv(source_url)
        df_temp.rename(
            columns={"Last_Update": "Date"}, inplace=True
        )  # Renane dataframe column from "Last_Update" to "Date"
        df_temp_2 = df_temp[
            ["Admin2", "Province_State", "Country_Region", "Confirmed", "Deaths"]
        ].copy()  # TODO: consider also other columns in future versions
        # like Recovered,Active,Combined_Key,Incident_Rate,Case_Fatality_Ratio
        df_temp_2.loc[:, "Date"] = date_now.strftime("%Y-%m-%d")
        dfs.append(df_temp_2)  # append dataframe to list
    res = pd.concat(dfs, ignore_index=True)  # concatenate list of dataframes

    # group by Country_Region and sum Confirmed and Deaths
    df = res.groupby(["Province_State", "Country_Region", "Date"]).agg(
        {"Confirmed": "sum", "Deaths": "sum"}
    )
    df.reset_index(inplace=True)
    df.rename(
        columns={"Confirmed": "ConfirmedCases", "Deaths": "Fatalities"}, inplace=True
    )
    df = preprocess(df)
    df = df[
        df["Date"] > df["Date"].min()
    ].copy()  # removes the first day since it has NaNs in the "prev" columns
    df.reset_index(inplace=True, drop=True)

    return df


@task
def predict_today_province_state(model, province_state, df):
    """
    Predicts the cases for today for a given Province.
    """
    y_pred = predict_today_world(model)  # Predict today worldwide
    index_ps = df[df["Province_State"] == province_state].iloc[0].name
    predictions = y_pred[index_ps]
    return predictions  # First the predicted Confirmed cases and second the predicted fatalities


def predict_today_world(model, features=None):  # Does the prediction for today
    """
    Predicts the cases for today for a the whole world.
    """
    if features is None:
        features = ["prev_ConfirmedCases", "prev_Fatalities"]
    df = get_data_last_days(1)  # Get data from yesterday
    yesterday = datetime.now() - timedelta(days=1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = Timestamp(yesterday)
    y_pred = np.clip(model.predict(df.loc[df["Date"] == yesterday][features]), None, 16)
    # NOTE: here predicting the targets for the first day and saturating (clip) them with max=16
    return y_pred


@task
def evaluate_yesterday(model):
    """
    Evaluate the RMSE for the yesterday
    """
    return evaluate_last_days(model, 1)


def rmse(y_true, y_pred):
    """
    Calculates the RMSE
    """
    return np.sqrt(mean_squared_error(y_true, y_pred))


def predict_past(model, num_days, TARGETS=None, features=None):
    """
    Makes predictions for the last "num_days" days.
    """
    if TARGETS is None:
        TARGETS = ["ConfirmedCases", "Fatalities"]
    if features is None:
        features = ["prev_ConfirmedCases", "prev_Fatalities"]
    test_df = get_data_last_days(num_days)
    first_day = datetime.now() - timedelta(days=num_days)
    first_day = first_day.replace(hour=0, minute=0, second=0, microsecond=0)
    first_day = Timestamp(first_day)
    y_pred = np.clip(
        model.predict(test_df.loc[test_df["Date"] == first_day][features]), None, 16
    )
    # NOTE: here he is predicting the targets for the first day and saturating (clip) them with max=16

    for i, col in enumerate(TARGETS):
        test_df["pred_{}".format(col)] = 0
        test_df.loc[test_df["Date"] == first_day, "pred_{}".format(col)] = y_pred[
            :, i
        ]  # NOTE: here he sets the predicted column
    for d in range(
        1, num_days
    ):  # NOTE: do the same that has been done for the first day but for the whole period
        y_pred = np.clip(model.predict(y_pred), None, 16)
        date_temp = first_day + timedelta(days=d)
        for i, col in enumerate(TARGETS):
            test_df.loc[test_df["Date"] == date_temp, "pred_{}".format(col)] = y_pred[
                :, i
            ]

    test_df = create_output(test_df)
    return test_df


def evaluate_last_days(model, num_days, TARGETS=None):
    """
    Evaluate the RMSE for the last "num_days" days
    """
    if TARGETS is None:
        TARGETS = ["ConfirmedCases", "Fatalities"]

    # get data from the last "num_days" days
    df = predict_past(model, num_days)

    # get the rmse
    error = 0
    for col in TARGETS:
        error += rmse(
            df[col].values, df["pred_{}".format(col)].values
        )  # NOTE: checks the error between the predicted columns and the target columns
    return np.round(error / len(TARGETS), 5)


@task
def load_model(run_id):
    logged_model = f"s3://mlflow-artifacts-remote-jaime/4/{run_id}/artifacts/models"
    model = mlflow.pyfunc.load_model(logged_model)
    return model


@task
def get_output_path(Province_State, run_id):
    run_date = date.today()
    year = run_date.year
    month = run_date.month
    day = run_date.day
    output_file = f"s3://covid-predictons-jaime/{Province_State}_predictions_{year:04d}-{month:02d}-{day:02d}/{run_id}.csv"
    return output_file


@task
def get_output_path_monitoring(run_id):
    run_date = date.today()
    year = run_date.year
    month = run_date.month
    day = run_date.day
    output_file = f"s3://covid-predictons-jaime/RSMME_evaluated_at_{year:04d}-{month:02d}-{day:02d}/{run_id}.csv"
    return output_file


@flow
def covid_prediction(Prov_St: str, run_id: str):
    output_file = get_output_path(Prov_St, run_id)

    logger = get_run_logger()
    logger.info(
        f">>>>>>>>>>>>>>>>>> Getting COVID data from yesterday from CSSE at Johns Hopkins University's Github ..."
    )
    df = get_data_last_days(1)  # Get data from yesterday

    logger.info(f">>>>>>>>>>>>>>>>>> Loading the model with RUN_ID={run_id}...")
    model = load_model(run_id)

    logger.info(f">>>>>>>>>>>>>>>>>> Applying the model...")
    predictions = predict_today_province_state(
        model, Prov_St, df
    )  # Returns first the predicted Confirmed cases and second the predicted fatalities

    logger.info(f">>>>>>>>>>>>>>>>>> Saving the result to {output_file}...")
    df_result = pd.DataFrame()
    df_result["Province_State"] = pd.Series(Prov_St)
    df_result["Date"] = pd.Series(date.today())
    df_result["pred_out_ConfirmedCases"] = pd.Series(
        np.expm1(predictions[0])
    )  # TODO: instead of doing the exp here, call create_output inside the pred_today_* functions
    df_result["pred_out_Fatalities"] = pd.Series(
        np.expm1(predictions[1])
    )  # TODO: instead of doing the exp here, call create_output inside the pred_today_* functions
    df_result["model_version"] = run_id
    df_result.to_csv(output_file, index=False)

    logger.info(f">>>>>>>>>>>>>>>>>> Finished succesfully!")


@flow
def monitor(run_id: str):
    output_file_monitoring = get_output_path_monitoring(run_id)

    logger = get_run_logger()

    logger.info(f">>>>>>>>>>>>>>>>>> Loading the model with RUN_ID={run_id}...")
    model = load_model(run_id)

    logger.info(f">>>>>>>>>>>>>>>>>> Loading the model with RUN_ID={run_id}...")
    eval_rmse = evaluate_yesterday(model)

    logger.info(
        f">>>>>>>>>>>>>>>>>> Saving the monitoring result to {output_file_monitoring}..."
    )
    df_result_monitoring = pd.DataFrame()
    df_result_monitoring["Date"] = pd.Series(date.today())
    df_result_monitoring["model_version"] = run_id
    df_result_monitoring["RMSE"] = eval_rmse
    df_result_monitoring.to_csv(output_file_monitoring, index=False)

    logger.info(f">>>>>>>>>>>>>>>>>> Finished succesfully!")
