import random
from copy import deepcopy


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        known_mines = set()

        if len(self.cells) == self.count:
            known_mines = self.cells

        return known_mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        known_safes = set()

        if self.count == 0:
            known_safes = self.cells

        return known_safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        if cell in self.cells and self.count != 0:
            self.cells.remove(cell)


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """

        self.mines.add(cell)

        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """

        self.safes.add(cell)

        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # Mark the cell as a safe
        self.mark_safe(cell)

        # Store a new sentence in the knowledge base
        if len(self.get_unknown_neighbors(cell)) != 0:
            self.knowledge.append(Sentence(self.get_unknown_neighbors(cell), count))

        copy_of_knowledge = deepcopy(self.knowledge)

        for sentence_x in copy_of_knowledge:
            copy_of_known_safes = deepcopy(sentence_x.known_safes())
            copy_of_known_mines = deepcopy(sentence_x.known_mines())
            for safe_cell in copy_of_known_safes:
                self.mark_safe(safe_cell)
            for mine_cell in copy_of_known_mines:
                self.mark_mine(mine_cell)

        for sentence_1 in self.knowledge:
            for sentence_2 in self.knowledge:
                if not sentence_1.__eq__(sentence_2):
                    if sentence_1.cells < sentence_2.cells:
                        subtracted_cells = set(sentence_2.cells - sentence_1.cells)
                        subtracted_count = sentence_2.count - sentence_1.count
                        inferred_sentence = Sentence(subtracted_cells, subtracted_count)
                        if inferred_sentence in self.knowledge:
                            continue
                        self.knowledge.append(inferred_sentence)
                        for sentence_3 in self.knowledge:
                            if not sentence_3.__eq__(sentence_1) or not sentence_3.__eq__(sentence_2):
                                if not sentence_2.cells < sentence_3.cells:
                                    self.knowledge = list(filter(sentence_2.__ne__, self.knowledge))

    def get_unknown_neighbors(self, cell):
        """
        Returns all neighboring cells of cell.
        """

        unknown_neighbors = set()
        x_coordinates, y_coordinates = cell

        # Add all neighbors which state is neither determined nor the current cell
        for i in range(x_coordinates - 1, x_coordinates + 2):
            if i < 0 or i > self.width - 1:
                continue
            for j in range(y_coordinates - 1, y_coordinates + 2):
                if j < 0 or j > self.height - 1:
                    continue
                if (i, j) == cell or (i, j) in self.safes or (i, j) in self.moves_made:
                    continue
                unknown_neighbors.add((i, j))

        return unknown_neighbors

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        for safe_cell in self.safes:
            if safe_cell not in self.moves_made:
                return safe_cell

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        possible_cells = set()

        for i in range(self.width):
            for j in range(self.height):
                cell = (i, j)
                if cell not in self.moves_made:
                    if cell not in self.mines:
                        possible_cells.add(cell)

        if len(possible_cells) == 0:
            return None

        random_cell = random.sample(possible_cells, 1)[0]

        return random_cell
