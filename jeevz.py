# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %% [markdown]
# ## Search and create GIF
# %% [markdown]
# ### Thoughts
# 
# * Don't just limit to one subtitle, but a set of adjacent ones should also be allowed
# * Fuzzy search

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:\\tejas_gcp_projects\\maybe-well-do-something-d7263a30102e.json"
from google.cloud import bigquery
client = bigquery.Client()

from moviepy.editor import *

# selected_dialogue="""that's what she said%"""
# selected_dialogue="""adult"""


bq_table="tvshow_dialogues.the_office_us"

def list_subtitle_options(selected_dialogue):
    fetch_query='select * from '+bq_table+' where lower(subtitle)like lower(\'\'\'%'+selected_dialogue+'%\'\'\');'
    # fetch_query="""select * from tvshow_dialogues.the_office_us where lower(subtitle) like "%that's what she said%";"""
    # fetch_query="""select * from tvshow_dialogues.the_office_us where lower(subtitle) like lower("%kidding me%");"""
    # select * from tvshow_dialogues.the_office_us where lower(subtitle) like lower("%that's what she said%");
    print(fetch_query)
    query_job = client.query(fetch_query)
    results = query_job.result()
    print(len(list(results)))

    drop_down=[]
    for row in query_job:
        start_time=row.start_time
        end_time=row.end_time
        subtitle_text=row.subtitle
        season_no=row.season
        episode_no=row.episode
        srt_path=row.srt_path
        video_path=row.video_path
        pkey=row.pkey
        drop_down.append(subtitle_text+'||'+video_path.split('\\')[-1]+'||'+srt_path.split('\\')[-1]+'||'+str(pkey))
        #print(row)
    # %%
    # import os
    # import ipywidgets as widgets
    # from ipywidgets import interact, interact_manual
    
    # !telegram-send "I earthling, we will be making GIFs rom the sitcom 'The Office (US)' today. You have choices from Seasons 4,5 and 6. Just enter the name of the dialogue."

    '''
    @interact
    def show_images(selection=drop_down):
        global pkey_selected
        pkey_selected=selection.split('||')[-1]
        #print(pkey_selected)
        return pkey_selected

    print(pkey_selected)
    '''

    return (list(dict.fromkeys(drop_down)))


def generate_gif(pkey_selected):
    fetch_query="select * from "+bq_table+" where pkey="+pkey_selected+";"
    print(fetch_query)
    query_job = client.query(fetch_query)
    results = query_job.result()
    print(len(list(results)))

    drop_down=[]
    for row in query_job:
        start_time=row.start_time
        end_time=row.end_time
        subtitle_text=row.subtitle
        season_no=row.season
        episode_no=row.episode
        srt_path=row.srt_path
        video_path=row.video_path
        pkey=row.pkey
        #drop_down.append(subtitle_text+'||'+video_path.split('\\')[-1]+'||'+srt_path.split('\\')[-1]+'||'+str(pkey))
        print(row)

    # !pip install moviepy
    

    #start_time="00:9:01.541000"
    #end_time="00:9:06.778000"
    start_list=start_time.split(':')
    end_list=end_time.split(':')
    print((int(start_list[1]),float(start_list[2])), (int(end_list[1]),float(end_list[2])))

    episode_clip = (VideoFileClip(video_path)
            .subclip((int(start_list[1]),float(start_list[2])), (int(end_list[1]),float(end_list[2])))
            .resize(0.6))
    #This is going to crash when seconds go negative!

    # subtitle=(TextClip(subtitle_text, fontsize=10, color='white', font='Amiri-Bold', interline=-25).set_duration(episode_clip.duration))
    subtitle=(TextClip(subtitle_text, font='Amiri-Bold', color='white').set_duration(episode_clip.duration))


    composition = CompositeVideoClip( [episode_clip, subtitle] )
    composition.write_gif("use_your_head.gif", fps=10, fuzz=2)

    # loading  gif
    gif = VideoFileClip("use_your_head.gif")
    # showing gif 
    gif.ipython_display() 



import gizoogle
from bot import telegram_chatbot
bot = telegram_chatbot("config.cfg")
update_id = None
firstmsg=0
dialog_entered=0
#subtitle_selected=0
app_started=0
while True:
    updates = bot.get_updates(offset=update_id)
    updates = updates["result"]
    if updates:
        for item in updates:
            print(item)
            update_id = item["update_id"]
            try:
                message = str(item["message"]["text"])
                print(message)
                from_ = item["message"]["from"]["id"]
                
            except:
                try:
                    message = str(item["edited_message"]["text"])
                    from_ = item["edited_message"]["from"]["id"]
                except:
                    pass
                    print("Na ho payega")
            #from_ = item["message"]["from"]["id"]
            #reply = make_reply(message)
            if firstmsg==0:
                reply="Hi earthling, we will be making GIFs from the sitcom 'The Office (US)' today. You have choices from Seasons 4,5 and 6. Type 'bazinga' to get started"
                bot.send_message(reply, from_)
                firstmsg=1
            elif dialog_entered==0 and "bazinga" in message.lower():
                bot.send_message("Which dialogue do you want to make a GIF out of?", from_)
                app_started=1
            elif app_started==1 and dialog_entered==0:    
                bot.send_message("Great choice, this is the format of dialogues that I'll be showing you:", from_)
                bot.send_message("[index_no]  Actual dialog from an episode||Epiosode name||primary_key", from_)
                bot.send_message("-----------------------------------------", from_)
                
                i=1
                list_options=list_subtitle_options(message)
                print("These many disticnt messages "+str(len(list_options)))
                buffer=10
                bot.send_message("There are "+str(len(list_options))+" matches found", from_)
                while buffer<=len(list_options):
                    
                    bot.send_message("Showing "+str(buffer)+" options out of "+str(len(list_options)), from_)
                    for subtitle in list_options[buffer-10:buffer]:
                        reply='['+str(i)+']  '+subtitle
                        bot.send_message(reply, from_)
                        i=i+1                 
                    buffer=buffer+10
                if len(list_options)<10:
                    buffer=0
                print(str(buffer)+" buffer")
                for subtitle in list_options[buffer:len(list_options)]:
                    reply='['+str(i)+']  '+subtitle
                    bot.send_message(reply, from_)
                    i=i+1         

                bot.send_message("-----------------------------------------", from_)
                if len(list_options)>0:
                    bot.send_message("Select the index number of the dialog you want", from_)
                dialog_entered=1
            
            elif dialog_entered==1:
                generate_gif(list_options[int(message)-1].split('||')[-1])
                bot.send_message("Sending you the GIF...", from_)
                gif_path="C:\\Users\\Tejaswa\\Documents\\GitHub\\GIFGenerator\\use_your_head.gif"
                bot.send_file(gif_path, from_)
                # os.system('telegram-send --file C:\\Users\\Tejaswa\\Documents\\GitHub\\GIFGenerator\\use_your_head.gif --timeout 40.0')

                firstmsg=0
                dialog_entered=0
                #subtitle_selected=0
                app_started=0

            else:
                reply = "Bleh"
                bot.send_message(reply, from_)
            #bot.send_message(reply, from_)
            








# %% [markdown]
# ### Making this accesible for all
# Any cloud based solution will basically need episodes available online to be downloaded ino an execution env
# 
# * Upload the seasons to GCS/ YouTube (Unlisted)
# * Turn this into a Colab notebook (thus avoiding data cost/time in downloading the whole episode from where GIF is to be picked)
# 
# * Maybe even break each episode into small ¬5MB chunks and upload
# * Pipe this into a whatsapp/telegram chat? Because share-ability is the most important part. 
# 

