#! python3
# itemRotator.py - Rotates items into and out of a temporary holding queue following a specified amount of time required in the queue
#
# Usage: Run program twice per day to determine what items can be removed from the waiting queue and what should be added.
#        The user must enter the itemIDs of those they wish to add to the queue.
#
# Items in the item shelf are formatted as below:
#           itemShelf = {'itemID': [TIME_ADDED_TO_SHELF, CURRENT_USAGE_STATUS]}
#           CURRENT_USAGE_STATUS Possibilities: [TESTING, WAITING, READY]
#
# @author - Will Parker

import shelve, time, sys
from pathlib import Path
import pyinputplus as pyip
from datetime import datetime

#----------------------------------------------------- Definitions -----------------------------------------------------#

#Prints a divider line to improve readability
def dividerLine():
    print('\n--------------------------------------------------------------------------------\n')

#The possibilities for CURRENT_USAGE_STATUS
CURRENT_USAGE_STATUS = ['TESTING', 'WAITING', 'READY']

#For testing purposes the time required to stay in the queue will only be 10 seconds
numSecondsInQueue = 10
numMinutesInQueue = 0
numHoursInQueue = 0
numDaysInQueue = 0

#timeInQueue will be the number of seconds the item stays in the queue. Adjust the timeInQueue with the above parameters
timeInQueue = numSecondsInQueue + (60 * numMinutesInQueue) + (3600 * numHoursInQueue) + (216000 * numDaysInQueue)

#-------------------------------------------------------- What is Waiting? What can be removed? --------------------------------------------------------#

#Get the state of the items from the shelf file
itemShelf = shelve.open('itemData')

#Record the current time so as to determine which items are ready to get dequeued
now = time.time()

#Get the list of items that are still waiting
itemsToWait = {}

#Get the list of items in the waiting queue that still have time to go before they can get removed
for keys, values in (list(itemShelf.items())):
    if (values[1] == CURRENT_USAGE_STATUS[1]) and ((now - values[0]) < timeInQueue):
        #itemsToWait.append(keys)
        itemsToWait.setdefault(keys, (timeInQueue - (now - values[0])))

queueCounter = 1
if len(itemsToWait) > 0:
    print('The following items still have time to wait before they can be removed from the waiting queue:\n')
    for keys, values in itemsToWait.items():
        print(str(queueCounter) + ': ', end='')
        seconds = values
        formattedSeconds = "{:.0f}".format(values)
        print(keys + ' - ' + formattedSeconds + ' seconds left in the waiting queue.')
        queueCounter += 1
    dividerLine()

#Set up the list that will become the items to dequeue and put back into use
itemsToDequeue = []

#Loop through the items in the shelf file. If they are ready to be dequeued, add them to the list and do so
for keys, values in (list(itemShelf.items())):
    if (values[1] == CURRENT_USAGE_STATUS[1]) and ((now - values[0]) >= timeInQueue):
        itemsToDequeue.append(keys)

#Prompt the user to remove items from the waiting queue as needed
if len(itemsToDequeue) > 0:
    print('Please remove the following items from the waiting queue for further use: ')
    print()
    removeCounter = 1
    for i in range(len(itemsToDequeue)):
        print(str(removeCounter) + ': ', end='')
        print(itemsToDequeue[i])
        #Set the item's status in the shelf to 'QUALIFIED' and assign a timestamp for removal
        itemShelf[itemsToDequeue[i]] = [now, CURRENT_USAGE_STATUS[2]]
        removeCounter += 1
    dividerLine()

if len(itemsToWait) == 0 and len(itemsToDequeue) == 0:
    print('There are no items in the waiting queue')
    dividerLine()

#Close the shelf file
itemShelf.close()

#-------------------------------------------------------- Begin populating log file. --------------------------------------------------------#

#Generate log files to maintain record
timeStamp = datetime.now()
timeStamp = datetime.now()
timeStamp = str(timeStamp)
timeStamp = timeStamp[0:13] + '_' + timeStamp[14:16] + '_' + timeStamp[17:19]
baseFile = str('log_' + timeStamp)

logFilePath = Path.cwd() / 'logs' / baseFile
logFile = open(logFilePath, 'w')

logFile.write('Items still in waiting queue:\n')
if len(itemsToWait) == 0:
    logFile.write('None\n')
elif len(itemsToWait) > 0:
    for keys, values in itemsToWait.items():
        formattedSeconds = "{:.0f}".format(values)
        logFile.write(keys + ' - ' + formattedSeconds + ' seconds left in the waiting queue.\n')

logFile.write('\nItems removed from waiting queue:\n')
if len(itemsToDequeue) == 0:
    logFile.write('None\n')
elif len(itemsToDequeue) > 0:
    for i in range(len(itemsToDequeue)):
        logFile.write(str(i + 1) + ': ' + itemsToDequeue[i] + '\n')

logFile.close()

#-------------------------------------------------------- What to add to Waiting Queue? --------------------------------------------------------#

#Ask the user if any items need to be added to the waiting queue
print('Do any items need to be added to the waiting queue?')

#Get the user's answer (Yes or No)
print()
answer = pyip.inputYesNo("Type 'Yes' or 'No' and press Enter: ")
print()

#The list of items to add to the queue
itemsToAdd = []

#True if list of items to add is confirmed. False otherwise.
itemsToAddConfirmed = False

#If there are items to add to the queue, do so
if answer == 'yes':
    #Open the shelf for manipulation
    itemShelf = shelve.open('itemData')
    while itemsToAddConfirmed == False:
        #Used to number the items in the list
        itemCounter = 1
        print('Enter the itemIDs to add to the waiting queue. Press Enter after each item entry. When done press Enter with no text entered.\n')
        print(str(itemCounter) + ': ', end='')
        itemToAdd = input()
        itemCounter += 1
        #Get items until the user is done
        while (itemToAdd != ''):
            print(str(itemCounter) + ': ', end='')
            itemsToAdd.append(itemToAdd)
            itemToAdd = input()
            itemCounter += 1
        print()

        #Let the user verify that what they have entered is correct
        print('You have entered the below items to add to the waiting queue. Is this correct?\n')
        addCounter = 1
        for i in range(len(itemsToAdd)):
            print(str(addCounter) + ': ', end='')
            print(itemsToAdd[i])
            addCounter += 1
        print()
        response = pyip.inputYesNo("Type 'Yes' or 'No' and press Enter: ")

        #If the list is correct exit the while loop and add the items to the queue
        print()
        if response == 'yes':
            print('Items have been added to the waiting queue.')
            dividerLine()
            itemsToAddConfirmed = True
        #If the list is incorrect start over (can improve later to edit the items that need to be modified)
        elif response == 'no':
            itemsToAdd.clear()
            dividerLine()

elif answer == 'no':
    dividerLine()

#Update the 'now' variable to account for time spent typing, double-checking, etc.
now = time.time()

#Add the items to the shelf once the list is confirmed
for i in range(len(itemsToAdd)):
    itemShelf[itemsToAdd[i]] = [now, CURRENT_USAGE_STATUS[1]]

#Close the shelf file
itemShelf.close()

#-------------------------------------------------------- Finish the log file. --------------------------------------------------------#

logFile = open(logFilePath, 'a')

logFile.write('\nItems added to waiting queue:\n')
if len(itemsToAdd) == 0:
    logFile.write('None\n')
elif len(itemsToAdd) > 0:
    for i in range(len(itemsToAdd)):
        logFile.write(str(i + 1) + ': ' + itemsToAdd[i] + '\n')

logFile.close()

#-------------------------------------------------------- Exit program. --------------------------------------------------------#

print('Please exit the program.')
dividerLine()

#Close the program
sys.exit()
