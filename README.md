# gitlab webhook telegram bot

Simple gitlab telegram bot that listen to gitlab webhooks and send each event
to the authenticated chats

https://core.telegram.org/bots

Create a new bot https://core.telegram.org/bots#create-a-new-bot
and then copy the token to the token file.

# Requirements

Only work with python3

# How to use

1. Change the authmsg file with some secret keyworld
1. Run the app.py in your server
1. Create a webhook in your gitlab project that points to
   http://yourserver:10111/
1. Talk to your bot and write only the keyworld
1. You will receive each event in your repo
