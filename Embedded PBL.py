import logging, time, smtplib
import RPi.GPIO as gp
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from multiprocessing import Process
import multiprocessing, sys, signal

#fill lines 12, 13, 15 and 222

mymail = 'mail here'
mypassword = 'password for mymail'
#the above two would be used to send usage statistics to the address below
email = 'user\'s email'

#declaring arrays and their shared memory forms
Fans = [False, False]
Lights = [False, False]
globalLights = [False, False]
Lights_Strobe = [False, False]
flagsLights = [False, False]
flagsFans = [False, False]
Fans_Start_Time = [0.0,0.0]
Fans_End_Time = [0.0,0.0]
Fans_Total_Time = [0.0,0.0]
Lights_Start_Time = [0.0,0.0]
Lights_End_Time = [0.0,0.0]
Lights_Total_Time = [0.0,0.0]

Fans = multiprocessing.Array('B', Fans)
Lights = multiprocessing.Array('B', Lights)
Lights_Strobe = multiprocessing.Array('B', Lights_Strobe)
globalLights = multiprocessing.Array('B', globalLights)
flagsLights = multiprocessing.Array('B', flagsLights)
flagsFans = multiprocessing.Array('B', flagsFans)
Fans_Start_Time = multiprocessing.Array('d', Fans_Start_Time)
Fans_End_Time = multiprocessing.Array('d', Fans_End_Time)
Fans_Total_Time = multiprocessing.Array('d', Fans_Total_Time)
Lights_Start_Time = multiprocessing.Array('d', Lights_Start_Time)
Lights_End_Time = multiprocessing.Array('d', Lights_End_Time)
Lights_Total_Time = multiprocessing.Array('d', Lights_Total_Time)

FanGPIO = [6,13]
LightGPIO = [16,21]


#Proc 1
def telegramAPI(Fans, Lights, Lights_Strobe, globalLights, Fans_Start_Time, Fans_End_Time, Fans_Total_Time, Lights_Start_Time, Lights_End_Time, Lights_Total_Time, flagsLights, flagsFans):
    def onOrOff(x):
        if x:
            return "on"
        else:
            return "off"


    def strobeOrNot(x):
        if x:
            return "strobe on"
        else:
            return "strobe off"

    def start(bot, update):
        keyboard = [[KeyboardButton("/start"),
                 KeyboardButton("/status")],

                [KeyboardButton("/settings"),
                 KeyboardButton("/reset")]]

        reply_markup = ReplyKeyboardMarkup(keyboard)

        update.message.reply_text('Please choose:', reply_markup=reply_markup)
        keyboard = [[InlineKeyboardButton("Fan 1 " + onOrOff(Fans[0]), callback_data='F0'),
                     InlineKeyboardButton("Light 1 " + onOrOff(globalLights[0]), callback_data='L0')],

                    [InlineKeyboardButton("Fan 2 " + onOrOff(Fans[1]), callback_data='F1'),
                    InlineKeyboardButton("Light 2 " + onOrOff(globalLights[1]), callback_data='L1')],

                    [InlineKeyboardButton("Email Usage", callback_data='email')]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('Click to toggle:', reply_markup=reply_markup)

    def status(bot, update):
        reply_text = "Light 1 " + onOrOff(globalLights[0]) + ".\nLight 2 " + onOrOff(globalLights[1]) +  ".\nFan 1 " +  onOrOff(Fans[0]) + ".\nFan 2 " +  onOrOff(Fans[1]) + "."
        bot.sendMessage(chat_id=update.message.chat_id, text=reply_text)
        reply_text = "Light 1 " +  strobeOrNot(Lights_Strobe[0]) + ".\nLight 2 " +  strobeOrNot(Lights_Strobe[1]) + "."
        bot.sendMessage(chat_id=update.message.chat_id, text=reply_text)

    def settings(bot, update):
        keyboard = [[InlineKeyboardButton("Light 1 " + strobeOrNot(Lights_Strobe[0]), callback_data='LS0')],
                    [InlineKeyboardButton("Light 2 " + strobeOrNot(Lights_Strobe[1]), callback_data='LS1')]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('Click to Toggle:', reply_markup=reply_markup)

    def button(bot, update):
        query = update.callback_query
        #print query.data

        device = query.data
        if (len(device) == 2):
            if device[0] == "L":
                if globalLights[int(device[1])]:
                    temp = 'Light %d off.' %(int(device[1])+1)
                    print temp
                    Lights[int(device[1])] = False
                    globalLights[int(device[1])] = False
                    #etime = time.time()
                    #Lights_Total_Time[int(device[1])] = Lights_Total_Time[int(device[1])] + (etime - Lights_Start_Time[int(device[1])])
                    bot.editMessageText(text="%s" % temp,
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
                else:
                    temp = 'Light %d on.' %(int(device[1])+1)
                    print temp
                    Lights[int(device[1])] = True
                    globalLights[int(device[1])] = True
                    #stime = time.time()
                    #Lights_Start_Time[int(device[1])] = stime
                    bot.editMessageText(text="%s" % temp,
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
                    
            elif device[0] == "F":
                if Fans[int(device[1])]:
                    temp = 'Fan %d off.' %(int(device[1])+1)
                    print temp
                    Fans[int(device[1])] = False
                    #etime = time.time()
                    #Fans_Total_Time[int(device[1])] = Fans_Total_Time[int(device[1])] + (etime - Fans_Start_Time[int(device[1])])
                    bot.editMessageText(text="%s" % temp,
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
                else:
                    temp = 'Fan %d on.' %(int(device[1])+1)
                    print temp
                    Fans[int(device[1])] = True
                    #stime = time.time()
                    #Fans_Start_Time[int(device[1])] = stime
                    bot.editMessageText(text="%s" % temp,
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
        elif (len(device)==3):
            if device[-1] == '0':
                Lights_Strobe[0] = not Lights_Strobe[0]
                temp = "Light 1 " + strobeOrNot(Lights_Strobe[0]) + "."
                print temp
                bot.editMessageText(text="%s" % temp,
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
            else:
                Lights_Strobe[1] = not Lights_Strobe[1]
                temp = "Light 2 " + strobeOrNot(Lights_Strobe[1]) + "."
                print temp
                bot.editMessageText(text="%s" % temp,
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)

        else:
            temp = 'Sending Email'
            print temp
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.login(mymail, mypassword)

            frommail = mymail
            tomail = email
            subject = "Usage Details"
            temp1 = 0
            temp2 = 0
            temp3 = 0
            temp4 = 0
            if flagsLights[0]:
                temp1 = temp1 + time.time() - Lights_Start_Time[0]
            if flagsLights[1]:
                temp2 = temp2 + time.time() - Lights_Start_Time[1]
            if flagsFans[0]:
                temp3 = temp3 + time.time() - Fans_Start_Time[0]
            if flagsFans[1]:
                temp4 = temp4 + time.time() - Fans_Start_Time[1]
            body = """
                Light 1: %fs,
                Light 2: %fs,
                            
                Fan 1: %fs,
                Fan 2: %fs,
                            
                Total Time: %fs""" %(Lights_Total_Time[0]+temp1,Lights_Total_Time[1]+temp2,Fans_Total_Time[0]+temp3,Fans_Total_Time[1]+temp4,sum(Fans_Total_Time)+sum(Lights_Total_Time)+temp1+temp2+temp3+temp4)

            msg = MIMEMultipart()
            msg['From'] = frommail
            msg['To'] = tomail
            msg['Subject'] = subject
            msg.attach(MIMEText(body))
            server.sendmail(frommail, tomail, msg.as_string())
            server.quit()
            print "Sent"
            bot.editMessageText(text="Sent Email",
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)

    def help(bot, update):
        update.message.reply_text("Use /start to test this bot.")


    def error(bot, update, error):
        logging.warning('Update "%s" caused error "%s"' % (update, error))

    def reset(bot, update):
        print "Reset"
        Fans[0] = Fans[1] = False
        Lights[0] = Lights[1] = False
        Lights_Strobe[0] = Lights_Strobe[1] = False
        globalLights[0] = globalLights[1] = False

    #updaters and event handlers
    updater = Updater("bot ID here")
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('status', status))
    updater.dispatcher.add_handler(CommandHandler('settings', settings))
    updater.dispatcher.add_handler(CommandHandler('reset', reset))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()

#Proc 2
def soundSensor(Fans, Lights, globalLights):
    while True:
        gp.output(23, True)
        time.sleep(0.00001)
        gp.output(23, False)

        while gp.input(24) == 0:
            pulseStart = time.time()

        while gp.input(24) == 1:
            pulseEnd = time.time()

        pulseDur = pulseEnd - pulseStart
        dist = pulseDur * 17150
        dist = round(dist, 2)

        if (dist < 10):
            print dist
            if Lights[0] == Fans[0]:
                Lights[0] = not Lights[0]
                globalLights[0] = Lights[0]
                Fans[0] = not Fans[0]
            else:
                Lights[0] = True
                globalLights[0] = True
                Fans[0] = True
            time.sleep(1)
        time.sleep(0.1)

#Proc 3
def strobeLights(Lights, Lights_Strobe, globalLights):
    while True:
        if(Lights_Strobe[0] and globalLights[0]):
            Lights[0] = not Lights[0]
        if(Lights_Strobe[1] and globalLights[1]):
            Lights[1] = not Lights[1]
        time.sleep(1)

#proc 4
def setLights(Fans, Lights):
    while True:
        gp.output(FanGPIO[0], Fans[0])
        gp.output(FanGPIO[1], Fans[1])
        gp.output(LightGPIO[0], Lights[0])
        gp.output(LightGPIO[1], Lights[1])

#Proc 5
def keepTime(Fans, Lights, Lights_Strobe, globalLights, Fans_Start_Time, Fans_End_Time, Fans_Total_Time, Lights_Start_Time, Lights_End_Time, Lights_Total_Time, flagsLights, flagsFans):
    flagFansOn = [False, False]
    flagFansOff = [True, True]
    flagLightsOn = [False, False]
    flagLightsOff = [True, True]

    while True:
        for i in range(0,2):
            if Lights[i] and flagLightsOn[i]:
                pass
            elif Lights[i] and not flagLightsOn[i]:
                flagLightsOn[i] = True
                flagLightsOff[i] = False
                Lights_Start_Time[i] = time.time()
                flagsLights[i] = True
            
            if not Lights[i] and flagLightsOff[i]:
                pass
            elif not Lights[i] and not flagLightsOff[i]:
                flagLightsOff[i] = True
                flagLightsOn[i] = False
                Lights_End_Time[i] = time.time()
##                print Lights_End_Time[i] - Lights_Start_Time[i]
                Lights_Total_Time[i] = Lights_End_Time[i] - Lights_Start_Time[i] + Lights_Total_Time[i]
                flagsLights[i] = False

            if Fans[i] and flagFansOn[i]:
                pass
            elif Fans[i] and not flagFansOn[i]:
                flagFansOn[i] = True
                flagFansOff[i] = False
                Fans_Start_Time[i] = time.time()
                flagsFans[i] = True
            
            if not Fans[i] and flagFansOff[i]:
                pass
            elif not Fans[i] and not flagFansOff[i]:
                flagFansOff[i] = True
                flagFansOn[i] = False
                Fans_End_Time[i] = time.time()
                Fans_Total_Time[i] = Fans_End_Time[i] - Fans_Start_Time[i] + Fans_Total_Time[i]
                flagsFans[i] = False
                

if __name__ == '__main__':
    gp.setmode(gp.BCM)
    gp.setup(21, gp.OUT)
    gp.setup(16, gp.OUT)
    gp.setup(13, gp.OUT)
    gp.setup(6, gp.OUT)
    gp.setup(23, gp.OUT)
    gp.setup(24, gp.IN)
    gp.setwarnings(False)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

    
    p1 = Process(target=telegramAPI, args=(Fans, Lights, Lights_Strobe, globalLights, Fans_Start_Time, Fans_End_Time, Fans_Total_Time, Lights_Start_Time, Lights_End_Time, Lights_Total_Time, flagsLights, flagsFans))
    p2 = Process(target=soundSensor, args=(Fans, Lights, globalLights))
    p3 = Process(target=strobeLights, args=(Lights, Lights_Strobe, globalLights))
    p4 = Process(target=setLights, args=(Fans, Lights))
    p5 = Process(target=keepTime, args=((Fans, Lights, Lights_Strobe, globalLights, Fans_Start_Time, Fans_End_Time, Fans_Total_Time, Lights_Start_Time, Lights_End_Time, Lights_Total_Time, flagsLights, flagsFans)))

    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()
