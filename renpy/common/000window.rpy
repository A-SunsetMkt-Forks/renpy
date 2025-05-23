﻿# Copyright 2004-2025 Tom Rothamel <pytom@bishoujo.us>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# This file contains the definition and implementation of the window show,
# window hide, and window auto statements.

init -1200 python:

    config.window_show_transition = None
    config.window_hide_transition = None
    config.window = None

    # A list of statements that cause the window to be auto-shown.
    config.window_auto_show = [ "say", "say-nvl", "menu-with-caption", "nvl-menu", "nvl-menu-with-caption" ]

    # A list of statements that cause the window to be auto-hidden.
    config.window_auto_hide = [ "scene", "call screen", "menu", "say-centered", "say-bubble" ]

    # Compat, with a fairly complicated history, this defaulted to True in the past.
    config.window_functions_set_auto = False

    # Compat for window_next.
    config.window_next = True

    _window_auto = False
    _window_next = True

    def _window_show(trans=False, auto=False):
        """
        :doc: window

        The Python equivalent of the ``window show`` statement.

        `trans`
            If False, the default window show transition is used. If None,
            no transition is used. Otherwise, the specified transition is
            used.

        `auto`
            If True, this becomes the equivalent of the ``window auto show``
            statement.
        """

        if config.window_functions_set_auto:
            store._window_auto = auto

        if store._window:
            return

        if trans is False:
            trans = config.window_show_transition

        if _preferences.show_empty_window and (not renpy.game.after_rollback):
            renpy.with_statement(None)
            store._window = True

            renpy.with_statement(trans)
        else:
            store._window = True

        store._after_scene_show_hide = None

        renpy.mode("window_show")

    def _window_hide(trans=False, auto=False):
        """
        :doc: window

        The Python equivalent of the ``window hide`` statement.

        `trans`
            If False, the default window hide transition is used. If None,
            no transition is used. Otherwise, the specified transition is
            used.

        `auto`
            If True, this becomes the equivalent of the ``window auto hide``
            statement.
        """

        if config.window_functions_set_auto:
            store._window_auto = auto

        if not store._window:
            return

        if trans is False:
            trans = config.window_hide_transition

        if _preferences.show_empty_window and (not renpy.game.after_rollback):
            renpy.with_statement(None)
            store._window = False
            renpy.with_statement(trans)
        else:
            store._window = False

        store._after_scene_show_hide = None
        store._window_next = config.window_next

        renpy.mode("window_hide")

    def _window_auto_callback(statement):

        if not store._window_auto:
            return

        if statement == 'menu' and menu == nvl_menu:
            statement = 'menu-nvl'

        if statement in config.window_auto_hide:
            _window_hide(auto=True)

        if statement in config.window_auto_show:
            _window_show(auto=True)

        if statement == "say" or statement.startswith("say-"):
            store._window_next = False

    config.statement_callbacks.append(_window_auto_callback)

    def _init_window():

        global _window
        global _window_auto

        if config.window == "auto":
            _window_auto = True
            _window = False

        elif config.window == "show":
            _window_auto = False
            _window = True

        elif config.window == "hide":
            _window_auto = False
            _window = False


python early hide:
    ##########################################################################
    # "window show" and "window hide" statements.

    def parse_window(l):
        p = l.simple_expression()
        if not l.eol():
            renpy.error('expected end of line')

        return p

    def lint_window(p):
        if p is not None:
            _try_eval(p, 'window transition')

    def execute_window_show(p):
        store._window_auto = False

        if p is not None:
            trans = eval(p)
        else:
            trans = False

        _window_show(trans)

    def execute_window_hide(p):
        store._window_auto = False

        if p is not None:
            trans = eval(p)
        else:
            trans = False

        _window_hide(trans)

    def parse_window_auto(l):

        rv = { }

        if l.keyword('hide'):
            hide = l.simple_expression() or "False"
            rv["hide"] = hide
            rv["auto"] = "True"

        elif l.keyword('show'):
            show = l.simple_expression() or "False"
            rv["show"] = show
            rv["auto"] = "True"

        else:
            rv["auto"] = l.simple_expression() or "True"

        if not l.eol():
            renpy.error('expected end of line')

        return rv

    def execute_window_auto(p):
        store._window_auto = True

        if "hide" in p:
            trans = eval(p["hide"])
            _window_hide(trans, auto=True)

        if "show" in p:
            trans = eval(p["show"])
            _window_show(trans, auto=True)

        if "auto" in p:
            store._window_auto = eval(p["auto"])


    def warp_true(p):
        return True


    renpy.register_statement('window show',
                              parse=parse_window,
                              execute=execute_window_show,
                              lint=lint_window,
                              warp=warp_true)

    renpy.register_statement('window hide',
                              parse=parse_window,
                              execute=execute_window_hide,
                              lint=lint_window,
                              warp=warp_true)

    renpy.register_statement('window auto',
                             parse=parse_window_auto,
                             execute=execute_window_auto,
                             warp=warp_true)


init 1200 python:
    _window_next = config.window_next
