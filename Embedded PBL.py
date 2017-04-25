import logging, time, smtplib
#import RPi.GPIO as gp
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from multiprocessing import Process
import multiprocessing, sys, signal
'''
gp.setmode(gp.BCM)
gp.setup(21, gp.OUT)
gp.setup(16, gp.OUT)
gp.setup(13, gp.OUT)
gp.setup(6, gp.OUT)
'''
#bot = telegram.Bot(token = "251903620:AAGQSJErICuLtrEEx_Enm90pyv-KpCNCbP0")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

mymail = 'pokedude.adi@gmail.com'
mypassword = 'qwerty203!((&'

email = 'sathe_aditya@hotmail.com'

Fans = [False, False]
Lights = [False, False]

Fans = multiprocessing.Array('B', Fans)
Lights = multiprocessing.Array('B', Lights)

Lights_Strobe = [False, False]

FanGPIO = [6,13]
LightGPIO = [16,21]

Fans_Start_Time = [0,0]
Fans_End_Time = [0,0]
Fans_Total_Time = [0,0]

Lights_Start_Time = [0,0]
Lights_End_Time = [0,0]
Lights_Total_Time = [0,0]

'''
def start(bot, update):
    keyboard = [[KeyboardButton("/start"),
                 KeyboardButton("/status")],

                [KeyboardButton("/settings")]]

    reply_markup = ReplyKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)

'''
def someFunc1(Fans, Lights):
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

    def components(value, port, strobe):
        while(1):
            if strobe:
                print value
                time.sleep(1)
                print not value
                time.sleep(1)
            else:
                print port, value

    def start(bot, update):
        print "Start:", Fans
        keyboard = [[KeyboardButton("/start"),
                 KeyboardButton("/status")],

                [KeyboardButton("/settings")]]

        reply_markup = ReplyKeyboardMarkup(keyboard)

        update.message.reply_text('Please choose:', reply_markup=reply_markup)
        keyboard = [[InlineKeyboardButton("Fan 1 " + onOrOff(Fans[0]), callback_data='F0'),
                     InlineKeyboardButton("Light 1 " + onOrOff(Lights[0]), callback_data='L0')],

                    [InlineKeyboardButton("Fan 2 " + onOrOff(Fans[1]), callback_data='F1'),
                    InlineKeyboardButton("Light 2 " + onOrOff(Lights[1]), callback_data='L1')],

                    [InlineKeyboardButton("Email Usage", callback_data='email')]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('Click to toggle:', reply_markup=reply_markup)

    def status(bot, update):
        reply_text = "Light 1 " + onOrOff(Lights[0]) + ".\nLight 2 " + onOrOff(Lights[1]) +  ".\nFan 1 " +  onOrOff(Fans[0]) + ".\nFan 2 " +  onOrOff(Fans[1]) + "."
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
        print query.data

        device = query.data
        if (len(device) == 2):
            if device[0] == "L":
                if Lights[int(device[1])]:
           #         gp.output(LightGPIO[int(device[1])], 0)
                    temp = 'Light %d off.' %(int(device[1])+1)
                    print temp
                    Lights[int(device[1])] = False
                    etime = time.time()
                    Lights_Total_Time[int(device[1])] = Lights_Total_Time[int(device[1])] + (etime - Lights_Start_Time[int(device[1])])
                    bot.editMessageText(text="%s" % temp,
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
                else:
            #        gp.output(LightGPIO[int(device[1])], 1)
                    temp = 'Light %d on.' %(int(device[1])+1)
                    print temp
                    Lights[int(device[1])] = True
                    stime = time.time()
                    Lights_Start_Time[int(device[1])] = stime
                    bot.editMessageText(text="%s" % temp,
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
                    
            elif device[0] == "F":
                if Fans[int(device[1])]:
             #       gp.output(FanGPIO[int(device[1])], 0)
                    temp = 'Fan %d off.' %(int(device[1])+1)
                    print temp
                    Fans[int(device[1])] = False
                    etime = time.time()
                    Fans_Total_Time[int(device[1])] = Fans_Total_Time[int(device[1])] + (etime - Fans_Start_Time[int(device[1])])
                    bot.editMessageText(text="%s" % temp,
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
                else:
              #      gp.output(FanGPIO[int(device[1])], 1)
                    temp = 'Fan %d on.' %(int(device[1])+1)
                    print temp
                    Fans[int(device[1])] = True
                    stime = time.time()
                    Fans_Start_Time[int(device[1])] = stime
                    bot.editMessageText(text="%s" % temp,
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
        elif (len(device)==3):
            if device[-1] == '0':
                Lights_Strobe[0] = not Lights_Strobe[0]
                temp = "Light 1 " + strobeOrNot(Lights_Strobe[0]) + "."
                bot.editMessageText(text="%s" % temp,
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
            else:
                Lights_Strobe[1] = not Lights_Strobe[1]
                temp = "Light 2 " + strobeOrNot(Lights_Strobe[1]) + "."
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

            body = """
                Light 1: %f,
                Light 2: %f,
                            
                Fan 1: %f,
                Fan 2: %f,
                            
                Total Time: %f""" %(Lights_Total_Time[0],Lights_Total_Time[1],Fans_Total_Time[0],Fans_Total_Time[1],sum(Fans_Total_Time)+sum(Lights_Total_Time))

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

    updater = Updater("251903620:AAGQSJErICuLtrEEx_Enm90pyv-KpCNCbP0")

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('status', status))
    updater.dispatcher.add_handler(CommandHandler('settings', settings))

    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()
'''
    def fun():
        while(1):
            updater.start_polling()
'''

def tryFun():
    global Fans, Lights
    parent_conn, child_conn = multiprocessing.Pipe()
    x = Process(target=fun2, args=(Fans,Lights,child_conn,))
    x.start()
    Fans = parent_conn.recv()
    x.join()

def echo(bot, update):
    if(update.message.text == 'X'):
        global Fans
        global Lights
        parent_conn, child_conn = multiprocessing.Pipe()
        x = Process(target=someFunc2, args=(Fans,Lights))
        x.start()
        # Fans = parent_conn.recv()
        x.join()
    Fans[1] = not Fans[1]
'''
def fun2(Fans, Lights, conn):
    Fans[0] = not Fans[0]
    print "User:", Fans
    conn.send(Fans)
    conn.close()
'''
def someFunc2(Fans, Lights):
    Lights[0] = True
# Create the Updater and pass it your bot's token.


if __name__ == '__main__':
    


    p1 = Process(target=someFunc1, args=(Fans, Lights))
    p2 = Process(target=someFunc2, args=(Fans, Lights))

    p1.start()
    p2.start()