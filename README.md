# ION STITCH

Ion Stitch is a small program that can be run headless or with a GUI. It takes positive and negative ion mode excel sheets exported from Compound Discoverer and stitches them together based on user preference.

## Installation
Install Python
Open a terminal and type:
    ```pip install openpyxl```
    ```pip install tkinter```

Copy the files from github at https://github.com/potatolancer/ion-stitch
Enter the directory that you saved the files to.
To run the program type:
    ```py main.py```

## Usage - Headless
Use the Python file labeled ion_stitch.py in a shell and provide flags. Any number of flags can be provided in a single operation. If you are uncertain, run the ion_stitch.exe for a graphical experience instead.
```
-h                  | print the help screen
-R                  | (GUI) specific command, this tells Ion Stitch to return a stitched data set.
-E                  | Export an ion stitched dataset as an excel sheet with two pages. The first is a Summary Table and the second is metaboanalyst ready.
--final_col_range   | Takes the following two args (as column letters or numbers) and sets the column range that will be included in the dataset.
--exlude            | Adds an exclusion rule for a specific compound, ignoring it in the final export.
--include           | Deletes and exclusion rule for a specific compound.
-pos                | Takes next arg as filename of positive ion mode.
-neg                | Takes next arg as filename of negative ion mode.
-mf                 | Rearranges the order of a filter
-mg                 | Rearranges the order of a group
-rf                 | Removes every filter specified until another flag is detected.
-rg                 | Removes every group specified until another flag is detected.'
-af(s)(A)           | Adds a filter. The next arg is the filter id which appears in the summary sheet. If (A) is not provided then the following arg (ideally encapsulated with "") is the name of the column that filter will filter in. Otherwise it will take the next two args as the range of data to average.
-ag                 | Adds a group. The next arg is the group name. The arg after is the size of the group.
--prio_large        | Takes a filter id and sets it's data priority to the larger of the two for stitching comparison.
--prio_large        | Takes a filter id and sets it's data priority to the smaller of the two for stitching comparison.
--match_single      | Takes a filter id and sets it's data collection style to be an exact match of the column header you are interested in comparing.
--match_average     | Takes a filter id and sets it's data collection style to be an average every column between (inclusive) two column letters.
```

## Usage - GUI
The GUI just runs headless commands based on how it is interacted with.

1. Provide your positive ion mode file.
2. Provide your negative ion mode file.
3. Create a filter id name (single word only), specify how you want the filter to collect and compare data, and then add the filter id.
4. Do step 3 as many times as needed for the best comparison results.
5. (Optional) Create group names that will be included in the final data table excel sheet. This streamlines some time taken to add group names for metaboanlyst.
6. Click Stitch to review the potential excel data that you will be exporting. A new window will open.
7. In the review window you will be presented with all of your compounds stitched in order. Data is stitched from the ion modes based on the filters.
8. There are lock buttons that will unlock an additional option for each compound. Use with care.
9. The additional option allows you to switch which ion mode you would like the compound to include it's final data from. Or you can exclude that compound completely.
10. Enter a column range that you will be pulling all of your sample data from for the final stitch.
11. Hit export.

## Configuration File
Each command provided to Ion Stitch updates a configuration file in "./conf/conf.txt". If you did not want to use headless or GUI you could also manually edit the configuration file (not recommended). If you want to save a configuraion simply copy it as a backup with a different name. When you are ready to use that configuration again rename it to "conf.txt" and place in the correct directory.

___
## ion_stitch.py - codebase

### Classes

#### ID_Filter

    init(id, filter_str, prio, match_type) - Initialize filter with ID, filter string, priority, and match type  
    get_col_min() - Returns minimum column index  
    get_col_max() - Returns maximum column index  
    set_col_range() - Parses filter string to extract column range  

#### Conf

    __init__() - Initialize configuration, setup directories
    load_conf(file) - Load configuration from file  
    print_id_filters() - Print all ID filters
    buf_wordlist_from_line(readline) - Parse line into word list
    get_id_filter(i) - Get filter by index or ID
    get_file(ion_mode) - Get file path for ion mode
    get_final_col_range() - Get final column range
    rearrange_id_filter(id, new_i) - Reorder filter in list
    rearrange_group(group, new_i) - Reorder group in list
    remove_id_filter(id) - Remove filter by ID
    add_id_filter(id, wordlist, prio, match_type) - Add new filter
    add_group(groupname, size) - Add new group
    switch_prio(id) - Toggle priority for filter
    log(str, space, nl, pr) - Write to log file
    save() - Save configuration to file
    error(error_msg) - Log error message
    check_error() - Check for errors and terminate if needed
    read_args(argv) - Parse command-line arguments
    print_log() - Print log file contents

#### xl_data

    __init__(filename) - Initialize with filename
    load_xl(conf) - Load Excel workbook
    append_mtb(mtb) - Add metabolite to data
    log(conf) - Log metabolite data

#### Metabolite

    __init__(name, data) - Initialize with name and data
    check_against_summary_data(othr, conf) - Compare metabolite data against another
    autoset_data(header, conf) - Automatically populate summary and group data

#### Functions

    get_col_letters_as_i(col_letters) - Convert column letters to integer index
    get_i_as_col_letters(i) - Convert integer to column letters
    sort_by_lowercase(list) - Sort list case-insensitively
    stitch_modes(conf, mode_p, mode_n) - Merge positive and negative ion mode data
    final_stitch(conf, ion_modes) - Final stitching of all ion modes
    setup_dir(conf, dir) - Create directory if it doesn't exist
    count_dir_files(dir) - Count files in directory
    create_xl(mode_p, mode_n, mode_s, conf) - Create Excel output file with summary and data table
    print_help() - Print command-line help information
    main(argv, ion_modes) - Main entry point

## main.py - codebase

### Classes

#### Index

    __init__() - Initialize empty index
    add(id) - Add item to index

#### Ctr

    __init__() - Initialize counter to 0
    count() - Return and increment counter
    reset() - Reset counter to 0

#### M_Frame

    __init__(parent, name, r, c) - Initialize frame
    add_child(name) - Add child frame
    add_label(id, label_text) - Add label widget
    add_btn(id, btn_text, cmd) - Add button widget
    add_entry(id, entry_text) - Add entry widget
    add_lb(id) - Add listbox widget

#### ReviewWindow - Toplevel window for reviewing stitched data

    __init__(parent, ion_modes) - Initialize review window with ion mode data
    button_pressed() - Close window
    yview(*args) - Vertical scroll
    xview(*args) - Horizontal scroll
    update_row_scroll_region(event) - Update scroll region
    mouse_scroll(event) - Handle mouse wheel scrolling
    lock_toggle(index, event) - Toggle lock on row
    swap_ion_mode(index, event) - Change ion mode selection
    col_min_typing(event) - Update minimum column range
    col_max_typing(event) - Update maximum column range
    stitch_final() - Export final stitched data to Excel

    EventWindow - Simple popup event notification window
    __init__(parent, label_text, button_text) - Initialize event window
    button_pressed() - Close window

#### App - Main application

    __init__(master) - Initialize main application
    File_Load_Frame__init__() - Initialize file loading section
    File_Load__add_elements__(parent) - Add file load widgets
    File_Load__grid_elements__() - Grid layout file load widgets
    Tabbing_Frame__init__() - Initialize tabbed interface
    Tabbing_Frame__filter_tab_init__() - Initialize filter tab
    Tabbing_Frame__add_elements__() - Add filter tab elements
    Tabbing_Frame__grid_frames__() - Grid filter tab frames
    Tabbing_Frame__grid_elements__() - Grid filter tab elements
    Tabbing_Frame__group_tab_init__() - Initialize group tab
    Tabbing_Frame__group_add_elements__() - Add group tab elements
    Tabbing_Frame__group_grid_frames__() - Grid group tab frames
    Tabbing_Frame__group_grid_elements__() - Grid group tab elements
    Tooltip__init__() - Initialize tooltip section
    Tooltip__add_elements__() - Add tooltip elements
    Tooltip__grid_elements__() - Grid tooltip elements
    bindify() - Bind event handlers
    tab_select(event) - Handle tab selection
    gridify() - Apply grid layout to all elements
    handle_filter_id_select(event) - Handle filter selection
    handle_group_id_select(event) - Handle group selection
    handle_column_name_range(event) - Handle column range display toggle
    filter_name_entry_keyboard_event(event) - Update button states on filter name input
    group_name_entry_keyboard_event(event) - Update button states on group name input
    browse_files(entry, mode) - Open file browser dialog
    get_id_btn_cmd(i) - Generate command from UI state
    filter_btn(i) - Handle filter button clicks
    update_filter_lb(new_i) - Refresh filter listbox
    group_btn(i) - Handle group button clicks
    update_group_lb(new_i) - Refresh group listbox
    begin_stitching() - Start stitching process
    end_program(event) - Close application

#### Functions

    get_m_frame(cur_m_frame, q_key) - Recursively find frame by name
    load_img(filename) - Load image file for button icons
    save_as() - Open save file dialog
    get_first_word(word) - Extract first word from string
    set_btn_img(btn, img) - Set button image
