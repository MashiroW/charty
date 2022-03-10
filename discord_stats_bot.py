import glob
from ensurepip import version

import os
import time
import json
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime
from datetime import timedelta, date
from discord_webhook import DiscordWebhook

def sending_procedure(TargetDate, kind=''):
    # -------SETUP------------
    global client_info
    global version  

    if kind == 'daily':
        cmd_arg = str(TargetDate + timedelta(days=-1))
        save_dir = "./plots/daily"
        pic_name = str(TargetDate + timedelta(days=-1)) + "_day.png"
        fig_name = "Distribution of the time where we sent our messages today ("+ str(date.today() + timedelta(days=-1)) + ")"
        log_over_message = "----- Daily stats sent\n\n"
        plot_color = 'lightsteelblue'
        new_TargetDate = TargetDate + timedelta(days=+1)
    
    elif kind == 'weekly':
        cmd_arg = str(TargetDate + timedelta(weeks=-1))
        save_dir = "./plots/weekly"
        pic_name = str(TargetDate + timedelta(weeks=-1)) + "_week.png"
        fig_name = "Distribution of the time where we sent our messages this week ("+ str(date.today() + timedelta(weeks=-1)) + " -> " + str(date.today()) +")"
        log_over_message = "----- Weekly stats sent\n\n"
        plot_color = 'orange'
        new_TargetDate = TargetDate + timedelta(weeks=+1)

    else:
        print("Missing or incorrect arguement")

 # -------SAVING AND OPENING THE DATASET------------
    write_log("----- Retrieving the dataset...") #~

    if client_info["channel_ID"] != []:
        channels_string = ""
        for channel in client_info["channel_ID"]:
            channels_string += channel + " "

        print(channels_string)
        os.system("dotnet ./DiscordChatExporter/DiscordChatExporter.Cli.dll export -t " + client_info["token"] + " -c " + channels_string + "--after " + cmd_arg + " -f csv -o channels/%C.csv")

    else:
        os.system("dotnet ./DiscordChatExporter/DiscordChatExporter.Cli.dll exportguild -t " + client_info["token"] + " -g " + client_info["server_ID"] + " --after " + cmd_arg + " -f csv -o channels/%C.csv")

    path = r'./channels' # use your path
    all_files = glob.glob(path + "/*.csv")

    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)
        
    df = pd.concat(li, axis=0, ignore_index=True)
    df.to_csv('dataset.csv', index=False)

    write_log("----- Opening the dataset...") #~
    df = pd.read_csv('dataset.csv')

 # -------PARSING THE DATASET------------
    write_log("----- Parsing the chat...") #~
    x_hours, y_hours, x_ratio, y_ratio = get_user_hours(df)
    
 # -------CREATING AND SAVING THE PLOT------------
    write_log("----- Drawing hours bar plot...") #~
    bar_plot(x=x_hours, y=y_hours, color=plot_color, save_dir=save_dir, pic_name=pic_name, xlabel="Hour", ylabel="Number of messages", title=fig_name)
    write_log("----- Chart #1 saved !")  #~

    write_log("----- Drawing ratio bar plot...") #~
    hbar_plot(x_ratio, y_ratio, save_dir, pic_name)
    write_log("----- Chart #2 saved !")  #~
 
 # -------SENDING TO DISCORD------------
    write_log("----- Sending the plots to Discord the discord channel...")

    #CHART 1
    message = "`Charty - Marketing Dpt. v" + version + " - by Mashiro ☯#8770" + "`\n" + "`[" + now.strftime("%H:%M:%S") + "] - " + pic_name + "`"
    picture_to_discord(path=save_dir + "/" + pic_name, webhook_URL=client_info["webhook_url"], message=message)
    write_log("----- Chart #1 sent...")

    #CHART 2
    picture_to_discord(path=save_dir + "/" + pic_name[0:-4] + "_leaderboard" + pic_name[-4:], webhook_URL=client_info["webhook_url"], message="")
    write_log("----- Chart #2 sent...")

    #picture_to_discord(path=None, webhook_URL=client_info["webhook_url"], message=pie_chart_txt(users_hours=users_hours)) #LINE FOR TXT PLOT
    print(log_over_message)

 # -------RETURNING THE NEW DATE TO WATCH------------
    time.sleep(10)
    return new_TargetDate

def write_log(message):
    logs_file = open('logs.txt', 'a+')
    logs_file.write("[" + datetime.now().strftime("%H:%M:%S") + "] - " + message + "\n")
    print(message)
    logs_file.close()

def get_user_profile(path = ''):
    with open("settings.json") as json_file:
        json_data = json.load(json_file)

        if json_data["token"] == "" or json_data["webhook_url"] == "" or (json_data["server_ID"] == "" and json_data["channel_ID"] == []):
            write_log("Error: No specified IDs, please fill the 'settings.json' file.")
            exit()            

        elif json_data["server_ID"] != "" and json_data["channel_ID"] != []:
            write_log("Error: Either specify a server_ID or channel_ID(s) the 'settings.json' file.")
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
    plt.clf()

def pie_chart_txt(users_hours):

    length   = 32
    done     = ":"
    not_done = ":"
    cursor   = "|"
    
    pie_chart_string = ""

    msgs_count = {}

    for user in users_hours:
        msgs_count[user] = sum(users_hours[user].values())

    for user in users_hours:

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

def version_check():
    global version

    response = requests.get("https://api.github.com/repos/MashiroW/charty/releases/latest")
    lastest = str(response.json()["name"].split(" ")[0])[1:]

    if version != lastest:
        print("Warning: A newer version of Charty (v" + lastest + ") is avaiable, this one could be outdated.")
        print("-------  You can either download it from: https://github.com/MashiroW/charty/releases")
        print("-------  Or you can run the 'git clone https://github.com/MashiroW/charty' command.")

def hbar_plot(x, y, save_dir, pic_name): # PLOTS THE HORIZONTAL BAR PLOT OF USERS PERCENTAGE
    global version

    sorted_x = []
    sorted_y = []

    users_limit = 25

    # SORTING X INTO SORTED X || SORTING Y INTO SORTED Y
    for a in range(0,len(y)):
        if a == users_limit:
            break

        elif a == 0:
            sorted_x.append(x[a])
            sorted_y.append(y[a])

        else:
            for b in range(0, len(sorted_y)):
                if y[a] >= sorted_y[b]:
                    sorted_x.insert(b, x[a])
                    sorted_y.insert(b, y[a])
                    break

                elif b == len(sorted_y)-1:
                    sorted_x.insert(b+1, x[a])
                    sorted_y.insert(b+1, y[a])

    # LABELING THE USERS
    for a in range(0, len(sorted_x)):
        sorted_x[a] = sorted_x[a] + " - " + str(a+1) + ""

   # INVERSING THE TABLES TO HAVE THEM ORDERED IN THE PLOT WITH THE HIGHEST ON TOP
    sorted_x.reverse()
    sorted_y.reverse()

    # PERCENTAGES TABLE
    percentages = []
    for a in range(0, len(sorted_y)):
        percentages.append((sorted_y[a]/sum(sorted_y))*100)

    # PLOTTING
    plt.style.use('dark_background')
    plt.rcParams.update({'font.size': 10})
    plt.rcParams["figure.figsize"] = (30, 12)
    plt.barh(sorted_x, percentages, align='center', height=0.2, color="red")   

    for i, v in enumerate(percentages):
        print(v, i)
        textcolor = "blue"
        size = 8

        if i == len(percentages) - 1:
            textcolor = "yellow"
            size = 13
        elif i == len(percentages) - 2:
            textcolor = "orange"
            size = 12
        elif i == len(percentages) - 3:
            textcolor = "cyan"
            size = 11

        plt.text(v + 0.02 , i, str(float("{:.2f}".format(v))) + "%", color=textcolor, fontname="Consolas" , fontweight="bold", fontsize=size)

    plt.xlabel("Proportion of messages")              
    plt.ylabel("User")
    plt.title("Top 25 of the users sending the more messages")
    #plt.text(0.02 , -1 , "Charty - Marketing Dpt. v" + version + " - by Mashiro ☯#8770", color='lightgrey', fontsize=8)
    #plt.show()

    #SAVING
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    path_pic = save_dir + "/" + pic_name[0:-4] + "_leaderboard" + pic_name[-4:]
    plt.savefig(path_pic)
    plt.clf()

def get_user_hours(df): #returns 2 arrays - x (hours), y (number of msgs)

    users_hours = {}
    users_ratio = {}

    for a in range (0,len(df)):
        msg_authorName = str(df["Author"][a])
        msg_authorID = str(df["AuthorID"][a])
        msg_hour   = str(df["Date"][a].split(" ")[1][0:2] + " " +  df["Date"][a].split(" ")[2])

        if msg_authorID in client_info["users_to_watch"] or (len(client_info["users_to_watch"]) == 0 and msg_authorID not in client_info["users_to_ignore"]):
            # users_hours here
            try:
                users_hours[msg_authorName][msg_hour] += 1
            except:
                #if msg_authorName not in users_hours: #CONDITION RETIREE CAR IMPLIQUEE SELON MOI
                users_hours[msg_authorName] = {}
                users_hours[msg_authorName][msg_hour] = 1

            # users_ratio here
            try:
                users_ratio[msg_authorName] += 1
            except:
                users_ratio[msg_authorName] = 1

    # HOUR FREQUENCY PLOT
    order = ["12 AM", "01 AM", "02 AM", "03 AM", "04 AM", "05 AM", "06 AM", "07 AM", "08 AM", "09 AM", "10 AM", "11 AM", "12 PM", "01 PM", "02 PM", "03 PM", "04 PM", "05 PM", "06 PM", "07 PM", "08 PM", "09 PM", "10 PM", "11 PM"]
    sorted_vals = {}
    
    for username in users_hours:
        if username not in sorted_vals:
            sorted_vals[username] = []

        for a in range (0, len(order)):
            try:
                sorted_vals[username].append(users_hours[username][order[a]])
            except:
                sorted_vals[username].append(0)

    merged_arrays = [0] * len(order)
    for array_to_merge in sorted_vals:
        print(sorted_vals[array_to_merge])
        merged_arrays = [a + b for a, b in zip(merged_arrays, sorted_vals[array_to_merge])]

    # RATIO PLOT
    names = []
    percentages = []

    for user in users_ratio:
        names.append(user)
        percentages.append(users_ratio[user])


    return order, merged_arrays, names, percentages

global version        
version = "1.2"
version_check()

global client_info    
client_info = get_user_profile()

Date_at_launch = date.today()
DayTargetDate  = Date_at_launch + timedelta(days=1)
WeekTargetDate = Date_at_launch + timedelta(weeks=1)

#CUSTOMIZED WEEK START DATE
write_log("Checking for custom dates...")
if client_info["custom_date_daily"] != "":
    try:
        target = client_info["custom_date_daily"].split("-")
        DayTargetDate = datetime(int(target[0]), int(target[1]), int(target[2])).date()
    except:
        print("Error: Make sure you have the right date format: YYYY-MM-DD")

if client_info["custom_date_weekly"] != "":
    try:
        target = client_info["custom_date_weekly"].split("-")
        WeekTargetDate = datetime(int(target[0]), int(target[1]), int(target[2])).date()
    except:
        print("Error: Make sure you have the right date format: YYYY-MM-DD")
#------------------------

write_log("Started !")

while (1):
    # LOGS
    log_msg = str("DayTargetDate: " + str(DayTargetDate) + " -- WeekTargetDate: " + str(WeekTargetDate))
    write_log(log_msg)

    # CURRENT DATE REFRESH
    now = datetime.now()

    # CHECK FOR DAILY
    if str(date.today()) == str(DayTargetDate):
        write_log("Daily plot condition OK")
        DayTargetDate = sending_procedure(DayTargetDate, kind='daily')

    # CHECK FOR WEEKLY
    if str(date.today()) == str(WeekTargetDate) and client_info["weekly"]:
        write_log("Weekly plot condition OK")
        WeekTargetDate = sending_procedure(WeekTargetDate, kind='weekly')

    time.sleep(10)
