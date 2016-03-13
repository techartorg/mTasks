"""
This example uses a repeat timer to update a gui clock window once every second.  The clock is non-blocking, so you can
work or run scripts. The updates will suspend during playback or long running tasks but the clock will resume
the correct time when Maya is idle again
"""

import maya.cmds as cmds
import datetime
import mTasks

# create a clock window

w = cmds.window(title = 'clock')
c = cmds.columnLayout(backgroundColor = (.1, .05, .05))
r = cmds.rowLayout(nc=2)
hour = cmds.text(width=128)
cmds.columnLayout()
secs = cmds.text()
am = cmds.text()
cmds.showWindow(w)




def update_time():
    '''
    update the clock display.  This will be called once very second by the repeat task.  It
    does need to yield at the end to allow time-slicing, however
    '''
    now = datetime.datetime.now().time()
    time_string = now.strftime("%-I:%M %S %p")

    hours, seconds, ampm = time_string.split()

    hour_style = "font-size:64px; font-family: Impact; color: #8A0F21"
    sec_style = "font-size:18px; font-family:Arial Black; color: #8A0F21"
    am_style = "font-size:24px; font-family:Arial Black; font-weight:900; color: #700D21"

    def set_control (ctl, value, style):
        def make_text(text, style):
            return '<span style="{0}">{1}</span>'.format(style, text)
        cmds.text(ctl, e=True, label = make_text(value, style))

    set_control(hour, hours, hour_style)
    set_control(secs, seconds, sec_style)
    set_control(am, ampm, am_style)
    yield

# set up the update job to repeat every second
update_task = mTasks.repeat(update_time, 0, 1, 0)
mTasks.task_system.start()
mTasks.spawn(update_task)