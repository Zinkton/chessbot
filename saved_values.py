from typing import Dict


class SavedValues:
    def __init__(self, value_table: Dict = None, legal_move_table: Dict = None):
        self.value_table = value_table
        self.legal_move_table = legal_move_table

    def clone(self):
        return SavedValues(self.value_table.copy(), self.legal_move_table.copy())