#!/usr/bin/env python
#-*-coding: utf8 -*-

""" User Interface for Git-Meta using Python curses library
"""

import curses

class Ui(object):
    def __init__(self, lines, *arg, **kwarg):
        ## Set parameters
        self.nb_row_head = 5
        self.nb_row_statusline = 1

        ## Get screen and init curses
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)
        self.screen.border(0)
        
        ## Get list of lines as a list of string
        self.lines = lines

    def run(self, debug=False):
        """ Run Ui: show display, and catch key press
        """
        while True:
            ## Display info
            if debug:
                curses.wrapper(self.display)
            else:
                self.display()
            ## Get user command
            c = self.screen.getch()
            #if c == curses.KEY_UP:
                #self.updown(self.UP)
            #elif c == curses.KEY_DOWN:
                #self.updown(self.DOWN)
            #elif c == self.SPACE_KEY:
                #self.markLine()
            if c == ord("q"):
                self.exit()

    def print_header(self, height, width):
        """ Print header on screen
        """
        title = "You are running User Interface for Git-Meta"
        y_pos_center = width-len(title)
        self.screen.addstr(0, 0, title)

    def display(self):
        """ Show information with curses
        """
        ## Clear screen
        self.screen.erase()

        ## Get screen size
        height, width = self.screen.getmaxyx()

        ## Print header
        self.print_header(height, width)
        
        ## Use panel for display middle

        loop = True
        index = 0
        #while loop:
            #if index <= 

        self.screen.refresh()


    def restoreScreen(self):
        """ Restore screen as before
        """
        curses.initscr()
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    
    def __del__(self):
        """ Catch any weird termination situations and restore screen
        """
        self.restoreScreen()

if __name__ == "__main__":
    lines = ['BaAcJy3b\n', 'Ve6oiMbSLfqmm0jsdVE35qjgPQ5sBgodCvI7\n', 'dEsIVNU2\n', 'eP4auN7I9jKvFouQIlBThDlkicENl8QPt0h5QUf\n', 'ZIROlLG7cAQQ1pdNYKHFIoNs\n', 'guKTfp2LGosuMaTgOZCtcL7RQZoU3W\n', 'V1QM\n', 'xUhF0BEjQ4IsUUVKk0kwKb4\n', '6xgYORyjneUli0VHUKUNba8MjjPAq5DdvPc7369H\n', 'B7wBGtgt\n', 'tDq8xDLbDvqPYS3fwrNLbCBZh3yiItm\n', 'xBC2qhV\n', 'bgY1YvARImTdx08gQhivjhpQpkj8B\n', 'hfU27q3jvqeUsai7HBmSpDzPnFffDMvFOCvll\n', '2OcNGgB8\n', 'ZDJaRDacj2VJT9xBCaBJ9Na2O\n', 'X0V\n', 'xLNN2fnsIhnW6FsxqDeOBpJWDhB7Vsm1rNhENvP\n', '3wbKtOPSbNxzrxvTuoH5RiqtOfxSHtqJIrxQ\n', 'iA52SIY4k\n', 'aEwn99DngjvmhwMI45qdAG3rOQzCT\n', 'UBvhxeDrZOqwrQ3xNcQnFmRZHwdSdpVZnihJB4\n', '16yEB2c4LDrnbZF6RdyY3e0FNsDvc4x2NGWpw2\n', 'zv0tmdmkY5Gn\n', 'G2Up8Cd1nNhcEnRIC4tIicXzFhJ5GD3D6o7i6Hl\n', 'zDBM\n', 'I0zhx4RUDtRiyOxuJYvGRRYA4UxFLkMGR1s\n', 'dzSXh7n3qQndsCRzvHjMD6pIS\n', '1Kpg\n', 'BYcbUKpitx80\n', 'D14st\n', 'QlQQmLE4aHqVKYL2APjDrGCW1onLm5TEB2\n', 'wFMmn\n', '8fcRZhOgHcaTKQJmddVNUb07mwBl\n', 'imTo9NhQWFCAnOw8Q2i\n', 'rcyE\n', 'TRsngOkhZeoIkUVSVNQH0IfPGLPXwOwo9Ykqi\n', '6DRJhndNxNCCTr6myDXEYAqNkS\n', 'jhoNm9Y8bYBv2ahyJb09Fm8MAS6ylVpx3eOyap\n', 'BSz9gtfEKuwNaJGvKbg\n', '5pPp3RS\n', 'o3KPEwXfixQbu4NHkoCkUR18gxZmN8qe\n', 'UIOHJO8ximVbh4Wro2bnSEDEkilHOFNSzS\n', 'jzccNvLHwhobYvU55twKClFt\n', 'gVfQzkTgHCsMkLEbpupUXVrCkjBo\n', 'XLiMkdv4h0zP6FDjgdM\n', 'I3AfSpUHzuu0eUbHXcSo\n', 'lz2NUeQWq7ogumTo8OOySToIQr3fpwWyS5GPzir\n', 'k5TQPl4pLJKFw6N\n', 'TOCjjClYSjANFGz69uLoW0mt7pJRX8G\n', 'xcU\n', 'Jqp\n', 'T61KKshSq\n', 'cBCjVTqF3NOJgeXjZb9tSzPakeOJRoYwfbB\n', 'cAgiktPeAXpTAZ5\n', 'n582kYl9keMyJZ\n', 'FLQjXRSXulEvf3u2hz28WLddRZUcv8HUmiR\n', 'G303fSTJTJyazH6plrEkWT82bGKKleJl0We4Q\n', 'iM4Q21QmnaPdTL8yrpPNlUIDaR40Ej\n', 'eKPacJ6CereCIk\n', 'sVB3aXIzI8m3kbpQcUJao9MTSdmA9k2H\n', 'tO73NUdJJ3T3dBaWpt\n', 'BFIIDQRT2yYrV8jpyNqSmo9c1Uk5Qf647dTtur\n', 'SvyhUh9kGX\n', 'pbSX8qZkHmZfCcO9o0lEoKdhFe\n', 'WJEEtf1kIl0FCciNktPftiLTb\n', 'MVQrJh0Ilq8JjJ7ssbVA7dMV\n', 'jW6sW1n1spfU4XI4iMwGYE116BqmDjstm9izQ\n', '9ewEA2S4NtE3I260lAVCQt98UD\n', '2r7WaPdIdVBaC4Q1ETn\n', 'VDzC1\n', 'KbxlzJ70O4FRytsU\n', 'FKB8CrDksKnUEzswgnItginJ0Og1rdn8\n', 'JclFu\n', 'PLQqCpnsPKPTxmd4FzXkyQ\n', 'sjjeZESqzTqZmpzp\n', '244NAenB8V4QIkNjmulBz3MF7MNxRoS8oI\n', 'ZfA1NZ3bKUkZa3UMrxANLusZNPvlXtLQtmlBfq\n', 'caxki7wXE4BDIhCEWXoNS\n', '1N69bVxKSZ1a1UReo08fayz7kdCwNJfkypk8UGf\n', 'SbdKxUOt8V7hD1tmUornUXB1R0\n', 'dpGdOMq\n', 'Rg7RV60thLAnMGPTasIph2kcFub9oRFbAvFmAaU\n', 'eUqbeMUKyAMfLYT3AjOIGoJ\n', 'bsorsLAb\n', 'ZgW7BNjzkg1JjkJOx6e1xhIpUiQ19d8hKNneXtnR\n', 'wxszERqpwC1n05bIbVPwV9k3vmbP1gC\n', 'NHNOITH1STXltLhvguNNOlGRmdmIyZu7C\n', 'u0E4MOlUaYKoHXnnqwQRhmKBC2sDpQrW0ObANVdQ\n', 'w6eW\n', '9OdqwUegAM2hEMsRCKMscl\n', 'RikHBLCqM9UkArKGiFFCv5s942ZB\n', 'Zhxuesz6Q6q5wlaFHklL1nri\n', 'YNSeFqRAlD\n', 'Tcfpaobm3JsfRHsfIc7bzEu9k9O8X\n', 'HgsUk7DpO4a0wPDM655Si\n', 'Fp8urlcrlg8TMWx4vS7l\n', 'wJlEf\n', 'Dfr1uVU1fKkDy7rQqUl4S\n', '9RUS2UkXT5DNFM\n']
    ui = Ui(lines)
