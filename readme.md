### Overview

This is a tool that can be used to host a Kris Kringle (Secret Santa) syndicate without the host knowing who got who.

By defining the following values, the tool will randomly generate a pairs of gift givers and recievers, if any of the pairs generated are invalid according to the rules defined by the user, the tool will reattempt until it has found a set of valid pairings or the maximum number of attempts has been exhausted.

When a valid set of pairs has been found, the tool uses the defined gmail account to send an email to each participant to tell them about the event.

### Here is a summary of the possible configurations and where to find them:
#### customtext.json
'kktitle' - The title of your Kris Kringle event, e.g. William's Secret Santa

'contactname' - The name of the person sending the emails and organising the event, e.g. William

'contactemailaddress' - The email address of the person sending the emails and organising the event, e.g. bill@example.com

#### config.json
'emailTemplateFileName' - The name of the email template JSON file 

'participantsFileName' - The name of the participants JSON file

'customTextFileName' - The name of the custom email text JSON file

'hostEmailAddress' - The gmail address to send mail from

'hostEmailPassword' - The password used to authenticate with, can be obtained by navigating through `Manage your Google Account > Security > Signing in to Google > App passwords`, where you can generate a new 16 char password

'totalBudget' - The amount of money that each particpant is excpected to spend on their gift to another participant

'maxNumberOfAttempts' - The maximum number of random pairings to generate before failing (between 100,000 and 10,000,000 should be good)

#### emailtemplate.html
The tool looks for an replace the following text strings in the email template so that the right data appears in the right email. These strings should be present and visible in the HTML.

`{kktitle}`,`{contactname}`,`{contactnameemailaddress}` - As in customtext.json

`{participantname}` - The name of the recipient of the email

`{buyingforname}` - The name of the person this email's recipient is buying for

`{totalbudget}` - The amount of money each gift giver is expected to spend

#### participants.json
This file contains the particpants of the Kris Kringle event the format is defined below:

Each element of the `participants` array contains a JSON object with the following values:
`id` - A unique identifier for this particpant, no two participants can have the same id, e.g. "01"

`name` - The participant's name, e.g. "Mary B"

`email` - The partipant's email address, e.g. "marybills@example.com"

`cannotbuyfor` - An array of ids for other participants that this participant should not be selected to buy for (if a couple is participating, they should be disallowed from buying for each other), e.g. ["02","05"]