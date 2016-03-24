__author__ = 'stevet'
"""
An example showing how to use an external thread without access problems.  It creates a simple window
which is updated in 'real time' for news stories, using an external thread to get the stories via
http and an mTask ExternalResultTask object to update the gui in 'quasi-real-time'.

The maya scene remains functional throughout: you can work or even play back animations and the window will continue
to receive updates (although these will not show during playback -- they'll be queued up while Maya plays
and will appear in a rush when playback stops).

"""

import urllib2
import xml.etree.ElementTree as et
import time
import maya.cmds as cmds
import mTasks
import mTasks.threads


def news_reader():
    '''

    Creates a news reader window with a scroll layout to display news stories coming from mTasks. This illustrates how
    mTasks can work directly on maya elements (in this case, gui -- but it could also be scene items) without the need
    for executeDeferredInMainThread.
    '''

    # create and display the news reader
    window = cmds.window(title= 'Sporting News')
    layout = cmds.formLayout()
    display_list = cmds.textScrollList()
    delete_button = cmds.button(label = 'delete selected')
    button_attachments = [ (delete_button, item, 0) for item in ( 'top', 'left', 'right')]
    cmds.formLayout(layout, e= True, attachForm = button_attachments)

    text_attachments = [ (display_list, item, 0) for item in ( 'bottom', 'left', 'right')]
    cmds.formLayout(layout, e= True, attachForm = text_attachments)
    cmds.formLayout(layout, e= True, attachControl = (display_list, 'top',  0, delete_button))

    # this deletes a story from the list -- it's useful for showing how there is no
    # problem with thread collisions

    def delete_item(_):
        selected =     cmds.textScrollList(display_list, q=True, sii=True)
        if selected:
            cmds.textScrollList(display_list, e=True, rii=selected)

    cmds.button(delete_button, e=True, command = delete_item)
    cmds.showWindow(window)



    def poll_news(result_queue):
        '''
        This function runs in its own thread, collecting rss feeds and putting them into the result queue
        '''

        feeds = {
            'http://feeds.thescore.com/uefa.rss',
            'http://feeds.thescore.com/nfl.rss',
            'http://feeds.thescore.com/nba.rss',
            'http://feeds.thescore.com/chlg.rss',
            'http://feeds.thescore.com/atp.rss',
            'http://feeds.thescore.com/wta.rss',
            'http://feeds.thescore.com/lpga.rss',
            'http://feeds.thescore.com/nhl.rss'

        }

        existing_stories = set()

        def get_news(feed):
            response = urllib2.urlopen(feed)
            tree = et.ElementTree().parse(response)
            headlines = []
            for item in tree:
                for child in item.findall('item'):
                    headlines.append(child.find('title').text)
            return headlines

        while len(existing_stories) < 1000:
            for feed in feeds:
    
                new_news = get_news(feed)
                new_stories = set(new_news) - existing_stories
                for new_story in new_stories:
                    existing_stories.add(new_story)
                    result_queue.put(new_story)
                    time.sleep(2.5)

    # this callback watches the result queue and updates the window as new items are added to the result queue

    def update_job(result_queue):
        if not result_queue.empty():
            new_item = result_queue.get()
            cmds.textScrollList(display_list, e = True, append = new_item)

    # the AsyncPollTask object will start the thread and share a python Queue object
    # between the news reader thread and the callback which publishes the results to the gui

    news_thread = mTasks.threads.AsyncPollTask(poll_news, update_job)
    mTasks.spawn(news_thread)

# start the task system and open the reader
mTasks.task_system.start()
news_reader()
