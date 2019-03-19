# coding: utf-8
# from __future__ import unicode_literals
import csv
import sys
import time
import datetime
import random
import pathlib
from glob import glob
from random import randint
import os
from shutil import copyfile
from os.path import join, dirname
from operator import itemgetter
from datetime import datetime
import encodings

import kivy
kivy.require('1.10.1')
from kivy import Config
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.pagelayout import PageLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from kivy.uix.button import Label
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty, NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty
from kivy.vector import Vector
from kivy.clock import Clock
Config.set('graphics', 'multisamples', '0')
Config.set('input', 'mouse', 'mouse,disable_multitouch')


# GLOBALS ======================================================================

global AdminMode

AdminMode = 0

if len(sys.argv) > 1:
    print("SYS = ", sys.argv[1])
    if str(sys.argv[1]) == "admin":
        AdminMode = 1

global CSV_invites
global Chaises 
global Tables
global curdir
global SelectedChair
global SelectedTable
# global SelectedChairLabelInstance
# global ChairsController


curdir = dirname(__file__)
CSV_invites = join(curdir, 'mariage.csv')




Chaises = []
Tables = []
# ChairsController = []
SelectedChair = "0000"
SelectedTable = "0000"



# CLASSES ========================================================================




class Mariage(App):
    def build(self):
        # root = self.root
        root = BoxLayout(orientation='horizontal')
        background = Background(size_hint=(.85, 1))

        # get any files into images directory
        # for filename in glob(join(curdir, 'images', '*')):
        #     try:
        #         # load the image
        #         picture = Picture(source=filename, rotation=randint(-30, 30))
        #         # add to the main field
        #         background.add_widget(picture)
        #     except Exception as e:
        #         Logger.exception('Pictures: Unable to load <%s>' % filename)

        # add tables to background
        for tab in Tables:
            # tablepic = TablePicture(source=tab["TEX"], tablename=tab["TABLE"], pos=(int(tab["X"]), int(tab["Y"])), rotation=0, do_rotation=False, do_scale=False)
            # tablepic.bind(pos=callback_pos)
            if tab["TYPE"]=="tableronde":
                tablepic = RoundTable(source=tab["TEX"], tablename=tab["TABLE"], pos=(int(tab["X"]), int(tab["Y"])),size=(int(tab["L"]), int(tab["H"])), on_press=callback_press)
                background.add_widget(tablepic)
            if tab["TYPE"]=="table":
                tablepic = TableButton(source=tab["TEX"], tablename=tab["TABLE"], pos=(int(tab["X"]), int(tab["Y"])),size=(int(tab["L"]), int(tab["H"])), on_press=callback_press)
                background.add_widget(tablepic)

        # global ChairsController
        for cha in Chaises:
            if cha["TYPE"]=="chaise":
                if cha["X"] == "0" and cha["Y"] == "0":
                    posit=(randint(0, 1500),randint(0, 1080))
                else:
                    posit=(int(cha["X"]), int(cha["Y"]))
                chairpic = ChairELT(id="CHAIR", source=cha["TEX"], tablename=cha["TABLE"], tid=str(cha["TID"]), cid=str(cha["CID"]), guestname=cha["NOM"], pos=posit, size=(int(cha["L"]), int(cha["H"])), rot=cha["ROT"], do_rotation=False, do_scale=False, do_translation=AdminMode)
                # ChairsController.append(ChairELT)
                background.add_widget(chairpic)

        # Button to save positions
        if AdminMode:
            svbutt = SaveButton()
            background.add_widget(svbutt)

        # Clock
        basicClock = ZeClock(pos=(200, 0), size=(200,50))
        background.add_widget(basicClock)
        Clock.schedule_interval(basicClock.update, 1)

        # Selected Chair Label
        # global SelectedChairLabelInstance
        lab = SelectedChairLabel(id="SelectedGuest",pos=(600, 0), size=(200,50), font_size='30sp')
        background.add_widget(lab)



        # Clock.schedule_interval(block.fall, 1/60)
        root.add_widget(background)

        scl = ScrollView(size_hint=(.10, 1))
        Buttonlayout = GridLayout(cols=1, spacing=2, size_hint_y=None)
        Buttonlayout.bind(minimum_height=Buttonlayout.setter('height'))
        for cha in Chaises:
            btn = ListButton(tablename=cha["TABLE"], tid=str(cha["TID"]), cid=str(cha["CID"]), guestname=cha["NOM"], text=cha["NOM"], size_hint_y=None, height=50, text_size=(100,None), font_size='20sp')
            Buttonlayout.add_widget(btn)
        scl.add_widget(Buttonlayout)
        root.add_widget(scl)

        return root
    # def on_pause(self):
    #     return True


class Background(Widget):
    source = StringProperty(None)



# CLASSES : Objects - - - - - - - - - - - - 

class ZeClock(Label):
    def update(self, *args):
        self.text = time.asctime()

class SelectedChairLabel(Label):
    guestname = StringProperty(None)


# class RoundTable(ButtonBehavior, Widget):
class RoundTable(ButtonBehavior, Widget):
    source = StringProperty(None)
    tablename = StringProperty(None)


class TableButton(Button):
    source = StringProperty(None)
    tablename = StringProperty(None)


class Chair(Widget):
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(-1)
    position = ReferenceListProperty(vel_x,vel_y)
    def fall(self, pos):
        self.pos =  Vector(self.position) + self.pos


class ChairELT(Scatter):
    source = StringProperty(None)
    guestname = StringProperty(None)
    tablename = StringProperty(None)
    tid = StringProperty(None)
    cid = StringProperty(None)
    col = ListProperty ([1,1,1,1])
    rot = NumericProperty(0)
    current_touch = None


    def on_touch_up(self, touch, after=False):
        if after:
            # print("Fired after the event has been dispatched!")
            for widget in self.parent.walk():
                if widget.id == "CHAIR":
                    # print("{} -> {}".format(widget, widget.id))
                    widget.col = [1,1,1,1]
            callback_chair_released(self.cid,self.tid,self.guestname,self.pos, self.rot)
            self.col = [1,0,0,1]
            if AdminMode:
                if touch.button == 'right' :
                    self.rot = (self.rot + 15) % 360 # TODO : filter event touch : prevent bubling

        else:
            Clock.schedule_once(lambda dt: self.on_touch_up(touch, True))
            return super(ChairELT, self).on_touch_up(touch)



        


class Picture(Scatter):
    source = StringProperty(None)


class SaveButton(Button):
    def save_chairs(self):
        callback_saveCSV()

class ListButton(Button):
    guestname = StringProperty(None)
    tablename = StringProperty(None)
    tid = StringProperty(None)
    cid = StringProperty(None)
    def on_press(self):
        callback_changeSC(self.cid,self.tid)
        for widget in self.parent.parent.parent.walk():
            if widget.id == "CHAIR":
                if widget.cid == self.cid:
                    widget.col = [1,0,0,1]
                else:
                    widget.col = [1,1,1,1]
            if widget.id == "SelectedGuest":
                widget.text = self.guestname




# FUNCTION ======================================================================
def callback_pos(instance, value):
    print('The widget', instance, 'moved to', int(value))




def callback_chair_released(*args):
    global Chaises
    c = str(args[0])
    t = str(args[1])
    n = str(args[2])
    x = int(args[3][0])
    y = int(args[3][1])
    r = int(args[4])
    print("chair ", c ," table ",t ," (",n,") released at [",str(x),",",str(y),"] rot=",str(r))
    for cha in Chaises:
        if cha["TID"] == t and cha["CID"] == c:
            cha["X"] = str(x)
            cha["Y"] = str(y)
            cha["ROT"] = str(r)


def callback_press(*args):
    print("i'm being pressed")

def callback_changeSC(*args):
    global SelectedChair
    SelectedChair = str(args[0])
    global SelectedTable
    SelectedTable = str(args[1])
    print("changing SC :", SelectedChair)
    print("changing ST :", SelectedTable)



def CSVRow(row):
    return {'ACTIVE':row['ACTIVE'],
                    'TID':row['TID'],
                    'CID':row['CID'],                
                    'NOM':row['NOM'],
                    'TYPE':row['TYPE'],
                    'INFO':row['INFO'],
                    'TABLE':row['TABLE'],
                    'L':row['L'],
                    'H':row['H'],
                    'X':row['X'],
                    'Y':row['Y'],
                    'Z':row['Z'],
                    'A':row['A'],
                    'TEX':row['TEX'],
                    'ROT':row['ROT']}




def callback_saveCSV(*args):
    global Tables
    global Chaises
    dt = datetime.now().strftime('%Y%m%d_%H%M%S')
    ext = pathlib.PurePosixPath(CSV_invites).suffix
    basename = os.path.basename(CSV_invites).split('.')[0]
    backupfile = basename + "_" + dt + ext
    copyfile(CSV_invites,backupfile)
    print(CSV_invites, ' archived in ', backupfile)
    tables = []
    chaises = []
    tables = sorted(Tables, key=itemgetter('TID'), reverse=False)
    chaises = sorted(Chaises, key=itemgetter('CID'), reverse=False)
    furniture = tables + chaises
    keys = furniture[0].keys()
    fhdl = open(CSV_invites, "w", newline="", encoding='utf8')
    with fhdl as output_csv_file:
        dict_writer = csv.DictWriter(output_csv_file, delimiter=";", fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(furniture)
    fhdl.close()


def loadCSV():
    sys.stdout.write("loading guests CSV : %s \n" % CSV_invites)
    fh = open(CSV_invites, encoding='utf8')
    global Tables
    global Chaises
    with fh as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row["ACTIVE"] == "1":
                if row["TYPE"] == "table" or row["TYPE"] == "tableronde":
                    Tables.append(CSVRow(row))
                if row["TYPE"] == "chaise":
                    Chaises.append(CSVRow(row))
    fh.close()
    Chaises = sorted(Chaises, key=itemgetter('NOM'), reverse=False)
    Tables = sorted(Tables, key=itemgetter('TID'), reverse=False)
    for tab in Tables:
        sys.stdout.write("table : %s \n" % tab["TABLE"])
    for cha in Chaises:
        sys.stdout.write("chaise : %s \n" % cha["NOM"])

# MAIN ===========================================================================

# load CSV
loadCSV()

# start UI
mariage = Mariage()
mariage.run()
