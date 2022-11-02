#coding=utf-8
import socket
import json
import sys
import os.path
import uuid
import stomp

STATUS = 'status'
MESSAGE = 'message'
TOKEN = 'token'
INVITE = 'invite'
FRIEND = 'friend'
POST = 'post'
SUBSCRIBE = 'subscribe'
GROUP = 'group'

listen_ip = sys.argv[1]
listen_port = int(sys.argv[2])

actvmq = stomp.Connection(host_and_ports=[('18.219.36.31', 61613)])
#actvmq.set_listener('', MyListener())
actvmq.start()
actvmq.connect('admin', 'admin', wait=True)

# load db
if os.path.isfile('user_db.txt'):
    fr = open('user_db.txt')
    user_db = json.loads(fr.read())
    fr.close()
else:
    user_db = {'SYSTEMgrouplist':[]}

user_struct = {
    'passwd' : None,
    'incoming_invitation' : None,
    'outgoing_invitation' : None,
    'friends' : None,
    'posts' : None,
    'groups' : None
}
login_db = {} # token : username

# creat socket
sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.bind((listen_ip, listen_port))
sk.listen(1)
while True:
    (connect_sk, client) = sk.accept()
    print 'connect by', client
    request = connect_sk.recv(2048).decode()
    print 'request:', request
    brok_rqst = request.split()
    cmd = brok_rqst[0]
    rsp = {
        STATUS : -1,
        MESSAGE: ''
    }
    # processing command
    if cmd == 'register':
        if len(brok_rqst) == 3:
            username = brok_rqst[1]
            if username not in user_db:
                user_db.update({brok_rqst[1] : dict(user_struct)})
                user_db[username]['passwd'] = brok_rqst[2]
                user_db[username]['incoming_invitation'] = list()
                user_db[username]['outgoing_invitation'] = list()
                user_db[username]['friends'] = list()
                user_db[username]['posts'] = list()
                user_db[username]['groups'] = list()
                rsp[STATUS] = 0
                rsp[MESSAGE] = u'Success!​'
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = username + ' is already used'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = u'Usage: register ​<id>​ ​<password>​'
    elif cmd == 'login':
        if len(brok_rqst) == 3:
            if brok_rqst[1] in user_db and brok_rqst[1] not in login_db.values() and brok_rqst[2] == user_db[brok_rqst[1]]['passwd']:
                token = str(uuid.uuid4())
                login_db.update({token:brok_rqst[1]})
                rsp.update({TOKEN:token})
                rsp.update({GROUP:user_db[brok_rqst[1]]['groups']})
                rsp[STATUS] = 0
                rsp[MESSAGE] = 'Success!​'
            elif brok_rqst[1] in user_db and brok_rqst[1] in login_db.values() and brok_rqst[2] == user_db[brok_rqst[1]]['passwd']:
                for tok, name in login_db.items():
                    if name == brok_rqst[1]:
                        token = tok
                        break
                rsp.update({TOKEN:token})
                rsp.update({GROUP:user_db[brok_rqst[1]]['groups']})
                rsp[STATUS] = 0
                rsp[MESSAGE] = 'Success!​'
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'No such user or password error'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Usage: login ​<id>​ ​<password>​'
    elif cmd == 'delete':
        if len(brok_rqst) >= 2 and brok_rqst[1] in login_db:
            if len(brok_rqst) == 2:
                username = login_db[brok_rqst[1]]
                for friend in user_db[username]['friends']:
                    user_db[friend]['friends'].remove(username)
                for invitee in user_db[username]['outgoing_invitation']:
                    user_db[invitee]['incoming_invitation'].remove(username)
                rsp.update({GROUP:user_db[username]['groups']})
                user_db.pop(username)
                login_db.pop(brok_rqst[1])
                rsp[STATUS] = 0
                rsp[MESSAGE] = 'Success!​'
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'Usage: delete ​<user>​'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Not login yet'
    elif cmd == 'logout':
        if len(brok_rqst) >= 2 and brok_rqst[1] in login_db:
            username = login_db[brok_rqst[1]]
            if len(brok_rqst) == 2:
                login_db.pop(brok_rqst[1])
                rsp[STATUS] = 0
                rsp.update({GROUP:user_db[username]['groups']})
                rsp[MESSAGE] = 'Bye!​'
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'Usage: logout ​<user>​'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Not login yet'
    elif cmd == 'invite':
        if 2 <= len(brok_rqst) and brok_rqst[1] in login_db:
            if len(brok_rqst) == 3:
                username = login_db[brok_rqst[1]]
                invitee = brok_rqst[2]

                if invitee in user_db[username]['friends']:
                    rsp[STATUS] = 1
                    rsp[MESSAGE] = invitee + ' is already your friend'
                elif invitee not in user_db:
                    rsp[STATUS] = 1
                    rsp[MESSAGE] = invitee + ' does not exist'
                elif username == invitee:
                    rsp[STATUS] = 1
                    rsp[MESSAGE] = 'You cannot invite yourself'
                elif invitee in user_db[username]['outgoing_invitation']:
                    rsp[STATUS] = 1
                    rsp[MESSAGE] = 'Already invited'
                elif invitee in user_db[username]['incoming_invitation']:
                    rsp[STATUS] = 1
                    rsp[MESSAGE] = invitee + ' has invited you'
                else:
                    user_db[username]['outgoing_invitation'].append(invitee)
                    user_db[invitee]['incoming_invitation'].append(username)
                    rsp[STATUS] = 0
                    rsp[MESSAGE] = 'Success!​'
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'Usage: invite ​<user>​ ​<id>​'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Not login yet'
    elif cmd == 'accept-invite':
        if 2 <= len(brok_rqst) and brok_rqst[1] in login_db:
            if len(brok_rqst) == 3:
                username = login_db[brok_rqst[1]]
                inviter = brok_rqst[2]

                if inviter not in user_db[username]['incoming_invitation']:
                    rsp[STATUS] = 1
                    rsp[MESSAGE] = inviter + ' did not invite you'
                else:
                    user_db[username]['incoming_invitation'].remove(inviter)
                    user_db[username]['friends'].append(inviter)
                    user_db[inviter]['outgoing_invitation'].remove(username)
                    user_db[inviter]['friends'].append(username)
                    rsp[STATUS] = 0
                    rsp[MESSAGE] = 'Success!​'
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'Usage: accept-invite ​<user>​ ​<id>​'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Not login yet'
    elif cmd == 'list-invite':
        if len(brok_rqst) >= 2 and brok_rqst[1] in login_db:
            if len(brok_rqst) == 2:
                username = login_db[brok_rqst[1]]
                rsp[STATUS] = 0
                rsp.update({INVITE : user_db[username]['incoming_invitation']})
                rsp.pop(MESSAGE)
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'Usage: list-invite ​<user>'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Not login yet'
    elif cmd == 'list-friend':
        if len(brok_rqst) >= 2 and brok_rqst[1] in login_db:
            if len(brok_rqst) == 2:
                username = login_db[brok_rqst[1]]
                rsp[STATUS] = 0
                rsp.update({FRIEND : user_db[username]['friends']})
                rsp.pop(MESSAGE)
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'Usage: list-friend ​<user>'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Not login yet'
    elif cmd == 'post':
        if len(brok_rqst) >= 2 and brok_rqst[1] in login_db:
            username = login_db[brok_rqst[1]]
            if len(brok_rqst) != 2:
                sentence = request.split(' ', 2)[2]
                user_db[username]['posts'].append(sentence)
                rsp[STATUS] = 0
                rsp[MESSAGE] = 'Success!​'
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'Usage: post ​<user> ​​<message>'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Not login yet'
    elif cmd == 'receive-post':
        if len(brok_rqst) >= 2 and brok_rqst[1] in login_db:
            if len(brok_rqst) == 2:
                username = login_db[brok_rqst[1]]
                received = []
                for friend in user_db[username]['friends']:
                    for post in user_db[friend]['posts']:
                        formed_post = {
                            'id' : friend,
                            'message' : post
                        }
                        received.append(formed_post)
                rsp[STATUS] = 0
                rsp.update({POST : received})
                rsp.pop(MESSAGE)
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'Usage: receive-post ​<user>'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Not login yet'
    elif cmd == 'send':
        if len(brok_rqst) >= 2 and brok_rqst[1] in login_db:
            username = login_db[brok_rqst[1]]
            if len(brok_rqst) >= 4:
                receiver = brok_rqst[2]
                if receiver in user_db:
                    if receiver in user_db[username]['friends']:
                        if receiver in login_db.values():
                            sentence = request.split(' ', 3)[3]
                            actvmq.send(body = sentence, destination = '/topic/private/' + receiver, headers = {'sender':username, 'type':'private'})
                            rsp[STATUS] = 0
                            rsp[MESSAGE] = 'Success!​'
                        else:
                            rsp[STATUS] = 1
                            rsp[MESSAGE] = receiver + ' is not online'
                    else:
                        rsp[STATUS] = 1
                        rsp[MESSAGE] = receiver + ' is not your friend'
                else:
                    rsp[STATUS] = 1
                    rsp[MESSAGE] = 'No such user exist'
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'Usage: send ​<user> <friend> ​​<message>'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Not login yet'
    elif cmd == 'create-group':
        if len(brok_rqst) >= 2 and brok_rqst[1] in login_db:
            username = login_db[brok_rqst[1]]
            if len(brok_rqst) == 3:
                group_name = brok_rqst[2]
                if group_name not in user_db['SYSTEMgrouplist']:
                    user_db[username]['groups'].append(group_name)
                    user_db['SYSTEMgrouplist'].append(group_name)
                    rsp[STATUS] = 0
                    rsp.update({SUBSCRIBE:group_name})
                    rsp[MESSAGE] = 'Success!​'
                else:
                    rsp[STATUS] = 1
                    rsp[MESSAGE] = group_name + ' already exist'
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'Usage: create-group <user> <group>'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Not login yet'
    elif cmd == 'list-group':
        if len(brok_rqst) >= 2 and brok_rqst[1] in login_db:
            if len(brok_rqst) == 2:
                rsp[STATUS] = 0
                rsp.update({GROUP:user_db['SYSTEMgrouplist']})
                rsp.pop(MESSAGE)
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'Usage: list-group ​<user>'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Not login yet'
    elif cmd == 'list-joined':
        if len(brok_rqst) >= 2 and brok_rqst[1] in login_db:
            username = login_db[brok_rqst[1]]
            if len(brok_rqst) == 2:
                rsp[STATUS] = 0
                rsp.update({GROUP:user_db[username]['groups']})
                rsp.pop(MESSAGE)
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'Usage: list-joined ​<user>'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Not login yet'
    elif cmd == 'join-group':
        if len(brok_rqst) >= 2 and brok_rqst[1] in login_db:
            username = login_db[brok_rqst[1]]
            if len(brok_rqst) == 3:
                group_name = brok_rqst[2]
                if group_name in user_db['SYSTEMgrouplist']:
                    if group_name not in user_db[username]['groups']:
                        user_db[username]['groups'].append(group_name)
                        rsp[STATUS] = 0
                        rsp.update({SUBSCRIBE:group_name})
                        rsp[MESSAGE] = 'Success!​'
                    else:
                        rsp[STATUS] = 1
                        rsp[MESSAGE] = 'Already a member of ' + group_name
                else:
                    rsp[STATUS] = 1
                    rsp[MESSAGE] = group_name + ' does not exist'
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'Usage: join-group <user> <group>'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Not login yet'
    elif cmd == 'send-group':
        if len(brok_rqst) >= 2 and brok_rqst[1] in login_db:
            username = login_db[brok_rqst[1]]
            if len(brok_rqst) >= 4:
                group = brok_rqst[2]
                if group in user_db['SYSTEMgrouplist']:
                    if group in user_db[username]['groups']:
                        sentence = request.split(' ', 3)[3]
                        actvmq.send(body = sentence, destination = '/topic/public/' + group, headers = {'sender':username, 'type':'group'})
                        rsp[STATUS] = 0
                        rsp[MESSAGE] = 'Success!​'
                    else:
                        rsp[STATUS] = 1
                        rsp[MESSAGE] = 'You are not the member of ' + group
                else:
                    rsp[STATUS] = 1
                    rsp[MESSAGE] = 'No such group exist'
            else:
                rsp[STATUS] = 1
                rsp[MESSAGE] = 'Usage: send-group ​<user> <group> ​​<message>'
        else:
            rsp[STATUS] = 1
            rsp[MESSAGE] = 'Not login yet'
    else:
        rsp[STATUS] = 1
        rsp[MESSAGE] = 'Unknown command ' + cmd
    # store user_db
    print json.dumps(user_db, indent=2, sort_keys=True)
    print json.dumps(login_db, indent=2, sort_keys=True)
    print json.dumps(rsp, indent=2, sort_keys=True)
    fw = open('user_db.txt', 'w')
    fw.write(json.dumps(user_db))
    fw.close()
    connect_sk.sendall(json.dumps(rsp).encode())
    connect_sk.close()
sk.close()
actvmq.disconnect()
