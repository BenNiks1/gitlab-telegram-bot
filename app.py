#!/usr/bin/env python3

import json
from flask import Flask, request, jsonify
from bot import Bot
import jinja2
import os
from config import AUTH_MSG, TOKEN

app = Flask(__name__)

class GitlabBot(Bot):
    def __init__(self):
        self.authmsg = AUTH_MSG
        super(GitlabBot, self).__init__(TOKEN)
        self.chats = {}
        try:
            with open('chats', 'r') as f:
                self.chats = json.loads(f.read())
        except FileNotFoundError:
            with open('chats', 'w') as f:
                f.write(json.dumps(self.chats))
        self.send_to_all('Hi !')

    def text_recv(self, txt, chatid):
        ''' registering chats '''
        txt = txt.strip()
        if txt.startswith('/'):
            txt = txt[1:]
        if txt == self.authmsg:
            if str(chatid) in self.chats:
                self.reply(chatid, "\U0001F60E  Вы уже авторизованы.")
            else:
                self.reply(chatid, "\U0001F60E  Авторизация прошла успешно!")
                self.chats[chatid] = True
                with open('chats', 'w') as f:
                    f.write(json.dumps(self.chats))
        elif txt == 'shutupbot':
            del self.chats[chatid]
            self.reply(chatid, "\U0001F63F Извини.")
            with open('chats', 'w') as f:
                f.write(json.dumps(self.chats))
        else:
            self.reply(chatid, "\U0001F612 Нет доступа.")

    def send_to_all(self, msg):
        print(self.chats)
        for c in self.chats:
            self.reply(c, msg, parse_mode='HTML')

b = GitlabBot()

environment = jinja2.Environment()

template = environment.from_string(
    '<a href="{{link}}">{{name}} - {{title}}</a> \n\n{{source_branch}} -> {{target_branch}} \n\n👨💻: {{user}}'
)

def requestStatus(status):
    if status == 'open':
        return '⭐ Новый МР'
    elif status == 'close':
        return '🪳 МР удален'
    elif status == 'update':
        return '✍🏻 Внесены изменения'
    elif status == 'reopen':
        return '🤡 МР вновь открыт'
    elif status == 'merge':
        return '🚣🏾 Залито'

def templateRender(type, title, data):
    if type == 'mr':
        return title + "\n" + template.render(
            name=data['project']['name'],
            link=data['object_attributes']['url'],
            title=data['object_attributes']['title'],
            source_branch=data['object_attributes']['source_branch'],
            target_branch=data['object_attributes']['target_branch'],
            user=data['user']['name']
        )
    else:
        return title + "\n" + template.render(
            name=data['project']['name'],
            link=data['object_attributes']['url'],
            title=data['merge_request']['title'],
            source_branch=data['merge_request']['source_branch'],
            target_branch=data['merge_request']['target_branch'],
            user=data['user']['name'],
            comment='Комментарий: ' + data['object_attributes']['note']
        )

@app.route("/", methods=['GET', 'POST'])
def webhook():
    data = request.json
    print(data)  # Inspect the payload structure in your logs

    kind = data['object_kind']
    if kind == 'merge_request':
        msg = templateRender('mr', requestStatus(data['object_attributes']['action']), data)
    elif kind == 'note':
        msg = generateCommentMsg(data)
    # TODO: мб добавить обработку других событий   
    b.send_to_all(msg)
    return jsonify({'status': 'ok'})

def generateCommentMsg(data):
    print(data)
    ntype = data['object_attributes']['noteable_type']
    if ntype == 'Commit':
        msg = templateRender('comment', '🪃 Новый коммит', data)
    elif ntype == 'MergeRequest':
        msg = templateRender('comment', '🪃 Новый комментарий', data)
    elif ntype == 'Issue':
        msg = templateRender('comment', '🪃', data)
    return msg

if __name__ == "__main__":
    b.run_threaded()
    app.run(host='0.0.0.0', port=10111)
