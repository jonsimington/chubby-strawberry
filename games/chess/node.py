class Node:
    def __init__(self, problem, parent=None, action=None):
        """
        :param problem: Data structure representing the abstraction of the problem itself. Expecting "Chess"
        :param parent: Parent Node of the current node. Root will have no parent.
        :param action: String representing what action was taken from the parent node to reach the current node
        """
        self._problem = problem
        if parent is not None:
            self.state = problem.result(parent.state, action)
            self.path_cost = parent.path_cost + problem.step_cost(parent, action)
            self.depth = parent.depth + 1
        else:
            self.state = problem.initial_state
            self.path_cost = 0
            self.depth = 0
        self.parent = parent
        self.action = action
        self.hash_val = self.__hash__()

    def __hash__(self):
        return hash(self.state)

    def __eq__(self, other):
        try:
            return self.hash_val == other.hash_val
        except AttributeError:
            return False
