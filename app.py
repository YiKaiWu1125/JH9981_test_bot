from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    MessageTemplateAction,
    TextMessage,
    DatetimePickerAction
)
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///'+ os.path.join(basedir, 'myDB.db')
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

db= SQLAlchemy(app)
db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255))
    catigory = db.Column(db.String(255))
    price = db.Column(db.Integer)
    date = db.Column(db.DateTime)

    def __init__(self, user_id, catigory, price):
        self.user_id = user_id
        self.catigory= catigory
        self.price   = price
    def __init__(self, user_id):
        self.user_id = user_id

@app.route('/callback/', methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

accounting_type = "ĺĺçŠć¨"


@app.route('/', method=['GET'])
def index():
    qu = request.args['q']
    user = User.query.filter_by(user_id=qu).all()
    return user

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user = User.query.filter_by(user_id=event.source.user_id).first()
    if user is None or user.price:
        db.session.add(User(event.source.user_id))
        line_bot_api.reply_message(  # ĺĺžŠĺłĺĽçč¨ćŻćĺ­
                        event.reply_token,
                        TemplateSendMessage(
                            alt_text='Buttons template',
                            template=ButtonsTemplate(
                                title='č¨ĺ¸łéĄĺ',
                                text='čŤé¸ćč¨ĺ¸łéĄĺ',
                                actions=[
                                    MessageTemplateAction(
                                        label='ĺ',
                                        text='ĺ'
                                    ),
                                    MessageTemplateAction(
                                        label='ĺ',
                                        text='ĺ'
                                    ),
                                    MessageTemplateAction(
                                        label='çŠ',
                                        text='çŠ'
                                    ),
                                    MessageTemplateAction(
                                        label='ć¨',
                                        text='ć¨'
                                    )
                                ]
                            )
                        )
                    )
    elif user.price == 'null':
        user.price = -1
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='čŤčź¸ĺĽĺšä˝')
        )
    elif user.price == -1 :
        user.price = event.message.text
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                            alt_text='Buttons template',
                            actions=DatetimePickerAction(
                                mode='date'
                            )
                        )
        )
    elif user.date == 'null':
        user.date = event.message.text
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='ĺĽ˝ă')
        )
    
    db.session.commit()
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=event.message.text)
    # )


@handler.default()
def handle_default(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Currently only support text message')
    )