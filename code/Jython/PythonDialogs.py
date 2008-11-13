# Jython/PythonDialogs.py
# Dialogs.java from "Thinking in Java, 2nd
# edition," Chapter 13, converted into Jython.
# Don't run this as part of the automatic make:
#=M @echo skipping PythonDialogs.py
from java.awt import FlowLayout
from javax.swing import JFrame, JDialog, JLabel
from javax.swing import JButton

class MyDialog(JDialog):
    def __init__(self, parent=None):
        JDialog.__init__(self,
          title="My dialog", modal=1)
        self.contentPane.layout = FlowLayout()
        self.contentPane.add(JLabel("A dialog!"))
        self.contentPane.add(JButton("OK",
          actionPerformed =
            lambda e, t=self: t.dispose()))
        self.pack()

frame = JFrame("Dialogs", visible=1,
  defaultCloseOperation=JFrame.EXIT_ON_CLOSE)
dlg = MyDialog()
frame.contentPane.add(
  JButton("Press here to get a Dialog Box",
    actionPerformed = lambda e: dlg.show()))
frame.pack()