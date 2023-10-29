import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())


    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        
        # Iterates through every variable within the domain
        for variable in self.domains.keys():
            
            # Gets variable length
            variable_length = variable.length
            # Gets the current domain of the variable
            variable_domain = self.domains[variable]
            
            # Creates a new set that is a filtered version of the domain, so that each word in the new set is the length of the variable
            filtered_words_by_length = set(filter(lambda x: len(x) == variable_length, variable_domain))

            # Sets the domain of the variable to the filtered set
            self.domains[variable] = filtered_words_by_length



    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        
        # Gets overlap between x and y
        overlap = self.crossword.overlaps[x, y]
        is_revised = False # variable to keep track of whether or not a revision has been made
        to_remove = set()

        # If there is an overlap, removes words from x for which there is no corresponding value for y at letter of overlap.
        # Will also remove words if the only corresponding word is the same between x and y
        if overlap:
            for word_x in self.domains[x]:
                consistent = False
                for word_y in self.domains[y]:
                    if word_x[overlap[0]] == word_y[overlap[1]] and word_x != word_y:
                        consistent = True
                        break
       
                if consistent == False:
                    to_remove.add(word_x)
                    is_revised = True

        # Remove variables from domain that aren't arc consistent, then return
        self.domains[x] = self.domains[x] - to_remove
        return is_revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        # Creates a queue with arcs if there are none
        if arcs == None:
            arcs = []
            for x in self.domains:
                for y in self.domains:
                    if x != y:
                        arcs.append((x, y))
        
        # Run arc queue
        while arcs:
            x, y = arcs.pop()
            # If domain can be revised
            if self.revise(x, y):
                # If the domain is empty, there is no solution
                if len(self.domains[x]) == 0:
                    return False
                # Gets all neighbors of x excluding y
                neighbors = self.crossword.neighbors(x) - {y}
                # Add those neighors to arcs
                arcs.extend([(neighbor, x) for neighbor in neighbors])


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Returns true if there is a var in 
        if all(var in assignment for var in self.domains):
            return True
        else:
            return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        
        # Checks if there are duplicate assignments
        if len(assignment.values()) != len(set(assignment.values())):
            return False
        
        for var in assignment:
            # Makes sure that var length is correct
            if len(assignment[var]) != var.length:
                return False
            
            # Checks if conflicts between neighbors
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    # Gets overlap
                    overlap = self.crossword.overlaps[var, neighbor]
                    # Checks if overlapping letter matches. If it doesn't, returns False
                    if assignment[var][overlap[0]] != assignment[neighbor][overlap[1]]:
                        return False
                    
        # If everything passes, returns True
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        
        # Creates a dicitonary to track how much each value rules out
        ruled_out_dict = {val:0 for val in self.domains[var]}

        # 
        for val in self.domains[var]:

            # 
            for neighbor in self.crossword.neighbors(var):

                # Checks if value is ruled out by var
                for neighbor_val in self.domains[neighbor]:
                    # Gets overlap
                    overlap = self.crossword.overlaps[var, neighbor]
                    # Checks if overlapping letter matches. If it doesn't, adds to ruleout dict
                    if val[overlap[0]] != neighbor_val[overlap[1]]:
                        ruled_out_dict[val] += 1

        # Returns a sorted list of vals
        return sorted(ruled_out_dict.keys(), key=lambda x: ruled_out_dict[x])
    

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # Get unassigned variables as a list
        unassigned = list(set(self.domains.keys()) - set(assignment.keys()))

        # Sorts unassigned
        unassigned.sort(key=lambda x: (len(self.domains[x]), -len(self.crossword.neighbors(x))))
        
        # Returns first value
        return unassigned[0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        
        # If assignment complete, return
        if self.assignment_complete(assignment):
            return assignment
    
        # Otherwise
        var = self.select_unassigned_variable(assignment)
        for val in self.order_domain_values(var, assignment):
            assignment[var] = val
            if self.consistent(assignment):
                backtrack = self.backtrack(assignment)
                if backtrack:
                    return backtrack
            

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
