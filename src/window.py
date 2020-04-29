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

@Gtk.Template(resource_path='/com/github/amikha1lov/ashot/window.ui')
class AshotWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'AshotWindow'

    fonts = Gtk.Template.Child()
    main_box = Gtk.Template.Child()
    color_button = Gtk.Template.Child()
    bottom_box = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        window = Gdk.get_default_root_window()
        x, y, width, height = window.get_geometry()

        coordinate = Popen("slop -n -c 0.3,0.4,0.6,0.4 -l -t 0 -f '%w %h %x %y'",shell=True,stdout=PIPE).communicate()
        listCoor = list(coordinate)
        listCoor = listCoor[0].decode().split()
        width,height,x,y=int(listCoor[0]),int(listCoor[1]),int(listCoor[2]),int(listCoor[3])
        pb = Gdk.pixbuf_get_from_window(window, x, y, width,height)
        pathImg = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)
        fileName =(pathImg + "/GShot") + time.strftime("%Y-%m-%d-%H:%M:%S.png", time.localtime())
        print(fileName)
        if pb:
            pb.savev(fileName,"png", (), ())
            print("Screenshot saved to screenshot.png.")
        else:
            print("Unable to get the screenshot.")





        print(self.color_button.get_rgba().to_color())
        print(self.color_button.get_rgba().to_string())

        print(self.color_button.get_rgba().red.hex())
        print(self.fonts.get_font_size())

        print(self.fonts.get_font_desc().get_family())










        self.image = GdkPixbuf.Pixbuf.new_from_file(fileName)

        self.set_default_size(self.image.get_width(), self.image.get_height())
        self.drawing_area = Gtk.DrawingArea()

        self.drawing_area.set_size_request(self.image.get_width(), self.image.get_height())
        self.drawing_area.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
        scrolledwindow = Gtk.ScrolledWindow()
        viewport = Gtk.Viewport()
        viewport.add(self.drawing_area)
        scrolledwindow.add(viewport)
        self.main_box.pack_start(scrolledwindow, True, True, 0)
        self.add(self.main_box)
        self.drawing_area.connect("enter-notify-event", self.on_drawing_area_mouse_enter)
        self.drawing_area.connect("leave-notify-event", self.on_drawing_area_mouse_leave)
        self.drawing_area.connect("button-press-event", self.on_drawing_area_mouse_click)
        self.drawing_area.connect("draw", self.on_drawing_area_draw)
        self.drawing_area.connect("motion-notify-event", self.on_drawing_area_mouse_motion)
        pixbuf = self.image
        self.drawing_area.set_size_request(pixbuf.get_width(), pixbuf.get_height())


        self.show_all()


    @Gtk.Template.Callback()
    def on_save(self, button):
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
    @Gtk.Template.Callback()
    def drawing_area_write(self,path):
        # drawingarea1 is a Gtk.DrawingArea
        window = self.drawing_area.get_window()

        # Some code to get the coordinates for the image, which is centered in the
        # in the drawing area. You can ignore it for the purpose of this example


        # Fetch what we rendered on the drawing area into a pixbuf
        pixbuf = Gdk.pixbuf_get_from_window(window, 0, 0,
                                          self.image.get_width(), self.image.get_height()-46)

        # Write the pixbuf as a PNG image to disk
        pixbuf.savev(path, 'png', [], [])



    def on_drawing_area_mouse_enter(self, widget, event):
        print("In - DrawingArea")

    def on_drawing_area_mouse_leave(self, widget, event):
        print("Out - DrawingArea")

    def on_drawing_area_mouse_motion(self, widget, event):

        (x, y) = int(event.x), int(event.y)
        offset = ( (y*self.image.get_rowstride()) +
                   (x*self.image.get_n_channels()) )
        pixel_intensity = self.image.get_pixels()[offset]
        print("(" + str(x) + ", " + str(y) + ") = " + str(pixel_intensity))


        (x, y) = int(event.x), int(event.y)
        print("click")
        print(x)
        print(y)

    @Gtk.Template.Callback()
    def on_drawing_area_mouse_click(self, widget, event):
        (x, y) = int(event.x), int(event.y)
        print("click")
        print(x)
        print(y)


        self.popover = Gtk.Popover()
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.main_box.pack_start(Gtk.ModelButton("Item 1"), False, True, 10)
        self.main_box.pack_start(Gtk.Label("Item 2"), False, True, 10)
        self.popover.add(self.main_box)
        self.popover.set_position(Gtk.PositionType.BOTTOM)

        self.popover.show_all()
        self.popover.popup()

        cairo_context = self.drawing_area.get_window().cairo_create()
        pixbuf = self.image
        self.drawing_area.set_size_request(pixbuf.get_width(), pixbuf.get_height())
        Gdk.cairo_set_source_pixbuf(cairo_context, pixbuf, 0, 0)
        cairo_context.paint()
        cr = cairo_context
        cr.set_font_size(20)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_NORMAL)
        cr.set_source_rgb(255 , 0 , 0)
        cr.move_to(x , y)
        cr.show_text("ТУТ 2 ТУТ ТЕКСТ")
        cr.stroke()
        cr.set_source_surface(pixbuf, 10, 10)
        cr.paint()
        self.drawing_area.queue_draw()

    @Gtk.Template.Callback()
    def on_drawing_area_draw(self, drawable, cairo_context):
        pixbuf = self.image
        self.drawing_area.set_size_request(pixbuf.get_width(), pixbuf.get_height())
        Gdk.cairo_set_source_pixbuf(cairo_context, pixbuf, 0, 0)
        cairo_context.paint()

