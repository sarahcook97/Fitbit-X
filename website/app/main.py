# main.py. 

import os
from app import app
from flask import Flask, flash, request, redirect, render_template, Markup
from werkzeug.utils import secure_filename
import pandas as pd 
import numpy as np
import datetime
import math
import zipfile
import json 

app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_EXTENSIONS = set(['csv','zip'])
#change to only allow zip and csv. edit so it can do different things for zip or csv stuff

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/howitworks')
def howitworks():
    return render_template("howitworks.html")

@app.route('/howitworks', methods=['GET','POST'])
def upload_file():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename) and file.filename.rsplit('.')[1].lower() == 'zip':
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			zip_ref = zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r')
			zip_ref.extractall(app.config['UPLOAD_FOLDER'])
			zip_ref.close()
			flash('Zip File successfully uploaded')
			#jsonToCSV()
			return redirect('/results')
		if file and allowed_file(file.filename) and file.filename.rsplit('.')[1].lower() == 'csv':
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			flash('CSV File successfully uploaded')
			return redirect('/results') #csv stuff works, only zip file is fucked up :(

        
def sleep(sleepDF):
    lightmins = sleepDF['minutesAsleep']
    timebed = sleepDF['timeInBed']
    return lightmins, timebed
    
# ----- CLEANING SECTION -----         
def jsonToCSV():
    path_to_json = 'uploads/Adele Bloch/user-site-export'   #issue that i am calling it sarah 
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json') and not pos_json.startswith('badge')]
    grouped = group_files(json_files)
    finalDF = form_dataframes(grouped)
    finalDF = check_and_add_datetime(finalDF)
    temp_filenames = ['df1.pk1','df2.pk1','df3.pk1','df4.pk1','df5.pk1','df6.pk1','df7.pk1','df8.pk1','df9.pk1','df10.pk1','df11.pk1','df12.pk1','df13.pk1','df14.pk1','df15.pk1','df16.pk1','df17.pk1']
    for i in range(len(temp_filenames)):
        finalDF[i].to_pickle('./uploads/' + temp_filenames[i])
    return finalDF
                      
                      
def first_3_letters(string):
    return string[0:3]

#Takes in a list of strings, extracts the first three objects of each string, and returns a list of unique values from
#the extracted values.
def unique_first_3(alist): 
    result = []
    for i in alist:
        result.append(first_3_letters(i))
    return list(set(result))

#Takes in a list of filenames and groups them according to the first three letters of the filename.
def group_files(list_files):
    starts = unique_first_3(list_files)
    copy_json_files = list_files
    
    grouped_files = [[] for i in range(len(starts))]
    for i in range(len(starts)):
        for j in range(len(list_files)):
            if (starts[i] == first_3_letters(copy_json_files[j])):
                grouped_files[i].append(copy_json_files[j])
    return grouped_files

def form_dataframes(grouped_list):
    path_to_json1 = 'uploads/Adele Bloch/user-site-export/'
    dataframes = [[] for i in range(len(grouped_list))]
    final_dfs = []      
    
    #converts the filenames to dataframes
    for i in range(len(grouped_list)):
        with open(path_to_json1 + grouped_list[i][0], 'r') as first:
            first_filename = json.load(first)
            df1 = pd.DataFrame(first_filename)
            dataframes[i].append(df1)
        for j in range(1, len(grouped_list[i])):
            with open(path_to_json1 + grouped_list[i][j], 'r') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                dataframes[i].append(df)
    
    #combines all similar dataframes
    for i in range(len(dataframes)):
        final_dfs.append(pd.concat(dataframes[i], sort=True))
    
    return final_dfs

#input is a date as a string. returns a datetime object
def separate_datetime(date):
    return datetime.datetime.strptime(date, '%m/%d/%y %H:%M:%S')

#returns day of week as integer for reference --> {0: Sunday,...., 6:Saturday}
def weekday(date):
    return datetime.datetime.strptime(date, '%m/%d/%y %H:%M:%S').weekday()

#inputs day of week as integer. 
def is_weekend(day):
    if day == 0 or day == 6:
        return True
    else:
        return False

def month(date):
    return datetime.datetime.strptime(date, '%m/%d/%y %H:%M:%S').month

def day_of_month(date):
    return datetime.datetime.strptime(date, '%m/%d/%y %H:%M:%S').day
    
def year(date):
    return datetime.datetime.strptime(date, '%m/%d/%y %H:%M:%S').year
    
def hour(date):
    return datetime.datetime.strptime(date, '%m/%d/%y %H:%M:%S').hour
    
def minute(date):
    return datetime.datetime.strptime(date, '%m/%d/%y %H:%M:%S').minute

def second(date):
    return datetime.datetime.strptime(date, '%m/%d/%y %H:%M:%S').second

#input dataframe with 'dateTime' column, adds date features to dataframe
def add_date_features(dataframe):
    
    series = dataframe['dateTime']
        
    dataframe['Day of Week'] = series.apply(weekday)
    dataframe['Is Weekend'] = dataframe['Day of Week'].apply(is_weekend)
    dataframe['Month'] = series.apply(month)
    dataframe['Day'] = series.apply(day_of_month)
    dataframe['Year'] = series.apply(year)
    dataframe['Hour'] = series.apply(hour)
    dataframe['Minute'] = series.apply(minute)
    dataframe['Second'] = series.apply(second)
    return dataframe

#Takes in a list of dataFrames and separates dateTime value adds these values as new columns
#dataframes w/o dataTime columns --> 1, 5, 7
def check_and_add_datetime(list_of_dataframes):
    a_list = list_of_dataframes
    
    for i in range(len(a_list)):
        if 'dateTime' in a_list[i].columns:
            a_list[i] = add_date_features(a_list[i])
    return a_list

# ----- END CLEANING SECTION ----- 

@app.route('/results')
def results():
    #finalDFs = jsonToCSV()
    lightmins, timebed = sleep(pd.read_pickle("./uploads/df11.pk1"))
    legend = ['Yay']
    labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    values = [2424, 2306, 2311, 2404, 2658, 2718, 2462, 2470, 2313, 2248, 2300, 2293]
    
    return render_template('results.html', values=values, labels=labels, legend=legend)


if __name__ == "__main__":
    app.run()