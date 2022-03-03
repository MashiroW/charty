from ensurepip import version
import os
import time
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime
from datetime import timedelta, date
from discord_webhook import DiscordWebhook

def watch_for_day_weeks(TargetDate, kind=''):
    # -------SETUP------------
    global client_info
    global version  

    if kind == 'daily':
        cmd_arg = str(TargetDate + timedelta(days=-1))
        save_dir = "./plots/daily"
        pic_name = str(TargetDate + timedelta(days=-1)) + "_day.png"
        fig_name = "Distribution of the time where WE BOTH sent our messages today ("+ str(date.today() + timedelta(days=-1)) + ")"
        log_over_message = "----- Daily stats sent\n\n"
        plot_color = 'lightsteelblue'
        new_TargetDate = TargetDate + timedelta(days=+1)
    
    elif kind == 'weekly':
        cmd_arg = str(TargetDate + timedelta(weeks=-1))
        save_dir = "./plots/weekly"
        pic_name = str(TargetDate + timedelta(weeks=-1)) + "_week.png"
        fig_name = "Distribution of the time where WE BOTH sent our messages this week ("+ str(date.today() + timedelta(weeks=-1)) + " -> " + str(date.today()) +")"
        log_over_message = "----- Weekly stats sent\n\n"
        plot_color = 'orange'
        new_TargetDate = TargetDate + timedelta(weeks=+1)

    else:
        print("Missing or incorrect arguement")

 # -------SAVING AND OPENING THE DATASET------------
    write_log("----- Retrieving the dataset...") #~
    os.system("dotnet ./DiscordChatExporter/DiscordChatExporter.Cli.dll export -t " + client_info["token"] + " -c " + client_info["channel_ID"] + " --after " + cmd_arg + " -f csv -o dataset.csv")

    write_log("----- Opening the dataset...") #~
    df = pd.read_csv('dataset.csv')

 # -------PARSING THE DATASET------------
    write_log("----- Parsing the chat...") #~

    users_data = {}

    for a in range (0,len(df)):
        msg_authorName = str(df["Author"][a])
        msg_authorID = str(df["AuthorID"][a])
        msg_date   = str(df["Date"][a].split(" ")[1][0:2] + " " +  df["Date"][a].split(" ")[2])

        if msg_authorID in client_info["users_to_watch"] or (len(client_info["users_to_watch"]) == 0 and msg_authorID not in client_info["users_to_ignore"]):
            try:
                users_data[msg_authorName][msg_date] += 1
            except:
                if msg_authorName not in users_data:
                    users_data[msg_authorName] = {}
                
                users_data[msg_authorName][msg_date] = 1

    order = ["12 AM", "01 AM", "02 AM", "03 AM", "04 AM", "05 AM", "06 AM", "07 AM", "08 AM", "09 AM", "10 AM", "11 AM", "12 PM", "01 PM", "02 PM", "03 PM", "04 PM", "05 PM", "06 PM", "07 PM", "08 PM", "09 PM", "10 PM", "11 PM"]
    sorted_vals = {}
    
    for username in users_data:
        if username not in sorted_vals:
            sorted_vals[username] = []

        for a in range (0, len(order)):
            try:
                sorted_vals[username].append(users_data[username][order[a]])
            except:
                sorted_vals[username].append(0)

    merged_arrays = [0] * len(order)
    for array_to_merge in sorted_vals:
        print(sorted_vals[array_to_merge])
        merged_arrays = [a + b for a, b in zip(merged_arrays, sorted_vals[array_to_merge])]

 # -------CREATING AND SAVING THE PLOT------------
    write_log("----- Drawing a pretty  bar plot...") #~
    bar_plot(x=order, y=merged_arrays, color=plot_color, save_dir=save_dir, pic_name=pic_name, xlabel="Hour", ylabel="Number of messages", title=fig_name)
    write_log("----- File saved !")  #~
 
 # -------SENDING TO DISCORD------------
    write_log("----- Sending the plot to Discord in channel #stats...")
    message = "`Charty - Marketing Dpt. v" + version + "`\n" + "`[" + now.strftime("%H:%M:%S") + "] - " + pic_name + "`"

    picture_to_discord(path=save_dir + "/" + pic_name, webhook_URL=client_info["webhook_url"], message=message)
    picture_to_discord(path=None, webhook_URL=client_info["webhook_url"], message=pie_chart_txt(users_data=users_data))

    print(log_over_message)

 # -------RETURNING THE NEW DATE TO WATCH------------
    time.sleep(3)
    return new_TargetDate

def write_log(message):
    logs_file = open('logs.txt', 'a+')
    logs_file.write("[" + datetime.now().strftime("%H:%M:%S") + "] - " + message + "\n")
    print(message)
    logs_file.close()

def get_user_profile(path = ''):
    with open("settings.json") as json_file:
        json_data = json.load(json_file)

        if json_data["token"] == "" or json_data["channel_ID"] == "" or json_data["webhook_url"] == "":
            write_log("Error: No specified IDs, please fill the 'settings.json' file.")
            exit()            

        return json_data

def picture_to_discord(path, webhook_URL, message):
    webhook = DiscordWebhook(url=webhook_URL, username="Charty - Marketing Dpt.", content = message)

    if path != None:
        with open(path , "rb") as f:
            webhook.add_file(file=f.read(), filename=path.split("/")[-1])
    
    webhook.execute()

def bar_plot(x, y, color, save_dir, pic_name, xlabel, ylabel, title):
    plt.style.use('dark_background')
    plt.rcParams.update({'font.size': 10})
    plt.rcParams["figure.figsize"] = (30, 12)
    plt.bar(x, y, align='center', width=0.5, color=color)   
    plt.xlabel(xlabel)              
    plt.ylabel(ylabel)
    plt.title(title)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    plt.savefig(save_dir + "/" + pic_name)

def pie_chart_txt(users_data):

    length   = 32
    done     = ":"
    not_done = ":"
    cursor   = "|"
    
    pie_chart_string = ""

    msgs_count = {}

    for user in users_data:
        msgs_count[user] = sum(users_data[user].values())

    for user in users_data:

        tick_value = 100/length
        user_percentage = (msgs_count[user] / sum(msgs_count.values())) * 100

        # LINE 1
        line1 = "`"
        line1 += str(format(user_percentage, '.2f')) + "%" + " - " + str(user)

        if user_percentage < 10:
            line1 += " "

        while len(line1) < length:
            line1 += " "

        line1 += "`"

        # LINE 2
        line2 = "`"
        for a in range (1,length):
            
            if tick_value * (a+1) < user_percentage:
                line2 += done

            elif tick_value * a < user_percentage:
                line2 += cursor

            elif tick_value * a > user_percentage:
                line2 += not_done
        
        line2 += "`"

        pie_chart_string += line1 + "\n" + line2 + "\n\n"         
    
    return pie_chart_string

global version        
version = "1.1"

global client_info    
client_info = get_user_profile()

Date_at_launch = date.today()
DayTargetDate  = Date_at_launch + timedelta(days=1)
WeekTargetDate = Date_at_launch #+ timedelta(weeks=1)

#CUSTOMIZE WEEK START DATE
WeekTargetDate = datetime(2022, 3, 7).date()
#------------------------

write_log("Started !")

while (1):
    # LOGS
    now = datetime.now()
    time.sleep(5)
    log_msg = str("DayTargetDate: " + str(DayTargetDate) + " -- WeekTargetDate: " + str(WeekTargetDate))
    write_log(log_msg)

    # CHECK FOR DAILY
    if str(date.today()) == str(DayTargetDate):
        write_log("Daily plot condition OK")
        DayTargetDate = watch_for_day_weeks(DayTargetDate, kind='daily')

    # CHECK FOR WEEKLY
    if str(date.today()) == str(WeekTargetDate):
        write_log("Weekly plot condition OK")
        WeekTargetDate = watch_for_day_weeks(WeekTargetDate, kind='weekly')