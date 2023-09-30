class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

class StackFrontier():
    def __init__(self):
        self.frontier = []
        self.explored_states = [] # set of movies that have already been added, purely for speed reasons

    def add(self, node:Node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        print(f"frontier: {self.frontier}")
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node
        


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise EmptyFrontierException
        else:
            # gets first node in queue
            node = self.frontier[0]
            # removes node from frontier and adds it to the explored nodes
            self.frontier = self.frontier[1:]
            # returns node
            return node



class EmptyFrontierException(Exception):
   pass