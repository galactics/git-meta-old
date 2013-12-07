#!/usr/bin/env python
#-*-coding: utf8 -*-

""" User Interface for Git-Meta using Python curses library
"""

import sys
import curses
import inspector
import logger

class Ui(object):
    """User Interface for git-meta"""
    def __init__(self, lines, status, **kwarg):
        # pylint: disable=C0103
        ## Set parameters
        self.debug = False if not 'debug' in kwarg.keys() else kwarg['debug']

        self.nb_row_head = 5 # Size of header
        self.nb_row_statusline = 1 # Size of footer
        if self.debug:
            self.shift = 3 # shift used for line number
        else:
            self.shift = 0
        self.top_line_to_show = 0 # set first line to be shown in lines

        ## Display configuration
        self.SELECT = " x "
        self.UNSELECT = "   "
        self.select_width = 3
        self.status_width = 6
        self.FILL = " " if not "fill" in kwarg.keys() else kwarg['fill']

        ## Internal variables
        self._UP = -1
        self._DOWN = 1
        self.highlight_line_nb = self.nb_row_head
        self.selected_lines = []
        self.current_line = 0

        ## Get screen and init curses
        self.screen = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)
        self.screen.border(0)
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

        ## Get list of lines as a list of string
        self.lines = lines
        self.status = status

        ## Run
        self.run()

    def run(self):
        """ Run Ui: show display, and catch key press
        """
        while True:
            ## Display info
            if self.debug:
                curses.wrapper(self.display)
            else:
                self.display()
            ## Bind key
            key = self.screen.getch()
            if key == curses.KEY_UP:
                self.updown(self._UP)
            elif key == curses.KEY_DOWN:
                self.updown(self._DOWN)
            elif key == ord(' '):
                self.toogle_select_line()
            elif key == ord('i'):
                self.inspect()
            elif key == ord("q"):
                self.exit()

    def inspect(self):
        """ Run inspector for each repo"""
        log = logger.Log()
        #self.restore_screen()
        #import pdb; pdb.set_trace()
        for line in self.selected_lines:
            inspector.Inspector(self.lines[line], log=log)

    def center_string(self, text, width):
        """ Center text by filling space with white space
        """
        # pylint: disable=R0201
        ## Verify that width > len(text)
        size = len(text)
        if width <= size:
            return text
        
        ## Fill it
        white_space_before = (width - size) / 2
        text = " " * white_space_before + text + " " * white_space_before

        ## Division give a not integer number add one at the end
        if width - len(text) == 1:
            text += " "

        ## Return
        return text

    def print_header(self, height, width):
        """ Print header on screen
        """
        ## Title
        title = "You are running User Interface for Git-Meta"
        self.screen.addstr(0, 0, self.center_string(title, width), 
                           curses.A_STANDOUT|curses.A_BOLD)

        ## Header
        self.screen.addstr(self.nb_row_head-1, 0, " " * width,
                           curses.A_STANDOUT|curses.A_BOLD)

    def print_footer(self, height, width):
        """ Print footer on screen
        """
        ## Get number of OK and NO status
        nb_status_ok = len([ s for s in self.status if s == "OK" ])
        nb_status_no = len([ s for s in self.status if s == "NO" ])
        ## Statusline
        statusline = "Git repo(s): %s, selected: %s, NO: %s, OK: %s" % (
                        len(self.lines), len(self.selected_lines),
                        nb_status_no, nb_status_ok)
        self.screen.addstr(height-1, 0,
                           self.center_string(statusline, width-1), 
                           curses.A_STANDOUT|curses.A_BOLD)


    def nb_lines(self, height):
        """ Show line number
        """
        for index in range(height):
            self.screen.addstr(index, 0, str(index+1) + "")

    def get_lines_index(self, index):
        """Convert index from screen to lines number"""
        return index + self.top_line_to_show - self.nb_row_head

    def toogle_select_line(self):
        """ Mark current line as selected
        """
        if self.get_lines_index(self.highlight_line_nb) in self.selected_lines:
            self.selected_lines.remove(
                self.get_lines_index(self.highlight_line_nb))
        else:
            self.selected_lines.append(
                self.get_lines_index(self.highlight_line_nb))
        self.selected_lines = sorted(self.selected_lines)

    def display(self, *args):
        """ Show information with curses
        """
        # pylint: disable=W0613
        ## Clear screen
        self.screen.erase()

        ## Get screen size
        height, width = self.screen.getmaxyx()
        line_width = width - self.shift - self.status_width - self.select_width

        ## Print header
        self.print_header(height, width)
        
        ## Use panel for display middle
        loop = True
        index = self.nb_row_head
        nb_line = self.top_line_to_show
        while loop:
            if index < height-self.nb_row_statusline:
                ## Get line
                line = self.lines[nb_line]
                line = line.ljust(line_width, self.FILL)

                ## Get status
                status = '[ ' + self.status[nb_line] + ' ]'
                if status == '[ OK ]':
                    color = curses.color_pair(1)
                else:
                    color = curses.color_pair(2)
                status = status.center(self.status_width, ' ')

                ## Select
                if self.get_lines_index(index) in self.selected_lines:
                    line = self.SELECT + line
                    color += curses.A_REVERSE
                else:
                    line = self.UNSELECT + line

                ## highlight
                if index == self.highlight_line_nb:
                    self.screen.addstr(index, self.shift, line, curses.A_BOLD)
                    self.screen.addstr(index, self.shift + line_width,
                                       status, color + curses.A_BOLD)
                else:
                    self.screen.addstr(index, self.shift, line)
                    self.screen.addstr(index, self.shift + line_width,
                                       status, color)
                index += 1
                nb_line += 1
            else:
                loop = False

        ## Show number of lines
        if self.debug:
            self.nb_lines(height)

        ## Footer
        self.print_footer(height, width)

        ## Refresh
        self.screen.refresh()

    def updown(self, increment):
        """ Move up or down depending on increment and position on screen
        """
        ## Get height and width
        height, width = self.screen.getmaxyx() # pylint: disable=W0612

        ## Get next step
        next_line_nb = self.highlight_line_nb + increment

        ## Go UP
        if increment == self._UP:
            if self.highlight_line_nb == self.nb_row_head:
                ## Current highlighted line is the first one
                #  Or you scroll down or you stay here
                ##
                if self.top_line_to_show > 0:
                    # scroll down
                    self.top_line_to_show += self._UP
                else:
                    return
            else:
                ## Go UP
                self.highlight_line_nb = next_line_nb

        ## Go DOWN
        if increment == self._DOWN:
            if self.highlight_line_nb == height - 1 - self.nb_row_statusline:
                ## Curent line is the last one
                # Or you scroll up or you stay here
                ##
                if self.top_line_to_show +\
                   (height - self.nb_row_head - self.nb_row_statusline)\
                    < len(self.lines):
                    # scroll up
                    self.top_line_to_show += self._DOWN
                else:
                    return
            else:
                ## Go DOWN
                self.highlight_line_nb = next_line_nb


    def restore_screen(self):
        """ Restore screen as before
        """
        # pylint: disable=R0201
        curses.initscr()
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    
    def __del__(self):
        """ Catch any weird termination situations and restore screen
        """
        self.restore_screen()

    def exit(self):
        """ Quit User Interface"""
        # pylint: disable=R0201
        sys.exit(1)

if __name__ == "__main__":
    LINES = ['BaAcJy3b', 'Ve6oiMbSLfqmm0jsdVE35qjgPQ5sBgodCvI7', 'dEsIVNU2', 'eP4auN7I9jKvFouQIlBThDlkicENl8QPt0h5QUf', 'ZIROlLG7cAQQ1pdNYKHFIoNs', 'guKTfp2LGosuMaTgOZCtcL7RQZoU3W', 'V1QM', 'xUhF0BEjQ4IsUUVKk0kwKb4', '6xgYORyjneUli0VHUKUNba8MjjPAq5DdvPc7369H', 'B7wBGtgt', 'tDq8xDLbDvqPYS3fwrNLbCBZh3yiItm', 'xBC2qhV', 'bgY1YvARImTdx08gQhivjhpQpkj8B', 'hfU27q3jvqeUsai7HBmSpDzPnFffDMvFOCvll', '2OcNGgB8', 'ZDJaRDacj2VJT9xBCaBJ9Na2O', 'X0V', 'xLNN2fnsIhnW6FsxqDeOBpJWDhB7Vsm1rNhENvP', '3wbKtOPSbNxzrxvTuoH5RiqtOfxSHtqJIrxQ', 'iA52SIY4k', 'aEwn99DngjvmhwMI45qdAG3rOQzCT', 'UBvhxeDrZOqwrQ3xNcQnFmRZHwdSdpVZnihJB4', '16yEB2c4LDrnbZF6RdyY3e0FNsDvc4x2NGWpw2', 'zv0tmdmkY5Gn', 'G2Up8Cd1nNhcEnRIC4tIicXzFhJ5GD3D6o7i6Hl', 'zDBM', 'I0zhx4RUDtRiyOxuJYvGRRYA4UxFLkMGR1s', 'dzSXh7n3qQndsCRzvHjMD6pIS', '1Kpg', 'BYcbUKpitx80', 'D14st', 'QlQQmLE4aHqVKYL2APjDrGCW1onLm5TEB2', 'wFMmn', '8fcRZhOgHcaTKQJmddVNUb07mwBl', 'imTo9NhQWFCAnOw8Q2i', 'rcyE', 'TRsngOkhZeoIkUVSVNQH0IfPGLPXwOwo9Ykqi', '6DRJhndNxNCCTr6myDXEYAqNkS', 'jhoNm9Y8bYBv2ahyJb09Fm8MAS6ylVpx3eOyap', 'BSz9gtfEKuwNaJGvKbg', '5pPp3RS', 'o3KPEwXfixQbu4NHkoCkUR18gxZmN8qe', 'UIOHJO8ximVbh4Wro2bnSEDEkilHOFNSzS', 'jzccNvLHwhobYvU55twKClFt', 'gVfQzkTgHCsMkLEbpupUXVrCkjBo', 'XLiMkdv4h0zP6FDjgdM', 'I3AfSpUHzuu0eUbHXcSo', 'lz2NUeQWq7ogumTo8OOySToIQr3fpwWyS5GPzir', 'k5TQPl4pLJKFw6N', 'TOCjjClYSjANFGz69uLoW0mt7pJRX8G', 'xcU', 'Jqp', 'T61KKshSq', 'cBCjVTqF3NOJgeXjZb9tSzPakeOJRoYwfbB', 'cAgiktPeAXpTAZ5', 'n582kYl9keMyJZ', 'FLQjXRSXulEvf3u2hz28WLddRZUcv8HUmiR', 'G303fSTJTJyazH6plrEkWT82bGKKleJl0We4Q', 'iM4Q21QmnaPdTL8yrpPNlUIDaR40Ej', 'eKPacJ6CereCIk', 'sVB3aXIzI8m3kbpQcUJao9MTSdmA9k2H', 'tO73NUdJJ3T3dBaWpt', 'BFIIDQRT2yYrV8jpyNqSmo9c1Uk5Qf647dTtur', 'SvyhUh9kGX', 'pbSX8qZkHmZfCcO9o0lEoKdhFe', 'WJEEtf1kIl0FCciNktPftiLTb', 'MVQrJh0Ilq8JjJ7ssbVA7dMV', 'jW6sW1n1spfU4XI4iMwGYE116BqmDjstm9izQ', '9ewEA2S4NtE3I260lAVCQt98UD', '2r7WaPdIdVBaC4Q1ETn', 'VDzC1', 'KbxlzJ70O4FRytsU', 'FKB8CrDksKnUEzswgnItginJ0Og1rdn8', 'JclFu', 'PLQqCpnsPKPTxmd4FzXkyQ', 'sjjeZESqzTqZmpzp', '244NAenB8V4QIkNjmulBz3MF7MNxRoS8oI', 'ZfA1NZ3bKUkZa3UMrxANLusZNPvlXtLQtmlBfq', 'caxki7wXE4BDIhCEWXoNS', '1N69bVxKSZ1a1UReo08fayz7kdCwNJfkypk8UGf', 'SbdKxUOt8V7hD1tmUornUXB1R0', 'dpGdOMq', 'Rg7RV60thLAnMGPTasIph2kcFub9oRFbAvFmAaU', 'eUqbeMUKyAMfLYT3AjOIGoJ', 'bsorsLAb', 'ZgW7BNjzkg1JjkJOx6e1xhIpUiQ19d8hKNneXtnR', 'wxszERqpwC1n05bIbVPwV9k3vmbP1gC', 'NHNOITH1STXltLhvguNNOlGRmdmIyZu7C', 'u0E4MOlUaYKoHXnnqwQRhmKBC2sDpQrW0ObANVdQ', 'w6eW', '9OdqwUegAM2hEMsRCKMscl', 'RikHBLCqM9UkArKGiFFCv5s942ZB', 'Zhxuesz6Q6q5wlaFHklL1nri', 'YNSeFqRAlD', 'Tcfpaobm3JsfRHsfIc7bzEu9k9O8X', 'HgsUk7DpO4a0wPDM655Si', 'Fp8urlcrlg8TMWx4vS7l', 'wJlEf', 'Dfr1uVU1fKkDy7rQqUl4S', '9RUS2UkXT5DNFM'] # pylint: disable=C0301
    import random
    STATUS = []
    for _ in LINES:
        if random.uniform(0, 1) >= 0.5:
            STATUS.append("OK")
        else:
            STATUS.append("NO")
    ui = Ui(LINES, STATUS) # pylint: disable=C0103
    #ui = Ui(LINES, STATUS, debug=True)
