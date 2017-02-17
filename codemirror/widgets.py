# -*- coding: utf-8 -*-
#
# Created:    2010/09/09
# Author:         alisue
#
from itertools import chain
import re

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

from codemirror import utils


# set default settings
CODEMIRROR_PATH = getattr(settings, 'CODEMIRROR_PATH', 'codemirror')
if CODEMIRROR_PATH.endswith('/'):
    CODEMIRROR_PATH = CODEMIRROR_PATH[:-1]
CODEMIRROR_MODE = getattr(settings, 'CODEMIRROR_MODE', 'javascript')
CODEMIRROR_THEME = getattr(settings, 'CODEMIRROR_THEME', 'default')
CODEMIRROR_CONFIG = getattr(settings, 'CODEMIRROR_CONFIG', {'lineNumbers': True})
CODEMIRROR_ADDON_JS = getattr(settings, 'CODEMIRROR_ADDON_JS', '')
CODEMIRROR_ADDON_CSS = getattr(settings, 'CODEMIRROR_ADDON_CSS', '')
CODEMIRROR_JS_VAR_FORMAT = getattr(settings, 'CODEMIRROR_JS_VAR_FORMAT', None)

THEME_CSS_FILENAME_RE = re.compile(r'[\w-]+')


class CodeMirrorTextarea(forms.Textarea):
    u"""Textarea widget render with `CodeMirror`

    CodeMirror:
        http://codemirror.net/
    """

    @property
    def media(self):
        mode_name = self.mode_name
        js = ["%s/lib/codemirror.js" % CODEMIRROR_PATH]

        if not self.custom_mode:
            js.append("%s/mode/%s/%s.js" % (CODEMIRROR_PATH, mode_name, mode_name))

        js.extend(
            "%s/mode/%s/%s.js" % (CODEMIRROR_PATH, dependency, dependency)
            for dependency in self.dependencies)
        js.extend("%s/addon/%s.js" % (CODEMIRROR_PATH, addon) for addon in self.addon_js)

        if self.keymap:
            js.append("%s/keymap/%s.js" % (CODEMIRROR_PATH, self.keymap))

        if self.custom_js:
            js.extend(self.custom_js)

        css = ["%s/lib/codemirror.css" % CODEMIRROR_PATH]
        css.extend(
            "%s/theme/%s.css" % (CODEMIRROR_PATH, theme_css_filename)
            for theme_css_filename in self.theme_css)
        css.extend(
            "%s/addon/%s.css" % (CODEMIRROR_PATH, css_file)
            for css_file in self.addon_css)

        if self.custom_css:
            css.extend(self.custom_css)

        return forms.Media(
            css={
                'all': css
            },
            js=js
        )

    def __init__(
            self, attrs=None, mode=None, theme=None, config=None, dependencies=(),
            js_var_format=None, addon_js=(), addon_css=(), custom_mode=None, custom_js=(),
            keymap=None, custom_css=None, **kwargs):
        u"""Constructor of CodeMirrorTextarea

        Attribute:
            path          - CodeMirror directory URI (DEFAULT = settings.CODEMIRROR_PATH)
            mode          - Name of language or a modal configuration object as described in CodeMirror docs.
                            Used to autoload an appropriate language plugin js file according to filename conventions.
                            (DEFAULT = settings.CODEMIRROR_MODE)
            theme         - Name of theme. Also autoloads theme plugin css according to filename conventions.
                            (DEFAULT = settings.CODEMIRROR_THEME)
            config        - The rest of the options passed into CodeMirror as a python map.
                            (updated from settings.CODEMIRROR_CONFIG)
            dependencies  - Some modes depend on others, you can pass extra modes dependencies with this argument.
                            For example for mode="htmlmixed", you must pass dependencies=("xml", "javascript", "css").
            js_var_format - A format string interpolated with the form field name to name a global JS variable that will
                            hold the CodeMirror editor object. For example with js_var_format="%s_editor" and a field
                            named "code", the JS variable name would be "code_editor". If None is passed, no global
                            variable is created (DEFAULT = settings.CODEMIRROR_JS_VAR_FORMAT)
            addon_js      - Various addons are available for CodeMirror. You can pass the names of any addons to load
                            with this argument. For example, for mode="django", you must pass addon_js=("mode/overlay", ).
            addon_css     - Some addons require corresponding CSS files. Since not every addon requires a CSS file, and
                            the names of these files do not always follow a convention, they must be listed separately.
                            For example, addon_css=("display/fullscreen", ).
            custom_mode   - To use a custom mode (i.e. one not included in the standard CodeMirror distribution), set this to
                            the name, or configuration object, of the mode, and ensure "mode" is None. For example,
                            custom_mode="my_custom_mode".
            custom_js     - To include other Javascript files with this widget that are not defined in the CodeMirror package,
                            set this to a list of pathnames. If "custom_mode" is defined, this will probably contain the path
                            of the file defining that mode. Paths in this list will not be prepended with settings.CODEMIRROR_PATH.
                            For example, custom_js=("site_js/my_custom_mode.js", )
            keymap        - The name of a keymap to use. Keymaps are located in settings.CODEMIRROR_PATH/keymap. Default: None.
            custom_css    - To include other CSS files with this widget that are not defined in the CodeMirror package,
                            set this to a list of pathnames. Paths in this list will not be prepended with any path.
                            For example, custom_css=("site_css/my_styles.css", )

        Example:
            *-------------------------------*
            + static
              + codemirror
                + lib
                  - codemirror.js
                  - codemirror.css
                + mode
                  + python
                    - python.js
                + theme
                  + cobalt.css
                + addon
                  + display
                    - fullscreen.js
                    - fullscreen.css
              + site_js
                - my_custom_mode.js
            *-------------------------------*
            CODEMIRROR_PATH = "codemirror"

            codemirror = CodeMirrorTextarea(mode="python", theme="cobalt", config={ 'fixedGutter': True })
            document = forms.TextField(widget=codemirror)
        """
        super(CodeMirrorTextarea, self).__init__(attrs=attrs, **kwargs)

        mode = mode or custom_mode or CODEMIRROR_MODE
        if utils.isstring(mode):
            mode = { 'name': mode }
        self.mode_name = mode['name']
        self.custom_mode = custom_mode
        self.dependencies = dependencies
        self.addon_js = addon_js or CODEMIRROR_ADDON_JS
        self.addon_css = addon_css or CODEMIRROR_ADDON_CSS
        self.custom_js = custom_js
        self.custom_css = custom_css
        self.keymap = keymap
        self.js_var_format = js_var_format or CODEMIRROR_JS_VAR_FORMAT

        theme = theme or CODEMIRROR_THEME
        theme_css_filename = THEME_CSS_FILENAME_RE.search(theme).group(0)
        if theme_css_filename == 'default':
            self.theme_css = []
        else:
            self.theme_css = [theme_css_filename]

        config = config or {}
        self.option_json = utils.CodeMirrorJSONEncoder().encode(dict(chain(
            CODEMIRROR_CONFIG.items(),
            config.items(),
            [('mode', 'spell-checker'), ('backdrop', self.mode_name), ('theme', theme)])))

    def render(self, name, value, attrs=None):
        u"""Render CodeMirrorTextarea"""
        if self.js_var_format is not None:
            js_var_bit = 'var %s = ' % (self.js_var_format % name)
        else:
            js_var_bit = ''
        output = [super(CodeMirrorTextarea, self).render(name, value, attrs),

                  '<script type="text/javascript">\n'
                  'CodeMirrorSpellChecker({\n'
                  ' codeMirrorInstance: CodeMirror,\n'
                  '});\n'
                  'var textArea = document.getElementById(%s);\n'
                  'if (textArea == null) {\n'
                  ' var thisScript = $("script").last();\n'
                  ' var thisForm = $(thisScript).closest("form");\n'
                  ' textArea = $(thisForm).find("textarea")[0];\n'
                  '}\n'

                  'var settings = %s;\n'
                  '/* Key Bidings */\n'
                  'settings.extraKeys = {\n'
                  ' "Enter": "newlineAndIndentContinueMarkdownList",\n'
                  ' "Cmd-B": function(cm) {\n'
                  '   var selection = cm.getSelection();\n'
                  '   cm.replaceSelection("**" + selection + "**");\n'
                  '   if (!selection) {\n'
                  '     var cursorPos = cm.getCursor();\n'
                  '     cm.setCursor(cursorPos.line, cursorPos.ch - 2);\n'
                  '   }\n'
                  ' },\n'
                  ' "Ctrl-B": function(cm) {\n'
                  '   var selection = cm.getSelection();\n'
                  '   cm.replaceSelection("**" + selection + "**");\n'
                  '   cm.replaceSelection("**" + selection + "**");\n'
                  '   if (!selection) {\n'
                  '     var cursorPos = cm.getCursor();\n'
                  '     cm.setCursor(cursorPos.line, cursorPos.ch - 2);\n'
                  '   }\n'
                  ' },\n'
                  ' "Cmd-I": function(cm) {\n'
                  '   var selection = cm.getSelection();\n'
                  '   cm.replaceSelection("_" + selection + "_");\n'
                  '   if (!selection) {\n'
                  '     var cursorPos = cm.getCursor();\n'
                  '     cm.setCursor(cursorPos.line, cursorPos.ch - 2);\n'
                  '   }\n'
                  ' },\n'
                  ' "Ctrl-I": function(cm) {\n'
                  '   var selection = cm.getSelection();\n'
                  '   cm.replaceSelection("_" + selection + "_");\n'
                  '   if (!selection) {\n'
                  '     var cursorPos = cm.getCursor();\n'
                  '     cm.setCursor(cursorPos.line, cursorPos.ch - 2);\n'
                  '   }\n'
                  ' },\n'
                  '},\n'

                  '/* Custom Buttons */\n'
                  'settings.buttons = [\n'
                  '{\n'
                  ' class: "tip",\n'
                  ' label: \'<i class="fa fa-lightbulb-o" aria-hidden="true"></i>\',\n'
                  ' callback: function (cm) {\n'
                  '   if (typeof tipid == "undefined"){\n'
                  '     tipid = 0;\n'
                  '   } else {\n'
                  '     tipid++;\n'
                  '   }\n'
                  '   var selection = cm.getSelection();\n'
                  '   if (!selection) selection = "Teaching tip content here";\n'
                  '     cm.replaceSelection("\\ntip!!!tip-" + tipid + "<!-- place where you\'d like the icon -->" +\n'
                  '           "\\n\\n!!!tip <tip-" + tipid + ">\\n\\n    " + selection + "\\n");\n'
                  '     if (!selection) {\n'
                  '       var cursorPos = cm.getCursor();\n'
                  '       cm.setCursor(cursorPos.line, cursorPos.ch - 1);\n'
                  '     }\n'
                  '   }\n'
                  ' },\n'
                  '{\n'
                  ' class: "discussion",\n'
                  ' label: \'<i class="fa fa-comments" aria-hidden="true"></i>\',\n'
                  ' callback: function (cm) {\n'
                  '   if (typeof discussionid == "undefined"){\n'
                  '     discussionid = 0;\n'
                  '   } else {\n'
                  '     discussionid++;\n'
                  '   }\n'
                  '   var selection = cm.getSelection();\n'
                  '   if (!selection) selection = "Discussion goal content here";\n'
                  '     cm.replaceSelection("\\ndiscussion!!!discussion-" + discussionid + "<!-- place where you\'d like the icon -->" +\n'
                  '           "\\n\\n!!!discussion <discussion-" + discussionid + ">\\n\\n    " + selection + "\\n");\n'
                  '     if (!selection) {\n'
                  '       var cursorPos = cm.getCursor();\n'
                  '       cm.setCursor(cursorPos.line, cursorPos.ch - 1);\n'
                  '     }\n'
                  '   }\n'
                  ' },\n'
                  '{\n'
                  ' class: "content",\n'
                  ' label: \'<i class="fa fa-mortar-board" aria-hidden="true"></i>\',\n'
                  ' callback: function (cm) {\n'
                  '   if (typeof contentid == "undefined"){\n'
                  '     contentid = 0;\n'
                  '   } else {\n'
                  '     contentid++;\n'
                  '   }\n'
                  '   var selection = cm.getSelection();\n'
                  '   if (!selection) selection = "Content corner content here";\n'
                  '     cm.replaceSelection("\\ncontent!!!content-" + contentid + "<!-- place where you\'d like the icon -->" +\n'
                  '           "\\n\\n!!!content <content-" + contentid + ">\\n\\n    " + selection + "\\n");\n'
                  '     if (!selection) {\n'
                  '       var cursorPos = cm.getCursor();\n'
                  '       cm.setCursor(cursorPos.line, cursorPos.ch - 1);\n'
                  '     }\n'
                  '   }\n'
                  ' },\n'
                  '{\n'
                  ' class: "remark",\n'
                  ' label: \'<i class="fa fa-microphone" aria-hidden="true"></i>\',\n'
                  ' callback: function (cm) {\n'
                  '   var selection = cm.getSelection();\n'
                  '   if (!selection) selection = "Say content here";\n'
                  '     cm.replaceSelection("\\n!!!say\\n\\n    " + selection + "\\n");\n'
                  '     if (!selection) {\n'
                  '       var cursorPos = cm.getCursor();\n'
                  '       cm.setCursor(cursorPos.line, cursorPos.ch - 1);\n'
                  '     }\n'
                  '   }\n'
                  ' },\n'
                  '{\n'
                  ' class: "studio",\n'
                  ' label: \'<i class="fa fa-desktop" aria-hidden="true"></i>\',\n'
                  ' callback: function (cm) {\n'
                  '   var selection = cm.getSelection();\n'
                  '   cm.replaceSelection("&fa-desktop;" + selection);\n'
                  '   }\n'
                  ' },\n'
                  '{\n'
                  ' class: "css",\n'
                  ' label: \'<i class="fa fa-css3" aria-hidden="true"></i>\',\n'
                  ' callback: function (cm) {\n'
                  '   var selection = cm.getSelection();\n'
                  '   cm.replaceSelection(selection + \'{: style="float:right"}\');\n'
                  '   }\n'
                  ' },\n'
                  ' {\n'
                  '   class: "a",\n'
                  '   label: "a",\n'
                  '   callback: function (cm) {\n'
                  '     var selection = cm.getSelection();\n'
                  '     var text = "";\n'
                  '     var link = "";\n'

                  '     if (selection.match(/^https?:\/\//)) {\n'
                  '       link = selection;\n'
                  '     } else {\n'
                  '       text = selection;\n'
                  '     }\n'
                  '     cm.replaceSelection("[" + text + "](" + link + ")");\n'

                  '     var cursorPos = cm.getCursor();\n'
                  '     if (!selection) {\n'
                  '       cm.setCursor(cursorPos.line, cursorPos.ch - 3);\n'
                  '     } else if (link) {\n'
                  '       cm.setCursor(cursorPos.line, cursorPos.ch - (3 + link.length));\n'
                  '     } else {\n'
                  '       cm.setCursor(cursorPos.line, cursorPos.ch - 1);\n'
                  '     }\n'
                  '   }\n'
                  ' },\n'
                  ' {\n'
                  '   class: "img",\n'
                  '   label: "img",\n'
                  '   callback: function (cm) {\n'
                  '     var selection = cm.getSelection();\n'
                  '     var text = "";\n'
                  '     var link = "";\n'

                  '     if (selection.match(/^https?:\/\//)) {\n'
                  '       link = selection;\n'
                  '     } else {\n'
                  '       text = selection;\n'
                  '     }\n'
                  '     cm.replaceSelection("![" + text + "](" + link + "){: style=\'\'}");\n'

                  '     var cursorPos = cm.getCursor();\n'
                  '     if (!selection) {\n'
                  '       cm.setCursor(cursorPos.line, cursorPos.ch - 15);\n'
                  '     } else if (link) {\n'
                  '       cm.setCursor(cursorPos.line, cursorPos.ch - (15 + link.length));\n'
                  '     } else {\n'
                  '       cm.setCursor(cursorPos.line, cursorPos.ch - 13);\n'
                  '     }\n'
                  '   }\n'
                  ' },\n'
                  ' {\n'
                  '   class: "tbl",\n'
                  '   label: \'<i class="fa fa-table" aria-hidden="true"></i>\',\n'
                  '   callback: function (cm) {\n'
                  '     cm.replaceSelection("\\n| First Header  | Second Header |\\n" +\n'
                  '                            "| ------------- | ------------- |\\n" +\n'
                  '                            "| Content Cell  | Content Cell  |\\n" +\n'
                  '                            "| Content Cell  | Content Cell  |\\n");\n'
                  '   }\n'
                  ' }\n'
                  ']\n'
                  'var editor = %sCodeMirror.fromTextArea(textArea, settings);\n'
                  'inlineAttachment.editors.codemirror4.attach(editor, { \n'
                  '  uploadUrl: "/upload/",\n'
                  '  uploadFieldName: "file",\n'
                  '  remoteFilename: function(file) { return file.name.toString().replace(/\s+/g, "-") },\n'
                  '  urlText: "![]({filename})",\n'
                  '  extraHeaders: {\n'
                  '    "X-CSRF-Token": window.__csrf_token\n'
                  '  }\n'
                  '});\n'
                  # 'inlineAttach.attachToCodeMirror(editor, {\n'
                  # '  uploadUrl: "/upload/",\n'
                  # '  uploadFieldName: "file",\n'
                  # '  downloadFieldName: "newAssetUrl",\n'
                  # '  allowedTypes: [ "image/jpeg", "image/png", "image/jpg", "image/gif" ],\n'
                  # '  progressText: "![Uploading file...]()",\n'
                  # '  urlText: "![]({filename})", // `{filename}` tag gets replaced with URL\n'
                  # '  errorText: "Error uploading file",\n'
                  # '  extraHeaders: {\n'
                  # '    "X-CSRF-Token": $(\'meta[name="csrf-token"]\').attr("content")\n'
                  # '  }\n'
                  # '});\n'
                  '</script>' %
                  ('"id_%s"' % name, self.option_json, js_var_bit)]
        return mark_safe('\n'.join(output))
