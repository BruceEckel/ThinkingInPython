import turtle
turtle.clear

class fractal(object):

     def __init__(self, lstring, rule, line_length, angle, shrink_factor):
         self.lstring = lstring
         self.rule = rule
         self.line_length = line_length
         self.angle = angle
         self.shrink_factor=shrink_factor

     def draw(self):
         drawingdict = {'F': lambda: turtle.forward(self.line_length),
                        '-':lambda: turtle.right(self.angle),
                        '+':lambda: turtle.left(self.angle),}
         for rule in self.lstring:
             drawingdict[rule]()

     def iterate(self):
         self.lstring = self.lstring.replace(rule[0],rule[1])
         self.line_length=self.line_length/self.shrink_factor

def recurse(f,smallest):
     if f.line_length>=smallest:
         turtle.reset()
         f.iterate()
         f.draw()
         recurse(f,smallest)

if __name__=='__main__':
     start = 'F+F+F+F'
     rule = ('F','F+F-F-FF+F+F-F')
     f = fractal(start,rule,50,90,2)
     recurse(f,10)
