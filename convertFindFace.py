import logging
import requests
import urllib.request
import pymongo
from pymongo import MongoClient
from telegram import InputMedia
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
from os import listdir
from os.path import isfile, join 
import pydub
from pydub import AudioSegment
import gridfs
from gridfs import GridFSBucket
import glob
import subprocess
import cv2


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

AudioSegment.converter = 'PATH\TO\ffmpeg.exe'
AudioSegment.ffmpeg = "PATH\TO\ffmpeg.exe"
AudioSegment.ffprobe ="PATH\TO\ffprobe.exe"


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


my_db = MongoClient('mongodb+srv://art:1234@cluster0.ei2iq.mongodb.net/<dbname>?retryWrites=true&w=majority')
db = my_db["AudioFace"]
collection = db['audio']

fs = gridfs.GridFS(db)

def start(update, context):
    update.message.reply_text('Привет, отправьте мне голосовое либо MP3 файл - и я сконвертирую его в файл формата WAV\nТакже я могу определить, есть ли на вашей фотографии лицо. Не веришь - просто отправь фото.\n---\nСоздатель - @Inefive')

def help_command(update, context):
    update.message.reply_text('Помогите')

def getvoice(update, context):
    voice_mess = update.message.voice
    user = update.message.from_user
    message = update.message
    get_file = voice_mess.get_file()
    down_file = get_file.download()

    update.message.reply_text(f'Пользователь {user.username} отправил голосовое сообщение со следующим id: {message.message_id}.\nВремя: {message.date} ')
    update.message.reply_voice(voice_mess)
   
    oga_files = glob.iglob('**/*.oga', recursive=True)
    oga_files = [f for f in oga_files if os.path.isfile(f)]

    voice_dict = {'username': f'{user.username}', 'message_id': f'{message.message_id}', 'file':f'{oga_files[-1]}', 'Date':f'{message.date}'}
    collection.insert_one(voice_dict)

    src_filename = oga_files[-1]

    g = (oga_files[-1].split('_'))
    gg = g[1].split('.')
    dest_filename = 'output' + f'{gg[0]}' + '.wav'

    process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename]) #прогоняем чтобы все src cделать dest через библиотеку ffmpeg
    if process.returncode != 0:
        raise Exception("Something went wrong")

    wav_files = glob.iglob('**/*.wav', recursive=True)
    wav_files = [w for w in wav_files if os.path.isfile(w)]
    
    document = open(wav_files[-1], 'rb')
    doc = update.message.reply_audio(document)

def getaudio(update, context):
    audio_mess = update.message.audio
    user = update.message.from_user
    message = update.message
    get_file = audio_mess.get_file()
    down_file = get_file.download()

    update.message.reply_text(f'Пользователь {user.username} отправил голосовое сообщение со следующим id: {message.message_id}.\nВремя: {message.date} ')
    update.message.reply_audio(audio_mess)

    mp3_files = glob.iglob('**/*.mp3', recursive=True)
    mp3_files = [mp for mp in mp3_files if os.path.isfile(mp)]

    audio_dict = {'username': f'{user.username}', 'message_id': f'{message.message_id}', 'file':f'{mp3_files[-1]}', 'Date':f'{message.date}'}
    collection.insert_one(audio_dict)

    src_filename = mp3_files[-1]
    

    l = (mp3_files[-1].split('_'))
    ll = l[1].split('.')
    dest_filename = 'output' + f'{ll[0]}' + '.wav'

    process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename]) #прогоняем чтобы все src cделать dest через библиотеку ffmpeg
    if process.returncode != 0:
        raise Exception("Something went wrong")
    
    wav_files = glob.iglob('**/*.wav', recursive=True)
    wav_files = [w for w in wav_files if os.path.isfile(w)]
    
    document = open(wav_files[-1], 'rb')
    doc = update.message.reply_audio(document)

def face(update,context):
    face_photo = update.message.photo
    user = update.message.from_user
    print(face_photo[-1])
    message_id = update.message.message_id
    get_file = face_photo[-1].get_file()
    down_file = get_file.download()
    
    direction_1 = os.listdir('D:\Put\ConvertFindFaceBot')
    files_1 = [ fname for fname in direction_1 if fname.startswith('f') and fname.endswith('.jpg')]
    print(files_1)
    img = cv2.imread(files_1[-2])

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    for (x,y,w,h) in faces:
        a = cv2.rectangle(img, (x,y), (x+w, y+h), (255,0,0), 2)

    helen = len(faces)
    if helen !=0:
        photo_file = cv2.imwrite('photo_face' + f'{message_id}' + '.jpg', img)
        update.message.reply_text(f'Найдено лиц на фото: {helen}')
        direction_2 = os.listdir('D:\Put\ConvertFindFaceBot')
        files_2 = [ fname for fname in direction_2 if fname.startswith('photo_')]
        true_file = open(files_2[-1], 'rb')
        update.message.reply_photo(true_file)
        update.message.reply_text('Больше не отправляй это фото')
    else:
        update.message.reply_text('Либо со мной что-то, либо ты скинул фото без лиц')


def main():

    updater = Updater("1252155050:AAEtDOGvecT8bDQWoj2Ja1LNC4LillgKmiE", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    dp.add_handler(MessageHandler(Filters.voice & ~Filters.command, getvoice))
    dp.add_handler(MessageHandler(Filters.audio & ~Filters.command, getaudio))
    dp.add_handler(MessageHandler(Filters.photo & ~Filters.command, face))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
