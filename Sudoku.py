import numpy as np


class SudokuGrid:
    ### The original grid is represented as a 2D numpy array of strings, where empty cells are represented as ''.

    def __init__(self, grid):
        self.grid = grid
        self.vars = {"any_changes": False}

        self.candidates = np.zeros_like(grid, dtype=object)
        self._initialize_candidates()

    def _initialize_candidates(self):
        for i in range(9):
            for j in range(9):
                if self.grid[i, j] != "":
                    self.candidates[i, j] = self.grid[i][j]

        self.updating_candidates()

    def check_invalid(self):
        for i in range(9):
            for j in range(9):
                if self.grid[i, j] != "":
                    value = self.grid[i, j]
                    # Check row
                    if value in self.grid[i, :j] or value in self.grid[i, j + 1 :]:
                        return True
                    # Check column
                    if value in self.grid[:i, j] or value in self.grid[i + 1 :, j]:
                        return True
                    # Check box
                    box_row_start = (i // 3) * 3
                    box_col_start = (j // 3) * 3
                    box = self.grid[
                        box_row_start : box_row_start + 3,
                        box_col_start : box_col_start + 3,
                    ]
                    if value in np.delete(
                        box.flatten(), np.where(box.flatten() == value)
                    ):
                        return True
        return False

    def updating_candidates(self):
        for i in range(9):
            for j in range(9):
                row_values = set(self.grid[i, :])
                col_values = set(self.grid[:, j])
                box_values = set(
                    self.grid[
                        i // 3 * 3 : (i // 3 + 1) * 3, j // 3 * 3 : (j // 3 + 1) * 3
                    ].flatten()
                )
                # First time
                if self.candidates[i, j] == 0:
                    self.candidates[i, j] = (
                        set(map(str, range(1, 10)))
                        - row_values
                        - col_values
                        - box_values
                    )
                # When you have already candidates, you need to update them
                elif isinstance(self.candidates[i, j], set):
                    self.candidates[i, j] = (
                        self.candidates[i, j] - row_values - col_values - box_values
                    )

    def hidden_candidate_line(self):
        # For each box, check if there is a candidate that only appears in one row or column
        for box_row in range(3):
            for box_col in range(3):
                box_candidates = {}
                for i in range(box_row * 3, (box_row + 1) * 3):
                    for j in range(box_col * 3, (box_col + 1) * 3):
                        if isinstance(self.candidates[i, j], set):
                            for candidate in self.candidates[i, j]:
                                if candidate not in box_candidates:
                                    box_candidates[candidate] = []
                                box_candidates[candidate].append((i, j))

                for candidate, positions in box_candidates.items():
                    x_list = [pos[0] for pos in positions]
                    y_list = [pos[1] for pos in positions]

                    # If all candidates are in the same row, eliminate that candidate from the rest of the row
                    if len(set(x_list)) == 1:
                        row = x_list[0]
                        for col in range(9):
                            if col < box_col * 3 or col >= (box_col + 1) * 3:
                                if (
                                    isinstance(self.candidates[row, col], set)
                                    and candidate in self.candidates[row, col]
                                ):
                                    self.candidates[row, col].discard(candidate)
                                    if not self.candidates[row, col]:
                                        return False  # Invalid puzzle state

                    # If all candidates are in the same column, eliminate that candidate from the rest of the column
                    if len(set(y_list)) == 1:
                        col = y_list[0]
                        for row in range(9):
                            if row < box_row * 3 or row >= (box_row + 1) * 3:
                                if (
                                    isinstance(self.candidates[row, col], set)
                                    and candidate in self.candidates[row, col]
                                ):
                                    self.candidates[row, col].discard(candidate)
                                    if not self.candidates[row, col]:
                                        return False  # Invalid puzzle state

        self.updating_candidates()

    def only_candidate_in_box(self):
        for box_row in range(3):
            for box_col in range(3):
                box_candidates = {}
                for i in range(box_row * 3, (box_row + 1) * 3):
                    for j in range(box_col * 3, (box_col + 1) * 3):
                        if isinstance(self.candidates[i, j], set):
                            for candidate in self.candidates[i, j]:
                                if candidate not in box_candidates:
                                    box_candidates[candidate] = []
                                box_candidates[candidate].append((i, j))

                for candidate, positions in box_candidates.items():
                    if len(positions) == 1:
                        i, j = positions[0]
                        self.grid[i, j] = candidate
                        self.candidates[i, j] = candidate
                        self.updating_candidates()

        self.updating_candidates()

    def fill_in_single_candidate(self):
        ### in terms of candidates choice
        for i in range(9):
            for j in range(9):
                if self.grid[i, j] == "" and len(self.candidates[i, j]) == 1:
                    self.grid[i, j] = list(self.candidates[i, j])[0]
                    self.candidates[i, j] = self.grid[i, j]
                    self.updating_candidates()

        ### in terms of box, if the a value can only be in one cell, then it must go there
        for box_row in range(3):
            for box_col in range(3):
                box_candidates = {}
                for i in range(box_row * 3, (box_row + 1) * 3):
                    for j in range(box_col * 3, (box_col + 1) * 3):
                        if self.grid[i, j] == "":
                            for candidate in self.candidates[i, j]:
                                if candidate not in box_candidates:
                                    box_candidates[candidate] = []
                                box_candidates[candidate].append((i, j))

                for candidate, positions in box_candidates.items():
                    if len(positions) == 1:
                        i, j = positions[0]
                        self.grid[i, j] = candidate
                        self.candidates[i, j] = candidate
                        self.updating_candidates()

        ### in terms of rows, if the a value can only be in one cell, then it must go there
        for i in range(9):
            row_candidates = {}
            for j in range(9):
                if self.grid[i, j] == "":
                    for candidate in self.candidates[i, j]:
                        if candidate not in row_candidates:
                            row_candidates[candidate] = []
                        row_candidates[candidate].append((i, j))

            for candidate, positions in row_candidates.items():
                if len(positions) == 1:
                    i, j = positions[0]
                    self.grid[i, j] = candidate
                    self.candidates[i, j] = candidate
                    self.updating_candidates()

        ### in terms of columns, if the a value can only be in one cell, then it must go there
        for j in range(9):
            col_candidates = {}
            for i in range(9):
                if self.grid[i, j] == "":
                    for candidate in self.candidates[i, j]:
                        if candidate not in col_candidates:
                            col_candidates[candidate] = []
                        col_candidates[candidate].append((i, j))

            for candidate, positions in col_candidates.items():
                if len(positions) == 1:
                    i, j = positions[0]
                    self.grid[i, j] = candidate
                    self.candidates[i, j] = candidate
                    self.updating_candidates()

    def check_if_single_candidate(self):
        for i in range(9):
            for j in range(9):
                if self.grid[i, j] == "" and len(self.candidates[i, j]) == 1:
                    return True

        ### in terms of row, if the a value can only be in one cell, then it must go there
        for i in range(9):
            row_candidates = {}
            for j in range(9):
                if self.grid[i, j] == "":
                    for candidate in self.candidates[i, j]:
                        if candidate not in row_candidates:
                            row_candidates[candidate] = []
                        row_candidates[candidate].append((i, j))

            for candidate, positions in row_candidates.items():
                if len(positions) == 1:
                    return True

        ### in terms of columns, if the a value can only be in one cell, then it must go there
        for j in range(9):
            col_candidates = {}
            for i in range(9):
                if self.grid[i, j] == "":
                    for candidate in self.candidates[i, j]:
                        if candidate not in col_candidates:
                            col_candidates[candidate] = []
                        col_candidates[candidate].append((i, j))

            for candidate, positions in col_candidates.items():
                if len(positions) == 1:
                    return True

        return False

    def solve(self):
        if self.check_invalid():
            return "Invalid Sudoku grid: duplicate values found in rows, columns, or boxes."

        while self.check_if_single_candidate() or self.vars["any_changes"]:
            self.fill_in_single_candidate()
            self.only_candidate_in_box()
            self.hidden_candidate_line()


if __name__ == "__main__":
    file_path = "sample.csv"

    # Load the CSV file into a 2D NumPy array
    data = np.genfromtxt(file_path, delimiter=",", dtype=str, filling_values=np.nan)

    s = SudokuGrid(data)
    s.solve()
    print(s.grid)
    # import pandas as pd

    # df = pd.DataFrame(s.grid)
    # df.to_csv("output.csv", index=False, header=False)
