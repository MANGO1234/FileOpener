from os.path import split, isdir, isfile, exists, join
from os import stat

import sublime
import sublime_plugin

from .fuzzy import fuzzy_filter
from .paths import directory_files
from .hist import FileHistory

views = {}


class FileOpenerCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view.window().new_file()
        view.set_scratch(True)
        view.settings().set("fileOpener", True)
        view.settings().set("word_wrap", False)
        views[view.id()] = {
            "pointer": FileHistory.get_entry_pointer()
        }
        # vintageous
        view.run_command("_enter_insert_mode", {
                         'count': 1, 'mode': 'mode_internal_normal'})
        view.settings().set("__vi_external_disable", True)


# class Views():
#     views = []

#     @staticmethod
#     def addAndGetView(view):
#         views[view.id()] = view

#     @staticmethod
#     def removeView(view):
#         del views[view.id()]


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


class FileSystem():
    currentDirectory = []
    fuzzyDirectory = []
    dirBase = ""
    fuzzyFilter = ""

    def updatePath(self, path):
        (base, end) = split(path)
        self.dirBase = base
        self.fuzzyFilter = end
        self.currentDirectory = directory_files(base)
        fs = [f[1] for f in self.currentDirectory]
        self.fuzzyDirectory = fuzzy_filter(end, fs)


fileSystem = FileSystem()

# class FileOpenerCommandListener(sublime_plugin.EventListener):

#     def on_text_command(self, view, command_name, args):
#         if view.settings().get("fileOpener", False):
#             print(command_name, args)
#             return None


class FileOpenerRedrawCommand(sublime_plugin.TextCommand):

    def run(self, edit, path, error=""):
        view = self.view
        if not view.settings().get("fileOpener", False):
            return

        if error == "":
            output = path + '\n' + self.getOutput(path)
        else:
            output = path + '\n' + error
        view.replace(edit, sublime.Region(0, view.size()), output)

    def getOutput(self, path):
        fileSystem.updatePath(path)
        return '\n'.join(map(lambda f: f, fileSystem.fuzzyDirectory))


class FileOpenerAutocompleteCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view
        if not view.settings().get("fileOpener", False):
            return

        sel = view.sel()
        r = view.line(0)
        if sel[0].b == r.b:
            path = view.substr(r)
            fileSystem.updatePath(path)
            fuzzyFile = fileSystem.fuzzyDirectory[0]
            if isdir(join(fileSystem.dirBase, fuzzyFile)):
                fuzzyFile += "/"
            view.replace(edit, sublime.Region(
                r.b - len(fileSystem.fuzzyFilter), r.b), fuzzyFile)


class FileOpenerOpenCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view
        if not view.settings().get("fileOpener", False):
            return

        activeWindow = sublime.active_window()
        path = view.substr(view.line(0))
        if not exists(path):
            updateView(view, "Unknown file/directory")
        elif isdir(path):
            activeWindow.run_command("close_file")
            project = activeWindow.project_data()
            project["folders"].append({"path": path})
            activeWindow.set_project_data(project)
            FileHistory.addEntry(path)
        elif isfile(path):
            activeWindow.run_command("close_file")
            v = activeWindow.open_file(path)
            activeWindow.focus_view(v)
            FileHistory.addEntry(path)
        else:
            print("what kind of file is this...")


class FileOpenerUpCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        pass
