# -*- coding: utf-8 -*-
import config
import allMessage
import telebot
import paramiko
import os
import sys
import time
from time import gmtime, strftime
import multiprocessing
import requests
import signal
import xml.etree.ElementTree as ET
import random
import string
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

bot = telebot.TeleBot(config.botToken)

class User:
    def __init__(self, userChatId): 
        self.userChatId = userChatId

    def userName(self, userName):
        self.userName = userName

    def sshUser(self, sshUser):
        self.sshUser = sshUser

    def sshPassword(self, sshPassword):
        self.sshPassword = sshPassword

    def sshHost(self, sshHost):
        self.sshHost = sshHost

    def cdCommand(self, cdCommand):
        self.cdCommand = cdCommand

    def cluster(self, cluster):
        self.cluster = cluster

    def cdCommandCluster(self, cdCommandCluster):
        self.cdCommandCluster = cdCommandCluster

    def userStep(self, userStep):
        self.userStep = userStep
        #(If user for chatId) = None - user not activate
        #step = 1 - wait everything
        #step = 2 - activ
    def sshStep(self, sshStep):
        self.sshStep = sshStep
        #step = 0 - not connected
        #step = 1 - ac
        #step = 2 - cluster
    def __str__(self):
        return "User information: \nUsername: " + self.userName \
           + "\nSsh User: " + self.sshUser \
           + "\nSsh Password: " + self.sshPassword \
           + "\nSsh Host: " + self.sshHost \
           + "\nCd Command: " + self.cdCommand \
           + "\nCluster: " + self.cluster \
           + "\nCd Command Cluster: " + self.cdCommandCluster \
           + "\nUser Step: " + str(self.userStep) \
           + "\nSsh Step: " + str(self.sshStep)
    def __repr__(self):
        return "User information: \nUsername: " + self.userName \
           + "\nSsh User: " + self.sshUser \
           + "\nSsh Password: " + self.sshPassword \
           + "\nSsh Host: " + self.sshHost \
           + "\nCd Command: " + self.cdCommand \
           + "\nCluster: " + self.cluster \
           + "\nCd Command Cluster: " + self.cdCommandCluster \
           + "\nUser Step: " + str(self.userStep) \
           + "\nSsh Step: " + str(self.sshStep)

knownUsers = {}

#
#
#Connect to ac
def connect(message):
     try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=knownUsers.get(message.chat.id).sshHost, \
                       username=knownUsers.get(message.chat.id).sshUser, \
                       password=knownUsers.get(message.chat.id).sshPassword)
        return client
     except Exception as e:
        bot.send_message(message.chat.id, "Error while establishing conection: " + str(e))
        return None

#
#
#Connect to cluster
def connect_cluster(message, client):
    #open a ssh channel between ac and cluster using local and ac transport
    client_transport = client.get_transport()
    dest_addr = (knownUsers.get(message.chat.id).cluster, 22)
    local_addr = (knownUsers.get(message.chat.id).sshHost, 22)
    client_channel = client_transport.open_channel("direct-tcpip", dest_addr, local_addr)

    try:
       jhost=paramiko.SSHClient()
       jhost.set_missing_host_key_policy(paramiko.AutoAddPolicy())
       jhost.connect(knownUsers.get(message.chat.id).cluster, username=knownUsers.get(message.chat.id).sshUser, \
                                 password=knownUsers.get(message.chat.id).sshPassword, sock=client_channel)
       return jhost
    except Exception as e:
       bot.send_message(message.chat.id, "Error while establishing conection: " + str(e))
       return None

def connect_cluster_sftp(message, client):
    client_transport = client.get_transport()
    dest_addr = (knownUsers.get(message.chat.id).cluster, 22)
    local_addr = (knownUsers.get(message.chat.id).sshHost, 22)
    client_channel = client_transport.open_channel("direct-tcpip", dest_addr, local_addr)

    try:
       jhost=paramiko.SSHClient()
       jhost.set_missing_host_key_policy(paramiko.AutoAddPolicy())
       jhost.connect(knownUsers.get(message.chat.id).cluster, username=knownUsers.get(message.chat.id).sshUser, \
                                 password=knownUsers.get(message.chat.id).sshPassword, sock=client_channel)

       jhost_transport = jhost.get_transport()
       sftp = paramiko.SFTPClient.from_transport(jhost_transport)

       return sftp
    except Exception as e:
       bot.send_message(message.chat.id, "Error while establishing conection: " + str(e))
       return None

#
#
#Pass all message(exclude /start, /on, /help), if user not activate:
@bot.message_handler(func=lambda message: \
                    ((knownUsers.get(message.chat.id) == None) or (knownUsers.get(message.chat.id) == 1)) \
                    and (message.text != '/start') and (message.text != '/on') \
                    and (message.text != '/help'), content_types=["text"])
def pass_message(message):
    bot.send_message(message.chat.id, "Command not recognized. Type /help to see a list of available commands")

#
#
#Message /start after and before register user
@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id) == None, commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, allMessage.commands['start_BeforeAuthorized'])

@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id).userStep == 2, commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, allMessage.commands['start_AfterAuthorized'])
#
#
#Message /help after and before register user
@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id) == None, commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, allMessage.commands['help_BeforeAuthorized'])

@bot.message_handler(func=lambda message: \
                    (knownUsers.get(message.chat.id).userStep == 2) \
                    and (knownUsers.get(message.chat.id).sshStep == 0), commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, allMessage.commands['help_AfterAuthorized'])

@bot.message_handler(func=lambda message: \
                    (knownUsers.get(message.chat.id).userStep == 2) \
                    and (knownUsers.get(message.chat.id).sshStep != 0), commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, allMessage.commands['help_AfterAuthorized'])

#
#
#Message /aboutBot
@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id).userStep == 2, commands=['aboutbot'])
def send_aboutBot(message):
    bot.send_message(message.chat.id, allMessage.commands['aboutBot'])

#
#
#Message /howto
@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id).userStep == 2, commands=['howto'])
def send_howto(message):
    bot.send_message(message.chat.id, allMessage.commands['howto'])

#
#
#User information:
@bot.message_handler(func=lambda message: True, commands=['information'])
def test_user(message):
    data = 'UserName: ' + knownUsers.get(message.chat.id).userName + '\n' +\
            'Ssh user: ' + knownUsers.get(message.chat.id).sshUser + '\n' +\
            'Ssh connection host: ' + knownUsers.get(message.chat.id).sshHost + '\n' +\
            'Your location on the server (pwd): ' + knownUsers.get(message.chat.id).cdCommand + '\n'
    if (knownUsers.get(message.chat.id).sshStep == 2):
        data += 'Your location on ' + knownUsers.get(message.chat.id).cluster + ' cluster (pwd): ' + knownUsers.get(message.chat.id).cdCommandCluster
    bot.send_message(message.chat.id, data)

#
#
#Login and logout:
@bot.message_handler(func=lambda message: True, commands=['on'])
def activate_user(message):
    if knownUsers.get(message.chat.id) == None:
          token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
          tree = ET.parse('../html/tokens.xml')
          root = tree.getroot()
          tokenset = ET.SubElement(root, "tokenset")
          ET.SubElement(tokenset, "chat").text = str(message.chat.id)
          ET.SubElement(tokenset, "token").text = token
          ET.ElementTree(root).write("../html/tokens.xml")
          bot.send_message(message.chat.id, "Use this link to login with your credentials. You must be connected to the UPV/EHU network. Connecting via VPN is also allowed.")
          bot.send_message(message.chat.id, "http://bot-telegram.sw.ehu.es/login.php?token=" + str(token))

    elif knownUsers.get(message.chat.id).userStep == 2:
        bot.send_message(message.chat.id, "You are already authorized on this bot")


@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id).userStep == 2, commands=['off'])
def deactivate_user(message):
    knownUsers.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "Bye")

#
#
#Check exist sshUser:
@bot.message_handler(func=lambda message: \
                    ((knownUsers.get(message.chat.id).userStep == 2) and \
                    (knownUsers.get(message.chat.id).sshUser == '') and \
                    (knownUsers.get(message.chat.id).sshPassword == '')), \
                    content_types=["text"])
def ssh_user_not_exist(message):
    bot.send_message(message.chat.id, "Ssh user not exist. Use /on or /help")

#
#
#Save cluster to connect to:
@bot.message_handler(func=lambda message: \
                    (knownUsers.get(message.chat.id).userStep == 2), commands=['connect'])
def ask_cluster_name(message):
    #Create MarkUp Keyboard
    clusterSelect = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    clusterSelect.add('ponto', 'hemera', 'atlas', 'exit')

    cluster=bot.send_message(message.chat.id, "Enter the name of the cluster you want to connect to ('exit' to return to ac):", reply_markup=clusterSelect)
    bot.register_next_step_handler(cluster, save_cluster)

def save_cluster(message):
    if (message.text == "exit"):
       bot.send_message(message.chat.id, "Disconnected from " + knownUsers.get(message.chat.id).cluster, reply_markup=telebot.types.ReplyKeyboardRemove())
       knownUsers.get(message.chat.id).cluster = ''
       knownUsers.get(message.chat.id).sshStep = 1
    elif (message.text == "ponto") or (message.text == "hemera") or (message.text == "atlas"):
       knownUsers.get(message.chat.id).cdCommandCluster = config.sshHomeDirectory
       knownUsers.get(message.chat.id).cluster = message.text
       knownUsers.get(message.chat.id).sshStep = 2
       bot.send_message(message.chat.id, "Connected to " + knownUsers.get(message.chat.id).cluster, reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
       #Inserted cluster doesn't exist, send them back to select a cluster
       cluster=bot.send_message(message.chat.id, "Please, select one of the available options")
       bot.register_next_step_handler(cluster, save_cluster)

#
#
#Measure consumption
@bot.message_handler(func=lambda message: \
                    (knownUsers.get(message.chat.id).userStep == 2) \
                    and (knownUsers.get(message.chat.id).sshStep == 2), commands=['consumption'])
def calculate_consumption(message):
    client = connect(message)
    if (client != None):
       jhost = connect_cluster(message, client)

       #Command for consumption: cu <USER> <CLUSTER_IN_UPPERCASE>
       stdin, stdout, stderr = jhost.exec_command("cu " + knownUsers.get(message.chat.id).sshUser + " " + knownUsers.get(message.chat.id).cluster.upper())
       actual_cons = stdout.read() + stderr.read()
       actual_cons = actual_cons[actual_cons.rindex(' ')+1:]

       #Command to see maximum consumption of an account: grep "^<USER>":" "/usr/local/administracion/cuentas_trabajo/usuarios.dat" | cut -d':' -f7
       sshCommand = "grep \"^" + knownUsers.get(message.chat.id).sshUser +":\" \"/usr/local/administracion/cuentas_trabajo/usuarios.dat\" | cut -d':' -f7"
       stdin, stdout, stderr = jhost.exec_command(sshCommand)
       max_cons = stdout.read() + stderr.read()

       percentage_cons = float(actual_cons)*100/float(max_cons)
       if (percentage_cons < 0.01):
          percentage_cons = 0.00

       jhost.close()
       client.close()
       bot.send_message(message.chat.id, \
                     "Your current consumption: \n{} / {} ({}%)".format(str(actual_cons).rstrip(), str(max_cons).rstrip(), str(round(percentage_cons, 2)).rstrip()))

#
#
#Show queue state
@bot.message_handler(func=lambda message: \
                    (knownUsers.get(message.chat.id).userStep == 2) \
                    and (knownUsers.get(message.chat.id).sshStep == 2), commands=['queue'])
def show_queue(message):
    client = connect(message)
    
    if (client != None):
       jhost = connect_cluster(message, client)

       #For some reason, maui library path is not added to these SSH connectiosn by default so we need to write the full name of the command.
       if (knownUsers.get(message.chat.id).cluster == "ponto"):
          stdin, stdout, stderr = jhost.exec_command("/software/maui/bin/showq -u " + knownUsers.get(message.chat.id).sshUser)
       elif (knownUsers.get(message.chat.id).cluster == "hemera"):
          stdin, stdout, stderr = jhost.exec_command("/software/maui/bin/showq -u " + knownUsers.get(message.chat.id).sshUser)
       else:
          #Atlas has another issue. Using the above solution, it cannot find a torque library that it needs to run the command.
          #As we cannot set LD_LIBRARY_PATH with the enviroment dictionary argument of the exec_command due to server-side restrictions in /etc/ssh/sshd_config,
          #we'll have to modify it using a command as shown below.
          env_dict="export LD_LIBRARY_PATH=/usr/local/lib ;"
          stdin, stdout, stderr = jhost.exec_command(env_dict + ' /usr/local/maui/bin/showq -u ' + knownUsers.get(message.chat.id).sshUser)
#         stdin, stdout, stderr = jhost.exec_command(env_dict + ' /usr/local/maui/bin/showq')

       data = stdout.read() + stderr.read()

       #We'll split the output in 3: Active jobs (msg_a), Idle jobs (msg_i) and Blocked jobs (msg_b)
       #To split it like that, we'll first have to build 3 matrices (active, idle and blocked) with the information from raw data of the command
       #and format our own output as we choose.
       #Apart from the matrices, we'll also have some additional information at the end of each block job_tuple[3,4,5]
       job_tuple = format_showq_data(data)

       #Header of the block
       msg_a = "ACTIVE JOBS---\nJOBID STATE PROC Remaining  STARTTIME\n"

       #Fill the block with data
       for i in range(len(job_tuple[0])):
          aux = '     '.join(map(str, job_tuple[0][i]))
          if len(aux) >= 51:
             msg_a += '    '.join(map(str, job_tuple[0][i]))
          else:
             msg_a += aux
          msg_a +="\n"

       #Add additional information
       active_info = job_tuple[3]
       msg_a += "\n" + active_info[:active_info.find('  ')].strip() + "\n" + active_info[active_info.find('  '):active_info.find(')')+1].strip() + "\n" + active_info[active_info.find(')')+2:].strip() + "\n"

       #Header of the block
       msg_i = "IDLE JOBS---\nJOBID STATE PROC Wclimit  QUEUETIME\n"
       
       #Fill the block with data
       for i in range(len(job_tuple[1])):
          aux = '     '.join(map(str, job_tuple[1][i]))
          if len(aux) >= 51:
             msg_i += '    '.join(map(str, job_tuple[1][i]))
          else:
             msg_i += aux
          msg_i +="\n"

       #Add additional information
       msg_i += "\n" + job_tuple[4] + "\n"

       #Header of the block
       msg_b = "BLOCKED JOBS---\nJOBID STATE PROC Wclimit  QUEUETIME\n"
  
       #Fill the block with data
       for i in range(len(job_tuple[2])):
          aux = '     '.join(map(str, job_tuple[2][i]))
          if len(aux) >= 51:
             msg_b += '    '.join(map(str, job_tuple[2][i]))
          else:
             msg_b += aux
          msg_b +="\n"
 
       #Add additional information
       final_info = job_tuple[5]
       msg_b += "\n" + final_info[:final_info.find(' ', final_info.find('Active Jobs: ')+13)] + "\n" + final_info[final_info.find('Idle'):] + "\n"

       #These could be made on another process if it takes too long
       send_showq(message, msg_a)
       send_showq(message, msg_i)
       send_showq(message, msg_b)
       
       jhost.close()
       client.close()


def send_showq(received_message, msg):
#   Max message length is 4096 UTF-8 chars, we choose 3000 as a precaution
    split = 3000
    for i in range((len(msg)/split)+1):
       #Find first newline after split characters
       split_msg=msg[:msg.find('\n', split)]
       bot.send_message(received_message.chat.id, split_msg)
       #Remove sent data from the message
       msg=msg[len(split_msg):]
       #Sleep for some time to "ensure" messages are sent in order, not needed in made tests. May slow a lot bot response time if not done with a subprocess
#       time.sleep(0.5)



def format_showq_data(data):
    #Remove show headers
    active = data[:data.find('IDLE JOBS----------------------')]
    idle = data[data.find('IDLE JOBS----------------------'):data.find('BLOCKED JOBS----------------')]
    blocked = data[data.find('BLOCKED JOBS----------------'):]

    #Get additional info from active block
    active_info = active[active.rfind('\n\n', 0, len(active)-2):].strip()
    #Remove more headers and additional info from active block. There should only be data inside active at this point
    active = active[active.find('STARTTIME')+9:active.find(active_info)].strip()
    #Divide each field with a whitespace
    active = " ".join(active.split())

    #Make a list from the string
    active_split = active.split()
    #Matrix from list
    active_2d = convert_to_matrix(active_split, int(active_info[:active_info.find(' ')]))

    #Get additional info from idle block
    idle_info = idle[idle.rfind('\n\n', 0, len(idle)-2):].strip()
    #Remove more headers and additional info from idle block. There should only be data inside idle at this point
    idle = idle[idle.find('QUEUETIME')+9:idle.find(idle_info)].strip()
    #Divide each field with a whitespace
    idle = " ".join(idle.split())

    #Make a list from the string
    idle_split = idle.split()
    #Matrix from list
    idle_2d = convert_to_matrix(idle_split, int(idle_info[:idle_info.find(' ')]))

    #Get additional info from blocked block
    blocked_info = blocked[blocked.rfind('\n\n', 0, len(blocked)-2):].strip()
    #Remove more headers and additional info from blocked block. There should only be data inside blocked at this point
    blocked = blocked[blocked.find('QUEUETIME')+9:blocked.find(blocked_info)].strip()
    #Divide each field with a whitespace
    blocked = " ".join(blocked.split())

    #Make a list from the string
    blocked_split = blocked.split()
    #Matrix from list
    blocked_2d = convert_to_matrix(blocked_split, int(blocked_info[blocked_info.find('Blocked Jobs:')+13:]))

    return active_2d, idle_2d, blocked_2d, active_info, idle_info, blocked_info

def convert_to_matrix(list, rows):
    matrix = []
    #Count is the index we're reading at in the list
    count=0

    for i in range(rows):
       sub = []
       for j in range(6):
          #These conditions are made to get only wanted data
          #No username
          if j == 1 :
             pass
          #Only initials for STATE
          elif j == 2 :
             state = list[count]
             sub.append(state[:1].strip())
          elif j < 5 :
             sub.append(list[count].strip())
          #STARTTIME and QUEUETIME are split in several indexes due to whitespaces inside SQLDATES
          #We'll join them all in a single index inside the matrix and get only the data we want
          else:
             hour = list[count+3]
             #Transform month to numeric formating with month_number() and remove seconds from hour
             date = month_number(list[count+1]) + "/" + list[count+2] + " " + hour[:hour.rfind(':')]
             sub.append(date.strip())
             count+=3
          count+=1
       matrix.append(sub)

    return matrix

def month_number(month):
    switcher = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12"
    }
    return switcher.get(month, "XX")
#
#
#Show scratch space
@bot.message_handler(func=lambda message: \
                    (knownUsers.get(message.chat.id).userStep == 2) \
                    and (knownUsers.get(message.chat.id).sshStep == 2), commands=['scratch'])
def show_scratch(message):
    client = connect(message)
    if (client != None):
       jhost = connect_cluster(message, client)

       stdin, stdout, stderr = jhost.exec_command("du -sh")
       data = stdout.read() + stderr.read()

       stdin, stdout, stderr = jhost.exec_command("du -sh /scratch/" + knownUsers.get(message.chat.id).sshUser)
       data2 = stdout.read() + stderr.read()

       jhost.close()
       client.close()

       bot.send_message(message.chat.id, "Used space in home directory (/dipc/" + knownUsers.get(message.chat.id).sshUser + "): " + data[:data.find('.')] + \
                                      "\nUsed scratch space in /scratch/" + knownUsers.get(message.chat.id).sshUser + ": " + data2[:data2.find('/')])

#
#
#Show DCRAB report
@bot.message_handler(func=lambda message: \
                    (knownUsers.get(message.chat.id).userStep == 2) \
                    and (knownUsers.get(message.chat.id).sshStep == 2), commands=['dcrab'])
def ask_dcrab_id(message):
    if knownUsers.get(message.chat.id).cluster == "atlas":
       bot.send_message(message.chat.id, "*WARNING*: DCRAB's report is designed to be viewed on a Desktop Browser. Opening it on a mobile device may show a wrong layout.")
       dcrabID = bot.send_message(message.chat.id, "Enter desired job ID:")
       bot.register_next_step_handler(dcrabID, show_dcrab_report)
    else:
       bot.send_message(message.chat.id, "DCRAB is only available in atlas")

def show_dcrab_report(message):
    client = connect(message)
    if (client != None):
       jhost = connect_cluster(message, client)
       sftp = connect_cluster_sftp(message, client)

       #Command used to get path of DCRAB report: qstat -f <JOBID> | grep Output_Path
       #This will only work with jobs in the job queue, so the whole functionality will only work with those jobs too
       stdin, stdout, stderr = jhost.exec_command("qstat -f " + message.text + " | grep Output_Path")
       data = stdout.read() + stderr.read()
       data = data[data.find('/'):data.rfind('/')+1]

       try:
          #Get document from <DCRAB_REPORT_PATH>/dcrab_report_<JOBID>/dcrab_report.html and save locally as <JOBID>_dcrab_report.html
          sftp.get(data + "dcrab_report_" + message.text + "/dcrab_report.html", message.text + "_dcrab_report.html")

          bot.send_document(message.chat.id, open('./' + message.text + '_dcrab_report.html', 'rb'))

          #Remove <JOBID>_dcrab_report.html from local storage
          os.remove(message.text + "_dcrab_report.html")
       except Exception as e:
          bot.send_message(message.chat.id, "No DCRAB report for job " + message.text)
          print e


       sftp.close()
       jhost.close()
       client.close()

#
#
#Do ssh command:
@bot.message_handler(func=lambda message: \
                    (knownUsers.get(message.chat.id).userStep == 2) \
                    and (knownUsers.get(message.chat.id).sshStep < 2), content_types=["text"])
def do_ssh_command(message):
        command_whitelist = open("command_whitelist.txt").read().split('\n')
        command_whitelist.remove('')

        #Check if cd command
        if (message.text[0:3] == 'cd '):
            if knownUsers.get(message.chat.id).cdCommand[-1] != '/':
                knownUsers.get(message.chat.id).cdCommand += '/'
            if message.text[3] == '/':
                knownUsers.get(message.chat.id).cdCommand = message.text.split()[1]
            elif message.text[3:5] == '..':
                #My approach to 'cd ..+'

                #Find number of '..', to see how many times we need to go up
                back = message.text[3:message.text.rfind('..')+2].count("..")
                #Split our saved command to ease the task
                cd_split = splitall(knownUsers.get(message.chat.id).cdCommand)

                #More or equal '..' as parent directories => new path is '/'
                if len(cd_split)-back <= 0:
                   knownUsers.get(message.chat.id).cdCommand = '/'
                else:
                   knownUsers.get(message.chat.id).cdCommand = ''
                   #Add saved path directories from top to bottom as many times as (directory number) - ('..' count)
                   for i in range(len(cd_split)-(back+1)):
                      if cd_split[i] != '/':
                         knownUsers.get(message.chat.id).cdCommand += cd_split[i] + '/'
                      else:
                         knownUsers.get(message.chat.id).cdCommand += cd_split[i]

                #Add path from last '..' to end to saved path
                knownUsers.get(message.chat.id).cdCommand += message.text[message.text.rfind('..')+3:]
            else:
                if knownUsers.get(message.chat.id).cdCommand[-1] =='/':
                    knownUsers.get(message.chat.id).cdCommand += message.text.split()[1]
                else:
                    knownUsers.get(message.chat.id).cdCommand += '/' + message.text.split()[1]
            bot.send_message(message.chat.id, knownUsers.get(message.chat.id).cdCommand)
        elif ((message.text.count(' ') == 0) and (message.text not in command_whitelist)) or \
             ((message.text.count(' ') > 0) and (message.text[:message.text.find(" ")] not in command_whitelist)) or ("|" in message.text):
                bot.send_message(message.chat.id, "Command not allowed")
        #Do ssh command:
        else:
            try:
                client = connect(message)
                knownUsers.get(message.chat.id).sshStep = 1
                sshCommand = 'cd ' +knownUsers.get(message.chat.id).cdCommand + '; ' + \
                            message.text
                if client != None :
                   stdin, stdout, stderr = client.exec_command(sshCommand)
                   stdout.channel.recv_exit_status()
                   data = stdout.read() + stderr.read()
                   if (sys.getsizeof(data) < 34):
                      pass
                   #6000 bytes is roughly 4100 UTF8 chararcters, not always though
                   elif (sys.getsizeof(data) > 6000):
                      bot.send_message(message.chat.id, \
                                "Answer from server is too large")
                   else:
                     if (len(data) == 0):
                        data = "Command executed"
                     bot.send_message(message.chat.id, data)
                   client.close()
            except Exception as e:
                bot.send_message(message.chat.id, e)


def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        # sentinel for absolute paths
        if parts[0] == path:
            allparts.insert(0, parts[0])
            break 
        # sentinel for relative paths
        elif parts[1] == path:
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts
#
#
#Do ssh command on cluster:
@bot.message_handler(func=lambda message: \
                    (knownUsers.get(message.chat.id).userStep == 2) \
                    and (knownUsers.get(message.chat.id).sshStep == 2), content_types=["text"])
def do_ssh_command_cluster(message):
        command_whitelist = open("command_whitelist.txt").read().split('\n')
        command_whitelist.remove('')
#check and remember 'cd'-command
        if (message.text[0:3] == 'cd '):
            if knownUsers.get(message.chat.id).cdCommandCluster[-1] != '/':
                knownUsers.get(message.chat.id).cdCommandCluster += '/'
            if message.text[3] == '/':
                knownUsers.get(message.chat.id).cdCommandCluster = message.text.split()[1]
            elif message.text[3:5] == '..':
                back = message.text[3:message.text.rfind('..')+2].count("..")
                cd_split = splitall(knownUsers.get(message.chat.id).cdCommandCluster)

                if len(cd_split)-back <= 0:
                   knownUsers.get(message.chat.id).cdCommandCluster = '/'
                else:
                   knownUsers.get(message.chat.id).cdCommandCluster = ''
                   for i in range(len(cd_split)-(back+1)):
                      if cd_split[i] != '/':
                         knownUsers.get(message.chat.id).cdCommandCluster += cd_split[i] + '/'
                      else:
                         knownUsers.get(message.chat.id).cdCommandCluster += cd_split[i]

                knownUsers.get(message.chat.id).cdCommandCluster += message.text[message.text.rfind('..')+3:]
            else:
                if knownUsers.get(message.chat.id).cdCommandCluster[-1] =='/':
                    knownUsers.get(message.chat.id).cdCommandCluster += message.text.split()[1]
                else:
                    knownUsers.get(message.chat.id).cdCommandCluster += '/' + message.text.split()[1]
            bot.send_message(message.chat.id, knownUsers.get(message.chat.id).cdCommandCluster)
        elif ((message.text.count(' ') == 0) and (message.text not in command_whitelist)) or \
             ((message.text.count(' ') > 0) and (message.text[:message.text.find(" ")] not in command_whitelist)) or ("|" in message.text):
                bot.send_message(message.chat.id, "Command not allowed")
#Do ssh command:
        else:
            try:
#
#Nested client approach
                client = connect(message)
                if (client != None):
                   jhost = connect_cluster(message, client)
                   sshCommand = 'cd ' +knownUsers.get(message.chat.id).cdCommandCluster + '; ' + \
                            message.text
                
                   stdin, stdout, stderr = jhost.exec_command(sshCommand)
                   data = stdout.read() + stderr.read()
                   if (sys.getsizeof(data) < 34):
                       pass
                   elif (sys.getsizeof(data) > 6000):
                       bot.send_message(message.chat.id, \
                                "Answer from server is too large")
                   else:
                       if (len(data) == 0):
                          data = "Command executed"
                       bot.send_message(message.chat.id, data)
                   jhost.close()
                   client.close()
 
            except Exception as e:
                bot.send_message(message.chat.id, e)

#
#   
#Observer class
class load_user(FileSystemEventHandler):
    def __init__(self):
        self.ignoreevents = []

    def ignoreevents(self, ignoreevents):
        self.ignoreevents = ignoreevents
    
    def on_modified(self, event):
       #As we have to modify credentials.xml each time it gets modified, the observer calls itself recursively
       #To avoid this, each time the observer modifies it, we will ignore that modification
       if (event.src_path in self.ignoreevents) and (str(event.src_path) == "../html/credentials.xml"):
          self.ignoreevents.remove(event.src_path)
       elif str(event.src_path) == "../html/credentials.xml" :
          tree = ET.parse('../html/credentials.xml')
          root = tree.getroot()
       
          #Create new user and add it to knownUsers
          for user in root.findall('user'):
             chatid = int(user[0].text)     
             newUser = User(chatid)
             newUser.userName = user[1].text 
             newUser.sshUser = user[1].text
             newUser.sshPassword = user[2].text
             newUser.sshHost = config.sshHost
             newUser.cdCommand = config.sshHomeDirectory
             newUser.cluster = ''
             newUser.cdCommandCluster = config.sshHomeDirectory
             newUser.userStep = 2
             newUser.sshStep = 0
             knownUsers[chatid] = newUser
        
          #Ignore this event and empty credentials.xml
          self.ignoreevents.append(event.src_path)
          tree = ET.Element('credentials')
          ET.ElementTree(tree).write("../html/credentials.xml")


def empty_tokens():
   tree = ET.Element('tokens')
   ET.ElementTree(tree).write("../html/tokens.xml")

if __name__ == '__main__':
   #Empty all tokens from tokens.xml each time we start the bot
   empty_tokens()
   
   #Set up Observer
   event_handler = load_user()
   observer = Observer()
   observer.schedule(event_handler, path='../html/', recursive=False)
   observer.start()
#   observer.join()

   #Start polling messages from the API
   bot.polling(none_stop=True, timeout=123)

