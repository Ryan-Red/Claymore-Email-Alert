import socket
import time
import json
import datetime
import ast

import smtplib

def sendEmail(BODY):

    gmail_user = ''
    gmail_password = ''


    TO = ""
    FROM = gmail_user
    SUBJECT = "Mining Rig Alert"

    email_text = f"Subject:{SUBJECT}\n\n \n{BODY}"
        
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)

        server.login(gmail_user, gmail_password)
        server.sendmail(FROM, TO, email_text)
        server.close()


    except:
        print('Something went wrong...')





def splitInput(dataDict):
    id = dataDict["id"]
    result = dataDict["result"]
    minerVersion = result[0]
    runTime = result[1]
    hashData = result[2].split(";")

    maxTemp = 0

    hashRate = float(hashData[0])/1000.0
    shareNum = hashData[1]
    rejectNum = hashData[2]

    individualGPUHashRate = result[3].split(";")
    tempAndFanData = result[6].split(";")

    GPUhashRateList = []
    cardTuples = []
    for i in range(0,len(individualGPUHashRate),1):
        cardTuples = cardTuples + [[float(individualGPUHashRate[i])/1000.0,tempAndFanData[2*i],tempAndFanData[2*i+1]]]
        GPUhashRateList = GPUhashRateList + [float(individualGPUHashRate[i])/1000.0]
        if int(tempAndFanData[2*i]) >= maxTemp:
            maxTemp = int(tempAndFanData[2*i])

    BODY = "CURRENT TIME: {}\n".format(datetime.datetime.now())

    BODY = BODY + "RUN TIME: Run time is of: {} minutes \n".format(runTime)
    if maxTemp >= 75 or hashRate <= 200:
        BODY = BODY + "WARNING: Temperature or Hash Rate attained threashold\n"
        BODY = BODY + "WARNING: Temperature of a GPU has reached: {} C\n".format(maxTemp)
        BODY = BODY + "WARNING: Hash Rate is of: {} MH/s\n".format(hashRate)

        sendEmail(BODY)
    

    powerConsumption = result[-1]
    errors = dataDict["error"]
    
    return runTime, hashRate, shareNum,rejectNum,cardTuples,powerConsumption,errors, maxTemp


ADDR = "RIG IP"
PORT = 3333



# Request Packet from the API
request = {
            "id": 0,
            "jsonrpc":"2.0",
            "method":"miner_getstat2"
        }

byteRequest = json.dumps(request, indent=2).encode()
while 1:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((ADDR,PORT))

        sock.sendall(byteRequest)
        time.sleep(1)
        data = sock.recv(1024).decode("utf-8")
        data = data.replace("null","0")
        dataDict  = eval(data)
        runTime, hashRate, shareNum,rejectNum,cardTuples,powerConsumption,errors, maxTemp = splitInput(dataDict)
        print(str(datetime.datetime.now()) + ": Run time (mins): " + str(runTime) + ", Hash Rate (MH/s): " + str(hashRate) + ", Max Temp: " + str(maxTemp))
        sock.close()

    except KeyboardInterrupt:
        break
    time.sleep(20)


print("Finished")
