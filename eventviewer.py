import PySimpleGUI as gui


def main():
    gui.theme('DarkAmber')

    testarray = [
        ["fuck", "this", "shit", "im", "out"],
        ["coffee", "tea", "whiskey", "and", "me"],
        ["ded", "meeeep", "one espresso depresso please thankyou", "meat bicycle", "chocolate milo shake"]
    ]

    testarray_headings = ["Time", "Filename", "Action", "Notes", "View Change"]

    top_row = [
        [gui.Text("Files Investigated ??/??"),
         gui.Text("Selected folder: ?:\\"),
         gui.Text("Start Time:???\nTime elapsed:???")]
    ]

    tab_selector = [
        [gui.Button("Events"), gui.Button("Files")]
    ]

    some_column = [
        [gui.Text("testing column")]
    ]

    other_column = [
        [gui.Text("testing column 2")]
    ]

    confirm_row = [
        [gui.Button('Ok'), gui.Button('Cancel')]
    ]

    layout = [
        top_row,
        tab_selector,
        # [
        #     gui.Column(some_column),
        #     gui.VSeperator(),
        #     gui.Column(other_column),
        #     gui.VSeperator(),
        #     gui.Column([[gui.Text("TEST")]])
        # ],
        [gui.Table(values=testarray,
                   headings=testarray_headings,
                   max_col_width=100,
                   auto_size_columns=True,
                   display_row_numbers=False,
                   justification="right",
                   num_rows=10,
                   key="-TABLE-",
                   row_height=35)],
        confirm_row
    ]

    window = gui.Window("Window Title", layout)
    while True:
        event, values = window.read()
        if event == gui.WIN_CLOSED or event == "Cancel":
            break


    window.close()

if __name__ == "__main__":
    main()