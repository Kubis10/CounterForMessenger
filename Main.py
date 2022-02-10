import os
import json

print(os.listdir('data/messages/inbox/'))
f = open('data/messages/inbox/18urodzinyandziuliny_jolrt76jwq/message_1.json', 'r')
data = json.load(f)
totalNum = 0
for i in data['messages']:
    totalNum += 1
print(totalNum)
f.close()
