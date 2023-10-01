from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # A can be a knight or knave but not both
    Or(AKnight, AKnave), Not(And(AKnight, AKnave)),

    # A is both a knight and a knave if and only if A is a knight
    Biconditional(AKnight, And(AKnight, AKnave)),

    # If A is a knight, then A is both a knight and a knave
    #Implication(AKnight, Not(And(AKnight, AKnave)))
    # If A is a knave, then A is not both a knight and a knave
    #Implication(AKnave, Not(And(AKnight, AKnave)))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # A and B can each be knights or knaves but not both
    Or(AKnight, AKnave), Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave), Not(And(BKnight, BKnave)),

    # A and B are both knaves if and only if A is a knight
    Biconditional(AKnight, And(AKnave, BKnave)),
    
    # OLD
    # If A is a knight, A and B must both be knaves since knights only tell the truth
    #Implication(AKnight, And(AKnave, BKnave)),
    # If A is a knave, then A and B are NOT both knaves
    #Implication(AKnave, Not(And(AKnave, BKnave)))
    
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # A and B can each be knights or knaves but not both
    Or(AKnight, AKnave), Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave), Not(And(BKnight, BKnave)),

    # A and B are of the same kind if and only if A is a knight
    Biconditional(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),

    # A and B are of different kinds if and only if B is a knight
    Biconditional(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight))),

    # OLD
    # If A is a knight, both A and B are of the same kind
    #Implication(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    # If A is a knave, A and B are not of the same kind
    #Implication(AKnave, And(Not(And(AKnight, BKnight)), Not(And(AKnave, BKnave)))),
    # If B is a knight, A and B are of different kinds
    #Implication(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight))),
    # If B is a knave, A and B are not of different kinds
    #Implication(BKnave, And(Not(And(AKnight, BKnave)), Not(And(AKnave, BKnight)))),

)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # A, B, and C can each be knights or knaves but not both
    Or(AKnight, AKnave), Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave), Not(And(BKnight, BKnave)),
    Or(CKnight, CKnave), Not(And(CKnight, CKnave)),

    # If B is a knight, then A said they are a knave, which means A is a knave if and only if A is a knight
    Implication(BKnight, Biconditional(AKnight, AKnave)),

    # C is a knave if and only if B is a knight
    Biconditional(BKnight, CKnave),

    # A is a knight if and only if C is a knight
    Biconditional(CKnight, AKnight)

)



def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
