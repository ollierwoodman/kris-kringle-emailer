configfilename = 'config.json'

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from os.path import dirname, join

import json
from types import SimpleNamespace

import random

current_dir = dirname(__file__)
configfilepath = join(current_dir,"./" + configfilename)

f = open (configfilepath, "r")
config = json.loads(f.read())

emailtemplatefilename = config["emailTemplateFileName"]
participantsfilename = config["participantsFileName"]
customtextfilename = config["customTextFileName"]

senderemailaddress = config['hostEmailAddress']
senderemailpassword = config['hostEmailPassword']

emailtemplatefilepath = join(current_dir,"./" + emailtemplatefilename)
participantsfilepath = join(current_dir,"./" + participantsfilename)
customtextfilepath = join(current_dir,"./" + customtextfilename)

f.close()

class Participant:
    def __init__(self, id, name, email, cannotbuyforids):
        self.id = id
        self.name = name
        self.email = email
        self.cannotbuyforids = cannotbuyforids
        self.buyforid = -1
    
    def assignBuyFor(self, buyforid):
        if (self.id == buyforid):
            return False

        for cannotbuyforid in self.cannotbuyforids:
            if (cannotbuyforid == buyforid):
                return False
        
        self.buyforid = buyforid
        return True

f = open (participantsfilepath, "r")
participantsJSON = json.loads(f.read())

participantObjectsArray = []
for participant in participantsJSON["participants"]:
    participantObjectsArray.append(Participant(participant["id"], participant["name"], participant["email"], participant["cannotbuyfor"]))

f.close()

participantObjectsArray.sort(key=lambda x: len(x.cannotbuyforids), reverse=True)

receiverids = []
for participant in participantObjectsArray:
    receiverids.append(participant.id)

attempts = 1000000
for i in range(attempts):
    receiveridscopy = receiverids.copy()

    random.shuffle(receiveridscopy)

    for participant in participantObjectsArray:
        if participant.assignBuyFor(receiveridscopy[0]):
            receiveridscopy.pop(0)
            continue
        else:
            break

    if len(receiveridscopy) == 0:
        break
    else:
        if i < attempts - 1:        
            #restart and try again
            continue
        else:
            print("I found no possible combinations of matches in %d attempts, try allowing participants more potential matches." % attempts)
            exit()

def getParticipantById(id):
    for participant in participantObjectsArray:
        if participant.id == id:
            return participant
    return None


for participant in participantObjectsArray:
    print("%s buys for %s" % (participant.name, getParticipantById(participant.buyforid).name))


def ConstructEmailBody(participant):
    text = """
    Hey {participantname}!\n\n
    You are a participant in {kktitle}.\n
    This email was generated automatically and the contents are only known to you.\n
    This email and its contents are to be kept a secret from all other participants!\n\n
    This year, you will be buying for:\n
    {buyingforname}\n\n
    The maximum budget for your gift is:\n
    ${totalbudget}\n\n
    Should you have any questions about this email, contact the host {contactname} via {contactemailaddress}.\n\n
    Happy Christmas!
    """

    html = ""
    with open(emailtemplatefilepath,"r") as emailtemplatereader:
        html = emailtemplatereader.read()

    customtext = ""
    with open(customtextfilepath, "r") as customtextreader:
        customtext = json.loads(customtextreader.read())

    kktitle = customtext["kktitle"]
    contactname = customtext["contactname"]
    contactemailaddress = customtext["contactemailaddress"]

    html = html.replace("{participantname}",participant.name)
    html = html.replace("{buyingforname}",getParticipantById(participant.buyforid).name)
    html = html.replace("{totalbudget}",str(config["totalBudget"]))

    html = html.replace("{kktitle}",kktitle)
    html = html.replace("{contactname}",contactname)
    html = html.replace("{contactemailaddress}",contactemailaddress)

    text = text.replace("{participantname}",participant.name)
    text = text.replace("{buyingforname}",getParticipantById(participant.buyforid).name)
    text = text.replace("{totalbudget}",str(config["totalBudget"]))

    text = text.replace("{kktitle}",kktitle)
    text = text.replace("{contactname}",contactname)
    text = text.replace("{contactemailaddress}",contactemailaddress)

    return [text, html]

def SendEmail(receiveremail, text, html):

    customtext = ""
    with open(customtextfilepath, "r") as customtextreader:
        customtext = json.loads(customtextreader.read())
        
    kktitle = customtext["kktitle"]

    message = MIMEMultipart("alternative")
    message["Subject"] = kktitle + " details: Important!"
    message["From"] = senderemailaddress
    message["To"] = receiveremail

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(senderemailaddress, senderemailpassword)
        server.sendmail(
            senderemailaddress, receiveremail, message.as_string()
        )


emails = [] #receiveremail, text, html
for participant in participantObjectsArray:
    texthtmlarray = ConstructEmailBody(participant)
    emails.append([participant.email,texthtmlarray[0],texthtmlarray[1]])

sendemails = input("\nWould you like me to send an email to each of the participants? (y/n)\n")
if(sendemails == "y"):
    for email in emails:
        if(input("Would you like me to send an email to %s? (y/n)\n" % (email[0])) == "y"):
            SendEmail(email[0], email[1], email[2])
            print("Email sent to " + email[0])
    print("All done!")
if(sendemails == "ya"):
    for email in emails:
        SendEmail(email[0], email[1], email[2])
        print("Email sent to " + email[0])
    print("All emails sent!")

