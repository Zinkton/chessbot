from constants import NodeState
import constants

class ChessNode:
    def __init__(self, move, value, min_value = constants.MAX_VALUE, children = None, parent = None, legal_moves = None, move_index = None, move_chain = None):
        self.move = move
        self.min_value = min_value
        self.children = children
        self.parent = parent
        self.legal_moves = legal_moves
        self.move_index = move_index
        self.value = value
        self.state = NodeState.UNEXPANDED
        self.depth = 0
        self.move_chain = move_chain
        
    def __repr__(self):
        return '; '.join([str(self.move), str(self.min_value), str(len(self.children)), str(self.value), str(self.state)])
    
    def reset_node_state(self):
        self.state = NodeState.UNEXPANDED

        if self.children is not None:
            for child in self.children:
                child.reset_node_state()
    
    def clone(self, parent = None):
        clone = ChessNode(self.move, self.value, self.min_value, None, parent, self.legal_moves, self.move_index)
        if self.children is not None:
            grandsons = [child for child in self.children if child.parent.move != self.move]
            grandson_clones = []
            for grandson in grandsons:
                son_clone = grandson.parent.clone(clone)
                grandson_clone = grandson.clone(son_clone)
                grandson_clones.append(grandson_clone)
            clone.children = grandson_clones

        return clone
        
