import streamlit as st
import pandas as pd
from Sudoku import SudokuGrid as sg


def clear_state():
    st.session_state.status = ""
    st.session_state.solution = None
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0
    st.session_state.uploader_key += 1

    # Clear the data editor input
    if "inputed_sudoku" in st.session_state:
        st.session_state.inputed_sudoku = st.session_state.initial_data

    st.session_state.clear_requested = True


def solving_sudoku(edited_df):
    st.session_state.status = ""
    st.session_state.solution = None

    # Turn the edited dataframe into a 2D list of string for the Sudoku solver, where empty cells are represented as ''
    edited_df = edited_df.astype(str)
    edited_df = edited_df.replace("0", "")
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
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    uploaded_file = st.file_uploader(
        "Choose a CSV file with the Sudoku puzzle", key=st.session_state.uploader_key
    )
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                data = pd.read_csv(uploaded_file, header=None).fillna(0)
            elif uploaded_file.name.endswith(".xlsx"):
                data = pd.read_excel(uploaded_file, header=None).fillna(0)

            data = data.astype(int)
            return data.to_numpy(dtype=str)
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            return None
    return None


def main():
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0
    if "clear_requested" not in st.session_state:
        st.session_state.clear_requested = False
    if "inputed_sudoku" not in st.session_state:
        st.session_state.inputed_sudoku = None

    # Handle rerun at the start of main
    if st.session_state.clear_requested:
        st.session_state.clear_requested = False
        st.rerun()

    st.title("Sudoku Solver")
    imported_data = import_file()

    # Initialize session state if needed
    if "status" not in st.session_state:
        st.session_state.status = ""
    if "solution" not in st.session_state:
        st.session_state.solution = None
    st.session_state.initial_data = pd.DataFrame(
        0,
        index=[f"Row {i + 1}" for i in range(9)],
        columns=[f"Col {j + 1}" for j in range(9)],
        dtype=int,
    )
    st.session_state.col_config = {
        col: st.column_config.NumberColumn(
            min_value=0,
            max_value=9,
            step=1,
            format="%d",
            required=True,
        )
        for col in st.session_state.initial_data.columns
    }

    if imported_data is not None:
        st.session_state.inputed_sudoku = pd.DataFrame(
            imported_data,
            index=[f"Row {i + 1}" for i in range(9)],
            columns=[f"Col {j + 1}" for j in range(9)],
        )
    else:
        st.session_state.inputed_sudoku = st.session_state.initial_data

    st.subheader("Inputed Sudoku Puzzle")
    st.write("Enter the Sudoku puzzle below (use 0 for empty cells):")

    ### Showing input
    edited_input_df = st.data_editor(
        st.session_state.inputed_sudoku,
        column_config=st.session_state.col_config,
        key="inputed_sudoku_display" + str(st.session_state.uploader_key),
    )

    # add 2 buttons: "Solve Sudoku", "Clear cache"
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button(
            "Solve Sudoku",
            on_click=solving_sudoku,
            args=(edited_input_df,),
            key="solve_button",
        )
    with col2:
        st.button("Clear cache", on_click=clear_state, key="clear_button")

    # Convert the dataframe to a 2D np-array for the Sudoku solver
    st.subheader("Result")

    status_message = st.empty()
    for_solved_puzzle = st.empty()

    # Display status from session state
    if st.session_state.status:
        status_message.write(st.session_state.status)

    # Display solution from session state
    if st.session_state.solution is not None:
        for_solved_puzzle.dataframe(
            pd.DataFrame(
                st.session_state.solution,
                index=[f"Row {i + 1}" for i in range(9)],
                columns=[f"Col {j + 1}" for j in range(9)],
            )
        )

    st.download_button(
        label="Export solution as CSV",
        data=pd.DataFrame(st.session_state.solution).to_csv(index=False, header=False),
        file_name="Solved_sudoku.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
