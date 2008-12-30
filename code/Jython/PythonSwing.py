# Jython/PythonSwing.py
# The HTMLButton.java example from "Thinking in Java"
# converted into Jython.
from javax.swing import JFrame, JButton, JLabel
from java.awt import FlowLayout

frame = JFrame("HTMLButton", visible=1,
  defaultCloseOperation=JFrame.EXIT_ON_CLOSE)

def kapow(e):
    frame.contentPane.add(JLabel("<html>"+
      "<i><font size=+4>Kapow!"))
    # Force a re-layout to
    # include the new label:
    frame.validate()

button = JButton("<html><b><font size=+2>" +
  "<center>Hello!<br><i>Press me now!",
  actionPerformed=kapow)
frame.contentPane.layout = FlowLayout()
frame.contentPane.add(button)
frame.pack()
frame.size=200, 500