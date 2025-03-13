def color(code):

    def inner(text, bold=False):
        c = code
        if bold:
            c = "1;{}".format(c)
        return "\033[{new}m{text}\033[{old}m".format(new=c, text=text, old=39)

    return inner


grey = color("0")
black = color("30")
red = color("31")
green = color("32")
yellow = color("33")
blue = color("34")
magenta = purple = color("35")
cyan = color("36")
white = color("37")
default = color("39")
