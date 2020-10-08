import slack
import datetime
import threading
import json
from requests_oauthlib import OAuth1Session

rtmclient = slack.RTMClient(token='xoxb-************-************-************************')

API_KEY = '*************************'
API_SECRET = '**************************************************'
ACCESS_TOKEN = '*******************-******************************'
ACCESS_TOKEN_SECRET = '*********************************************'

auth = OAuth1Session(API_KEY, client_secret=API_SECRET,
                        resource_owner_key=ACCESS_TOKEN,
                        resource_owner_secret=ACCESS_TOKEN_SECRET)

@slack.RTMClient.run_on(event='hello')
def Hello(**payload):
    webClient = payload['web_client']
    def current_Hour():
        time = datetime.datetime.now().strftime("%H:%M:%S")
        webClient.chat_postMessage(channel='#content', text='Current Hour: ' + time)
        threading.Timer(3600.0, current_Hour).start()

    def start_Stream():
        r = auth.get('https://stream.twitter.com/1.1/statuses/filter.json?follow=1210363485273628674', stream=True)
        for tweet in r.iter_lines():
            if tweet:
                try:
                    webClient.chat_postMessage(channel='#content', text="New Tweet from David Saal - " +
                                                                    json.loads(tweet.decode("utf-8"))['text'])
                except Exception:
                    pass

    current_Hour()
    threading.Thread(target=start_Stream).start()

@slack.RTMClient.run_on(event='message')
def Tweets(**payload):
    Data = payload['data']
    webClient = payload['web_client']

    def pullTweets(name):
        Date = datetime.datetime.now().date()
        Hour = datetime.datetime.now().hour
        r = auth.get('https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=' + name + '&count=100&'
                                                                                                     'tweet_mode=extended')
        for tweet in r.json():
            i = 1
            tweetDate = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            if tweetDate.date() < Date:
                break
            if tweetDate.hour + 2 == Hour:
                if 'retweeted_status' in tweet:
                    webClient.chat_postMessage(channel='#content', text=str(i) + ') ' + tweet['retweeted_status']['full_text'])
                else:
                    webClient.chat_postMessage(channel='#content', text=str(i) + ') ' + tweet['full_text'])
                i += 1

    if Data['text'] == 'new-content':
        webClient.chat_postMessage(channel='#content', text="---'Python Weekly' Tweets---")
        pullTweets('PythonWeekly')

        webClient.chat_postMessage(channel='#content', text="---'Real Python' Tweets---")
        pullTweets('realpython')

        webClient.chat_postMessage(channel='#content', text="---'Full Stack Python' Tweets---")
        pullTweets('fullstackpython')

    elif 'new-content '  in Data['text']:
        text = Data['text'].split("new-content ",1)[1]
        webClient.chat_postMessage(channel='#content', text='---' + text + ' Tweets---')
        pullTweets(text)

    if Data['text'] == 'timenow':
        time = datetime.datetime.now().strftime("%H:%M:%S")
        webClient.chat_postMessage(channel='#content', text='Current Hour: ' + time)

    if 'tweetnow ' in Data['text']:
        text = Data['text'].split("tweetnow ",1)[1]
        auth.post('https://api.twitter.com/1.1/statuses/update.json', {'status': text})

try:
    print("SlackBot Is Connected!")
    rtmclient.start()
except Exception as error:
    print(error)