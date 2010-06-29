import PyQt4
from PyQt4 import QtCore, QtGui, QtSvg

app = QtGui.QApplication([])

i = QtGui.QSystemTrayIcon()

m = QtGui.QMenu()
def quitCB():
	QtGui.QApplication.quit()
def aboutToShowCB():
	print 'about to show'
m.addAction('Quit', quitCB)
QtCore.QObject.connect(m, QtCore.SIGNAL('aboutToShow()'), aboutToShowCB)
i.setContextMenu(m)

svg = QtSvg.QSvgRenderer('icon.svg')
if not svg.isValid():
	raise RuntimeError('bad SVG')
pm = QtGui.QPixmap(16, 16)
painter = QtGui.QPainter(pm)
svg.render(painter)
icon = QtGui.QIcon(pm)
i.setIcon(icon)
i.show()

app.exec_()

del painter, pm, svg
del i, icon
del app

