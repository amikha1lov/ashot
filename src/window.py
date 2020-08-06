# window.py
#
# Copyright 2020 Alexey Mikhailov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from subprocess import Popen, PIPE
import time
from gi.repository import Gtk, Gdk, Gio, GdkPixbuf, GLib, Pango
from subprocess import Popen, PIPE
import time
import cairo

class MouseButton:
    LEFT_BUTTON = 1
    MIDDLE_BUTTON = 2
    RIGHT_BUTTON = 3

@Gtk.Template(resource_path='/com/github/amikha1lov/ashot/window.ui')
class AshotWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'AshotWindow'

    surface = None
    isDrawing = False
    drawType = "Drawing"
    brushSizeValue = 0
    currentWidth = 0
    currentHeight = 0
    image = None
    i = 0
    elements = []
    brushColorValue =[0.0, 0.0, 0.0, 1.0]
    abCoords =[ [0.0, 0.0], [0.0, 0.0] ]
    linePoints = []
    fileName = ""

    main_box = Gtk.Template.Child()
    bottom_box = Gtk.Template.Child()
    color_button = Gtk.Template.Child()
    brushSizeProp = Gtk.Template.Child()
    drawArea = Gtk.Template.Child()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.brushSizeValue = self.brushSizeProp.get_value()
        self.drawArea.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawArea.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.drawArea.add_events(Gdk.EventMask.BUTTON_MOTION_MASK)
        window = Gdk.get_default_root_window()
        coordinate = Popen("slop -n -c 0.3,0.4,0.6,0.4 -l -t 0 -f '%w %h %x %y'",shell=True,stdout=PIPE).communicate()
        listCoor = list(coordinate)
        listCoor = listCoor[0].decode().split()
        width,height,x,y=int(listCoor[0]),int(listCoor[1]),int(listCoor[2]),int(listCoor[3])
        pb = Gdk.pixbuf_get_from_window(window, x, y, width,height)
        pathImg = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)
        self.fileName =(pathImg + "/GShot") + time.strftime("%Y-%m-%d-%H:%M:%S.png", time.localtime())
        print(self.fileName)
        if pb:
            pb.savev(self.fileName,"png", (), ())
            print("Screenshot saved to screenshot.png.")
        else:
            print("Unable to get the screenshot.")

        self.image = GdkPixbuf.Pixbuf.new_from_file(self.fileName)

        self.set_default_size(self.image.get_width(), self.image.get_height())

    @Gtk.Template.Callback()
    def setDrawState(self,widget):
        self.drawType = widget.get_label()

    @Gtk.Template.Callback()
    def onBrushSizeChange(self,widget):
        self.brushSizeValue = self.brushSizeProp.get_value()

    @Gtk.Template.Callback()
    def onColorSet(self,widget):
        rgba = widget.get_rgba()
        self.brushColorValue = [rgba.red, rgba.green, rgba.blue, rgba.alpha]

    @Gtk.Template.Callback()
    def onButtonPress(self,widget,event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == MouseButton.LEFT_BUTTON:
            self.isDrawing = True
            self.abCoords[0] = [event.x, event.y]
            self.linePoints.append([event.x, event.y])
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == MouseButton.LEFT_BUTTON:
            self.abCoords[1] = [event.x, event.y]

    @Gtk.Template.Callback()
    def onButtonRelease(self,widget,event):
        self.isDrawing = False
        self.abCoords[1] = [event.x, event.y]
        del self.linePoints[:]

    @Gtk.Template.Callback()
    def onDraw(self,area,context):
        if self.surface:
            context.set_source_surface(self.surface, 0.0, 0.0)
            context.paint()
        else:
            print("No surface")

        return False



    @Gtk.Template.Callback()
    def onConfigure(self,area,event, data = None):
        areaWidth = area.get_allocated_width()
        areaHeight = area.get_allocated_height()
        print(self.image)
        print(type(self.image))
        _surface = cairo.ImageSurface.create_from_png(self.fileName)

        if self.surface:
            surfaceWidth = self.surface.get_width()
            surfaceHeight = self.surface.get_height()

            if areaWidth < surfaceWidth or areaHeight < surfaceHeight:
                return False

            context = cairo.Context(_surface)

            context.rectangle(0,0,areaWidth,areaHeight)
            context.set_source_rgba(1,1,1,1.0)
            context.fill()

            context.set_source_surface(self.surface, 0.0, 0.0)
            context.scale(areaWidth,areaHeight)
            context.paint()
            self.currentWidth = areaWidth
            self.currentHeight = areaHeight
        else:
            self.drawArea.set_size_request(self.currentWidth, self.currentHeight)

        self.surface = _surface
        self.context = cairo.Context(_surface)
        return False


    @Gtk.Template.Callback()
    def onMotion(self,area,event):
        if self.isDrawing:
            self.abCoords[1] = [event.x, event.y]

            p1 = self.abCoords[0]
            p2 = self.abCoords[1]

            x1 = p1[0]
            y1 = p1[1]
            x2 = p2[0]
            y2 = p2[1]
            w = x2 - x1
            h = y2 - y1
            if "Drawing" in self.drawType:
                self.linePoints.append([event.x, event.y])
                self.drawFree()
            if "Square" in self.drawType:
                self.drawSquare([x1,y1,w,h])
            if "Line" in self.drawType:
                self.linePoints.append([event.x, event.y])
                self.drawLine()
            self.drawArea.queue_draw()




    def drawFree(self):
        rgba = self.brushColorValue
        self.context.set_source_rgba(rgba[0],rgba[1],rgba[2],rgba[3])
        self.context.set_line_width(self.brushSizeValue)
        self.context.set_line_cap(1)

        for i in self.linePoints:
            for j in self.linePoints:
                self.context.move_to(i[0], i[1])
                self.context.line_to(j[0], j[1])
                self.context.stroke()

        del self.linePoints[len(self.linePoints) - 2: -1]


    def drawLine(self):
        prgba = self.brushColorValue
        self.context.set_source_rgba(rgba[0],rgba[1],rgba[2],rgba[3])
        self.context.set_line_width(self.brushSizeValue)
        self.context.set_line_cap(1)

        for i in self.linePoints:
            for j in self.linePoints:
                self.context.move_to(i[0], i[1])
                self.context.line_to(j[0], j[1])
                self.context.stroke()

        del self.linePoints[len(self.linePoints) - 2: -1]

    def drawSquare(self,coords):



        rgba = self.brushColorValue
        self.context.set_source_rgba(rgba[0],rgba[1],rgba[2],rgba[3])
        self.context.rectangle(coords[0],coords[1],coords[2],coords[3])

        self.context.fill()


        self.drawArea.queue_draw()


    @Gtk.Template.Callback()
    def onSave(self, button):
        dialog = Gtk.FileChooserDialog("Please choose a folder",self,Gtk.FileChooserAction.SAVE,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK),)
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Select clicked")
            print("Folder selected: " + dialog.get_filename())
            self.pathAndFileName = dialog.get_filename() + ".png"
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()


        print(self.pathAndFileName)
        self.drawing_area_write(self.pathAndFileName)



    def drawing_area_write(self,path):
        # drawingarea1 is a Gtk.DrawingArea
        window = self.drawArea.get_window()

        # Some code to get the coordinates for the image, which is centered in the
        # in the drawing area. You can ignore it for the purpose of this example


        # Fetch what we rendered on the drawing area into a pixbuf
        pixbuf = Gdk.pixbuf_get_from_window(window, 0, 0,
                                          self.image.get_width(), self.image.get_height()-46)

        # Write the pixbuf as a PNG image to disk
        pixbuf.savev(path, 'png', [], [])


 
