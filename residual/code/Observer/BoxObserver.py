# Observer/BoxObserver.py
# Demonstration of Observer pattern using
# Java's built-in observer classes.

# You must inherit a type of Observable:
class BoxObservable(Observable):
    def notifyObservers(self, Object b):
        # Otherwise it won't propagate changes:
        setChanged()
        super.notifyObservers(b)

class BoxObserver(JFrame):
    Observable notifier = BoxObservable()
    def __init__(self, grid):
        setTitle("Demonstrates Observer pattern")
        Container cp = getContentPane()
        cp.setLayout(GridLayout(grid, grid))
        for(int x = 0 x < grid x++)
            for(int y = 0 y < grid y++)
                cp.add(OCBox(x, y, notifier))

    def main(self, String[] args):
        grid = 8
            if(args.length > 0)
                grid = Integer.parseInt(args[0])
            JFrame f = BoxObserver(grid)
            f.setSize(500, 400)
            f.setVisible(1)
            # JDK 1.3:
            f.setDefaultCloseOperation(EXIT_ON_CLOSE)
            # Add a WindowAdapter if you have JDK 1.2

class OCBox(JPanel) implements Observer:
    Color cColor = newColor()
    colors = [
      Color.black, Color.blue, Color.cyan,
      Color.darkGray, Color.gray, Color.green,
      Color.lightGray, Color.magenta,
      Color.orange, Color.pink, Color.red,
      Color.white, Color.yellow
    ]
    def newColor():
        return colors[
          (int)(Math.random() * colors.length)
        ]

    def __init__(self, x, y, Observable notifier):
        self.x = x
        self.y = y
        notifier.addObserver(self)
        self.notifier = notifier
        addMouseListener(ML())

    def paintComponent(self, Graphics g):
        super.paintComponent(g)
        g.setColor(cColor)
        Dimension s = getSize()
        g.fillRect(0, 0, s.width, s.height)

    class ML(MouseAdapter):
        def mousePressed(self, MouseEvent e):
            notifier.notifyObservers(OCBox.self)

    def update(self, Observable o, Object arg):
        OCBox clicked = (OCBox)arg
        if(nextTo(clicked)):
            cColor = clicked.cColor
            repaint()

    def nextTo(OCBox b):
        return Math.abs(x - b.x) <= 1 &&
            Math.abs(y - b.y) <= 1