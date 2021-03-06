#from wsgiref.simple_server import make_server
#from pyramid.mako_templating import renderer_factory as mako_factory
#from pyramid.config import Configurator

#sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
#sys.path.insert(0, 'c:/')

#sys.path.append('D:\Office Stuff\Office Data\My Dropbox\Python Projects\PointTracker\airline_scrapers')
#import os
#import sys

#Then in your code that gets the username and password, you just do:

#from pyramid.security import remember

#remember(request, <bool>)
#The bool is True to remember the password and False to not remember.
#Then to check to see if the person is logged in, you do
#if authenticated_userid(request):
#You can also decorate your route handlers by adding permission=Authenticated as a final param. We can have lunch sometime and I can show you how this all fits together. Probably can't do it for a week and a half. We are going skiing for a week so I'm slammed trying to get everything in place by Friday.



import airline_scrapers.american
import airline_scrapers.united
import airline_scrapers.britishairways
import airline_scrapers.delta
import airline_scrapers.usairways
import airline_scrapers.evaair
import airline_scrapers.southwest
import airline_scrapers.hiltonhonors
import airline_scrapers.marriottrewards
#from ptserver import AES_Key

import mtk              #Mike's toolkit
#import subprocess
from pymongo import Connection
import uuid
import hashlib
#import base64
import Globalvars
import sys,os

#email modules
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

import base64

from Globalvars import NO_ERROR as NO_ERROR
from Globalvars import LOGIN_ERROR as LOGIN_ERROR
from Globalvars import SCRAPER_ERROR as SCRAPER_ERROR



def Init_App():

    global  PT_database

#    if Globalvars.DEVELOPMENT:
    if not 'OPENSHIFT_DATA_DIR' in os.environ:                              #if no OPENSHIFT key then we must be local

        Globalvars.DEVELOPMENT = True
        Globalvars.DEPLOY = False

        Globalvars.AES_Key = mtk.read_file("AES_Key.dng")
        Globalvars.Saltstring = mtk.read_file("Saltstring.dng")
        Globalvars.gmail_username = mtk.read_file("gmail_username.dng")
        Globalvars.gmail_password = mtk.read_file("gmail_password.dng")
        mongo_con = Connection('localhost', 27017)
        mongo_db = mongo_con.PT_database                                     ## is the database created? if not created it (PT_database)

    else:
        Globalvars.DEVELOPMENT = False
        Globalvars.DEPLOY = True

        Globalvars.AES_Key = mtk.read_file2(os.environ['OPENSHIFT_DATA_DIR'],"AES_Key.dng")
        Globalvars.Saltstring = mtk.read_file2(os.environ['OPENSHIFT_DATA_DIR'],"Saltstring.dng")
        Globalvars.gmail_username = mtk.read_file2(os.environ['OPENSHIFT_DATA_DIR'],"gmail_username.dng")
        Globalvars.gmail_password = mtk.read_file2(os.environ['OPENSHIFT_DATA_DIR'],"gmail_password.dng")
        mongo_con = Connection(os.environ['OPENSHIFT_MONGODB_DB_HOST'],
                           int(os.environ['OPENSHIFT_MONGODB_DB_PORT']))

        mongo_db = mongo_con[os.environ['OPENSHIFT_APP_NAME']]
        mongo_db.authenticate(os.environ['OPENSHIFT_MONGODB_DB_USERNAME'],
                              os.environ['OPENSHIFT_MONGODB_DB_PASSWORD'])



    PT_database = mongo_db.PT_accounts                           ## Create our collection



#    subprocess.Popen(['C:\\Dropbox\\PyProjects\\PointTracker\\pointtracker\\mongodb\\bin\\mongod', '--dbpath', 'C:\\Dropbox\\PyProjects\\PointTracker\\pointtracker\\static\\mongodb\\'])  ## Start the Mongo Database daemon

    return




def Init_PointTracker_Database():
    global  PT_database

#    subprocess.Popen(['C:\\Dropbox\\PyProjects\\PointTracker\\pointtracker\\mongodb\\bin\\mongod', '--dbpath', 'C:\\Dropbox\\PyProjects\\PointTracker\\pointtracker\\static\\mongodb\\'])  ## Start the Mongo Database daemon

    con = Connection('localhost', 27017)
    db = con.PT_database                                     ## is the database created? if not created it (PT_database)
    PT_database = db.PT_accounts                           ## Create our collection
    return


def Update_PointTracker_Database(_id, PT_account):
#    Encrypt_PT_account_Reward_Program_Passwords(PT_account)                                 #encrypt all Reward Program Password before sending to database
#    PT_database.update({'_id':PT_account['_id']} ,{'PT_account':PT_account})
    PT_database.update({'_id':_id} ,{'PT_account':PT_account})
    return PT_account


#def Insert_PointTracker_Database(_id, PT_account):
##    Encrypt_PT_account_Reward_Program_Passwords(PT_account)                                 #encrypt all Reward Program Password before sending to database
#    PT_database.insert({'_id':_id,'PT_account':PT_account})
#    return





def Get_PointTracker_Account(_id):
    db_obj = PT_database.find_one({'_id':_id})
    if db_obj is None:
        PT_account = None                                                   ## No such PT_account
    else:
        PT_account = db_obj['PT_account']
#        Remove_PT_account_Reward_Program_Passwords(PT_account)                             #we need to remove RP_account passwords so that they can't be seen on client side
#        Decrypt_PT_account_Reward_Program_Passwords(PT_account)                             #we need to decrypt RP_account passwords so that they can be edited on the client side
#        Encrypt_PT_account_Reward_Program_Passwords(PT_account)
    return PT_account                                               ## return the a valid authentiated PT_account





def Register_PointTracker_Account(register_info):

    PT_account = {
#                    "_id" : "",
                    "PT_account_lastname" :  "Guest_lastname",
                    "PT_account_firstname" : "Guest_firstname",
#                    "PT_password" :          "Guest_password",
                    "PT_username" :          "Guest_username",
                    "PT_sub_accounts" : [{
                        "SA_id":"",
                        "SA_name" : "Guest_firstname",
                        "SA_program_accounts" : []
                      }],
                  }


    hash = hashlib.sha256()
    string = register_info['username']  + Globalvars.Saltstring + register_info['password']
    encode_string = string.encode('utf-8')

    hash.update(encode_string)

    _id = hash.hexdigest()

#    PT_account['_id'] = _id
    PT_account['PT_account_firstname'] = register_info['firstname']
    PT_account['PT_account_lastname'] =  register_info['lastname']
    PT_account['PT_username'] = register_info['username']

#    PT_account['PT_password'] = register_info['password']
#    PT_account['PT_email'] = register_info['email']

    Sub_accounts = PT_account['PT_sub_accounts']
    Sub_account = Sub_accounts[0]
    Sub_account['SA_name'] = register_info['firstname']
    Sub_account['SA_id'] = str(uuid.uuid4())                       #create a new id for this sub account
#    PT_database.insert({'_id':PT_account['_id'],'PT_account':PT_account})
    PT_database.insert({'_id':_id,'PT_account':PT_account})
    return



def Valid_PointTracker_Account(_id):
    db_obj = PT_database.find_one({'_id':_id})
    if db_obj is None:
        return False                                     ## No such PT_account
    else:
        return True                                     ## An account exists





def Change_PointTracker_Account_Password(PT_obj):

    hash = hashlib.sha256()
    string = PT_obj['username']  + Globalvars.Saltstring + PT_obj['password']                           #make them re enter username and password to make sure it's them
    encode_string = string.encode('utf-8')
    hash.update(encode_string)
    _id = hash.hexdigest()                                                          # old _id

    if Valid_PointTracker_Account(_id):
        PT_account = Get_PointTracker_Account(_id)                                           ##Current account info

        hash = hashlib.sha256()
        string = PT_obj['username']  + Globalvars.Saltstring + PT_obj['new_password']  #create new hash with new password
        encode_string = string.encode('utf-8')
        hash.update(encode_string)
        new_id = hash.hexdigest()

        hash = hashlib.sha256()                                                 #now we have to hash new password and re encrypt all the RP accounts with it
        string = Globalvars.Saltstring + PT_obj['new_password']
        encode_string = string.encode('utf-8')
        hash.update(encode_string)
        new_key = hash.hexdigest()
        new_key = new_key[:16]                                         #use the first 16 chars for key

        Re_encrypt_PT_account_Reward_Program_Passwords(new_key, PT_obj['PT_password_encrypted'], PT_account)

        PT_database.insert({'_id':new_id,'PT_account':PT_account})                  ## Add the PT_account with new _id
        PT_database.remove({'_id':_id})                                           ## Remove the old PT_account with old _id
        return True
    else:
        return False







def Send_PointTracker_Account1(_id, email):

    from_addr = 'thepointtracker@gmail.com'
    to_addr_list = [email]
    cc_addr_list = []
    subject = 'PointTracker Account Update'
    smtpserver='smtp.gmail.com:587'


    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject


    PT_account = Get_PointTracker_Account(_id)
    message_text = Build_Text_Email_Message_Body(PT_account)
    message_html = Build_HTML_Email_Message_Body(PT_account)
    message = header + message_text

    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login('thepointtracker','!pointtracker#')

    status = True                                           #email sent  with no erros

    try:
        server.sendmail(from_addr, to_addr_list, message)
    except Exception as e:
        status = False

    server.quit()
    return status





def Send_PointTracker_Account(_id, email):

    # Construct email
    msg = MIMEMultipart('alternative')
    msg['To'] = email
    msg['From'] = 'thepointtracker@gmail.com'
    msg['Subject'] = 'PointTracker Account Update'

    PT_account = Get_PointTracker_Account(_id)
    message_text = Build_Text_Email_Message_Body(PT_account)
    message_html = Build_HTML_Email_Message_Body(PT_account)

#    message_text = "this is plain text"
#    message_html = "<html><head></head><body><h1>This is html text</h1></body></html>"

    part1 = MIMEText(message_text, 'plain')
    part2 = MIMEText(message_html, 'html')

    msg.attach(part1)
    msg.attach(part2)


#    f = open("pointtracker_email_header.jpg","rb")
#    img = MIMEImage(f.read())
#    f.close()
#    msg.attach(img)



##    image = mtk.read_file("pointtracker_email_header.jpg")
#    try:
#        f = open("pointtracker_email_header.jpg","rb")
#        encoded_image = base64.b64encode(f.read())
#    except Exception as e:
#        msg = "An exception of type {0} occured, these were the arguments:\n{1!r}"
#        print (msg.format(type(e).__name__, e.args))
#    f.close()
#
#    image_str = encoded_image.decode("ASCII")
#    try:
#        msg.attach(MIMEImage(image_str))
#    except Exception as e:
#        msg = "An exception of type {0} occured, these were the arguments:\n{1!r}"
#        print (msg.format(type(e).__name__, e.args))


#    msg.attach(MIMEImage(file("image.png").read()))



    status = True                                           #email sent  with no errors
    server = smtplib.SMTP('smtp.gmail.com:587')
    try:
        server.starttls()
        server.login(Globalvars.gmail_username,Globalvars.gmail_password)
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
    except Exception as e:
        emsg = "An exception of type {0} occured, these were the arguments:\n{1!r}"
        print (emsg.format(type(e).__name__, e.args))
        status = False

    server.quit()
    return status









def Build_Text_Email_Message_Body(PT_account):


    message = 'PointTracker Account Update\n\n'

    grand_total_points = 0

    for sub_account in PT_account['PT_sub_accounts']:                                        #PointTracker accounts are made up of sub accounts of other people's accounts
        message += 'Account :'
        message += sub_account['SA_name']  + '\n'                                               #sub_account name
        message += '{:<30}{:<25}{:<15}{:>10}\t\t{:<25}{:<20}{:<15}{:<15}'.format('Name','Program','Account','Balance','Last Activity Date','Expiration Date','Program Time','Days Remaining') + '\n'
        message += '------------------------------------------------------------------------------------------------------------------------------------------------------------------\n'

        sub_total_points =0
        for RP_account in sub_account['SA_program_accounts']:                                                       #go thru list of program accounts for each sub account
            message += '{:<30}{:<25}{:<15}{:>10,d}\t\t{:<25}{:<20}{:<15}{:<15}'.format(
                                    RP_account['RP_name'],RP_account['RP_account_name'],RP_account['RP_account_num'],RP_account['RP_balance'],RP_account['RP_last_activity_date'],RP_account['RP_expiration_date'],RP_account['RP_inactive_time'],RP_account['RP_days_remaining']) + '\n'


            sub_total_points = sub_total_points + RP_account['RP_balance']

        message += '------------------------------------------------------------------------------------------------------------------------------------------------------------------\n'
        message += '                                                         Sub Total    {:>10,d}'.format(sub_total_points) + '\n'
        message += '\n'
        grand_total_points += sub_total_points

    message += '                                            All Sub Accounts Total    {:>10,d}'.format(grand_total_points) + '\n\n\n'
    message += 'You may view your PointTracker account at pointtracker-fatapps.rhcloud.com\n'

#    print (message)
#    mtk.write_file(message,'email.txt')

    return message






def Build_HTML_Email_Message_Body(PT_account):
#    message = '<html><head><body style ="background: #ECF7FE">'

    message = '<img src="https://pointtracker-fatapps.rhcloud.com/static/graphics/pointtracker_email_header.png">'

#    current_directory  = os.path.dirname(os.path.realpath(__file__))                                                    #get current working directory
#    filepath  = os.path.join(current_directory,"static/graphics/pointtracker_email_header.png")                       #add the filename to it
#
#    f = open(filepath,"rb")
#    img = f.read()
#    f.close()
#
#    encoded_image = base64.b64encode(img)
#    img_str = encoded_image.decode("utf-8")
#
#    message = '<img src="data:image/png;base64,'+ img_str + '">'

    message += '<br>'

    grand_total_points = 0

    for sub_account in PT_account['PT_sub_accounts']:                                        #PointTracker accounts are made up of sub accounts of other people's accounts
        message += 'Account :' + sub_account['SA_name'] + '<br>'                                             #sub_account name

        message += '<table style ="background: #ECF7FE" border = "1">'

        message += "<thead>"
        message += "<tr>"
        message += "<th>Program</th>"
        message += "<th>Account</th>"
        message += "<th>Balance</th>"
        message += "<th>Last Activity</th>"
        message += "<th>Expiration</th>"
        message += "<th>Program Time</th>"
        message += "<th>Last Updated</th>"
        message += "</tr>"
        message += "</thead>"

        message += "<tbody>"

        for RP_account in sub_account['SA_program_accounts']:                                                       #go thru list of program accounts for each sub account
            message += "<tr>"
            message += "<td>" + RP_account['RP_name'] + "</td>"
            message += "<td style='text-align: right'>" + RP_account['RP_account_name'] + '<br>' +RP_account['RP_account_num'] + "</td>"
            message += "<td style='text-align: right'>" + str(RP_account['RP_balance']) + "</td>"
            message += "<td style='text-align: right'>" + RP_account['RP_last_activity_date'] + "</td>"
            message += "<td style='text-align: right'>" + RP_account['RP_expiration_date'] + "</td>"
            message += "<td style='text-align: right'>" + RP_account['RP_inactive_time'] + "</td>"
            message += "<td style='text-align: right'>" + RP_account['RP_datestamp'] + '<br>' + RP_account['RP_timestamp'] + "</td>"
            message += "</tr>"

#            sub_total_points = sub_total_points + RP_account['RP_balance']
        message += "</tbody>"
        message += "</table>"
        message += '<br>'
#    grand_total_points += sub_total_points

    message += 'You may view your PointTracker account at ' + '<a href="https://pointtracker-fatapps.rhcloud.com">https://pointtracker-fatapps.rhcloud.com</a>'
#    message = '</body></head></html>'

#    mtk.write_file(message,'email.html')

    return message









def Add_Reward_Program(PT_obj):

    RP_account = {
        "RP_id":"",
        "RP_callback_tag":"",
        "RP_datestamp":"",
        "RP_password":"",
        "RP_expiration_date":"",
        "RP_account_name":"",
        "RP_days_remaining":"",
        "RP_balance_delta":"",
        "RP_username":"",
        "RP_balance":"0",
        "RP_timestamp":"",
        "RP_name":"",
        "RP_last_activity_date":"",
        "RP_inactive_time":"",
        "RP_partner": "",
        "RP_error":False,
        #no program accounts at this time
    }

    key = PT_obj['PT_password_encrypted']                                              # use as AES key

#    RP_account['RP_callback_tag'] = PT_obj['RP_callback_tag']                         #call back info
    RP_account['SA_id'] = PT_obj['SA_id']                                              #store the Sub Account id
    RP_account['RP_id'] = str(uuid.uuid4())                                         #create a new id for this program account
    RP_account['RP_name']= PT_obj['RP_name']                                    ## set the new name
    RP_account['RP_username']= PT_obj['RP_username']                                 ## set the new name
    RP_account['RP_password']= mtk.encrypt(key ,PT_obj['RP_password'])                 ## encrypt RP password using the encrypted PT_password as the AES_key

#    RP_account['RP_password']= encrypt_password(PT_obj['RP_password'])                 ## set the new name
#    RP_account['RP_password']= PT_obj['RP_password']                                 ## set the new name

    RP_account = Process_Reward_Program(key, RP_account)                                     #scrape and check for error before inserting in PT

    if not RP_account['RP_error']:                                                  #no error, so add it to the database
        _id = PT_obj['_id']
        PT_account = Get_PointTracker_Account(_id)                                  #get our PT account out of the database
        PT_sub_accounts = PT_account['PT_sub_accounts']                         #get our PT sub account list
        #now find our sub account
        for SA_account in PT_sub_accounts:
            if SA_account['SA_id'] == PT_obj['SA_id']:
                break                                                           # we now have our sub account

        SA_program_accounts = SA_account['SA_program_accounts']                #get the list of Reward Programs
        SA_program_accounts.append(RP_account)                                  ## append to list
        Update_PointTracker_Database(PT_obj['_id'], PT_account)                                # update the database

    return RP_account









def Delete_Reward_Program(PT_obj):

    PT_account = Get_PointTracker_Account(PT_obj['_id'])              #get our PT account out of the database
    PT_sub_accounts = PT_account['PT_sub_accounts']                   #get our PT sub account list

    #now find our sub account
    for SA_account in PT_sub_accounts:
        if SA_account['SA_id'] == PT_obj['SA_id']:
            break                                                           # we now have our sub account

    SA_program_accounts = SA_account['SA_program_accounts']

    for RP_account in list(SA_program_accounts):                     #iterate over a copy of the list so we can remove the RP accounts with out messing with the original
        if RP_account['RP_id'] == PT_obj['RP_id']:
            SA_program_accounts.remove(RP_account)                         # remove it from list
            break

    Update_PointTracker_Database(PT_obj['_id'], PT_account)                 # update the database

    return






def Refresh_Reward_Program(PT_obj):
    key = PT_obj['PT_password_encrypted']
    PT_account = Get_PointTracker_Account(PT_obj['_id'])                #Get the PT account
    RP_account = Get_Reward_Program_Account(PT_account,PT_obj)         # Get the Reward Program account
#    return RP_account

    refreshed_RP_account = Process_Reward_Program(key, RP_account)                  # Refresh it by calling the appropriate scraper
    if not refreshed_RP_account['RP_error']:                  #no error update the database otherwise display error in client
        Set_Reward_Program_Account(PT_account, refreshed_RP_account, PT_obj)
        Update_PointTracker_Database(PT_obj['_id'], PT_account)
    return refreshed_RP_account




def Edit_Reward_Program(PT_obj):
#    AES_Key = '0123456789abcdef'
    key = PT_obj['PT_password_encrypted']
    PT_account = Get_PointTracker_Account(PT_obj['_id'])                #Get the PT account
    RP_account = Get_Reward_Program_Account(PT_account,PT_obj)         # Get the Reward Program account that we want to modify
    RP_account['RP_username'] = PT_obj['RP_username']                  # Update with edited information from user
    RP_account['RP_password']= mtk.encrypt(PT_obj['PT_password_encrypted'],PT_obj['RP_password'])                 ## encrypt RP password using the encrypted PT_password as the AES_key
#    RP_account['RP_password'] = mtk.encrypt(Globalvars.AES_Key,PT_obj['RP_password'])  #encrypt new password
#    RP_account['RP_password'] = PT_obj['RP_password']  #encrypt new password
    RP_account['RP_name'] = PT_obj['RP_name']
    RP_account['RP_balance'] = 0                                        #zero out balance because user could enter in a whole different account. We want don't want the account balance delta based off old account
    RP_account['RP_balance_delta'] = 0
    edited_RP_account = Process_Reward_Program(key, RP_account)                  # Refresh it by calling the appropriate scraper
    if not edited_RP_account['RP_error']:                                 #no error update the database otherwise display error in client
        Set_Reward_Program_Account(PT_account, edited_RP_account, PT_obj)
        Update_PointTracker_Database( PT_obj['_id'], PT_account)
    return edited_RP_account








def Set_Reward_Program_Account (PT_account, new_RP_account, PT_obj):

    PT_sub_accounts = PT_account['PT_sub_accounts']
    for SA_account in PT_sub_accounts:
        if SA_account['SA_id'] == PT_obj['SA_id']:                      #We now have our SA_account
            break

    SA_program_accounts = SA_account['SA_program_accounts']
    for RP_account in SA_program_accounts:
        if RP_account['RP_id'] == PT_obj['RP_id']:                      #We now have our RP_account
            break
    for key in new_RP_account:                                          #copy the new updated reward program into the RP_account in PT account
        RP_account[key] = new_RP_account[key]
    return





def Get_Reward_Program_Account (PT_account, PT_obj):

    PT_sub_accounts = PT_account['PT_sub_accounts']
    for SA_account in PT_sub_accounts:
        if SA_account['SA_id'] == PT_obj['SA_id']:                      #We now have our SA_account
            break

    SA_program_accounts = SA_account['SA_program_accounts']
    for RP_account in SA_program_accounts:
        if RP_account['RP_id'] == PT_obj['RP_id']:                      #We now have our RP_account
            break
    RP_account['RP_callback_tag'] = PT_obj['RP_callback_tag']           # embed tag for callback functions
#    RP_account['RP_password'] = ''                                      #remove password for client for security
    return RP_account





## We store all Reward Program Passwords in the database encrypted.  However, when the client pulls the PT_account we need to decrypt
## all of the Reward Program Passwords so he can edit them if he desires.

def Decrypt_PT_account_Reward_Program_Passwords(PT_account):
#    AES_Key = '0123456789abcdef'
    PT_sub_accounts = PT_account['PT_sub_accounts']

    for SA_account in PT_sub_accounts:                               #iterate over a sub accounts
        SA_program_accounts = SA_account['SA_program_accounts']        #get the Reward program accounts for this subaccount
        for RP_account in SA_program_accounts:                               #decrypt the passwords for the client side.  Our datebase is still encrypted
            RP_account['RP_password'] = mtk.decrypt(Globalvars.AES_Key,RP_account['RP_password'])
    return PT_account


## We store all Reward Program Passwords in the database encrypted.  However, when the client pulls the PT_account we need to remove
## all of the Reward Program Passwords so client can't see them for security. If client wants to edit a RP account they just have to enter new password

def Remove_PT_account_Reward_Program_Passwords(PT_account):
#    AES_Key = '0123456789abcdef'
    PT_sub_accounts = PT_account['PT_sub_accounts']

    for SA_account in PT_sub_accounts:                               #iterate over a sub accounts
        SA_program_accounts = SA_account['SA_program_accounts']        #get the Reward program accounts for this subaccount
        for RP_account in SA_program_accounts:                               #Remove the passwords for the client side.  Our datebase is still encrypted
            RP_account['RP_password'] = ""
    return PT_account



def Add_Sub_Account(PT_obj):

    new_sub_account = {
        "SA_id":"",
        "SA_name":"",
        "SA_program_accounts":[]                                        #no program accounts at this time
    }

    _id = PT_obj['_id']
    PT_account = Get_PointTracker_Account(_id)                          #get our PT account out of the database
    PT_sub_accounts = PT_account['PT_sub_accounts']                     #get our PT sub account list

    new_sub_account['SA_name']= PT_obj['SA_name']                                 ## set the new name
    new_sub_account['SA_id'] = str(uuid.uuid4())                       #create a new id for this sub account

    PT_sub_accounts.insert(0,new_sub_account)               ## insert at beginning of list

    PT_account['PT_sub_accounts'] = PT_sub_accounts         # the list has been updated so put it back

    Update_PointTracker_Database(PT_obj['_id'], PT_account)                 # update the database

    return





def Delete_Sub_Account(PT_obj):

    _id = PT_obj['_id']                                                    #The id of what PT_account we are working on

    SA_id = PT_obj['SA_id']                               # sub account to be removed
#    SA_id = PT_obj['Current_SA_id']                               # sub account to be removed
    PT_account = Get_PointTracker_Account(_id)                          # Get the PT account
    PT_sub_accounts = PT_account['PT_sub_accounts']                        # Get a list of all the sub accounts

    for sub_account in list(PT_sub_accounts):                               #iterate over a copy of the list
            if sub_account['SA_id'] == SA_id:
                PT_sub_accounts.remove(sub_account)                         # remove it from list
                break

#    print ('Sub Account {} has been deleted.'.format(PT_obj['SA_id']))

    Update_PointTracker_Database(PT_obj['_id'], PT_account)                                 #update it in database
    return





def Process_Reward_Program(key, RP_account):
    try:
        if RP_account['RP_name'] == 'American Airlines':
            html = airline_scrapers.american.get_program_account_info(key, RP_account)                                 #login and grab necessary web pages to scrape
            RP_updated_account = airline_scrapers.american.scrape_webpage(html)

        elif RP_account['RP_name'] == 'United Airlines':
            html = airline_scrapers.united.get_program_account_info(key, RP_account)                                 #login and grab necessary web pages to scrape
            RP_updated_account = airline_scrapers.united.scrape_webpage(html)

        elif RP_account['RP_name'] == 'Delta Airlines':
            html = airline_scrapers.delta.get_program_account_info(key, RP_account)                                 #login and grab necessary web pages to scrape
            RP_updated_account = airline_scrapers.delta.scrape_webpage(html)

        elif RP_account['RP_name'] == 'US Airways':
            html = airline_scrapers.usairways.get_program_account_info(key, RP_account)                                 #login and grab necessary web pages to scrape
            RP_updated_account = airline_scrapers.usairways.scrape_webpage(html)

        elif RP_account['RP_name'] == 'British Airways':
            html = airline_scrapers.britishairways.get_program_account_info(key, RP_account)                                 #login and grab necessary web pages to scrape
            RP_updated_account = airline_scrapers.britishairways.scrape_webpage(html)

        elif RP_account['RP_name'] == 'EVA Air':
            html = airline_scrapers.evaair.get_program_account_info(key, RP_account)                                 #login and grab necessary web pages to scrape
            RP_updated_account = airline_scrapers.evaair.scrape_webpage(html)

        elif RP_account['RP_name'] == 'Southwest Airlines':
            html = airline_scrapers.southwest.get_program_account_info(key, RP_account)                                 #login and grab necessary web pages to scrape
            RP_updated_account = airline_scrapers.southwest.scrape_webpage(html)

        elif RP_account['RP_name'] == 'Hilton Honors':
            html = airline_scrapers.hiltonhonors.get_program_account_info(key, RP_account)                                 #login and grab necessary web pages to scrape
            RP_updated_account = airline_scrapers.hiltonhonors.scrape_webpage(html)

        elif RP_account['RP_name'] == 'Marriott Rewards':
            html = airline_scrapers.marriottrewards.get_program_account_info(key, RP_account)                                 #login and grab necessary web pages to scrape
            RP_updated_account = airline_scrapers.marriottrewards.scrape_webpage(html)

    except Exception as e:                                                                          #got a error in scraping webpage due to webpage changing or pop up
        RP_account['RP_error'] = SCRAPER_ERROR
        return RP_account

    RP_updated_account['RP_callback_tag'] = RP_account['RP_callback_tag']                       #we still need this info for the call back
    RP_updated_account['RP_name'] = RP_account['RP_name']
    RP_updated_account['RP_id'] = RP_account['RP_id']
    RP_updated_account['SA_id'] = RP_account['SA_id']


    if not RP_updated_account['RP_error']:                              # No Error so finish the last steps
        RP_updated_account['RP_username'] = RP_account['RP_username']         #put username and password back in new dict
        RP_updated_account['RP_password'] = RP_account['RP_password']
        RP_updated_account['RP_balance_delta'] = int(RP_updated_account['RP_balance']) - int(RP_account['RP_balance'])

    return RP_updated_account





def encrypt_password(password):
#    AES_Key = '0123456789abcdef'

    encrypted_password = mtk.encrypt(Globalvars.AES_Key,password)
    return encrypted_password





## This is just a test function to return the Reward Program without out updating the database
##

def Return_Reward_Program(PT_obj):

    PT_account = Get_PointTracker_Account(PT_obj['_id'])                #Get the PT account
    RP_account = Get_Reward_Program_Account(PT_account,PT_obj)         # Get the Reward Program account
    RP_account['RP_error'] = False                                    #Clear error status
    return RP_account







def Re_encrypt_PT_account_Reward_Program_Passwords(new_key, old_key, PT_account):
    PT_sub_accounts = PT_account['PT_sub_accounts']

    for SA_account in PT_sub_accounts:                               #iterate over a sub accounts
        SA_program_accounts = SA_account['SA_program_accounts']        #get the Reward program accounts for this subaccount
        for RP_account in SA_program_accounts:                               #decrypt the passwords for the client side.  Our datebase is still encrypted
            password = mtk.decrypt(old_key,RP_account['RP_password'])        #get the password
            RP_account['RP_password'] = mtk.encrypt(new_key, password)       #now encrypt it with new key

    return PT_account




## This is just a utility to encrypt all the passwords for the PT_account and update it in the datebase
##It is not normally used in the program
def Encrypt_PT_account_Reward_Program_Passwords(key, PT_account):
#    AES_Key = '0123456789abcdef'
    PT_sub_accounts = PT_account['PT_sub_accounts']

    for SA_account in PT_sub_accounts:                               #iterate over a sub accounts
        SA_program_accounts = SA_account['SA_program_accounts']        #get the Reward program accounts for this subaccount
        for RP_account in SA_program_accounts:                               #decrypt the passwords for the client side.  Our datebase is still encrypted
            RP_account['RP_password'] = mtk.encrypt(Globalvars.AES_Key,RP_account['RP_password'])


#    Update_PointTracker_Database(PT_account)                        #write it back out to the database

    return PT_account






def Manual_MongoDB_Modify(old_id, new_id):

    db_obj = PT_database.find_one({'_id':old_id})

#    db_obj._id = ObjectId(new_id)
    db_obj['_id']= new_id

    PT_database.insert(db_obj)

    PT_database.remove(old_id)
    return



def hack_mongo(request):
    _id = '434a54829180d1c606ecfa8f86e8745d8eb2e0a534e9d8f990c85e973b32f750'
#    _id = 'a7f8400519df31402eed6b052217946f04e079d8cad25a59994402f511eadf9f'            #old id
    PT_account = Get_PointTracker_Account(_id)
    username = request['username']
    password = request['password']
    hash = hashlib.sha256()
    string = request['username']  + Globalvars.Saltstring + request['password']
    encode_string = string.encode('utf-8')

    hash.update(encode_string)
    _id = hash.hexdigest()

#    _id = 'a7f8400519df31402eed6b052217946f04e079d8cad25a59994402f511eadf9f'            #new _id
    PT_account['_id'] = _id
    Encrypt_PT_account_Reward_Program_Passwords(PT_account)                                 #encrypt all Reward Program Password before sending to database
    PT_database.insert({'_id':PT_account['_id'],'PT_account':PT_account})               #insert new one
    return

