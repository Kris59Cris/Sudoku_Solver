import numpy as np
import pandas as pd
from itertools import combinations


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

                    # If all candidates are in the same row, eliminate that candidate from the rest of the row and box
                    if len(set(x_list)) == 1:
                        row = x_list[0]
                        for col in range(9):
                            if col < box_col * 3 or col >= (box_col + 1) * 3:
                                if (
                                    isinstance(self.candidates[row, col], set)
                                    and candidate in self.candidates[row, col]
                                ):
                                    self.candidates[row, col].discard(candidate)
                                    self.vars["any_changes"] = True
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
                                    self.vars["any_changes"] = True
                                    if not self.candidates[row, col]:
                                        return False  # Invalid puzzle state

        # For each row, check if there is a candidate that only appears in one box, delete that candidate from the rest of the box
        for i in range(9):
            row_candidates = {}
            for j in range(9):
                if isinstance(self.candidates[i, j], set):
                    for candidate in self.candidates[i, j]:
                        if candidate not in row_candidates:
                            row_candidates[candidate] = []
                        row_candidates[candidate].append(j)

            for candidate, positions in row_candidates.items():
                box_col_start = (positions[0] // 3) * 3
                box_row_start = (i // 3) * 3

                if all(
                    (pos // 3) * 3 == box_col_start for pos in positions
                ):  # All candidates are in the same box
                    for col in range(box_col_start, box_col_start + 3):
                        for row in range(box_row_start, box_row_start + 3):
                            if row != i:
                                if (
                                    isinstance(self.candidates[row, col], set)
                                    and candidate in self.candidates[row, col]
                                ):
                                    self.candidates[row, col].discard(candidate)
                                    self.vars["any_changes"] = True
                                    if not self.candidates[row, col]:
                                        return False  # Invalid puzzle state

        # For each column, check if there is a candidate that only appears in one box, delete that candidate from the rest of the box
        for j in range(9):
            col_candidates = {}
            for i in range(9):
                if isinstance(self.candidates[i, j], set):
                    for candidate in self.candidates[i, j]:
                        if candidate not in col_candidates:
                            col_candidates[candidate] = []
                        col_candidates[candidate].append(i)

            for candidate, positions in col_candidates.items():
                box_row_start = (positions[0] // 3) * 3
                box_col_start = (j // 3) * 3
                if all(
                    (pos // 3) * 3 == box_row_start for pos in positions
                ):  # All candidates are in the same box
                    for row in range(box_row_start, box_row_start + 3):
                        for col in range(box_col_start, box_col_start + 3):
                            if col != j:
                                if (
                                    isinstance(self.candidates[row, col], set)
                                    and candidate in self.candidates[row, col]
                                ):
                                    self.candidates[row, col].discard(candidate)
                                    self.vars["any_changes"] = True
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
                        self.vars["any_changes"] = True

        self.updating_candidates()

    def naked_candidate_pair_line_and_box(self):
        ### Note that this is working on for candidates pair.
        # For each row, there is a naked pair or naked triple, if there are 2 or 3 cells in the same row that have the same 2 or 3 candidates, then those candidates can be eliminated from the rest of the row
        for i in range(9):
            row_candidates = {}
            for j in range(9):
                if isinstance(self.candidates[i, j], set):
                    candidates_tuple = tuple(sorted(self.candidates[i, j]))
                    if candidates_tuple not in row_candidates:
                        row_candidates[candidates_tuple] = []
                    row_candidates[candidates_tuple].append(j)

            for candidates_tuple, positions in row_candidates.items():
                if len(candidates_tuple) == len(positions) and len(positions) > 1:
                    for col in range(9):
                        if col not in positions:
                            if isinstance(self.candidates[i, col], set) and any(
                                candidate in self.candidates[i, col]
                                for candidate in candidates_tuple
                            ):
                                self.candidates[i, col] -= set(candidates_tuple)
                                self.vars["any_changes"] = True
                                if not self.candidates[i, col]:
                                    return False  # Invalid puzzle state

        # For each column, there is a naked pair or naked triple, if there are 2 or 3 cells in the same column that have the same 2 or 3 candidates, then those candidates can be eliminated from the rest of the column
        for j in range(9):
            col_candidates = {}
            for i in range(9):
                if isinstance(self.candidates[i, j], set):
                    candidates_tuple = tuple(sorted(self.candidates[i, j]))
                    if candidates_tuple not in col_candidates:
                        col_candidates[candidates_tuple] = []
                    col_candidates[candidates_tuple].append(i)

            for candidates_tuple, positions in col_candidates.items():
                if len(candidates_tuple) == len(positions) and len(positions) > 1:
                    for row in range(9):
                        if row not in positions:
                            if isinstance(self.candidates[row, j], set) and any(
                                candidate in self.candidates[row, j]
                                for candidate in candidates_tuple
                            ):
                                self.candidates[row, j] -= set(candidates_tuple)
                                self.vars["any_changes"] = True
                                if not self.candidates[row, j]:
                                    return False  # Invalid puzzle state

        # For each box, there is a naked pair or naked triple, if there are 2 or 3 cells in the same row that have the same 2 or 3 candidates, then those candidates can be eliminated from the rest of the row
        for box_row in range(3):
            for box_col in range(3):
                box_candidates = {}
                for i in range(box_row * 3, (box_row + 1) * 3):
                    for j in range(box_col * 3, (box_col + 1) * 3):
                        if isinstance(self.candidates[i, j], set):
                            candidates_tuple = tuple(sorted(self.candidates[i, j]))
                            if candidates_tuple not in box_candidates:
                                box_candidates[candidates_tuple] = []
                            box_candidates[candidates_tuple].append((i, j))

                for candidates_tuple, positions in box_candidates.items():
                    if len(candidates_tuple) == len(positions) and len(positions) > 1:
                        for i in range(box_row * 3, (box_row + 1) * 3):
                            for j in range(box_col * 3, (box_col + 1) * 3):
                                if (i, j) not in positions:
                                    if isinstance(self.candidates[i, j], set) and any(
                                        candidate in self.candidates[i, j]
                                        for candidate in candidates_tuple
                                    ):
                                        self.candidates[i, j] -= set(candidates_tuple)
                                        self.vars["any_changes"] = True
                                        if not self.candidates[i, j]:
                                            return False  # Invalid puzzle state

        self.updating_candidates()

    def naked_triple_line_and_box(self):
        # For each box
        for box_row in range(3):
            for box_col in range(3):
                cells_candidates = {}
                # Collect all cells with 2 or 3 candidates in the box
                for i in range(box_row * 3, (box_row + 1) * 3):
                    for j in range(box_col * 3, (box_col + 1) * 3):
                        if (
                            isinstance(self.candidates[i, j], set)
                            and 2 <= len(self.candidates[i, j]) <= 3
                        ):
                            cells_candidates[(i, j)] = self.candidates[i, j]

                # Check all possible combinations of 3 cells
                for cells in combinations(cells_candidates.items(), 3):
                    positions = [cell[0] for cell in cells]
                    candidates_sets = [cell[1] for cell in cells]
                    union_candidates = set().union(*candidates_sets)

                    # If union has 3 numbers and all cells only contain these numbers
                    if len(union_candidates) == 3:
                        # Remove these candidates from other cells in the box
                        for i in range(box_row * 3, (box_row + 1) * 3):
                            for j in range(box_col * 3, (box_col + 1) * 3):
                                if (i, j) not in positions:
                                    if isinstance(self.candidates[i, j], set):
                                        before_len = len(self.candidates[i, j])
                                        self.candidates[i, j] -= union_candidates
                                        if len(self.candidates[i, j]) != before_len:
                                            self.vars["any_changes"] = True
                                        if not self.candidates[i, j]:
                                            return False  # Invalid puzzle state

        # For each row
        for i in range(9):
            cells_candidates = {}
            for j in range(9):
                if (
                    isinstance(self.candidates[i, j], set)
                    and 2 <= len(self.candidates[i, j]) <= 3
                ):
                    cells_candidates[j] = self.candidates[i, j]

            for cols in combinations(cells_candidates.items(), 3):
                positions = [col[0] for col in cols]
                candidates_sets = [col[1] for col in cols]
                union_candidates = set().union(*candidates_sets)

                if len(union_candidates) == 3:
                    for j in range(9):
                        if j not in positions:
                            if isinstance(self.candidates[i, j], set):
                                before_len = len(self.candidates[i, j])
                                self.candidates[i, j] -= union_candidates
                                if len(self.candidates[i, j]) != before_len:
                                    self.vars["any_changes"] = True
                                if not self.candidates[i, j]:
                                    return False

        # For each column
        for j in range(9):
            cells_candidates = {}
            for i in range(9):
                if (
                    isinstance(self.candidates[i, j], set)
                    and 2 <= len(self.candidates[i, j]) <= 3
                ):
                    cells_candidates[i] = self.candidates[i, j]

            for rows in combinations(cells_candidates.items(), 3):
                positions = [row[0] for row in rows]
                candidates_sets = [row[1] for row in rows]
                union_candidates = set().union(*candidates_sets)

                if len(union_candidates) == 3:
                    for i in range(9):
                        if i not in positions:
                            if isinstance(self.candidates[i, j], set):
                                before_len = len(self.candidates[i, j])
                                self.candidates[i, j] -= union_candidates
                                if len(self.candidates[i, j]) != before_len:
                                    self.vars["any_changes"] = True
                                if not self.candidates[i, j]:
                                    return False

        self.updating_candidates()
        return True

    def fill_in_single_candidate(self):
        ### in terms of candidates choice
        for i in range(9):
            for j in range(9):
                if self.grid[i, j] == "" and len(self.candidates[i, j]) == 1:
                    self.grid[i, j] = list(self.candidates[i, j])[0]
                    self.candidates[i, j] = self.grid[i, j]
                    self.updating_candidates()
                    self.vars["any_changes"] = True

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
                        self.vars["any_changes"] = True

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
                    self.vars["any_changes"] = True

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
                    self.vars["any_changes"] = True

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

        self.only_candidate_in_box()
        self.hidden_candidate_line()
        self.naked_candidate_pair_line_and_box()
        self.naked_triple_line_and_box()
        while self.check_if_single_candidate() or self.vars["any_changes"]:
            self.vars["any_changes"] = False
            self.fill_in_single_candidate()
            self.only_candidate_in_box()
            self.hidden_candidate_line()
            self.naked_candidate_pair_line_and_box()
            self.naked_triple_line_and_box()


if __name__ == "__main__":
    file_path = "input_sudoku.csv"

    # Load the CSV file into a 2D NumPy array
    data = np.genfromtxt(file_path, delimiter=",", dtype=str, filling_values=np.nan)

    s = SudokuGrid(data)
    s.solve()
    print(s.grid)
    print(s.candidates)

    # export the result to a csv file
    # df = pd.DataFrame(s.grid)
    # df.to_csv("output_sudoku.csv", index=False, header=False)
