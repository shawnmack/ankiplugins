# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Show statistics about the current and previous card while reviewing.
# Activate from the tools menu.
#

from anki.hooks import addHook
from aqt import mw
from aqt.qt import *
from aqt.webview import AnkiWebView
import aqt.stats

class CardStats(object):
    def __init__(self, mw):
        self.mw = mw
        self.shown = False
        addHook("showQuestion", self._update)
        addHook("deckClosing", self.hide)
        addHook("reviewCleanup", self.hide)

    def _addDockable(self, title, w):
        class DockableWithClose(QDockWidget):
            def closeEvent(self, evt):
                self.emit(SIGNAL("closed"))
                QDockWidget.closeEvent(self, evt)
        dock = DockableWithClose(title, mw)
        dock.setObjectName(title)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetClosable)
        dock.setWidget(w)
        if mw.width() < 600:
            mw.resize(QSize(600, mw.height()))
        mw.addDockWidget(Qt.RightDockWidgetArea, dock)
        return dock

    def _remDockable(self, dock):
        mw.removeDockWidget(dock)

    def show(self):
        if not self.shown:
            class ThinAnkiWebView(AnkiWebView):
                def sizeHint(self):
                    return QSize(200, 100)
            self.web = ThinAnkiWebView()
            self.shown = self._addDockable(_("Card Info"), self.web)
            self.shown.connect(self.shown, SIGNAL("closed"),
                               self._onClosed)
        self._update()

    def hide(self):
        if self.shown:
            self._remDockable(self.shown)
            self.shown = None
            #actionself.mw.form.actionCstats.setChecked(False)

    def toggle(self):
        if self.shown:
            self.hide()
        else:
            self.show()

    def _onClosed(self):
        # schedule removal for after evt has finished
        self.mw.progress.timer(100, self.hide, False)

    def _update(self):
        if not self.shown:
            return
        txt = ""
        r = self.mw.reviewer
        d = self.mw.col
        if r.card:
            txt += _("<h3>Current</h3>")
            txt += d.cardStats(r.card)
        lc = r.lastCard()
        if lc:
            txt += _("<h3>Last</h3>")
            txt += d.cardStats(lc)
        if not txt:
            txt = _("No current card or last card.")
        self.web.setHtml("""
<html><head>
</head><body><center>%s</center></body></html>"""% txt)

_cs = CardStats(mw)

def cardStats(on):
    _cs.toggle()

action = QAction(mw)
action.setText("Card Stats")
action.setCheckable(True)
action.setShortcut(QKeySequence("Shift+C"))
mw.form.menuTools.addAction(action)
mw.connect(action, SIGNAL("toggled(bool)"), cardStats)
