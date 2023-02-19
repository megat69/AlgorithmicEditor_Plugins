# GrAPiC plugin
Allows you to use functions from Alexandre Meyer's GrAPiC library.

## Available bindings :
- "winit" : `winInit(str name, int width, int height)`
- "wclear" : `winClear()`
- "wdisplay" : `winDisplay()`
- "wquit" : `winQuit()`
- "color" : `color(unsigned char r, unsigned char g, unsigned char b)`
- "bcolor" : `backgroundColor(unsigned char r, unsigned char g, unsigned char b)`
- "pspace" : `pressSpace()`
- "circle" : `circle(int xc, int yc, int radius)`
- "circlef" : `circleFill(int xc, int yc, int radius)`
- "line" : `line(int x1, int y1, int x2, int y2)`
- "rect" : `rectangle(int x1, int y1, int x2, int y2)`
- "rectf" : `rectangleFill(int x1, int y1, int x2, int y2)`
- "ppixel" : `putPixel(int x, int y, unsigned char r, unsigned char g, unsigned char b, unsigned char a=255)`
- "delay" : `delay(int duration)`
- "img" : `image(str filename)`
  - Note : Having this function called in the form `img <filename> -> <var_name>` will store the image in the given variable.

