#!/usr/bin/python
# coding: utf-8

from xdg.DesktopEntry import DesktopEntry
from lxml import etree as XML
import glob

apps = []                                                       #List of .desktop object representations
subCats = []                                                    #List of only subcategories
topNCats = []                                                   #List of top level numeric categories
topCats = []                                                    #List of top level nonnumeric categories
uniqueCats = []                                                 #List of only unique desktop categories
relatedCats = []                                                #List of related desktop categories
elemList = []                                                   #List of XML Elements for use as parent objects when SubElementing
topLevelsWithSubLevels = {}                                     #Key-Value pair for storing top level directories (string keys) and their related sublevels (values as list)

for file in glob.glob("/usr/share/applications/*.desktop"):
    de = DesktopEntry(file)                                     #GLOB through each .desktop file in the directory and create a Desktop Entry for each
    apps.append(de)                                             #Append each Desktop entry to apps
    cats = de.getCategories()                                   #Get the categories related to each DE
    if(len(cats) != 0):                                         #If categories field is not empty
        mainCat = cats[0]                                       #Set the main category for the application to its first listed category
        uniqueCats.append(mainCat)                                 #Generate a list of every apps categories

uniqueCats = sorted(set(uniqueCats))                            #Use set to get rid of duplicate categories and sorted to organize/alphabetize them

with open('/root/.config/compiz/boxmenu/menu.xml', "w") as f:
    f.write('<menu></menu>')

tree = XML.parse('/root/.config/compiz/boxmenu/menu.xml')                      #Parse base XML file which should contain <menu></menu>
root = tree.getroot()                                           #Get <menu></menu> as root

for cat in uniqueCats:                                          #For each unique category
    cats = cat.split('-')                                       #Split out the name into a list
    if len(cats) >= 1:
        if cats[0].isdigit() and cats[1].isdigit():             #If toplevel numbered cat and sublevel numbered cat
            subCats.append(cat)                                 #Append to list of sublevel numbered cats
        elif cats[0].isdigit():                                 #Else if only toplevel numbered cat
            topNCats.append(cat)                                #Append to list of toplevel numbered cats
        else:                                                   #Else
            topCats.append(cat)                                 #Is just a plain ole top level category

kattrib = {'name': 'Hacking Tools'}
kalimenu = root.makeelement('menu', kattrib)
root.append(kalimenu)

for cat in topNCats:                                            #For each toplevel numbered category
    relatedCats.clear()                                         #Clear the list of related categories
    splitTopCat = cat.split('-')
    for sCat in subCats:
        splitSubCat = sCat.split('-')
        if(splitTopCat[0] == splitSubCat[0]):
            relatedCats.append(sCat)
    topLevelsWithSubLevels[cat] = relatedCats
    tAttrib = {'name' : cat}
    elem = XML.SubElement(kalimenu, 'menu', tAttrib)
    elemList.append(elem)
    for rCat in topLevelsWithSubLevels[cat]:
        attrib = {'name': rCat}
        babyElem = XML.SubElement(elem, 'menu', attrib)
        elemList.append(babyElem)

for cat in topCats:
    attrib = {'name': cat}
    elem = root.makeelement('menu', attrib)
    elemList.append(elem)
    root.append(elem)

for app in apps:
    attrib = {'type': 'launcher'}
    attrib2 = { 'name': app.getName(), 'exec': app.getExec()}
    if len(app.getCategories()) > 0:
        for elem in elemList:
            if elem.get('name') == app.getCategories()[0]:
                item = XML.SubElement(elem, 'item', attrib)
                theName = XML.SubElement(item, 'name')
                theName.text = app.getName()
                if app.getIcon().startswith("/") or app.getIcon().startswith("kali"):
                    iconAttrib = {'mode1': 'file'}
                    if app.getIcon().startswith("kali"):
                        theIcon = XML.SubElement(item, 'icon', iconAttrib)
                        theIcon.text = "/usr/share/icons/hicolor/16x16/apps/" + app.getIcon()
                    else:
                        theIcon = XML.SubElement(item, 'icon', iconAttrib)
                        theIcon.text = app.getIcon()
                else:
                    theIcon = XML.SubElement(item, 'icon')
                    theIcon.text = app.getIcon()
                theCmd = XML.SubElement(item, 'command')
                properCmd = app.getExec().split('%')
                if properCmd[0].startswith('sh '):
                    properCmd[0] = 'urxvt -e ' + properCmd[0]
                theCmd.text = properCmd[0]

attrib = {'type': 'windowlist'}
attrib2 = {'type': 'viewportlist'}
attrib3 = {'type': 'reload'}
elem1 = root.makeelement('item', attrib)
elem2 = root.makeelement('item', attrib2)
elem3 = root.makeelement('item', attrib3)
root.append(elem1)
root.append(elem2)
root.append(elem3)

tree.write('/root/.config/compiz/boxmenu/menu.xml', pretty_print=True)