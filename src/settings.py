# Copyright (c) 2014-2016 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gio, Gtk, GLib

from gettext import gettext as _

from eolie.define import El
from eolie.utils import get_current_monitor_model


class Settings(Gio.Settings):
    """
        Eolie settings
    """

    def __init__(self):
        """
            Init settings
        """
        Gio.Settings.__init__(self)

    def new():
        """
            Return a new Settings object
        """
        settings = Gio.Settings.new("org.gnome.Eolie")
        settings.__class__ = Settings
        return settings


class SettingsDialog:
    """
        Dialog showing eolie options
    """

    def __init__(self):
        """
            Init dialog
        """
        builder = Gtk.Builder()
        builder.add_from_resource("/org/gnome/Eolie/SettingsDialog.ui")

        self.__settings_dialog = builder.get_object("settings_dialog")
        self.__settings_dialog.set_transient_for(El().active_window)
        # self.__settings_dialog.connect("destroy", self.__on_destroy)

        if False:
            self.__settings_dialog.set_title(_("Preferences"))
        else:
            headerbar = builder.get_object("header_bar")
            headerbar.set_title(_("Preferences"))
            self.__settings_dialog.set_titlebar(headerbar)

        download_chooser = builder.get_object("download_chooser")
        dir_uri = El().settings.get_value("download-uri").get_string()
        if not dir_uri:
            directory = GLib.get_user_special_dir(
                                         GLib.UserDirectory.DIRECTORY_DOWNLOAD)
            dir_uri = GLib.filename_to_uri(directory, None)
        download_chooser.set_uri(dir_uri)

        open_downloads = builder.get_object("open_downloads_check")
        open_downloads.set_active(
                                El().settings.get_value("open-downloads"))

        self.__start_page_uri = builder.get_object("start_page_uri")
        combo_start = builder.get_object("combo_start")
        start_page = El().settings.get_value("start-page").get_string()
        if start_page.startswith("http"):
            combo_start.set_active_id("address")
            self.__start_page_uri.set_text(start_page)
            self.__start_page_uri.show()
        else:
            combo_start.set_active_id(start_page)

        combo_engine = builder.get_object("combo_engine")
        combo_engine.set_active_id(
                        El().settings.get_value("search-engine").get_string())

        remember_session = builder.get_object("remember_session_check")
        remember_session.set_active(
                                El().settings.get_value("remember-session"))

        enable_plugins = builder.get_object("plugins_check")
        enable_plugins.set_active(
                                El().settings.get_value("enable-plugins"))

        self.__fonts_grid = builder.get_object("fonts_grid")
        use_system_fonts = builder.get_object("system_fonts_check")
        use_system_fonts.set_active(
                                El().settings.get_value("use-system-fonts"))
        self.__fonts_grid.set_sensitive(
                            not El().settings.get_value("use-system-fonts"))

        sans_serif_button = builder.get_object("sans_serif_button")
        sans_serif_button.set_font_name(
                       El().settings.get_value("font-sans-serif").get_string())
        serif_button = builder.get_object("serif_button")
        serif_button.set_font_name(
                       El().settings.get_value("font-serif").get_string())
        monospace_button = builder.get_object("monospace_button")
        monospace_button.set_font_name(
                       El().settings.get_value("font-monospace").get_string())

        min_font_size_spin = builder.get_object("min_font_size_spin")
        min_font_size_spin.set_value(
                       El().settings.get_value("min-font-size").get_int32())

        monitor_model = get_current_monitor_model()
        zoom_levels = El().settings.get_value("default-zoom-level")
        zoom_level = 1.0
        try:
            for zoom_level in zoom_levels:
                zoom_splited = zoom_level.split('@')
                if zoom_splited[0] == monitor_model:
                    wanted_zoom_level = float(zoom_splited[1])
        except:
            pass
        default_zoom_level = builder.get_object("default_zoom_level")
        default_zoom_level.set_value(float(wanted_zoom_level))

        cookies_combo = builder.get_object("cookies_combo")
        storage = El().settings.get_enum("cookie-storage")
        cookies_combo.set_active_id(str(storage))

        tracking_check = builder.get_object("tracking_check")
        tracking_check.set_active(
                                El().settings.get_value("do-not-track"))
        builder.connect_signals(self)

    def show(self):
        """
            Show dialog
        """
        self.__settings_dialog.show()

#######################
# PROTECTED           #
#######################
    def _on_tracking_toggled(self, button):
        """
            Save state
            @param button as Gtk.ToggleButton
        """
        El().settings.set_value("do-not-track",
                                GLib.Variant("b", button.get_active()))

    def _on_cookies_changed(self, combo):
        """
            Save engine
            @param combo as Gtk.ComboBoxText
        """
        El().settings.set_enum("cookie-storage", int(combo.get_active_id()))
        for window in El().windows:
            for view in window.container.views:
                El().set_cookie_manager(view.get_context())

    def _on_default_zoom_changed(self, button):
        """
            Save size
            @param button as Gtk.SpinButton
        """
        monitor_model = get_current_monitor_model()
        try:
            # Add current value less monitor model
            zoom_levels = []
            for zoom_level in El().settings.get_value("default-zoom-level"):
                zoom_splited = zoom_level.split('@')
                if zoom_splited[0] == monitor_model:
                    continue
                else:
                    zoom_levels.append("%s@%s" % (zoom_splited[0],
                                                  zoom_splited[1]))
            # Add new zoom value for monitor model
            zoom_levels.append("%s@%s" % (monitor_model, button.get_value()))
            El().settings.set_value("default-zoom-level",
                                    GLib.Variant("as", zoom_levels))
            for window in El().windows:
                window.update_zoom_level(True)
        except Exception as e:
            print("SettingsDialog::_on_default_zoom_changed():", e)

    def _on_min_font_size_changed(self, button):
        """
            Save size
            @param button as Gtk.SpinButton
        """
        value = GLib.Variant("i", button.get_value())
        El().settings.set_value("min-font-size", value)
        El().set_setting("minimum-font-size", button.get_value())

    def _on_system_fonts_toggled(self, button):
        """
            Save state
            @param button as Gtk.ToggleButton
        """
        self.__fonts_grid.set_sensitive(not button.get_active())
        El().settings.set_value("use-system-fonts",
                                GLib.Variant("b", button.get_active()))

    def _on_font_sans_serif_set(self, fontbutton):
        """
            Save font setting
            @param fontchooser as Gtk.FontButton
        """
        value = GLib.Variant("s", fontbutton.get_font_name())
        El().settings.set_value("font-sans-serif", value)
        El().set_setting("sans-serif-font-family", fontbutton.get_font_name())

    def _on_font_serif_set(self, fontbutton):
        """
            Save font setting
            @param fontchooser as Gtk.FontButton
        """
        value = GLib.Variant("s", fontbutton.get_font_name())
        El().settings.set_value("font-serif", value)
        El().set_setting("serif-font-family", fontbutton.get_font_name())

    def _on_font_monospace_set(self, fontbutton):
        """
            Save font setting
            @param fontchooser as Gtk.FontButton
        """
        value = GLib.Variant("s", fontbutton.get_font_name())
        El().settings.set_value("font-monospace", value)
        El().set_setting("monospace-font-family", fontbutton.get_font_name())

    def _on_plugins_toggled(self, button):
        """
            Save state
            @param button as Gtk.ToggleButton
        """
        value = GLib.Variant("b", button.get_active())
        El().settings.set_value("enable-plugins", value)
        El().set_setting("enable-plugins", button.get_active())

    def _on_remember_session_toggled(self, button):
        """
            Save state
            @param button as Gtk.ToggleButton
        """
        El().settings.set_value("remember-session",
                                GLib.Variant("b", button.get_active()))

    def _on_start_page_uri_changed(self, entry):
        """
            Save startup page
            @param entry as Gtk.Entry
        """
        El().settings.set_value("start-page",
                                GLib.Variant("s", entry.get_text()))

    def _on_start_changed(self, combo):
        """
            Save startup page
            @param combo as Gtk.ComboBoxText
        """
        if combo.get_active_id() == 'address':
            self.__start_page_uri.show()
        else:
            self.__start_page_uri.hide()
            El().settings.set_value("start-page",
                                    GLib.Variant("s", combo.get_active_id()))

    def _on_engine_changed(self, combo):
        """
            Save engine
            @param combo as Gtk.ComboBoxText
        """
        El().settings.set_value("search-engine",
                                GLib.Variant("s", combo.get_active_id()))
        El().search.update_default_engine()

    def _on_open_downloads_toggled(self, button):
        """
            Save state
            @param button as Gtk.ToggleButton
        """
        El().settings.set_value("open-downloads",
                                GLib.Variant("b", button.get_active()))

    def _on_selection_changed(self, chooser):
        """
            Save uri
            @chooser as Gtk.FileChooserButton
        """
        uri = chooser.get_uri()
        if uri is None:
            uri = ""
        El().settings.set_value("download-uri", GLib.Variant("s", uri))
