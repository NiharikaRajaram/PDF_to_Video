import PyPDF2
import textract
import re
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import shutil
import os
from gtts import gTTS
from google_images_download import google_images_download
from moviepy import editor as mp
from PIL import Image
import pygame

response = google_images_download.googleimagesdownload()

stop = set(stopwords.words('english'))
lemma = WordNetLemmatizer()
_FPS = 24

f_dict = open('dictionary.txt')  # from scrabble words list
scrabble_list = []
for line in f_dict:
    scrabble_list.append(str(line.replace('\n', '').lower()))
f_dict.close()
# print scrabble_list
print("scrabble_list loaded!")

filename = input("Enter the filename :  ")
pdfFileObj = open(filename, 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
num_pages = pdfReader.numPages
count = 0
text = ""
while count < num_pages:
    pageObj = pdfReader.getPage(count)
    count +=1
    text += pageObj.extractText()
if text != "":
    text = text
else:
    text = textract.process(filename, method='tesseract', language='eng')

print(text)

f = open("extracted_text.txt", "w", encoding='utf-8')
f.write(text)
print("Done!")
f.close()

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

def convert_txt_to_clean():
    fr = open('extracted_text.txt', encoding='utf-8')
    full_text = ''
    for line in fr:
        if line == '\n':
            full_text += line + '\n'
            continue
        line = line.replace('\n','')
        line = re.sub(r"[^a-zA-Z0-9'\".,!-]+", ' ', line)
        if len(line) > 3:
            full_text += line+' '
    # print full_text
    fr.close()
    fw = open('clean.txt', 'w') # final text final is stored as filename_clean.txt
    fw.write(full_text.replace('Fig.', 'Figure'))
    fw.close()
    print("conversion from TXT to Clean TXT done!\n")

def format_text(string): #break in to lines to fit the screen
    words=string.split()
    output=''
    buffer_string=''
    for w in words:
        if(len(buffer_string)<50):
            buffer_string+=w+' '
        else:
            output+=buffer_string+'\n'
            buffer_string=w+' '
    output+=buffer_string
    return output

def clean_txt_to_clean_words(doc):
    global scrabble_list
    doc = doc.replace(',', ' ')
    propernouns = doc.lower().split()
    propernouns_clean = [word for word in propernouns if (word not in scrabble_list)]
    propernouns_string = ' '.join(propernouns_clean)
    stop_free = " ".join([i for i in propernouns_string.split() if i not in stop])
    normalized = " ".join(lemma.lemmatize(word) for word in stop_free.split())
    return normalized

def get_topics_from_text1(line):
    doc_complete = line.split('.')
    doc_clean = [clean_txt_to_clean_words(doc).split() for doc in doc_complete]# ignore if length of docs for topic analysis is less than 3
    doc_clean_empty = True
    doc_total_list = []
    all_topics = []
    for doc in doc_clean:
        if len(doc) > 0:
            doc_clean_empty = False
    if len(doc_clean) >=1 and doc_clean_empty == False:
        for doc in doc_clean:
            doc_total_list = doc_total_list + doc

    #print " important word list: ", doc_total_list
    for i in range(0,len(doc_total_list),2):
        if i+2 < len(doc_total_list):
            if (str(doc_total_list[i]) == str(doc_total_list[i+1])) and (str(doc_total_list[i+2]) == str(doc_total_list[i+1])) :
                topic_name = (doc_total_list[i+2])
            elif str(doc_total_list[i]) == str(doc_total_list[i+1]):
                topic_name = (' '.join([doc_total_list[i],doc_total_list[i+2]]))
            elif str(doc_total_list[i+1]) == str(doc_total_list[i+2]):
                topic_name = (' '.join([doc_total_list[i],doc_total_list[i+1]]))
            elif str(doc_total_list[i]) == str(doc_total_list[i+2]):
                topic_name = (' '.join([doc_total_list[i],doc_total_list[i+1]]))
            else:
                topic_name = (' '.join([doc_total_list[i],doc_total_list[i+1],doc_total_list[i+2]]))
            add = False
            for ch in topic_name:# ignore numerical topics
                if ch in r"[abcdefghijklmnopqrstuvwxyz]":
                    add = True
            if add:
                if topic_name not in all_topics:
                    all_topics.append(str(topic_name))

        elif i+1 < len(doc_total_list):
            if str(doc_total_list[i]) == str(doc_total_list[i+1]):
                topic_name = (doc_total_list[i])
            else:
                topic_name = (' '.join([doc_total_list[i],doc_total_list[i+1]]))
            add = False
            for ch in topic_name:# ignore numerical topics
                if ch in r"[abcdefghijklmnopqrstuvwxyz]":
                    add = True
            if add:
                if topic_name not in all_topics:
                    all_topics.append(str(topic_name))

    return all_topics

convert_txt_to_clean()

audio_dir = './audio/tmp'
picture_dir = './downloads'
video_dir = './video'
if os.path.exists(audio_dir):
    shutil.rmtree(audio_dir)

fr = open('clean.txt', encoding='utf-8')
count_lines = 1
for line in fr:
    line = line.replace('\n', '')
    all_topics = get_topics_from_text1(line)
    print('\n\n', line, '\n')
    print("all topics ", all_topics, '\n\n')

audio_dir = './audio/tmp'

if os.path.exists(audio_dir):
    shutil.rmtree(audio_dir)

fr = open('clean.txt', encoding='utf-8')
count_lines = 1
for line in fr:
    line = line.replace('\n', '')
    all_topics = get_topics_from_text1(line)
    print('\n\n', line, '\n')
    if(len(all_topics) > 0):
        print("all topics ", all_topics, '\n\n')
    folder_names = []
    for i in range(0, len(all_topics)):
        if len(all_topics) > 4:
            arguments = {"keywords": all_topics[i], "limit": 2, "size": "medium",
                         "print_urls": False}  # creating list of arguments
            paths = response.download(arguments)  # passing the arguments to the function
            print(paths)
        else:
            arguments = {"keywords": all_topics[i], "limit": 2, "size": "medium",
                         "print_urls": False}  # creating list of arguments
            paths = response.download(arguments)  # passing the arguments to the function
            #print(paths)
        folder_names.append(all_topics[i])

    text_sentences = [f for f in line.split('.') if len(f) > 1]

    if len(text_sentences)<=0:
        continue

    if not os.path.exists(audio_dir):
        os.mkdir(audio_dir)

    print("Creating " + str(len(text_sentences)) + " audio files ")
    for i in range(0, len(text_sentences)):
        tts = gTTS(text=text_sentences[i], lang='en', slow=False)
        tts.save(audio_dir + '/' + str(i) + '.mp3')
        print('\n', text_sentences[i], '\n')
        print("created " + str(i) + " audio file")

    text_clip_list = []
    audio_clip_list = []
    silence = mp.AudioFileClip('./audio/silence.mp3').subclip(0, 0.1)
    audio_clip_list.append(silence)
    for i in range(0, len(text_sentences)):
        sent_audio_clip = mp.AudioFileClip(audio_dir + '/' + str(i) + '.mp3')
        print("length of audio: " + str(i) + " = ", sent_audio_clip.duration)
        audio_clip_list.append(sent_audio_clip)
        sent_txt_clip = mp.TextClip(format_text(text_sentences[i]), font='Courier-Bold', fontsize=150, color='yellow', bg_color='black', stroke_width=30).set_pos('bottom').set_duration(sent_audio_clip.duration).resize(width=1000)
        text_clip_list.append(sent_txt_clip)

    audio_clip = mp.concatenate_audioclips(audio_clip_list)

    file_names = []
    for i in range(0, len(folder_names)):
        files = (fn for fn in os.listdir(picture_dir + '/' + folder_names[i]) if fn.endswith('.jpg') or fn.endswith('.png') or fn.endswith('.PNG') or fn.endswith('.JPG') or fn.endswith('.jpeg') or fn.endswith('.JPEG'))
        for file in files:
            file_names.append(folder_names[i] + '/' + file)

    # s_file_names = sorted(file_names, key=lambda x: x.split('.')[0].split('/')[1])
    s_file_names = file_names
    number_of_images = len(s_file_names)
    print("s_file_names")

    video_clip_list = []
    black_clip = mp.ImageClip('./downloads/black1.jpg').set_duration(0.1).set_fps(_FPS)
    video_clip_list.append(black_clip)
    black = './downloads/black1.jpg'
    title_clip_list = []
    if number_of_images > 0:
        for f in s_file_names:
            temp_clip = mp.ImageClip(picture_dir + '/' + f).set_duration(audio_clip.duration / number_of_images).set_position('center').set_fps(_FPS).crossfadein(0.5)
            name_txt_clip = mp.TextClip(format_text(' '.join([word[:1].upper() + word[1:] for word in f.split('/')[0].split('_')])),font='Courier-Bold', fontsize=200, color='yellow', bg_color='black', stroke_width=30).set_position('top').set_duration(audio_clip.duration / number_of_images).resize(height=30)
            title_clip_list.append(name_txt_clip)
            # temp_clip = CompositeVideoClip([temp1_clip,name_txt_clip])
            video_clip_list.append(temp_clip)
            # minimum_image_size=min([minimum_image_size,temp_clip.size[0]])
            print('temp_clip width: ', temp_clip.size)
    else:
        temp_clip = mp.ImageClip(black).set_duration(audio_clip.duration).set_fps(_FPS)
        video_clip_list.append(temp_clip)
        # minimum_image_size=min([minimum_image_size,temp_clip.size[0]])

    video_clip = mp.concatenate_videoclips(video_clip_list).set_position('center')

    txt_clip = mp.concatenate_videoclips(text_clip_list).set_position('bottom')
    if len(title_clip_list) > 0:
        title_clip = mp.concatenate_videoclips(title_clip_list).set_position('top')
        result = mp.CompositeVideoClip([video_clip, txt_clip, title_clip])
    else:
        result = mp.CompositeVideoClip([video_clip, txt_clip])

    print("Composite video clip size: ", result.size)

    result_with_audio = result.set_audio(audio_clip)

    print("audio duration: " + str(audio_clip.duration))
    print("result duration: " + str(result.duration))
    print("result audio duration: " + str(result_with_audio.duration))

    result_with_audio.write_videofile(video_dir+'/'+str(count_lines)+'.mp4', codec='libx264', fps=_FPS)
    count_lines += 1

    shutil.rmtree(audio_dir)

fr.close()

video_files = [fn for fn in os.listdir(video_dir) if fn.endswith('.mp4')]
video_files = sorted(video_files, key=lambda x: int(x.split('.')[0]))
video_clip_list = []
for video in video_files:
    clip = mp.VideoFileClip(video_dir+'/'+video).crossfadein(0.5)
    video_clip_list.append(clip)

video_clip = mp.concatenate_videoclips(video_clip_list)
video_clip.write_videofile('final.mp4', codec='libx264', fps=_FPS)

clip = mp.VideoFileClip('final.mp4')
clip.preview()

pygame.quit()

