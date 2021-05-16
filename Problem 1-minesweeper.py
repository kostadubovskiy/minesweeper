from tkinter import *
from tkinter import messagebox
import random


class MsCell(Label):
    """
    self.number —> int, num of adjacent bombs
        or a Boolean 'Tr ue' if the object is a bomb
    self.color —> str
    self.coord -> tuple (x,y)
    
    parent: the parent minesweeper grid object
    """

    def __init__(self, coord, number, parent):
        # set up cell label
        self.text = str(number)
        
        # set up cell
        Label.__init__(self, width=2, height=1, text='', bg='white', font=('Times New Roman', 24), relief=RAISED)
        self.grid(row=coord[0], column=coord[1])
        self.coord = coord
        self.isExposed = False
        colormap = ['', 'blue', 'darkgreen', 'red', 'purple', 'maroon', 'cyan', 'black', 'dim gray']
        self.textColor = colormap[number]
        # set up listeners
        self.bind('<Button-1>', self.left_click)
        self.bind('<Button-2>', self.right_click)  # 2-button mouse
        self.bind('<Button-3>', self.right_click)  # 3-button mouse
        # set up parent grid
        self.parentGrid = parent

    def get_coord(self):
        """
        MsCell.get_coord() -> tuple
        returns the coordinates of the cell
        """
        return self.coord

    def is_blank(self):
        """
        MsCell.is_blank() -> boolean
        return if the cell is blank
        """
        return self.text == '0'

    def left_click(self, event):
        """
        MsCell.left_click(event)
        handler method for left click
        """
        if self.text == 'True':  # player clicks on bomb
            messagebox.showerror('Minesweeper', 'Kaboom! You lose.', parent=self)
            self.parentGrid.reveal_bombs()
        elif self.text != '0':  # reveal cell
            self['text'] = self.text
            self['fg'] = self.textColor
            self['bg'] = 'light gray'
            self['relief'] = SUNKEN
            self.parentGrid.exposed_new_cell(self.coord)
        else:  # reveal cell(s) if it is a blank cell
            self.parentGrid.reveal_blank_cells(self)

    def right_click(self, event):
        """
        MsCell.right_click(event)
        handler method for right click
        """
        if self['text'] == '*' and self.text == '*':  # player right-clicks again
            self.auto_expose()
            self.parentGrid.update_number(True)
        else:  # first right-click
            self['text'] = '*'
            self['fg'] = 'black'
            self.parentGrid.update_number()

    def auto_expose(self):
        """
        MsCell.auto_expose()
        exposes a cell without the left click
        """
        if self.text == 'True':  # bomb
            messagebox.showerror('Minesweeper', 'KABOOM! You lose.', parent=self)
            self.parentGrid.reveal_bombs()
        elif self.text != '0':  # reveal cell
            self['text'] = self.text
            self['fg'] = self.textColor
            self['bg'] = 'light gray'
            self['relief'] = SUNKEN
            self.parentGrid.exposed_new_cell(self.coord)
        else:  # reveal blank cell
            self['bg'] = 'light gray'
            self['relief'] = SUNKEN
            self.parentGrid.exposed_new_cell(self.coord)

    def expose_bomb(self):
        """
        MsGrid.expose_bomb()
        exposes a bomb cell
        """
        self['bg'] = 'red'
        self['text'] = '*'


class MsGrid(Frame):
    """
    the whole grid for Minesweeper
    """

    def __init__(self, master, width, height, number):
        """
        MsGrid(master,width,height,number)
        construct a new MsGrid object
        """
        Frame.__init__(self, master)
        # create list of minesweeper cell coords
        cellCoords = []
        for h in range(height):
            for w in range(width):
                cellCoords.append((h, w))
        random.shuffle(cellCoords)
        # find bombs
        self.bombCoords = cellCoords[:number]
        self.bombs = []
        for bomb in self.bombCoords:
            self.bombs.append(MsCell(bomb, True, self))
        # make the rest non-bomb cells
        self.cellCoords = cellCoords[number:]
        self.nonExposed = self.cellCoords[:]
        self.nonBombcells = []
        for cell in self.cellCoords:
            adjacentBombs = 0
            for h in range(max(0, cell[0] - 1), min(cell[0] + 2, height)):
                for w in range(max(0, cell[1] - 1), min(cell[1] + 2, width)):
                    if (h, w) in self.bombCoords:
                        adjacentBombs += 1
            self.nonBombcells.append(MsCell(cell, adjacentBombs, self))
        # set cell
        self.number = number
        self.height = height
        self.width = width
        # set number label
        self.numberLabel = Label(master, text=str(self.number))
        self.numberLabel.grid(row=self.height, columnspan=self.width)

    def update_number(self, addnumber=False):
        """
        MsGrid.update_number(addnumber)
        update the number of bombs after the player has right-clicked
        addnumber: boolean that tells the program if to add a bomb
        """
        if addnumber:
            self.number += 1
        else:
            self.number -= 1
        self.numberLabel['text'] = str(self.number)

    def reveal_bombs(self):
        """
        MsGrid.reveal_bombs()
        reveal all bombs in the grid
        """
        for bomb in self.bombs:
            bomb.expose_bomb()

    def reveal_blank_cells(self, cellObject):
        """
        Minesweeper.reveal_blank_cells(cellCoord)
            automatic reveal of blank cells adjacent of
            MsCell object with coord as the coordinates
        
        cellCoord: list/tuple of the coordinates of the
            MsCell object
        """
        blankcells = [cellObject]
        investigated = []
        while len(blankcells) != 0:  # while more blank cells to expose
            cell = blankcells[0]
            blankcells.remove(cell)
            investigated.append(cell)
            coord = cell.get_coord()
            for h in range(max(0, coord[0] - 1), min(coord[0] + 2, self.height)):  # loop through adjacent cells
                for w in range(max(0, coord[1] - 1), min(coord[1] + 2, self.width)):
                    index = self.cellCoords.index((h, w))
                    targetcell = self.nonBombcells[index]
                    targetcell.auto_expose()
                    if targetcell.is_blank() and targetcell not in investigated:  # found new blank cell
                        blankcells.append(targetcell)

    def exposed_new_cell(self, cellCoord):
        """
        MsGrid.exposed_new_cell(cellCoord)
            removes exposed cell from non-exposed list of
            cells and checks for a win
        """
        if cellCoord in self.nonExposed:
            self.nonExposed.remove(cellCoord)
        if len(self.nonExposed) == 0:  # player wins!
            messagebox.showinfo('Minesweeper', 'Congratulations -- you won!', parent=self)


def play_minesweeper(width, height, number):
    """
    play_minesweeper(width,height,number) —> (int, int, int)

    play a game of Minesweeper
    """
    root = Tk()
    root.title('Minesweeper')
    MsGrid(root, width, height, number)
    root.mainloop()


play_minesweeper(12, 10, 15) # start a game of minesweeper!