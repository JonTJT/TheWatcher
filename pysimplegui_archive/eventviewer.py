import PySimpleGUI as gui
import threading

# def updateTable(window, filelist, testlist_headings):
#     """Threading: Function to update the filelist"""
#     window["-TABLE-"].update(gui.Table(values=filelist,
#                                         headings=testlist_headings,
#                                         max_col_width=100,
#                                         auto_size_columns=True,
#                                         display_row_numbers=False,
#                                         justification="right",
#                                         num_rows=10,
#                                         key="-TABLE-",
#                                         row_height=35))


def appendToList(window, the_list):
    """Testing if I can add stuff to the list"""
    the_list.append(["test", "test", "test", "test", "test"])
    window["-TABLE-"].update(values=the_list)



def main():
    gui.theme('DarkAmber')

    testlist = [
        ["fuck", "this", "shit", "im", "out"],
        ["coffee", "tea", "whiskey", "and", "me"],
        ["ded", "meeeep", "one espresso depresso please thankyou", "meat bicycle", "chocolate milo shake"]
    ]

    testlist_headings = ["Time", "Filename", "Action", "Notes", "View Change"]

    top_row = [
        [gui.Text("Files Investigated ??/??"),
         gui.Text("Selected folder: ?:\\"),
         gui.Text("Start Time:???\nTime elapsed:???")]
    ]

    tab_selector = [
        [gui.Button("Events"), gui.Button("Files")]
    ]

    confirm_row = [
        [gui.Button('Ok'), gui.Button('Cancel'), gui.Button("Append"), gui.Button("Print"), gui.Button("Update")]
    ]

    layout = [
        # top_row,
        # tab_selector,
        [gui.Table(values=testlist,
                   headings=testlist_headings,
                   max_col_width=100,
                   auto_size_columns=True,
                   display_row_numbers=False,
                   justification="right",
                   num_rows=10,
                   key="-TABLE-",
                   row_height=35)],
        
        [gui.Button('Ok'), gui.Button('Cancel'), gui.Button("Append"), gui.Button("Print"), gui.Button("Update")]
        
    ]

    window = gui.Window("Window Title", layout)
    while True:
        event, values = window.read()
        if event == gui.WIN_CLOSED or event == "Cancel":
            break
        if event == "Append":
            appendToList(window, testlist)
            print("Appending...")
        
        # if event == "Update":
        #     event_thread = threading.Thread(target=updateTable, args=(window, testlist, testlist_headings))
        #     event_thread.start()

        # DEBUGGING
        # if event == "Print":
        #     print(testlist)


    window.close()

if __name__ == "__main__":
    main()