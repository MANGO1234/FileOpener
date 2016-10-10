from os.path import split, isdir, isfile, exists
from os import stat

import sublime
import sublime_plugin

from .fuzzy import fuzzy_filter
from .paths import directory_files


class FileOpenerCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view.window().new_file()
        view.set_scratch(True)
        view.settings().set("fileOpener", True)
        view.settings().set("word_wrap", False)
        # vintageous
        view.run_command("_enter_insert_mode", {
                         'count': 1, 'mode': 'mode_internal_normal'})
        view.settings().set("__vi_external_disable", True)


def updateView(view, error=""):
    r = view.line(0)
    s = view.substr(r)
    sel = view.sel()
    if not (len(sel) > 1 or sel[0].b > r.b):
        view.lastSelection = sel[0]
    view.settings().set("fileOpenerRedrawing", True)
    view.run_command("file_opener_redraw", {"path": s, "error": error})
    sel.clear()
    sel.add(view.lastSelection)
    view.show(view.lastSelection)


class FileOpenerListener(sublime_plugin.ViewEventListener):

    @classmethod
    def is_applicable(cls, settings):
        return settings.get("fileOpener", False)

    def __init__(self, view):
        sublime_plugin.ViewEventListener.__init__(self, view)
        view.lastSelection = sublime.Region(0, 0)

    def on_modified(self):
        view = self.view
        # prevent repeating update that breaks it 
        if view.settings().get("fileOpenerRedrawing", False):
            view.settings().set("fileOpenerRedrawing", False)
            view.settings().set("fileOpenerRedrawing2", True)
            return
        updateView(view)

    def on_selection_modified(self):
        view = self.view
        # prevent repeating update that breaks it 
        if view.settings().get("fileOpenerRedrawing2", False):
            view.settings().set("fileOpenerRedrawing2", False)
            return
        sel = view.sel()
        r = view.line(0)
        if len(sel) > 1 or sel[0].b > r.b:
            sel.clear()
            sel.add(view.lastSelection)
            view.show(view.lastSelection)
        else:
            view.lastSelection = sel[0]

    # turn off autocompletion
    def on_query_completions(self, prefix, locations):
        view = self.view
        view.run_command("hide_auto_complete", {})
        return None


class FileOpenerCommandListener(sublime_plugin.EventListener):

    def on_text_command(self, view, command_name, args):
        if view.settings().get("fileOpener", False):
            print(command_name, args)
            return None


class FileOpenerRedrawCommand(sublime_plugin.TextCommand):

    def run(self, edit, path, error=""):
        view = self.view
        if view.settings().get("fileOpener", False):
            print(error)
            print(error =="")
            if error == "":
                view.replace(edit, sublime.Region(
                    0, view.size()), self.getOutput(path))
            else:
                view.replace(edit, sublime.Region(
                    0, view.size()), path + '\n' + error)

    def getOutput(self, path):
        (base, end) = split(path)
        fs = directory_files(base)
        fs = [f[1] for f in fs]
        fs = fuzzy_filter(end, fs)
        return path + '\n' + '\n'.join(map(lambda f: f, fs))


class FileOpenerAutocompleteCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view
        sel = view.sel()
        r = view.line(0)
        if sel[0].b == r.b:
            path = view.substr(r)
            (base, end) = split(path)
            fs = directory_files(base)
            fs = [f[1] for f in fs]
            fs = fuzzy_filter(end, fs)
            view.replace(edit, sublime.Region(r.b - len(end), r.b), fs[0])


class FileOpenerOpenCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view
        activeWindow = sublime.active_window()
        r = view.line(0)
        path = view.substr(r)
        if not exists(path):
            updateView(view, "Unknown file/directory")
        elif isdir(path):
            activeWindow.run_command("close_file")
            project = activeWindow.project_data()
            project["folders"].append({"path": path})
            activeWindow.set_project_data(project)
        elif isfile(path):
            activeWindow.run_command("close_file")
            v = activeWindow.open_file(path)
            activeWindow.focus_view(v)
        else:
            print("what kind of file is this...")
