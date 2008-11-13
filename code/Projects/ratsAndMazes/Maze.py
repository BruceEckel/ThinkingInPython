# Projects/ratsAndMazes/Maze.py

class Maze(Canvas):
    lines = [] # a line is a char array
    width = -1
    height = -1
    main(self):
        if (args.length < 1):
            print("Enter filename")
            System.exit(0)

        Maze m = Maze()
        m.load(args[0])
        Frame f = Frame()
        f.setSize(m.width*20, m.height*20)
        f.add(m)
        Rat r = Rat(m, 0, 0)
        f.setVisible(1)

    def __init__(self):
        lines = Vector()
        setBackground(Color.lightGray)

    def isEmptyXY(x, y):
        if (x < 0) x += width
        if (y < 0) y += height
        # Use mod arithmetic to bring rat in line:
        byte[] by =
            (byte[])(lines.elementAt(y%height))
        return by[x%width]==' '

    def setXY(x, y, byte newByte):
        if (x < 0) x += width
        if (y < 0) y += height
        byte[] by =
            (byte[])(lines.elementAt(y%height))
        by[x%width] = newByte
        repaint()

    def  load(String filename):
        String currentLine = null
        BufferedReader br = BufferedReader(
          FileReader(filename))
        for(currentLine = br.readLine()
            currentLine != null
            currentLine = br.readLine()) :
            lines.addElement(currentLine.getBytes())
            if(width < 0 ||
               currentLine.getBytes().length > width)
                width = currentLine.getBytes().length

        height = len(lines)
        br.close()

    def update(self, Graphics g): paint(g)
    def paint(Graphics g):
        canvasHeight = self.getBounds().height
        canvasWidth  = self.getBounds().width
        if (height < 1 || width < 1)
            return # nothing to do
        width =
            ((byte[])(lines.elementAt(0))).length
        for (int y = 0 y < len(lines) y++):
            byte[] b
            b = (byte[])(lines.elementAt(y))
            for (int x = 0 x < width x++):
                switch(b[x]):
                    case ' ': # empty part of maze
                        g.setColor(Color.lightGray)
                        g.fillRect(
                          x*(canvasWidth/width),
                          y*(canvasHeight/height),
                          canvasWidth/width,
                          canvasHeight/height)
                        break
                    case '*':     # a wall
                        g.setColor(Color.darkGray)
                        g.fillRect(
                          x*(canvasWidth/width),
                          y*(canvasHeight/height),
                          (canvasWidth/width)-1,
                          (canvasHeight/height)-1)
                        break
                    default:      # must be rat
                        g.setColor(Color.red)
                        g.fillOval(x*(canvasWidth/width),
                        y*(canvasHeight/height),
                        canvasWidth/width,
                        canvasHeight/height)
                        break::


# Projects/ratsAndMazes/Rat.py

class Rat:
    ratCount = 0
    prison = Maze()
    vertDir = 0
    horizDir = 0
    x = 0, y = 0
    myRatNo = 0
    def __init__(self, maze, xStart, yStart):
        myRatNo = ratCount++
        print ("Rat no." + myRatNo + " ready to scurry.")
        prison = maze
        x = xStart
        y = yStart
        prison.setXY(x,y, (byte)'R')

    def run(self): scurry().start()

    def scurry(self):
        # Try and maintain direction if possible.
        # Horizontal backward
        boolean ratCanMove = 1
        while(ratCanMove):
            ratCanMove = 0
            # South
            if (prison.isEmptyXY(x, y + 1)):
                vertDir = 1 horizDir = 0
                ratCanMove = 1

            # North
            if (prison.isEmptyXY(x, y - 1))
                if (ratCanMove)
                    Rat(prison, x, y-1)
                    # Rat can move already, so give
                    # this choice to the next rat.
                else:
                    vertDir = -1 horizDir = 0
                    ratCanMove = 1

            # West
            if (prison.isEmptyXY(x-1, y))
                if (ratCanMove)
                    Rat(prison, x-1, y)
                    # Rat can move already, so give
                    # this choice to the next rat.
                else:
                    vertDir = 0 horizDir = -1
                    ratCanMove = 1

            # East
            if (prison.isEmptyXY(x+1, y))
                if (ratCanMove)
                    Rat(prison, x+1, y)
                    # Rat can move already, so give
                    # this choice to the next rat.
                else:
                    vertDir = 0 horizDir = 1
                    ratCanMove = 1

            if (ratCanMove): # Move original rat.
                x += horizDir
                y += vertDir
                prison.setXY(x,y,(byte)'R')
                # If not then the rat will die.
            Thread.sleep(2000)

        print ("Rat no." + myRatNo +
          " can't move..dying..aarrgggh.")