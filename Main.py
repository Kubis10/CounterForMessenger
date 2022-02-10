import os
import json

def countPerPerson(data):
    totalNum = 0
    for i in os.listdir('data/messages/inbox/'+data):
        with open('data/messages/inbox/' + i + "/" + j, 'r') as f:
            data = json.load(f)
            for i in data['messages']:
                totalNum += 1
    f.close()
    return totalNum


for i in os.listdir('data/messages/inbox/'):
    print(countPerPerson(i))

