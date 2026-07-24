import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Combobox, Notebook

import ion_stitch

class Index:
    def __init__(self):
        self.i = {}
        self.index_tracker = 0

    def add(self, id):
        self.i[id] = self.index_tracker
        self.index_tracker += 1


class Ctr:
    def __init__(self):
        self.ctr = 0

    def count(self):
        cur_ctr = self.ctr
        self.ctr += 1
        return cur_ctr

    def reset(self):
        self.ctr = 0


CMD_INDEX = Index()
CMD_INDEX.add("-mf top")
CMD_INDEX.add("-mf up")
CMD_INDEX.add("-mf down")
CMD_INDEX.add("-mf bottom")
CMD_INDEX.add("-af new")
CMD_INDEX.add("-af upd")
CMD_INDEX.add("-rf")
CMD_INDEX.add("-mg top")
CMD_INDEX.add("-mg up")
CMD_INDEX.add("-mg down")
CMD_INDEX.add("-mg bottom")
CMD_INDEX.add("-ag new")
CMD_INDEX.add("-ag upd")
CMD_INDEX.add("-rg")
CMD_INDEX.add("-Review")
CMD_INDEX.add("-Export")

MEDIA_DIR = "assets/"
PRIO_LARGE = "Larger"
PRIO_SMALL = "Smaller"
VAL_SINGLE = "Single"
VAL_AVERAGE = "Average"

LB_H = 12


def get_mode_mtb(ion_modes, mode_index, mtb_index, target_name):
    if mode_index < 0 or mode_index >= len(ion_modes):
        return None, mtb_index, False
    if mtb_index < 0 or mtb_index >= len(ion_modes[mode_index].mtb):
        return None, mtb_index, False

    mtb = ion_modes[mode_index].mtb[mtb_index]
    if mtb.name == target_name:
        return mtb, mtb_index + 1, True

    return None, mtb_index, False


class M_Frame:
    def __init__(self, parent, name, r=0, c=0):
        self.name = name
        self.frame = tk.Frame(parent, borderwidth=1)
        self.children = {}
        self.label = {}
        self.btn = {}
        self.radio = {}
        self.entry = {}
        self.lb = {}
        self.sb = {}

    def add_child(self, name):
        self.children[name] = M_Frame(self.frame, name)
        return self.children[name]

    def add_label(self, id, label_text):
        self.label[id] = tk.Label(self.frame, text=label_text)

    def add_btn(self, id, btn_text, cmd):
        self.btn[id] = tk.Button(self.frame, text=btn_text, command=cmd)

    def add_entry(self, id, entry_text):
        self.entry[id] = tk.Entry(self.frame, textvariable=tk.StringVar())

    def add_lb(self, id):
        self.lb[id] = tk.Listbox(self.frame)


def get_m_frame(cur_m_frame, q_key):
    if cur_m_frame.name == q_key:
        return cur_m_frame

    for key in cur_m_frame.children:
        ret_m_frame = get_m_frame(cur_m_frame.children[key], q_key)
        if ret_m_frame is None:
            continue
        else:
            return ret_m_frame


GRID_COL = Index()
GRID_COL.add("lock")
GRID_COL.add("swap")
GRID_COL.add("detected")
GRID_COL.add("selected")
GRID_COL.add("name")
GRID_COL.add("filters")


class ReviewWindow(tk.Toplevel):
    def __init__(self, parent, ion_modes):
        super().__init__(parent)
        self.title = "Review"
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry("%dx%d" % (width, height))
        self.resizable(True, True)
        self.ion_modes = ion_modes
        self.locked_img = load_img(MEDIA_DIR + "locked.png")
        self.unlocked_img = load_img(MEDIA_DIR + "unlocked.png")

        self.name_col_w = 40
        self.filter_w = 20

        conf = ion_stitch.Conf()
        conf.load_conf(ion_stitch.CONF_FILE)
        self.final_col_range = conf.final_col_range

        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Export", command=self.stitch_final)

        self.row_canvas = tk.Canvas(self)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.row_canvas.grid(sticky="nwse")
        self.rows = tk.Frame(self.row_canvas, bg="gray20")

        self.row_canvas.bind(
            "<Configure>",
            lambda e: self.row_canvas.configure(
                scrollregion=self.row_canvas.bbox("all")
            ),
        )
        self.row_canvas.create_window((0, 0), window=self.rows, anchor="nw")

        self.v_scrollbar = tk.Scrollbar(self)
        self.v_scrollbar.config(command=self.yview)
        self.h_scrollbar = tk.Scrollbar(self)
        self.h_scrollbar.config(orient=tk.HORIZONTAL, command=self.xview)
        self.v_scrollbar.grid(sticky="nwse", row=0, column=1)
        self.h_scrollbar.grid(sticky="nwse", row=2, column=0)
        self.row_canvas.config(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set,
            bg="gray70",
        )

        self.row_frame = {}
        self.row_compound_name = {}
        self.row_filter_frame = {}
        self.row_filter = {}
        self.header_label = {}
        r_ctr = Ctr()
        c_ctr = Ctr()

        self.header_lock = tk.Label(self.rows, text="")
        self.header_ion = tk.Label(self.rows, text="Ion Mode")
        self.header_name = tk.Label(self.rows, text="Compound Names")
        self.header_lock.grid(row=r_ctr.ctr, column=c_ctr.count(), sticky="nsew")
        self.header_ion.grid(row=r_ctr.ctr, column=c_ctr.count(), sticky="nsew")
        self.header_name.grid(row=r_ctr.ctr, column=c_ctr.count(), sticky="nsew")

        for r in range(0, conf.num_id_filters):
            id = conf.get_id_filter(r).id
            for mode in range(0, 2):
                self.header_label[id + str(mode)] = tk.Label(self.rows, text=id)
                self.header_label[id + str(mode)].config(
                    width=self.filter_w, bg=("gray" + str(90 - 10 * mode))
                )
                self.header_label[id + str(mode)].grid(
                    row=r_ctr.ctr, column=c_ctr.count(), sticky="nsew"
                )
        mtb_ctr = [0, 0]
        r_ctr.count()
        self.lock = {}
        self.lockvar = {}
        self.mode_sel = {}
        self.modevar = {}
        self.filter_pair_frame = {}
        for r in range(0, self.ion_modes[2].num_mtbs):
            cur_mtb = self.ion_modes[2].mtb[r]
            c_ctr.reset()

            self.modevar[r] = tk.StringVar(self.rows)
            self.lockvar[r] = False
            self.lock[r] = tk.Button(
                self.rows, text="L", command=lambda r=r: self.lock_toggle(index=r)
            )
            self.lock[r].grid(row=r_ctr.ctr, column=c_ctr.count(), sticky="nsew")
            set_btn_img(self.lock[r], self.locked_img)
            self.mode_sel[r] = Combobox(
                self.rows, textvariable=self.modevar[r], width=10
            )
            self.mode_sel[r].grid(row=r_ctr.ctr, column=c_ctr.count(), sticky="nsew")
            if self.ion_modes[2].mtb[r].selected_mode == "P":
                self.modevar[r].set("Positive")
                self.mode_sel[r]["values"] = ("Positive", "Negative*", "Exclude*")
            elif self.ion_modes[2].mtb[r].selected_mode == "N":
                self.modevar[r].set("Negative")
                self.mode_sel[r]["values"] = ("Positive*", "Negative", "Exclude*")
            elif (self.ion_modes[2].mtb[r].name in conf.exclusions):
                self.modevar[r].set("Exclude*")
            self.mode_sel[r].config(state=tk.DISABLED)
            self.mode_sel[r].bind(
                "<<ComboboxSelected>>", lambda event, r=r: self.swap_ion_mode(index=r)
            )

            row_color = "gray80"
            if r % 2 == 0:
                row_color = "gray90"
            self.row_compound_name[r] = tk.Label(self.rows, text=cur_mtb.name)
            self.row_compound_name[r].config(
                relief="raised",
                borderwidth=1,
                width=self.name_col_w,
                anchor="w",
                bg=row_color,
            )
            self.row_compound_name[r].grid(
                row=r_ctr.ctr, column=c_ctr.count(), sticky="nsew"
            )

            mode_has_mtb = [False, False]
            for mode in range(0, 2):
                mtb_mode, next_index, matched = get_mode_mtb(
                    self.ion_modes,
                    mode,
                    mtb_ctr[mode],
                    self.ion_modes[-1].mtb[r].name,
                )
                if matched:
                    mode_has_mtb[mode] = True
                    mtb_ctr[mode] = next_index
                for i in range(0, conf.num_id_filters):
                    id = conf.get_id_filter(i).id
                    uid = id + str(mode) + str(r)
                    self.row_filter[uid] = tk.Label(self.rows, text="")
                    if mode_has_mtb[mode] and mtb_mode is not None:
                        scientific = mtb_mode.summary_data[id]
                        if mtb_mode.summary_data[id] > 10000:
                            scientific = "{:0.3e}".format(scientific)
                        self.row_filter[uid].config(text=scientific)
                    self.row_filter[uid].config(
                        width=self.filter_w,
                        bg=row_color,
                        relief="sunken",
                        borderwidth=1,
                    )
                    self.row_filter[uid].grid(
                        row=r_ctr.ctr, column=c_ctr.ctr + (i * 2) + mode, sticky="nwse"
                    )

            r_ctr.ctr += 1

        self.final_col_range_frame = tk.Frame(self, relief="sunken", padx=20)
        self.config(bg="gray90")
        self.title_frame = tk.Frame(self.final_col_range_frame)
        self.title = tk.Label(self.title_frame, text="Data Table Column Range", pady=10)

        self.col_frame = tk.Frame(self.final_col_range_frame, pady=10)
        self.col_min = tk.Entry(self.col_frame, width=10)
        self.col_min.delete(0, tk.END)
        self.col_min.insert(0, self.final_col_range[0])
        self.col_range_fill = tk.Label(self.col_frame, text=":")
        self.col_max = tk.Entry(self.col_frame, width=10)
        self.col_max.delete(0, tk.END)
        self.col_max.insert(0, self.final_col_range[1])

        self.btn_frame = tk.Frame(self.final_col_range_frame)
        self.export = tk.Button(
            self.btn_frame, text="Export", command=self.stitch_final
        )

        self.col_min.bind("<Key>", self.col_min_typing)
        self.col_min.bind(
            "<KeyRelease>", self.col_min_typing
        )
        self.col_max.bind("<Key>", self.col_max_typing)
        self.col_max.bind(
            "<KeyRelease>", self.col_max_typing
        )

        self.final_col_range_frame.grid(row=0, column=2, sticky="nw")
        self.title_frame.grid(row=0, column=0, sticky="nw")
        self.title.grid(sticky="nw")
        self.col_frame.grid(row=1, column=0, sticky="nw")
        self.btn_frame.grid(row=2, column=0, sticky="e")
        self.col_min.grid(row=0, column=0, sticky="nw")
        self.col_range_fill.grid(row=0, column=1, padx=15, sticky="nw")
        self.col_max.grid(row=0, column=2, sticky="nw")
        self.export.grid(pady=20, padx=20)

        self.bind_all("<MouseWheel>", self.mouse_scroll)
        self.rows.bind("<Configure>", self.update_row_scroll_region)
        # self.row_canvas.bind_all("<<Button-4>>", self.mouse_scroll)	MACOS
        # self.row_canvas.bind_all("<<Button-5>>", self.mouse_scroll)	MACOS

    def button_pressed(self):
        self.destroy()

    def yview(self, *args):
        self.row_canvas.yview(*args)

    def xview(self, *args):
        self.row_canvas.xview(*args)

    def update_row_scroll_region(self, event):
        self.row_canvas.configure(scrollregion=self.row_canvas.bbox("all"))

    def mouse_scroll(self, event):
        delta = event.delta if event.delta != 0 else -event.num * 40
        self.row_canvas.yview_scroll(int(-delta / 120), "units")

    def lock_toggle(self, index=0, event=None):
        if self.lockvar[index] == True:
            set_btn_img(self.lock[index], self.locked_img)
            self.lockvar[index] = False
            self.mode_sel[index].config(state=tk.DISABLED)
        else:
            set_btn_img(self.lock[index], self.unlocked_img)
            self.lockvar[index] = True
            self.mode_sel[index].config(state="readonly")

    def swap_ion_mode(self, index=0, event=None):
        cmd = []
        cmd.append("--include")
        cmd.append(self.ion_modes[2].mtb[index].name)
        if (self.modevar[index].get() == "Positive"):
            self.ion_modes[2].mtb[index].selected_mode = "P"
        elif (self.modevar[index].get() == "Negative"):
            self.ion_modes[2].mtb[index].selected_mode = "N"
        else:
            cmd[0] = "--exclude"

        ion_stitch.main(cmd)
        print(cmd)

    def col_min_typing(self, event=None):
        self.final_col_range[0] = self.col_min.get()

    def col_max_typing(self, event=None):
        self.final_col_range[1] = self.col_max.get()

    def stitch_final(self):
        cmd = []
        cmd.append("--final_col_range")
        cmd.append(self.final_col_range[0])
        cmd.append(self.final_col_range[1])
        cmd.append("-E")
        stitch_filename = save_as()
        if stitch_filename == "":
            return
        cmd.append(stitch_filename)

        try:
            ion_stitch.main(cmd, ion_modes=self.ion_modes)
            event_text = "Success!"
        except:
            event_text = "Error: ensure Data Table Column Range is within bounds."

        event_window = EventWindow(self, event_text, "OK")
        event_window.mainloop()


class EventWindow(tk.Toplevel):
    def __init__(self, parent, label_text, button_text):
        super().__init__(parent)
        self.title("")

        self.success_text = tk.Label(self, text=label_text, padx=10, pady=10)
        self.ok_button = tk.Button(
            self, text=button_text, width=10, command=self.button_pressed
        )

        self.success_text.pack(side=tk.TOP, pady=10)
        self.ok_button.pack(side=tk.TOP, pady=10)

    def button_pressed(self):
        self.destroy()


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # master.geometry("800x800")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.grid()

        self.cur_id = ""
        self.cur_id_i = 0
        self.m_frame = M_Frame(self, "root")
        self.m_frame.frame.configure(bg="#DDDDDD")
        self.old_conf = ion_stitch.Conf()
        self.old_conf.load_conf(ion_stitch.CONF_FILE)

        self.file_load_img = load_img(MEDIA_DIR + "file_load_icon.png")
        self.arrow_top_img = load_img(MEDIA_DIR + "arrow_top.png")
        self.arrow_up_img = load_img(MEDIA_DIR + "arrow_up.png")
        self.arrow_down_img = load_img(MEDIA_DIR + "arrow_down.png")
        self.arrow_btm_img = load_img(MEDIA_DIR + "arrow_btm.png")

        self.File_Load_Frame__init__()

        self.Tabbing_Frame__init__()

        self.Tabbing_Frame__filter_tab_init__()
        self.Tabbing_Frame__grid_frames__()
        self.Tabbing_Frame__add_elements__()
        self.Tabbing_Frame__grid_elements__()

        self.Tabbing_Frame__group_tab_init__()
        self.Tabbing_Frame__group_grid_frames__()
        self.Tabbing_Frame__group_add_elements__()
        self.Tabbing_Frame__group_grid_elements__()

        self.Tooltip__init__()

        self.gridify()
        self.bindify()

    # BEGIN///////////////////////////////////////////////////////////////////
    # FILE LOAD//////////////////////////////////////////////////////////////
    def File_Load_Frame__init__(self):
        self.fl_frame = self.m_frame.add_child("load frame")
        self.fl_frame.frame.columnconfigure(0, weight=1)

        self.File_Load__add_elements__(self.fl_frame)

    def File_Load__add_elements__(self, parent):
        entry_w = 65
        pos_id = "load child pos"
        self.pos_load = parent.add_child(pos_id)
        self.pos_load.add_label(pos_id, "Positive Ion Mode File:")
        self.pos_load.add_entry(pos_id, "Select a file")
        self.pos_load.entry[pos_id].insert(0, self.old_conf.pos)
        self.pos_load.add_btn(
            pos_id, "Load", lambda: self.browse_files(self.pos_load.entry[pos_id], 0)
        )
        set_btn_img(self.pos_load.btn[pos_id], self.file_load_img)
        self.pos_load.entry[pos_id].config(width=entry_w)

        neg_id = "load child neg"
        self.neg_load = parent.add_child(neg_id)
        self.neg_load.add_label(neg_id, "Negative Ion Mode File:")
        self.neg_load.add_entry(neg_id, "Select a file")
        self.neg_load.entry[neg_id].insert(0, self.old_conf.neg)
        self.neg_load.add_btn(
            neg_id, "Load", lambda: self.browse_files(self.neg_load.entry[neg_id], 1)
        )
        set_btn_img(self.neg_load.btn[neg_id], self.file_load_img)
        self.neg_load.entry[neg_id].config(width=entry_w)

    def File_Load__grid_elements__(self):
        pos_id = "load child pos"
        self.pos_load.label[pos_id].grid(row=0, column=0, sticky='w')
        self.pos_load.entry[pos_id].grid(row=1, column=0)
        self.pos_load.btn[pos_id].grid(row=1, column=1)

        neg_id = "load child neg"
        self.neg_load.label[neg_id].grid(row=0, column=0, sticky='w')
        self.neg_load.entry[neg_id].grid(row=1, column=0)
        self.neg_load.btn[neg_id].grid(row=1, column=1)

    # BEGIN///////////////////////////////////////////////////////////////////
    # TABBING FRAME//////////////////////////////////////////////////////////
    def Tabbing_Frame__init__(self):
        self.tab_frame = self.m_frame.add_child("tabbing frame")
        self.tab_frame.frame.columnconfigure(0, weight=1)
        self.tab_frame.frame.config(relief="groove")
        self.tabbing_nb = Notebook(self.tab_frame.frame)
        self.option_btns = self.tab_frame.add_child("filter opt btns")

    # BEGIN///////////////////////////////////////////////////////////////////
    # FILTER TAB/////////////////////////////////////////////////////////////
    def Tabbing_Frame__filter_tab_init__(self):
        self.filter_tab = M_Frame(self.tabbing_nb, "filter tab")
        self.filter_headers = self.filter_tab.add_child("filter headers")
        self.filter_lb_btns = self.filter_tab.add_child("filter lb btns")
        self.filter_tab_lb = self.filter_tab.add_child("filter lb")
        self.filter_options = self.filter_tab.add_child("filter opt")
        self.filter_range = self.filter_tab.add_child("filter range")

    def Tabbing_Frame__add_elements__(self):
        self.filter_headers.add_label("List", "Filter List")

        self.filter_lb_btns.btn["Top"] = tk.Button(
            self.filter_lb_btns.frame,
            text="T",
            command=lambda: self.filter_btn(CMD_INDEX.i["-mf top"]),
        )
        self.filter_lb_btns.btn["Up"] = tk.Button(
            self.filter_lb_btns.frame,
            text="U",
            command=lambda: self.filter_btn(CMD_INDEX.i["-mf up"]),
        )
        self.filter_lb_btns.btn["Down"] = tk.Button(
            self.filter_lb_btns.frame,
            text="D",
            command=lambda: self.filter_btn(CMD_INDEX.i["-mf down"]),
        )
        self.filter_lb_btns.btn["Btm"] = tk.Button(
            self.filter_lb_btns.frame,
            text="B",
            command=lambda: self.filter_btn(CMD_INDEX.i["-mf bottom"]),
        )
        set_btn_img(self.filter_lb_btns.btn["Top"], self.arrow_top_img)
        set_btn_img(self.filter_lb_btns.btn["Up"], self.arrow_up_img)
        set_btn_img(self.filter_lb_btns.btn["Down"], self.arrow_down_img)
        set_btn_img(self.filter_lb_btns.btn["Btm"], self.arrow_btm_img)

        id_list = []
        for i in range(0, self.old_conf.num_id_filters):
            id = self.old_conf.get_id_filter(i).id
            id_list.append(id)
        list_items = tk.Variable(value=id_list)
        self.filter_tab_lb.lb["List"] = tk.Listbox(
            self.filter_tab_lb.frame,
            listvariable=list_items,
            selectmode=tk.SINGLE,
            height=LB_H,
        )

        self.option_btns.btn["Add"] = tk.Button(
            self.option_btns.frame,
            text="Add",
            command=lambda: self.filter_btn(CMD_INDEX.i["-af new"]),
        )
        self.option_btns.btn["Upd"] = tk.Button(
            self.option_btns.frame,
            text="Update",
            command=lambda: self.filter_btn(CMD_INDEX.i["-af upd"]),
        )
        self.option_btns.btn["Del"] = tk.Button(
            self.option_btns.frame,
            text="Delete",
            command=lambda: self.filter_btn(CMD_INDEX.i["-rf"]),
        )
        self.option_btns.btn["Add"].config(state=tk.DISABLED)
        self.option_btns.btn["Upd"].config(state=tk.DISABLED)
        self.option_btns.btn["Del"].config(state=tk.DISABLED)
        for key in self.option_btns.btn:
            self.option_btns.btn[key].config(width=10)

        self.filter_options.add_label("Filter Name", "Name:")
        self.filter_options.add_label("Filter Type", "Filter Type:")
        self.filter_options.add_entry("Filter Name", "Filter Name")

        self.filter_options.add_label("Value Type", "Value Type:")
        self.dd_valuetype = tk.StringVar()
        self.dd_valuetype.set("--type--")
        self.filter_options.dd_value = Combobox(
            self.filter_options.frame, textvariable=self.dd_valuetype, width=10
        )
        self.filter_options.dd_value["values"] = (VAL_SINGLE, VAL_AVERAGE)
        self.filter_options.dd_value.config(state="readonly")

        self.filter_options.add_label("Priority", "Priority:")
        self.dd_priotype = tk.StringVar()
        self.dd_priotype.set("--priority--")
        self.filter_options.dd_prio = Combobox(
            self.filter_options.frame, textvariable=self.dd_priotype, width=10
        )
        self.filter_options.dd_prio["values"] = (PRIO_LARGE, PRIO_SMALL)
        self.filter_options.dd_prio.config(state="readonly")

        self.filter_range.add_label("Column Name", "Column Name:")
        self.filter_range.add_entry("Column Name", "Column Name")
        self.filter_range.entry["Column Name"].config(width=50)
        self.filter_range.fill = tk.Frame(self.filter_range.frame, height=10)
        self.filter_range.add_label("Column Range", "Column Range:")
        self.filter_range.add_label("Column Range Min", "min")
        self.filter_range.add_entry("Column Range Min", "Column Range Min")
        self.filter_range.entry["Column Range Min"].config(width=10)
        self.filter_range.add_label("Column Range Break", ":")
        self.filter_range.label["Column Range Break"]
        self.filter_range.add_entry("Column Range Max", "Column Range Max")
        self.filter_range.entry["Column Range Max"].config(width=10)
        self.tabbing_nb.add(self.filter_tab.frame, text="Filters")

    def Tabbing_Frame__grid_frames__(self):
        self.filter_tab.frame.grid()
        self.filter_headers.frame.grid(row=0, column=1, sticky="n")
        self.filter_lb_btns.frame.grid(row=1, column=0, rowspan=3, sticky="n")
        self.filter_tab_lb.frame.grid(row=1, column=1, rowspan=4, sticky="n")
        self.filter_options.frame.grid(
            row=1, column=2, columnspan=1, padx=10, rowspan=2, sticky="nw"
        )
        self.filter_range.frame.grid(
            row=3, column=2, columnspan=1, padx=10, sticky="nw"
        )

    def Tabbing_Frame__grid_elements__(self):
        btn_ctr = 0
        for key in self.filter_lb_btns.btn:
            self.filter_lb_btns.btn[key].grid(row=btn_ctr, sticky="nswe")
            btn_ctr += 1
        self.filter_headers.label["List"].grid(row=0, column=0)

        self.filter_tab_lb.lb["List"].grid(row=1, column=0, sticky="nswe")

        self.filter_options.label["Filter Name"].grid(
            row=1, column=0, pady=5, sticky="w"
        )
        self.filter_options.entry["Filter Name"].grid(
            row=1, column=1, rowspan=1, sticky="e"
        )
        self.filter_options.label["Value Type"].grid(
            row=2, column=0, pady=5, sticky="w"
        )
        self.filter_options.label["Priority"].grid(row=3, column=0, pady=5, sticky="w")
        self.filter_options.dd_value.grid(row=2, column=1, sticky="e")
        self.filter_options.dd_prio.grid(row=3, column=1, sticky="e")

        self.filter_range.label["Column Name"].grid(
            row=0, column=0, columnspan=10, sticky="w"
        )
        self.filter_range.entry["Column Name"].grid(
            row=1, column=0, columnspan=10, sticky="w"
        )
        self.filter_range.fill.grid(row=2)
        self.filter_range.label["Column Range"].grid(
            row=3, column=0, columnspan=10, sticky="w"
        )
        self.filter_range.entry["Column Range Min"].grid(row=4, column=0, sticky="w")
        self.filter_range.label["Column Range Break"].grid(row=4, column=1, sticky="w")
        self.filter_range.entry["Column Range Max"].grid(row=4, column=2, sticky="w")

        self.option_btns.btn["Add"].grid(row=0, column=1, sticky="e")
        self.option_btns.btn["Upd"].grid(row=0, column=2)
        self.option_btns.btn["Del"].grid(row=0, column=3, sticky="e")

    # BEGIN///////////////////////////////////////////////////////////////////
    # GROUP TAB//////////////////////////////////////////////////////////////
    def Tabbing_Frame__group_tab_init__(self):
        self.group_tab = M_Frame(self.tabbing_nb, "group tab")
        self.group_tab_header = self.group_tab.add_child("header")
        self.group_lb_btns = self.group_tab.add_child("group lb btns")
        self.group_lb = self.group_tab.add_child("group lb")
        self.group_options = self.group_tab.add_child("group options")

    def Tabbing_Frame__group_add_elements__(self):
        self.group_tab_header.add_label("List", "Group List")
        self.group_lb_btns.btn["Top"] = tk.Button(
            self.group_lb_btns.frame,
            text="T",
            command=lambda: self.group_btn(CMD_INDEX.i["-mg top"]),
        )
        self.group_lb_btns.btn["Up"] = tk.Button(
            self.group_lb_btns.frame,
            text="U",
            command=lambda: self.group_btn(CMD_INDEX.i["-mg up"]),
        )
        self.group_lb_btns.btn["Down"] = tk.Button(
            self.group_lb_btns.frame,
            text="D",
            command=lambda: self.group_btn(CMD_INDEX.i["-mg down"]),
        )
        self.group_lb_btns.btn["Btm"] = tk.Button(
            self.group_lb_btns.frame,
            text="B",
            command=lambda: self.group_btn(CMD_INDEX.i["-mg bottom"]),
        )
        set_btn_img(self.group_lb_btns.btn["Top"], self.arrow_top_img)
        set_btn_img(self.group_lb_btns.btn["Up"], self.arrow_up_img)
        set_btn_img(self.group_lb_btns.btn["Down"], self.arrow_down_img)
        set_btn_img(self.group_lb_btns.btn["Btm"], self.arrow_btm_img)

        id_list = []
        for key in self.old_conf.group:
            id_list.append(key)
        list_items = tk.Variable(value=id_list)
        self.group_lb.lb["List"] = tk.Listbox(
            self.group_lb.frame,
            listvariable=list_items,
            selectmode=tk.SINGLE,
            height=LB_H,
        )

        self.tabbing_nb.add(self.group_tab.frame, text="Groups")

        self.group_options.add_label("Group Name", "Name:")
        self.group_options.add_entry("Group Name", "Name")
        self.group_options.add_label("Group Size", "Group Size:")
        self.group_options.sb["sb"] = tk.Spinbox(
            self.group_options.frame,
            from_=0,
            width=5,
            relief="sunken",
            repeatdelay=500,
            repeatinterval=100,
        )

    def Tabbing_Frame__group_grid_frames__(self):
        self.group_tab.frame.grid()
        self.group_tab_header.frame.grid(column=1)
        self.group_lb_btns.frame.grid(row=1, column=0, rowspan=3, sticky="n")
        self.group_lb.frame.grid(row=1, column=1, rowspan=4, sticky="n")
        self.group_options.frame.grid(
            row=1, column=2, columnspan=1, padx=10, rowspan=2, sticky="nw"
        )

    def Tabbing_Frame__group_grid_elements__(self):
        self.group_tab_header.label["List"].grid()
        btn_ctr = 0
        for key in self.group_lb_btns.btn:
            self.group_lb_btns.btn[key].grid(row=btn_ctr, sticky="nswe")
            btn_ctr += 1
        self.group_tab_header.label["List"].grid(row=0, column=1)
        self.group_lb.lb["List"].grid()

        self.group_options.label["Group Name"].grid(row=1, column=0, pady=5, sticky="w")
        self.group_options.entry["Group Name"].grid(
            row=1, column=1, rowspan=1, sticky="e"
        )
        self.group_options.label["Group Size"].grid(row=2, column=0, pady=5, sticky="w")
        self.group_options.sb["sb"].grid(row=2, column=1, pady=5, sticky="e")

    # BEGIN///////////////////////////////////////////////////////////////////
    # TOOLTIP AND STITCH/////////////////////////////////////////////////////
    def Tooltip__init__(self):
        self.tooltip_and_stitch = self.m_frame.add_child("tooltip and stitch frame")
        self.tooltip_and_stitch.frame.config(width=50, bg="#DDDDDD")
        self.Tooltip__add_elements__()

    def Tooltip__add_elements__(self):
        self.tooltip_and_stitch.add_label("Tooltip", "Tooltip:")
        self.tooltip_and_stitch.label["Tooltip"].config()
        self.tooltip_and_stitch.add_btn(
            "Stitch", "Stitch", lambda: self.begin_stitching()
        )
        self.tooltip_and_stitch.btn["Stitch"].config(width=15)
        self.tooltip_and_stitch.add_btn("Exit", "Exit", quit)
        self.tooltip_and_stitch.btn["Exit"].config(width=15)

    def Tooltip__grid_elements__(self):
        # self.tooltip_and_stitch.label["Tooltip"].grid(row=0, column=0,sticky="nw")
        self.tooltip_and_stitch.btn["Stitch"].grid(row=0, column=0, padx=45, sticky="w")
        self.tooltip_and_stitch.btn["Exit"].grid(row=0, column=1, padx=45, sticky="e")

    # BEGIN///////////////////////////////////////////////////////////////////
    # FINAL TOUCHES//////////////////////////////////////////////////////////
    def bindify(self):
        self.filter_tab_lb.lb["List"].bind(
            "<<ListboxSelect>>", self.handle_filter_id_select
        )
        self.filter_options.entry["Filter Name"].bind(
            "<Key>", self.filter_name_entry_keyboard_event
        )
        self.filter_options.entry["Filter Name"].bind(
            "<KeyRelease>", self.filter_name_entry_keyboard_event
        )
        self.filter_options.dd_value.bind(
            "<<ComboboxSelected>>", self.handle_column_name_range
        )
        self.group_lb.lb["List"].bind("<<ListboxSelect>>", self.handle_group_id_select)
        self.group_options.entry["Group Name"].bind(
            "<Key>", self.group_name_entry_keyboard_event
        )
        self.group_options.entry["Group Name"].bind(
            "<KeyRelease>", self.group_name_entry_keyboard_event
        )
        self.tabbing_nb.bind("<<NotebookTabChanged>>", self.tab_select)

    def tab_select(self, event):
        for btn in self.option_btns.btn:
            self.option_btns.btn[btn].config(state=tk.DISABLED)
        notebook = event.widget
        tab_id = notebook.select()
        tab_text = notebook.tab(tab_id, "text")
        if tab_text == "Groups":
            self.option_btns.btn["Add"].config(
                command=lambda: self.group_btn(CMD_INDEX.i["-ag new"])
            )
            self.option_btns.btn["Upd"].config(
                command=lambda: self.group_btn(CMD_INDEX.i["-ag upd"])
            )
            self.option_btns.btn["Del"].config(
                command=lambda: self.group_btn(CMD_INDEX.i["-rg"])
            )
        else:
            self.option_btns.btn["Add"].config(
                command=lambda: self.filter_btn(CMD_INDEX.i["-af new"])
            )
            self.option_btns.btn["Upd"].config(
                command=lambda: self.filter_btn(CMD_INDEX.i["-af upd"])
            )
            self.option_btns.btn["Del"].config(
                command=lambda: self.filter_btn(CMD_INDEX.i["-rf"])
            )

    def gridify(self):
        self.m_frame.frame.grid()

        self.pos_load.frame.grid(row=0, column=0, padx=10, pady=10)
        self.neg_load.frame.grid(row=1, column=0, padx=10, pady=20)

        self.fl_frame.frame.grid(row=2, column=0, sticky='nwse')
        self.File_Load__grid_elements__()

        self.tabbing_nb.grid()
        self.tab_frame.frame.grid(sticky="w")
        self.option_btns.frame.grid(row=3, column=0, pady=10, sticky="e")

        self.tooltip_and_stitch.frame.grid(row=4, column=0, pady=20)
        self.Tooltip__grid_elements__()

    # BEGIN///////////////////////////////////////////////////////////////////
    # EVENTS/////////////////////////////////////////////////////////////////
    def handle_filter_id_select(self, event):
        conf = ion_stitch.Conf()
        conf.load_conf(ion_stitch.CONF_FILE)

        try:
            self.cur_id = self.filter_tab_lb.lb["List"].get(
                self.filter_tab_lb.lb["List"].curselection()
            )
            self.cur_id_i = self.filter_tab_lb.lb["List"].index(
                self.filter_tab_lb.lb["List"].curselection()
            )
        except Exception as e:
            print(e)
            return

        self.option_btns.btn["Add"].config(state=tk.DISABLED)
        self.option_btns.btn["Upd"].config(state=tk.NORMAL)
        self.option_btns.btn["Del"].config(state=tk.NORMAL)

        self.dd_valuetype.set(VAL_SINGLE)
        if conf.get_id_filter(self.cur_id).match_type == ion_stitch.MATCH_AVERAGE:
            self.dd_valuetype.set(VAL_AVERAGE)

        self.dd_priotype.set(PRIO_LARGE)
        if conf.get_id_filter(self.cur_id).prio == ion_stitch.PRIO_SMALLER:
            self.dd_priotype.set(PRIO_SMALL)

        self.handle_column_name_range(None)
        self.filter_options.entry["Filter Name"].delete(0, tk.END)
        self.filter_options.entry["Filter Name"].insert(0, self.cur_id)
        self.filter_range.entry["Column Name"].delete(0, tk.END)
        self.filter_range.entry["Column Name"].insert(
            0, conf.get_id_filter(self.cur_id).filter_str
        )
        self.filter_range.entry["Column Range Min"].delete(0, tk.END)
        if len(conf.get_id_filter(self.cur_id).col_range) > 0:
            self.filter_range.entry["Column Range Min"].insert(
                0, conf.get_id_filter(self.cur_id).col_range[0]
            )
        self.filter_range.entry["Column Range Max"].delete(0, tk.END)
        if len(conf.get_id_filter(self.cur_id).col_range) > 1:
            self.filter_range.entry["Column Range Max"].insert(
                0, conf.get_id_filter(self.cur_id).col_range[1]
            )

    def handle_group_id_select(self, event):
        conf = ion_stitch.Conf()
        conf.load_conf(ion_stitch.CONF_FILE)

        try:
            self.cur_id = self.group_lb.lb["List"].get(
                self.group_lb.lb["List"].curselection()
            )
            self.cur_id_i = self.group_lb.lb["List"].index(
                self.group_lb.lb["List"].curselection()
            )
        except Exception:
            return

        self.option_btns.btn["Add"].config(state=tk.DISABLED)
        self.option_btns.btn["Upd"].config(state=tk.NORMAL)
        self.option_btns.btn["Del"].config(state=tk.NORMAL)

        self.handle_column_name_range(None)
        self.group_options.entry["Group Name"].delete(0, tk.END)
        self.group_options.entry["Group Name"].insert(0, self.cur_id)

        self.group_options.sb["sb"].delete(0, tk.END)
        self.group_options.sb["sb"].insert(0, conf.group[self.cur_id])

    def handle_column_name_range(self, event):
        conf = ion_stitch.Conf()
        conf.load_conf(ion_stitch.CONF_FILE)

        if self.dd_valuetype.get() == VAL_AVERAGE:
            self.filter_range.entry["Column Name"].delete(0, tk.END)
            self.filter_range.label["Column Name"].config(state=tk.DISABLED)
            self.filter_range.entry["Column Name"].config(state=tk.DISABLED)
            self.filter_range.label["Column Range"].config(state=tk.NORMAL)
            self.filter_range.entry["Column Range Min"].config(state=tk.NORMAL)
            self.filter_range.label["Column Range Break"].config(state=tk.NORMAL)
            self.filter_range.entry["Column Range Max"].config(state=tk.NORMAL)
            if conf.get_id_filter(self.cur_id) is not None:
                if (
                    conf.get_id_filter(self.cur_id).match_type
                    == ion_stitch.MATCH_AVERAGE
                ):
                    if len(conf.get_id_filter(self.cur_id).col_range) > 0:
                        self.filter_range.entry["Column Range Min"].insert(
                            0, conf.get_id_filter(self.cur_id).col_range[0]
                        )
                    if len(conf.get_id_filter(self.cur_id).col_range) > 1:
                        self.filter_range.entry["Column Range Max"].insert(
                            0, conf.get_id_filter(self.cur_id).col_range[1]
                        )
        else:
            self.filter_range.label["Column Name"].config(state=tk.NORMAL)
            self.filter_range.entry["Column Name"].config(state=tk.NORMAL)
            self.filter_range.label["Column Range"].config(state=tk.DISABLED)
            self.filter_range.entry["Column Range Min"].delete(0, tk.END)
            self.filter_range.entry["Column Range Min"].config(state=tk.DISABLED)
            self.filter_range.entry["Column Range Max"].delete(0, tk.END)
            self.filter_range.label["Column Range Break"].config(state=tk.DISABLED)
            self.filter_range.entry["Column Range Max"].config(state=tk.DISABLED)
            if conf.get_id_filter(self.cur_id) is not None:
                if (
                    conf.get_id_filter(self.cur_id).match_type
                    == ion_stitch.MATCH_SINGLE
                ):
                    self.filter_range.entry["Column Name"].insert(
                        0, conf.get_id_filter(self.cur_id).filter_str
                    )

    def filter_name_entry_keyboard_event(self, event):
        conf = ion_stitch.Conf()
        conf.load_conf(ion_stitch.CONF_FILE)

        self.option_btns.btn["Upd"].config(state=tk.DISABLED)
        self.option_btns.btn["Del"].config(state=tk.DISABLED)
        for i in range(0, conf.num_id_filters):
            id = conf.get_id_filter(i).id
            if self.filter_options.entry["Filter Name"].get() == id:
                self.option_btns.btn["Add"].config(state=tk.DISABLED)
                self.option_btns.btn["Upd"].config(state=tk.NORMAL)
                self.option_btns.btn["Del"].config(state=tk.NORMAL)
                return

        if len(self.filter_options.entry["Filter Name"].get()) > 0:
            self.option_btns.btn["Add"].config(state=tk.NORMAL)
        else:
            self.option_btns.btn["Add"].config(state=tk.DISABLED)

    def group_name_entry_keyboard_event(self, event):
        conf = ion_stitch.Conf()
        conf.load_conf(ion_stitch.CONF_FILE)

        self.option_btns.btn["Upd"].config(state=tk.DISABLED)
        self.option_btns.btn["Del"].config(state=tk.DISABLED)
        group_name = None
        for key in conf.group:
            if self.group_options.entry["Group Name"].get() == key:
                group_name = key

        if self.group_options.entry["Group Name"].get() == group_name:
            self.option_btns.btn["Add"].config(state=tk.DISABLED)
            self.option_btns.btn["Upd"].config(state=tk.NORMAL)
            self.option_btns.btn["Del"].config(state=tk.NORMAL)
        elif len(self.group_options.entry["Group Name"].get()) > 0:
            self.option_btns.btn["Add"].config(state=tk.NORMAL)
        else:
            self.option_btns.btn["Add"].config(state=tk.DISABLED)

    def browse_files(self, entry, mode):
        conf = ion_stitch.Conf()
        conf.load_conf(ion_stitch.CONF_FILE)

        cmd = "-pos"
        old_file = conf.pos
        if mode == 1:
            cmd = "-neg"
            old_file = conf.neg
        filename = filedialog.askopenfilename(
            initialdir=".",
            title="Select a File",
            filetypes=(("xlsx files", "*.xlsx*"), ("all files", "*.*")),
        )
        if filename != old_file:
            cmd += " " + filename
            ion_stitch.main(cmd)

        entry.delete(0, tk.END)
        entry.insert(0, filename)
        return

    def get_id_btn_cmd(self, i):
        cmd = []
        if (CMD_INDEX.i["-mf top"] <= i) and (CMD_INDEX.i["-mf bottom"] >= i):
            cmd.append("-mf")
            cmd.append(str(self.cur_id))
            if CMD_INDEX.i["-mf top"] == i:
                cmd.append(str(0))
            elif CMD_INDEX.i["-mf up"] == i:
                cmd.append(str(self.cur_id_i - 1))
            elif CMD_INDEX.i["-mf down"] == i:
                cmd.append(str(self.cur_id_i + 1))
            else:
                cmd.append(str(self.filter_tab_lb.lb["List"].size() + 1))

        elif CMD_INDEX.i["-af new"] == i or CMD_INDEX.i["-af upd"] == i:
            cmd.append("-af")
            new_id = self.cur_id
            if CMD_INDEX.i["-af new"] == i:
                new_id = get_first_word(self.filter_options.entry["Filter Name"].get())
            cmd.append(new_id)
            if self.dd_valuetype.get() == VAL_AVERAGE:
                if len(self.filter_range.entry["Column Range Min"].get()) > 0:
                    cmd.append(self.filter_range.entry["Column Range Min"].get())
                if len(self.filter_range.entry["Column Range Max"].get()) > 0:
                    cmd.append(self.filter_range.entry["Column Range Max"].get())
                cmd.append("--match_average")
            else:
                if len(self.filter_range.entry["Column Name"].get()) > 0:
                    cmd.append(self.filter_range.entry["Column Name"].get())
                cmd.append("--match_single")
            cmd.append(new_id)
            if self.dd_priotype.get() == PRIO_LARGE:
                cmd.append("--prio_large")
            elif self.dd_priotype.get() == PRIO_SMALL:
                cmd.append("--prio_small")
            cmd.append(new_id)

        elif CMD_INDEX.i["-rf"] == i:
            cmd.append("-rf")
            cmd.append(get_first_word(self.filter_options.entry["Filter Name"].get()))

        elif (CMD_INDEX.i["-mg top"] <= i) and (CMD_INDEX.i["-mg bottom"] >= i):
            cmd.append("-mg")
            cmd.append(str(self.cur_id))
            if CMD_INDEX.i["-mg top"] == i:
                cmd.append(str(0))
            elif CMD_INDEX.i["-mg up"] == i:
                cmd.append(str(self.cur_id_i - 1))
            elif CMD_INDEX.i["-mg down"] == i:
                cmd.append(str(self.cur_id_i + 1))
            else:
                cmd.append(str(self.group_lb.lb["List"].size() + 1))

        elif (CMD_INDEX.i["-ag new"] == i) or (CMD_INDEX.i["-ag upd"] == i):
            cmd.append("-ag")
            cmd.append(get_first_word(self.group_options.entry["Group Name"].get()))
            cmd.append(str(self.group_options.sb["sb"].get()))

        elif CMD_INDEX.i["-rg"] == i:
            cmd.append("-rg")
            cmd.append(get_first_word(self.group_options.entry["Group Name"].get()))

        elif CMD_INDEX.i["-Review"] == i:
            cmd.append("-R")

        elif CMD_INDEX.i["-Export"] == i:
            cmd.append("-E")
            cmd.append(save_as())

        print(cmd)
        return cmd

    def filter_btn(self, i):
        new_i = 0
        if i == CMD_INDEX.i["-mf top"]:
            ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-mf top"]))
        elif i == CMD_INDEX.i["-mf up"]:
            ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-mf up"]))
            if self.cur_id_i - 1 >= 0:
                new_i = self.cur_id_i - 1
        elif i == CMD_INDEX.i["-mf down"]:
            ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-mf down"]))
            new_i = self.cur_id_i + 1
            if new_i > self.filter_tab_lb.lb["List"].size() - 1:
                new_i = self.filter_tab_lb.lb["List"].size() - 1
        elif i == CMD_INDEX.i["-mf bottom"]:
            ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-mf bottom"]))
            new_i = self.filter_tab_lb.lb["List"].size() - 1
        elif i == CMD_INDEX.i["-af new"]:
            conf = ion_stitch.Conf()
            conf.load_conf(ion_stitch.CONF_FILE)
            ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-af new"]))
            new_i = conf.num_id_filters
        elif i == CMD_INDEX.i["-af upd"]:
            ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-af upd"]))
            new_i = self.cur_id_i
        elif i == CMD_INDEX.i["-rf"]:
            ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-rf"]))
        self.update_filter_lb(new_i)

    def update_filter_lb(self, new_i):
        conf = ion_stitch.Conf()
        conf.load_conf(ion_stitch.CONF_FILE)

        self.filter_tab_lb.lb["List"].delete(0, tk.END)
        for i in range(0, conf.num_id_filters):
            id = conf.get_id_filter(i).id
            self.filter_tab_lb.lb["List"].insert(tk.END, id)
        self.filter_tab_lb.lb["List"].selection_set(new_i, last=None)
        self.filter_tab_lb.lb["List"].activate(new_i)
        self.handle_filter_id_select(None)
        self.filter_range.entry["Column Name"].delete(0, tk.END)
        self.filter_range.entry["Column Name"].insert(
            0, conf.get_id_filter(self.cur_id).filter_str
        )
        self.filter_range.entry["Column Range Min"].delete(0, tk.END)
        if len(conf.get_id_filter(self.cur_id).col_range) > 0:
            self.filter_range.entry["Column Range Min"].insert(
                0, conf.get_id_filter(self.cur_id).col_range[0]
            )
        self.filter_range.entry["Column Range Max"].delete(0, tk.END)
        if len(conf.get_id_filter(self.cur_id).col_range) > 1:
            self.filter_range.entry["Column Range Max"].insert(
                0, conf.get_id_filter(self.cur_id).col_range[1]
            )

    def group_btn(self, i):
        new_i = 0
        if i == CMD_INDEX.i["-mg top"]:
            ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-mg top"]))
        elif i == CMD_INDEX.i["-mg up"]:
            ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-mg up"]))
        elif i == CMD_INDEX.i["-mg down"]:
            ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-mg down"]))
        elif i == CMD_INDEX.i["-mg bottom"]:
            ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-mg bottom"]))
        elif i == CMD_INDEX.i["-ag new"]:
            ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-ag new"]))
        elif i == CMD_INDEX.i["-ag upd"]:
            ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-ag upd"]))
        elif i == CMD_INDEX.i["-rg"]:
            ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-rg"]))
        self.update_group_lb(new_i)

    def update_group_lb(self, new_i):
        conf = ion_stitch.Conf()
        conf.load_conf(ion_stitch.CONF_FILE)

        self.group_lb.lb["List"].delete(0, tk.END)
        for key in conf.group:
            self.group_lb.lb["List"].insert(tk.END, key)
        self.group_lb.lb["List"].selection_set(new_i, last=None)
        self.group_lb.lb["List"].activate(new_i)
        self.handle_group_id_select(None)

    def begin_stitching(self):
        cmd = []
        cmd.append("-pos")
        cmd.append(self.pos_load.entry["load child pos"].get())
        cmd.append("-neg")
        cmd.append(self.neg_load.entry["load child neg"].get())
        ion_stitch.main(cmd)
        self.ion_modes = ion_stitch.main(self.get_id_btn_cmd(CMD_INDEX.i["-Review"]))
        self.update_filter_lb(self.filter_tab_lb.lb["List"].size() - 1)
        event = ReviewWindow(self, self.ion_modes)
        event.mainloop()

        return

    def end_program(self, event=None):
        self.destroy()
        self.quit()


def load_img(filename):
    img = None
    try:
        img = tk.PhotoImage(file=filename)
    except Exception as e:
        print(e)
    return img


def save_as():
    filename = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if filename is None:
        return  # open error dialog
    if ".xlsx" not in filename:
        filename += ".xlsx"
    return filename


def get_first_word(word):
    first_word = ""
    for c in word:
        if (c == " ") or (c == "\n"):
            break
        first_word += c
    return first_word


def set_btn_img(btn, img):
    if (btn is None) or (img is None):
        return
    btn.config(image=img)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    app.handle_column_name_range(None)

    app.master.title("Ion Mode Stitcher")
    app.mainloop()
