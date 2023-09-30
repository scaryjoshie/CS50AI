import itertools
import random


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

        # If the count of the set is equal to the number of cells in the set (and greater than 0) --> all cells are mines
        if self.count == len(self.cells) and self.count > 0:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        # If the count of the set is 0, then all cells in the set must be safe
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        # If the marked cell is in the set, removes cell from set and also decreases count by 1
        if cell in self.cells:
            self.cells.remove(cell)
            self.count = self.count - 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        # If the marked cell is in the set, removes cell from set and also decreases count by 1
        if cell in self.cells:
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

        # Marks the cell as a move that has been made,
        self.moves_made.add(cell)
        # Marks the cell as safe
        self.mark_safe(cell)

        # Creates an empty set representing the sentence we are building
        new_sentence_cells = set()

        # Iterates through all cells from 1 below to 1 above the target cell, but only if they are within the bounds of the field
        for i in range(max(0, cell[0] - 1), min(self.height, cell[0] + 2)):
            for j in range(max(0, cell[1] - 1), min(self.width, cell[1] + 2)):
                # Ignores the input cell since it is safe
                if (i, j) == cell:
                    continue

                # If the cell is safe, skips
                elif (i, j) in self.safes:
                    continue

                # If the cell is a mine, decreases count by 1 and skips
                elif (i, j) in self.mines:
                    count = count - 1
                    continue

                # If all criteria are met, adds cell to new sentence cells
                else:
                    new_sentence_cells.add((i, j))

        # Adds sentence containing new information to knowledge
        self.knowledge.append(Sentence(cells=new_sentence_cells, count=count))

        # Keeps trying to update information until knowledge base stops changing
        while True:
            # This variable keeps track of whether information in the knowledge base is changing
            change_this_iteration = False

            # Iterates through (a copy of) all sentences, marking mines/safes when information is known
            for sentence in self.knowledge:
                for safe in sentence.known_safes().copy():
                    self.mark_safe(safe)
                    change_this_iteration = True

                for mine in sentence.known_mines().copy():
                    self.mark_mine(mine)
                    change_this_iteration = True

            # Removes all empty sentences from knowledge
            self.knowledge = [
                sentence for sentence in self.knowledge if len(sentence.cells) != 0
            ]

            # For all sentences, performs subset comprehension
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    # Skips comparisons between the same list
                    if sentence1 == sentence2:
                        continue

                    # If sentence1 is a subset of sentence 2, creates a new sentence subtracting sentence1 from sentence2
                    if sentence1.cells.issubset(sentence2.cells):
                        # Finds difference between sentence 2 and sentence 1
                        cell_difference = sentence2.cells - sentence1.cells
                        count_difference = sentence2.count - sentence1.count
                        sentence_to_add = Sentence(
                            cells=cell_difference, count=count_difference
                        )

                        # Adds new sentence if it isn't already in the knowledge base
                        if not sentence_to_add in self.knowledge:
                            self.knowledge.append(sentence_to_add)
                            change_this_iteration = True

            # Exits the while loop if no change occurs during the iteration
            if change_this_iteration == False:
                break

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        # Gets available moves by subtracting (cells already checked) from (known safe cells)
        available_moves = self.safes - self.moves_made

        # If set is empty, returns None. Otherwise, returns the first cell that is available
        if len(available_moves) == 0:
            return None
        else:
            move = list(available_moves)[0]
            print(f"making a move at: {move}")
            return move

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # Gets total moves
        total_moves = set()
        for y in range(0, self.height):
            for x in range(0, self.width):
                total_moves.add((y, x))

        # Gets available moves by subtracting (known mines) and (moves already made) from (all possible moves)
        available_moves = total_moves - self.moves_made - self.mines

        # If available moves is empty, returns None.
        if len(available_moves) == 0:
            print("No available random moves")
            return None
        # Else, returns random move in available moves
        else:
            move = random.choice(list(available_moves))
            print(f"RANDOM MOVE AT: {move}")
            return move
