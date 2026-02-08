import streamlit as st
import pandas as pd
from Sudoku import SudokuGrid as sg


def clear_state():
    st.session_state.status = ""
    st.session_state.solution = None


def solving_sudoku(edited_df):
    clear_state()
    # Turn the edited dataframe into a 2D list of string for the Sudoku solver, where empty cells are represented as ''
    edited_df = edited_df.fillna(0)
    edited_df = edited_df.replace(0, "")
    sudoku_grid = edited_df.to_numpy(dtype=str)  # Convert to numpy array of str

    try:
        st.session_state.status = "Attempting to solve the Sudoku puzzle..."
        sudoku = sg(sudoku_grid)
        solution = sudoku.solve()
        if not isinstance(solution, str):
            st.session_state.status = "Solved Sudoku Puzzle:"
            st.session_state.solution = sudoku.grid
        else:
            st.session_state.status = solution
    except Exception as e:
        st.session_state.status = f"An error occurred: {e}"


def import_file():
    uploaded_file = st.file_uploader("Choose a CSV file with the Sudoku puzzle")
    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file, header=None)
            return data.to_numpy(dtype=str)
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            return None
    return None


def main():
    st.title("Sudoku Solver")
    imported_data = import_file()

    # Initialize session state if needed
    if "status" not in st.session_state:
        st.session_state.status = ""
    if "solution" not in st.session_state:
        st.session_state.solution = None

    st.subheader("Inputed Sudoku Puzzle")
    st.write("Enter the Sudoku puzzle below (use 0 for empty cells):")

    ### Showing input
    place_holder = st.empty()
    if imported_data is not None:
        edited_df = pd.DataFrame(
            imported_data,
            columns=edited_df.columns,
            column_config=column_config,
        )
        st.session_state.sudoku_input = edited_df

    # Create a 9x9 dataframe for user input
    input_data = pd.DataFrame(
        0,
        index=[f"Row {i + 1}" for i in range(9)],
        columns=[f"Col {j + 1}" for j in range(9)],
    )
    column_config = {
        col: st.column_config.NumberColumn(
            min_value=0,
            max_value=9,
            step=1,
            format="%d",
            required=True,
        )
        for col in input_data.columns
    }
    edited_df = st.data_editor(
        input_data,
        key="sudoku_input",
        num_rows="fixed",
        hide_index=False,
        column_config=column_config,
    )

    # add 2 buttons: "Solve Sudoku", "Clear Input"
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button(
            "Solve Sudoku",
            on_click=solving_sudoku,
            args=(edited_df,),
        )

    # Convert the dataframe to a 2D np-array for the Sudoku solver
    st.subheader("Result")

    status_message = st.empty()
    for_solved_puzzle = st.empty()

    # Display status from session state
    if st.session_state.status:
        status_message.write(st.session_state.status)

    # Display solution from session state
    if st.session_state.solution is not None:
        for_solved_puzzle.dataframe(pd.DataFrame(st.session_state.solution))


if __name__ == "__main__":
    main()
