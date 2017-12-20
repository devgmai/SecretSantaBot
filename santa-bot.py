import logging
import asyncio
import os.path
import random
import discord
import copy
from configobj import ConfigObj
from random import shuffle

class Participant(object):
    """class defining a participant and info associated with them"""
    #Removed address from object params
    def __init__(self, name, idstr, usrnum, preferences='', partnerid='', username=''):
        self.name = name                #string containing name of user
        self.idstr = idstr              #string containing id of user
        self.usrnum = usrnum            #int value referencing the instance's location in usr_list
        #self.address = address          #string for user's address
        self.preferences = preferences  #string for user's gift preferences
        self.partnerid = partnerid      #string for id of partner
        self.username = username        #additional string for username identifier
    
    #Removed address functionality. 
    #def address_is_set(self):
    #    """returns whether the user has set an address"""
    #    if self.address == '':
    #        return False
    #    else:
    #        return True
    
    def pref_is_set(self):
        """returns whether the user has set gift preferences"""
        if self.preferences == '':
            return False
        else:
            return True

#initialize config file
#try to open config file if its exists
try:
    myfile = open('./files/botdata.cfg', 'r')
    config = ConfigObj('./files/botdata.cfg')
#create config file if it does not exist
except:
    #if there is a path, just create the file
    if os.path.exists('./files/'):
        config = ConfigObj('./files/botdata.cfg')
        config['programData'] = {'exchange_started': False}
        config['members'] = {}
        config.write()
    #else if there is no path, create the path, then create the file
    else:
        os.mkdir('./files/')
        config = ConfigObj('./files/botdata.cfg')
        config['programData'] = {'exchange_started': False}
        config['members'] = {}
        config.write()

#initialize data from config file
usr_list = []
total_users = 0
exchange_started = config['programData'].as_bool('exchange_started')
for key in config['members']:
    total_users = total_users + 1
    temp1 = config['members'][key]['name']
    temp2 = config['members'][key]['idstr']
    #temp3 = config['members'][key]['email']
    temp4 = config['members'][key]['preference']
    temp5 = config['members'][key]['partner']
    temp6 = config['members'][key]['username']
    usr_list.append(Participant(temp1, temp2, total_users, temp4, temp5, temp6))

def user_is_participant(usrid, usrlist=usr_list):
    """Takes a discord user ID string and returns whether a user with that ID is in usr_list"""
    result = False
    for person in usrlist:
        if person.idstr == usrid:
            result = True
            break
    return result

def get_participant_object(usrid, usrlist=usr_list):
    """takes a discord user ID string and list of participant objects, and returns the first participant object with matching id."""
    for person in usrlist:
        if person.idstr == usrid:
            return person
            break

#set up discord connection debug logging
client_log = logging.getLogger('discord')
client_log.setLevel(logging.DEBUG)
client_handler = logging.FileHandler(filename='./files/debug.log', encoding='utf-8', mode='w')
client_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
client_log.addHandler(client_handler)

#initialize client class instance
client = discord.Client()

#handler for all on_message events
@client.event
async def on_message(message):
    #declare global vars
    global usr_list
    global total_users
    global exchange_started
    #write all messages to a chatlog
    with open('./files/chat.log', 'a+') as chat_log:
        chat_log.write('[' + message.author.name + message.author.id + ' in ' + message.channel.name + ' at ' + str(message.timestamp) + ']' + message.content + '\n')
    
    #ignore messages from the bot itself
    if message.author == client.user:
        return
    
    #event for a user joining the secret santa
    elif message.content.startswith('$$join'):
        #check if the exchange has already started
        if exchange_started:
            await client.send_message(message.channel, '`Error: Too late, the gift exchange is already in progress.`')
        #check if message author has already joined
        elif user_is_participant(message.author.id):
            await client.send_message(message.channel, '`Error: You have already joined.`')
        else:
            #write details of the class instance to config and increment total_users
            total_users = total_users + 1
            #initialize instance of participant class for the author
            usr_list.append(Participant(message.author.name, message.author.id, total_users))
            #config['members'][str(total_users)] = [message.author.name, message.author.id, total_users, '', '', '']
            config['members'][str(total_users)] = {'name': message.author.name, 'idstr': message.author.id, 'usrnum': total_users, 'preference': '', 'partner': '', 'username': message.author}
            config.write()
            #prompt user about inputting info
            await client.send_message(message.channel, message.author.mention + ' Has been added to the Siege 2017 Secret Santa exchange!')
            await client.send_message(message.author, 'Please set your gift preferences so your secret santa can send you something!\n'
            #+ 'Use `$$setaddress` to set your mailing address\n'
            + 'Use `$$setpreference` to set gift preferences for your secret santa')
    
    #accept address of participants
    #elif message.content.startswith('$$setaddress'):
    #    #check if author has joined the exchange yet
    #    if user_is_participant(message.author.id):
    #        #add the input to the value in the user's class instance
    #        user = get_participant_object(message.author.id)
    #        user.address = message.content.replace('$$setaddress', '', 1)
    #        print(user.address)
    #        #save to config file
    #        config['members'][str(user.usrnum)]['email'] = user.address
    #        config.write()
    #        await client.send_message(message.author, 'You have added your address!')
    #    else:
    #        await client.send_message(message.author, 'Error: you have not yet joined the secret santa exchange. Use `$$join` to join the exchange.')
    
    #accept gift preferences of participants
    elif message.content.startswith('$$setpreference'):
        #check if author has joined the exchange yet
        if user_is_participant(message.author.id):
            #add the input to the value in the user's class instance
            user = get_participant_object(message.author.id)
            user.preferences = message.content.replace('$$setpreference ', '', 1)
            #save to config file
            config['members'][str(user.usrnum)]['preference'] = user.preferences
            config.write()
            await client.send_message(message.author, 'You set your preferences to ' + "'" + user.preferences + "'")
        else:
            await client.send_message(message.author, 'Error: you have not yet joined the secret santa exchange. Use `$$join` to join the exchange.')
    
    #command for admin to begin the secret santa partner assignmenet
    elif message.content.startswith('$$start'):
        #only allow people with admin permissions to run
        if message.author.top_role == message.server.role_hierarchy[0]:
            flag = True
            while flag:
                if exchange_started:
                    await client.send_message(message.channel, 'Too Late, the secret santa exchange has already started.')
                    flag = False
                    break
                #first ensure all users have all info submitted
                all_fields_complete = True
                for user in usr_list:
                    #if user.address_is_set() and
                    if user.pref_is_set():
                        pass
                    else:
                        all_fields_complete = False
                        await client.send_message(message.channel, '`Error: ' + user.name + ' has not submitted gift preferences.`')
                        #await client.send_message(message.channel, '`Partner assignment canceled: participant info incomplete.`')

                if all_fields_complete:
                    #Stable-marriage algorithm begins here
                    tempList = copy.copy(usr_list)
                    appendedList = []
                    #creating a list of lists for each participant
                    for i in range(0,len(tempList)):
                        appendedList.append([tempList[i],tempList[i]])

                    shuffledList = appendedList
                    random.shuffle(shuffledList)

                    #store the first user's pairing as a temp
                    temp = shuffledList[0][1]
                    for i in range(0, len(shuffledList)):
                        if i < len(shuffledList) - 1:
                            shuffledList[i][1] = shuffledList[i + 1][1]
                        else:
                            #reassign the last user to pair with the first user stored in temp
                            shuffledList[len(shuffledList) - 1][1] = temp

                    for pair in shuffledList:
                        pair[0].partnerid = pair[1].idstr
                        config['members'][str(pair[0].usrnum)]['partner'] = pair[1].idstr
                        config.write()

                        #tell participants who their partner is
                        print(pair[1].name)
                        await client.send_message(message.server.get_member(pair[0].idstr), pair[1].name + ' is your secret santa partner! Now pick out a gift and send it to them!')
                        #await client.send_message(user, 'Their mailing address is ' + partner.address)
                        await client.send_message(message.server.get_member(pair[0].idstr), 'Here are their gift preferences: ' + config['members'][str(pair[1].usrnum)]['preference'] )
                    exchange_started = True
                    config['programData']['exchange_started'] = True
                    config.write()
                flag = False
                break
        else:
            await client.send_message(message.channel, '`Error: you do not have permission to do this.`')
    
    #allows a way to exit the bot
    elif message.content.startswith('$$shutdown') and not message.channel.is_private:
        #Fonly allow ppl with admin permissions to run
        if message.author.top_role == message.server.role_hierarchy[0]:
            await client.send_message(message.channel, 'Thanks for participating in the Secret Santa!')
            raise KeyboardInterrupt
        else:
            await client.send_message(message.channel, '`Error: you do not have permission to do this.`')
    
    #lists off all participant names and id's
    elif message.content.startswith('$$listparticipants'):
        if total_users == 0:
            await client.send_message(message.channel, 'Nobody has signed up for the secret santa exchange yet. Use `$$join` to enter the exchange.')
        else:
            msg = '```The following people are signed up for the secret santa exchange:\n'
            for user in usr_list:
                msg = msg + user.name + '\n'
            msg = msg + 'Use `$$join` to enter the exchange.```'
            await client.send_message(message.channel, msg)
    
    #lists total number of participants
    elif message.content.startswith('$$totalparticipants'):
        if total_users == 0:
            await client.send_message(message.channel, 'Nobody has signed up for the secret santa exchange yet. Use `$$join` to enter the exchange.')
        elif total_users == 1:
            await client.send_message(message.channel, '1 person has signed up for the secret santa exchange. Use `$$join` to enter the exchange.')
        else:
            await client.send_message(message.channel, 'A total of ' + total_users + ' users have joined the secret santa exchange so far. Use `$$join` to enter the exchange.')
    
    #allows a user to have the details of their partner restated
    elif message.content.startswith('$$partnerinfo'):
        if exchange_started and user_is_participant(message.author.id):
            userobj = get_participant_object(message.author.id)
            partnerobj = get_participant_object(userobj.partnerid)
            msg = 'Your partner is ' + userobj.partner + '\n'
            #msg = msg + 'Their mailing address is ' + partnerobj.address + '\n'
            msg = msg + 'their gift preference is as follows:\n'
            msg = msg + partnerobj.preferences
            await client.send_message(message.author, msg)
        elif exchange_started:
            await client.send_message(message.channel, '`Error: partners have not been assigned yet.`')
        else:
            await client.send_message(message.author, '`Error: You are not participating in the gift exchange.`')

@client.event
async def on_ready():
    """print message when client is connected"""
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#event loop and discord initiation
client.run('insert_token_here')
