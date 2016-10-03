import sublime
import sublime_plugin

class FileOpenerCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view=self.view.window().new_file()
        view.set_scratch(True)
        view.settings().set("fileOpener", True)

class FileOpenerListener(sublime_plugin.ViewEventListener):
    @classmethod
    def is_applicable(self,settings):
        return settings.get("fileOpener", False)

    def __init__(self, input):
        sublime_plugin.ViewEventListener.__init__(self, input)
        self.lastSelection=sublime.Region(0, 0)

    def on_modified(self):
        view = self.view
        # remove some bugs on updating
        if view.settings().get("fileOpenerRedrawing", False):
            view.settings().set("fileOpenerRedrawing", False)
            view.settings().set("fileOpenerRedrawing2", True)
            return
        r = self.view.line(0)
        s = self.view.substr(r)
        sel = view.sel()
        if not(len(sel) > 1 or sel[0].b>r.b):
            self.lastSelection = sel[0]
        view.settings().set("fileOpenerRedrawing", True)
        view.run_command("opening_files_redraw", {"text": s})
        sel.clear()
        sel.add(self.lastSelection)
        self.view.show(self.lastSelection)
        pass

    def on_selection_modified(self):
        view = self.view
        # remove some bugs on updating
        if view.settings().get("fileOpenerRedrawing2", False):
            view.settings().set("fileOpenerRedrawing2", False)
            return
        sel = view.sel()
        r = view.line(0)
        if len(sel) > 1 or sel[0].b>r.b:
            sel.clear()
            sel.add(self.lastSelection)
            view.show(self.lastSelection)
        else:
            self.lastSelection = sel[0]

class fileOpenerRedrawCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        view = self.view
        if view.settings().get("fileOpener", False):
            view.replace(edit, sublime.Region(0, view.size()), text)