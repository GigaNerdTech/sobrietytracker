import discord
import re
import mysql.connector
from mysql.connector import Error
import urllib.request
import subprocess
import time
import requests
import random
from discord.utils import get
import discord.utils
from datetime import datetime
from discord import Webhook, RequestsWebhookAdapter, File
import csv

client = discord.Client()

async def calculate_role(check_date):
    now = datetime.now()
    roles = ["One Day Sober","One Week Sober","One Month Sober","Two Months Sober","Three Months Sober","Four Months Sober","Six Months Sober","Nine Months Sober","One Year Sober","Two Years Sober","Three Years Sober","Five Years Sober","Ten Years Sober","Fifteen Years Sober","20+ years Sober"]
    
    date_to_check = datetime.strptime(check_date, '%Y-%m-%d')
    delta_time = now - date_to_check
    days_delta = delta_time.days
    
    if days_delta >= 1 and days_delta <=6:
        return "One Day Sober"
    elif days_delta >= 7 and days_delta <= 29:
        return "One Week Sober"
    elif days_delta >= 30 and days_delta <= 59:
        return "One Month Sober"
    elif days_delta >= 60 and days_delta <= 89:
        return "Two Months Sober"
    elif days_delta >= 90 and days_delta <= 119:
        return "Three Months Sober"
    elif days_delta >= 120 and days_delta <= 179:
        return "Four Months Sober"
    elif days_delta >= 180 and days_delta <= 269:
        return "Six Months Sober"
    elif days_delta >= 270 and days_delta <= 364:
        return "Nine Months Sober"
    elif days_delta >= 365 and days_delta <= 729:
        return "One Year Sober"
    elif days_delta >= 730 and days_delta <= (365 * 3) - 1:
        return "Two Years Sober"
    elif days_delta >= (365 * 3) and days_delta <= (365 * 5) -1:
        return "Three Years Sober"
    elif days_delta >= (365 * 5) and days_delta <= (365 * 10) -1:
        return "Five Years Sober"
    elif days_delta >= (365 * 10) and days_delta <= (365 * 15) -1:
        return "Ten Years Sober"
    elif days_delta >= (365 * 15) and days_delta <= (365 * 20) - 1:
        return "Fifteen Years Sober"
    elif days_delta >= 365 * 20:
        return "20+ years Sober"
    else:
        return "None"
    
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='SobrietyTracker', user='REDACTED', password='REDACTED')    
        cursor = connection.cursor()
        result = cursor.execute(sql_query, params)
        connection.commit()
        return True
    except mysql.connector.Error as error:
        await log_message("Database error! " + str(error))
        return False
    finally:
        if(connection.is_connected()):
            cursor.close()
            connection.close()
            
                
async def select_sql(sql_query, params = None):
    await log_message("Select SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='SobrietyTracker', user='REDACTED', password='REDACTED')
        cursor = connection.cursor()
        result = cursor.execute(sql_query, params)
        records = cursor.fetchall()
        await log_message("Returned " + str(records))
        return records
    except mysql.connector.Error as error:
        await log_message("Database error! " + str(error))
        return None
    finally:
        if(connection.is_connected()):
            cursor.close()
            connection.close()

async def execute_sql(sql_query):
    try:
        connection = mysql.connector.connect(host='localhost', database='SobrietyTracker', user='REDACTED', password='REDACTED')
        cursor = connection.cursor()
        result = cursor.execute(sql_query)
        return True
    except mysql.connector.Error as error:
        await log_message("Database error! " + str(error))
        return False
    finally:
        if(connection.is_connected()):
            cursor.close()
            connection.close()
            
       
async def post_webhook(message, name, response, picture):
    temp_webhook = await message.channel.create_webhook(name='Chara-Tron')
    await temp_webhook.send(content=response, username=name, avatar_url=picture)
    await message.delete()
    await temp_webhook.delete() 
    
async def reply_message(message, response):
    if not message.guild:
        channel_name = dm_tracker[message.author.id]["commandchannel"].name
        server_name = str(dm_tracker[message.author.id]["server_id"])
    else:
        channel_name = message.channel.name
        server_name = message.guild.name
        
    await log_message("Message sent back to server " + server_name + " channel " + channel_name + " in response to user " + message.author.name + "\n\n" + response)
    
    message_chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
    for chunk in message_chunks:
        await message.channel.send(">>> " + chunk)
        time.sleep(1)
        
@client.event
async def on_ready():
    await log_message("Logged into Discord!")
    
@client.event
async def on_guild_join(guild):
    await log_message("Joined guild " + guild.name)
    
@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name)

@client.event
async def on_message(message):
    invite_url = "https://discordapp.com/api/oauth2/authorize?client_id=702681888250396743&permissions=268520512&scope=bot"
    roles = ["One Day Sober","One Week Sober","One Month Sober","Two Months Sober","Three Months Sober","Four Months Sober","Six Months Sober","Nine Months Sober","One Year Sober","Two Years Sober","Three Years Sober","Five Years Sober","Ten Years Sober","Fifteen Years Sober","20+ years Sober"]
#    roles = ["One Day","One Week","One Month","Two Months","Three Months","Four Months","Six Months","Nine Months","One Year","Two Years","Three Years","Five Years","Ten Years","Fifteen Years","20+ years"]
    
    if message.content.startswith('st!'):

        
        command_string = message.content.split(' ')
        command = command_string[0].replace('st!','')
        parsed_string = message.content.replace("st!" + command + " ","")
        await log_message("Command " + message.content + " called by " + message.author.name + " from server " + message.guild.name + " in channel " + message.channel.name)
        await log_message("Parsed string: " + parsed_string)

        if command == 'createroles':
            for role in roles:
                await message.guild.create_role(name=role)
            await reply_message(message, "Roles created!")
        elif command == 'deleteroles':
            for role_name in roles:
                role = discord.utils.get(message.guild.roles, name=role_name)
                await role.delete()
            await reply_message(message, "Deleted roles from server.")
            
        elif command == 'trackme':
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d')
            result = await commit_sql("""INSERT INTO ServerSettings (ServerId, UserId, DateStarted) VALUES (%s, %s, %s);""",(str(message.guild.id),str(message.author.id), formatted_date))
            if result:
                await reply_message(message, "Created new entry for user " + message.author.display_name + "!")
            else:
                await reply_message(message, "Database error!")
        elif command == 'sethabit':
            records = await select_sql("""SELECT DateStarted FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "You don't have a record!")
                return            
            if not parsed_string:
                await reply_message(message, "You didn't set a habit!")
                return
            result = await commit_sql("""UPDATE ServerSettings SET Habit=%s WHERE ServerId=%s AND UserId=%s;""",(parsed_string, str(message.guild.id),str(message.author.id)))
            if result:
                await reply_message(message, "Set your habit to " + parsed_string + ".")
            else:
                await reply_message("Database error!")
        elif command == 'checkin':
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d')
            records = await select_sql("""SELECT DateStarted FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "You don't have a record!")
                return
            for row in records:
                sober_since = str(row[0])
            for role_name in roles:
                role = discord.utils.get(message.guild.roles, name=role_name)
                for user_role in message.author.roles:
                    if user_role == role:
                        await message.author.remove_roles(role)            
            role = await calculate_role(sober_since)
            if role != 'None':
            
                role_obj = discord.utils.get(message.guild.roles, name=role)
                await message.author.add_roles(role_obj)
                await reply_message(message, "Set your role to " + role + ".")
                
            result = await commit_sql("""UPDATE ServerSettings SET LastCheckin=%s WHERE ServerId=%s AND UserId=%s;""",(formatted_date, str(message.guild.id),str(message.author.id)))
            if result:
                await reply_message(message, "Checked you in as sober for today.")
            else:
                await reply_message("Database error!")
                
        elif command == 'relapse':
            records = await select_sql("""SELECT DateStarted FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "You don't have a record!")
                return        
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d')        
            result = await commit_sql("""UPDATE ServerSettings SET LastRelapse=%s WHERE ServerId=%s AND UserId=%s;""",(formatted_date, str(message.guild.id),str(message.author.id)))
            for role_name in roles:
                role = discord.utils.get(message.guild.roles, name=role_name)
                for user_role in message.author.roles:
                    if user_role == role:
                        await message.author.remove_roles(role)
                        
            if result:
                await reply_message(message, "Recorded your relapse today.")
            else:
                await reply_message("Database error!") 
                
        elif command == 'sobersince':
            records = await select_sql("""SELECT DateStarted FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "You don't have a record!")
                return        
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d')        
            result = await commit_sql("""UPDATE ServerSettings SET SoberSince=%s WHERE ServerId=%s AND UserId=%s;""",(parsed_string, str(message.guild.id),str(message.author.id)))
            for role_name in roles:
                role = discord.utils.get(message.guild.roles, name=role_name)
                for user_role in message.author.roles:
                    if user_role == role:
                        await message.author.remove_roles(role)
            role = await calculate_role(parsed_string)
            if role != 'None':
                role_obj = discord.utils.get(message.guild.roles, name=role)
                await message.author.add_roles(role_obj)
                await reply_message(message, "Set your role to " + role + ".")            
            if result:
                await reply_message(message, "Set your sober since date to " + parsed_string + ".")
            else:
                await reply_message("Database error!")        
        
        elif command == 'invite':
            await reply_message(message, "Click here to invite SobrietyTracker: " + invite_url)
            
        elif command == 'info' or command == 'help':
            response = "**Sobriety Tracker Discord Bot**\n\nThis bot will help people on a Discord server track and be accountable for their sobriety. The data will be visible to others on the server when roles are given or commands are used unless it is in a private channel.\n\n*Commands*\n\n`Prefix: st!`\n\n`st!createroles`: Create roles on the server (no color, not grouped separately by default) showing length of sobriety.\n\n`st!deleteroles`: Delete the bot server roles.\n\n`st!trackme`: Create an entry for you.\n\n`st!sethabit <habit>`: Set a habit to track (free text)\n\n`st!sobersince YYYY-MM-DD` Set the last date you did your habit.\n\n`st!checkin`: Check in as not doing your habit today.\n\n`st!relapse`: Admit that you did your habit today and reset your roles.\n\n`st!displaymydata`: Show your data for this server.\n\n`st!untrackme`: Delete your data for this server from the bot.\n\n"
            await reply_message(message, response)
        elif command == 'untrackme':
            result = await commit_sql("""DELETE FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if result:
                await reply_message(message, "Your data has been deleted!")
            else:
                await reply_message(message, "Database error!!")
        elif command == 'displaymydata':
            records = await select_sql("""SELECT IFNULL(Habit,'No data'), IFNULL(DateStarted,'No data'), IFNULL(LastRelapse,'No data'), IFNULL(LastCheckin,'No data'), IFNULL(SoberSince,'No data') FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "You have no data!")
                return
            for row in records:
                habit = str(row[0])
                date_started = str(row[1])
                last_relapse = str(row[2])
                last_checkin = str(row[3])
                sober_since = str(row[4])
            response = "Your data:\n\nHabit: " + habit + "\nDate tracking started: " + date_started + "\nLast Relapse: " + last_relapse + "\nLast checkin: " + last_checkin + "\nSober since: " + sober_since + "\n"
            await reply_message(message, response)
        else:
            pass
        
client.run('REDACTED')    