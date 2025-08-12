# app_tk.py
from __future__ import annotations

import os
import sys
import io
import threading
import traceback
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from typing import Optional, Callable, Any
import sqlite3

# Your modules
from modules import ai
from db.init_db import initialize_db
from seed.insert_dummy_data import insert_dummy_data

DB_PATH = os.path.join(os.path.dirname(__file__), "clinic.db")

# ================= THEME (Windows-safe fonts) =================
class ThemeManager:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.style = ttk.Style(root)
        try: self.style.theme_use("clam")
        except tk.TclError: pass

        try:
            self.default_font = tkfont.nametofont("TkDefaultFont")
            self.text_font = tkfont.nametofont("TkTextFont")
            self.fixed_font = tkfont.nametofont("TkFixedFont")
        except tk.TclError:
            self.default_font = tkfont.Font(name="TkDefaultFont", family="Segoe UI", size=10)
            self.text_font = tkfont.Font(name="TkTextFont", family="Segoe UI", size=10)
            self.fixed_font = tkfont.Font(name="TkFixedFont", family="Consolas", size=10)

        self.default_font.configure(family="Segoe UI", size=10)
        self.text_font.configure(family="Segoe UI", size=10)
        self.fixed_font.configure(family="Consolas", size=10)

        self.label_bold = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.heading_bold = ("Segoe UI", 10, "bold")
        self.base_font = ("Segoe UI", 10)

        self.dark_mode = False
        self.apply_theme(False)

    def apply_theme(self, dark: bool) -> None:
        self.dark_mode = dark
        if dark:
            bg, fg, sub_bg = "#1e1f22", "#e6e6e6", "#26282c"
            muted, border = "#a9b1bb", "#3a3d43"
            sel, tree_sel = "#2f3136", "#3a65a0"
        else:
            bg, fg, sub_bg = "#f7f7fb", "#222222", "#ffffff"
            muted, border = "#616975", "#d9dbe1"
            sel, tree_sel = "#eef2ff", "#cfe0ff"

        self.root.configure(bg=bg)
        s = self.style
        s.configure(".", background=bg, foreground=fg)

        s.configure("TNotebook", background=bg, borderwidth=0, tabmargins=[8,4,8,0])
        s.configure("TNotebook.Tab", padding=(14,8), background=sub_bg, foreground=fg, font=self.base_font)
        s.map("TNotebook.Tab", background=[("selected", sel)], foreground=[("selected", fg)])

        s.configure("TFrame", background=bg)
        s.configure("TLabelframe", background=bg, bordercolor=border, relief="solid")
        s.configure("TLabelframe.Label", background=bg, foreground=muted, font=self.label_bold)

        s.configure("TLabel", background=bg, foreground=fg, font=self.base_font)
        s.configure("TButton", padding=(12,8), relief="flat", background=sub_bg,
                    foreground=fg, borderwidth=1, font=self.base_font)
        s.configure("TEntry", foreground=fg)
        s.configure("TCombobox", foreground=fg)

        s.configure("Treeview", background=sub_bg, fieldbackground=sub_bg, foreground=fg,
                    rowheight=28, bordercolor=border, borderwidth=1, font=self.base_font)
        s.configure("Treeview.Heading", background=sub_bg, foreground=muted,
                    font=self.heading_bold, bordercolor=border)
        s.map("Treeview", background=[("selected", tree_sel)], foreground=[("selected", fg)])

    def apply_text_widget_colors(self, text: tk.Text) -> None:
        if self.dark_mode:
            text.configure(bg="#0f1113", fg="#e6e6e6", insertbackground="#e6e6e6")
        else:
            text.configure(bg="#ffffff", fg="#1f2328", insertbackground="#1f2328")

# ================= UTILITIES =================
class GuiStream(io.TextIOBase):
    def __init__(self, text_widget: tk.Text) -> None:
        self._text = text_widget
    def write(self, s: str) -> int:
        if s: self._text.after(0, self._append, s); return len(s)
        return 0
    def flush(self) -> None: ...
    def _append(self, s: str) -> None:
        self._text.configure(state="normal")
        self._text.insert("end", s); self._text.see("end")
        self._text.configure(state="disabled")

def in_thread(fn: Callable, on_error: Optional[Callable[[BaseException], None]] = None) -> None:
    def _runner():
        try: fn()
        except BaseException as e:
            if on_error: on_error(e)
    threading.Thread(target=_runner, daemon=True).start()

def confirm(title: str, msg: str) -> bool:
    return messagebox.askyesno(title, msg)

# ================= DB HELPERS =================
def _ensure_appointments_table() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            date TEXT NOT NULL,      -- YYYY-MM-DD
            time TEXT NOT NULL,      -- HH:MM
            reason TEXT,
            status TEXT DEFAULT 'Scheduled',
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(doctor_id) REFERENCES doctors(id)
        );
        """)

# ================= BASE CRUD WITH SEARCH + SORT =================
class CrudTab(ttk.Frame):
    columns: list[str] = []
    headings: list[str] = []
    idcol: str = "id"

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=12)
        self._sort_col: Optional[str] = None
        self._sort_desc: bool = False
        self._build_toolbar()
        self._build_table()
        self._build_form()
        self._build_buttons()
        self.refresh()

    def _build_toolbar(self) -> None:
        bar = ttk.Frame(self); bar.pack(fill=tk.X, pady=(0,8))
        ttk.Label(bar, text="Search").pack(side=tk.LEFT)
        self._filter_var = tk.StringVar()
        ent = ttk.Entry(bar, textvariable=self._filter_var)
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        ent.bind("<KeyRelease>", lambda _e: self.refresh())
        ttk.Button(bar, text="Clear", command=self._clear_filter).pack(side=tk.LEFT)
    def _clear_filter(self):
        self._filter_var.set(""); self.refresh()

    def _build_table(self) -> None:
        top = ttk.Frame(self); top.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(top, columns=self.columns, show="headings", selectmode="browse")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,6))
        for col, head in zip(self.columns, self.headings, strict=False):
            self.tree.heading(col, text=head, anchor=tk.W, command=lambda c=col: self._on_sort(c))
            self.tree.column(col, width=140, anchor=tk.W, stretch=True)
        vsb = ttk.Scrollbar(top, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set); vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _build_form(self) -> None:
        self.form = ttk.Labelframe(self, text="Details", padding=12)
        self.form.pack(fill=tk.X, pady=(10,6))
        self.inputs: dict[str, tk.Entry] = {}
        for col, head in zip(self.columns, self.headings, strict=False):
            if col == self.idcol: continue
            row = ttk.Frame(self.form); row.pack(fill=tk.X, pady=4)
            ttk.Label(row, text=head, width=18).pack(side=tk.LEFT)
            ent = ttk.Entry(row); ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.inputs[col] = ent

    def _build_buttons(self) -> None:
        bar = ttk.Frame(self); bar.pack(fill=tk.X, pady=(6,0))
        ttk.Button(bar, text="Add", command=self.on_add).pack(side=tk.LEFT)
        ttk.Button(bar, text="Update", command=self.on_update).pack(side=tk.LEFT, padx=6)
        ttk.Button(bar, text="Delete", command=self.on_delete).pack(side=tk.LEFT)
        ttk.Button(bar, text="Refresh", command=self.refresh).pack(side=tk.RIGHT)

    # ---- Hooks to implement ----
    def query_all(self) -> list[tuple[Any, ...]]: raise NotImplementedError
    def insert_row(self, values: dict[str,str]) -> None: raise NotImplementedError
    def update_row(self, row_id: Any, values: dict[str,str]) -> None: raise NotImplementedError
    def delete_row(self, row_id: Any) -> None: raise NotImplementedError

    # ---- Shared handlers ----
    def _on_select(self, _evt=None) -> None:
        sel = self.tree.selection()
        if not sel: return
        values = self.tree.item(sel[0])["values"]
        for col, val in zip(self.columns, values, strict=False):
            if col == self.idcol: continue
            ent = self.inputs.get(col)
            if ent is not None:
                ent.delete(0, tk.END); ent.insert(0, str(val))

    def _get_form_values(self) -> dict[str,str]:
        return {k: e.get().strip() for k, e in self.inputs.items()}

    def _get_selected_id(self) -> Optional[Any]:
        sel = self.tree.selection()
        return None if not sel else self.tree.item(sel[0])["values"][0]

    def on_add(self) -> None:
        try: self.insert_row(self._get_form_values()); self.refresh()
        except Exception as e: messagebox.showerror("Add failed", str(e))

    def on_update(self) -> None:
        row_id = self._get_selected_id()
        if row_id is None: messagebox.showinfo("Select a row", "Please select a row to update."); return
        try: self.update_row(row_id, self._get_form_values()); self.refresh()
        except Exception as e: messagebox.showerror("Update failed", str(e))

    def on_delete(self) -> None:
        row_id = self._get_selected_id()
        if row_id is None: messagebox.showinfo("Select a row", "Please select a row to delete."); return
        if not confirm("Confirm delete", f"Delete record #{row_id}?"): return
        try: self.delete_row(row_id); self.refresh()
        except Exception as e: messagebox.showerror("Delete failed", str(e))

    # ---- Filter/sort/render ----
    def _on_sort(self, col: str) -> None:
        if getattr(self, "_sort_col", None) == col: self._sort_desc = not self._sort_desc
        else: self._sort_col, self._sort_desc = col, False
        self.refresh()

    def _apply_filter_sort(self, rows: list[tuple[Any,...]]) -> list[tuple[Any,...]]:
        q = self._filter_var.get().strip().lower()
        if q:
            rows = [r for r in rows if any(q in str(v).lower() for v in r)]
        if getattr(self, "_sort_col", None):
            idx = self.columns.index(self._sort_col)
            rows.sort(key=lambda r: str(r[idx]).lower(), reverse=self._sort_desc)
        return rows

    def refresh(self) -> None:
        for iid in self.tree.get_children(): self.tree.delete(iid)
        rows = self._apply_filter_sort(self.query_all())
        for i, row in enumerate(rows):
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", values=row, tags=(tag,))
        dark = isinstance(self.winfo_toplevel(), App) and self.winfo_toplevel().theme.dark_mode
        self.tree.tag_configure("even", background="#23262a" if dark else "#ffffff")
        self.tree.tag_configure("odd", background="#1f2226" if dark else "#f6f7fb")
        for e in self.inputs.values(): e.delete(0, tk.END)

# ================= TABS =================
class DoctorsTab(CrudTab):
    columns = ["id","vcn","name","phone","email","graduated_year"]
    headings= ["ID","VCN","Name","Phone","Email","Graduated Year"]
    def query_all(self):
        with sqlite3.connect(DB_PATH) as c:
            return c.execute("SELECT id,vcn,name,phone,email,graduated_year FROM doctors").fetchall()
    def insert_row(self, v):
        with sqlite3.connect(DB_PATH) as c:
            try:
                c.execute("INSERT INTO doctors (vcn,name,phone,email,graduated_year) VALUES (?,?,?,?,?)",
                          (v["vcn"], v["name"], v["phone"], v["email"], v["graduated_year"]))
                c.commit()
            except sqlite3.IntegrityError as e:
                raise ValueError("VCN must be unique.") from e
    def update_row(self, row_id, v):
        with sqlite3.connect(DB_PATH) as c:
            c.execute("UPDATE doctors SET vcn=?,name=?,phone=?,email=?,graduated_year=? WHERE id=?",
                      (v["vcn"], v["name"], v["phone"], v["email"], v["graduated_year"], row_id)); c.commit()
    def delete_row(self, row_id):
        with sqlite3.connect(DB_PATH) as c:
            c.execute("DELETE FROM doctors WHERE id=?", (row_id,)); c.commit()

class PatientsTab(CrudTab):
    columns = ["id","name","species","breed","owner_name","owner_contact"]
    headings= ["ID","Name","Species","Breed","Owner Name","Owner Contact"]
    def query_all(self):
        with sqlite3.connect(DB_PATH) as c:
            return c.execute("SELECT id,name,species,breed,owner_name,owner_contact FROM patients").fetchall()
    def insert_row(self, v):
        with sqlite3.connect(DB_PATH) as c:
            c.execute("INSERT INTO patients (name,species,breed,owner_name,owner_contact) VALUES (?,?,?,?,?)",
                      (v["name"], v["species"], v["breed"], v["owner_name"], v["owner_contact"])); c.commit()
    def update_row(self, row_id, v):
        with sqlite3.connect(DB_PATH) as c:
            c.execute("UPDATE patients SET name=?,species=?,breed=?,owner_name=?,owner_contact=? WHERE id=?",
                      (v["name"], v["species"], v["breed"], v["owner_name"], v["owner_contact"], row_id)); c.commit()
    def delete_row(self, row_id):
        with sqlite3.connect(DB_PATH) as c:
            c.execute("DELETE FROM patients WHERE id=?", (row_id,)); c.commit()

class InventoryTab(CrudTab):
    columns = ["id","item_name","description","quantity","unit_price","expiry_date"]
    headings= ["ID","Item Name","Description","Quantity","Unit Price","Expiry Date"]
    def query_all(self):
        with sqlite3.connect(DB_PATH) as c:
            return c.execute("SELECT id,item_name,description,quantity,unit_price,expiry_date FROM inventory").fetchall()
    def insert_row(self, v):
        try: qty, price = int(v["quantity"]), float(v["unit_price"])
        except ValueError: raise ValueError("Quantity must be integer and Unit Price a number.")
        with sqlite3.connect(DB_PATH) as c:
            c.execute("""INSERT INTO inventory (item_name,description,quantity,unit_price,expiry_date)
                         VALUES (?,?,?,?,?)""", (v["item_name"], v["description"], qty, price, v["expiry_date"])); c.commit()
    def update_row(self, row_id, v):
        try: qty, price = int(v["quantity"]), float(v["unit_price"])
        except ValueError: raise ValueError("Quantity must be integer and Unit Price a number.")
        with sqlite3.connect(DB_PATH) as c:
            c.execute("""UPDATE inventory SET item_name=?,description=?,quantity=?,unit_price=?,expiry_date=? WHERE id=?""",
                      (v["item_name"], v["description"], qty, price, v["expiry_date"], row_id)); c.commit()
    def delete_row(self, row_id):
        with sqlite3.connect(DB_PATH) as c:
            c.execute("DELETE FROM inventory WHERE id=?", (row_id,)); c.commit()

class PrescriptionsTab(CrudTab):
    columns = ["id","patient","doctor","date","diagnosis","medication","dosage","instructions"]
    headings= ["ID","Patient","Doctor","Date","Diagnosis","Medication","Dosage","Instructions"]
    def query_all(self):
        with sqlite3.connect(DB_PATH) as c:
            return c.execute("""
                SELECT p.id, pt.name, d.name, p.date, p.diagnosis, p.medication, p.dosage, p.instructions
                FROM prescriptions p
                JOIN patients pt ON p.patient_id=pt.id
                JOIN doctors d ON p.doctor_id=d.id
                ORDER BY p.id DESC
            """).fetchall()
    def _insert_dialog(self):
        dlg = tk.Toplevel(self); dlg.title("Add Prescription"); dlg.transient(self.winfo_toplevel()); dlg.grab_set()
        frm = ttk.Frame(dlg, padding=12); frm.pack(fill=tk.BOTH, expand=True)
        with sqlite3.connect(DB_PATH) as c:
            pats = c.execute("SELECT id,name FROM patients ORDER BY name").fetchall()
            docs = c.execute("SELECT id,name FROM doctors ORDER BY name").fetchall()
        def row(label): r = ttk.Frame(frm); r.pack(fill=tk.X, pady=4); ttk.Label(r, text=label, width=16).pack(side=tk.LEFT); return r
        r=row("Patient"); patient_var=tk.StringVar(); ttk.Combobox(r, textvariable=patient_var, state="readonly",
            values=[f"{i} - {n}" for i,n in pats]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        r=row("Doctor"); doctor_var=tk.StringVar(); ttk.Combobox(r, textvariable=doctor_var, state="readonly",
            values=[f"{i} - {n}" for i,n in docs]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        fields={}
        for lab in ("Diagnosis","Medication","Dosage","Instructions"):
            r=row(lab); ent=ttk.Entry(r); ent.pack(side=tk.LEFT, fill=tk.X, expand=True); fields[lab.lower()] = ent
        res={"ok":False,"values":None}; btns=ttk.Frame(frm); btns.pack(fill=tk.X, pady=(8,0))
        def on_ok():
            if not patient_var.get() or not doctor_var.get(): messagebox.showerror("Missing","Select patient & doctor."); return
            try:
                pid=int(patient_var.get().split(" - ",1)[0]); did=int(doctor_var.get().split(" - ",1)[0])
            except ValueError: messagebox.showerror("Invalid","Bad selection."); return
            res["ok"]=True; res["values"] = dict(pid=pid,did=did,
                diagnosis=fields["diagnosis"].get().strip(),
                medication=fields["medication"].get().strip(),
                dosage=fields["dosage"].get().strip(),
                instructions=fields["instructions"].get().strip())
            dlg.destroy()
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side=tk.RIGHT)
        ttk.Button(btns, text="Add", command=on_ok).pack(side=tk.RIGHT, padx=6)
        dlg.wait_window(); return res["ok"], res["values"]
    def insert_row(self, _v):
        ok, data = self._insert_dialog()
        if not ok: return
        from datetime import date
        with sqlite3.connect(DB_PATH) as c:
            c.execute("""INSERT INTO prescriptions (patient_id,doctor_id,date,diagnosis,medication,dosage,instructions)
                         VALUES (?,?,?,?,?,?,?)""",
                      (data["pid"], data["did"], date.today().isoformat(),
                       data["diagnosis"], data["medication"], data["dosage"], data["instructions"])); c.commit()
    def update_row(self, row_id, v):
        with sqlite3.connect(DB_PATH) as c:
            c.execute("UPDATE prescriptions SET diagnosis=?,medication=?,dosage=?,instructions=? WHERE id=?",
                      (v["diagnosis"], v["medication"], v["dosage"], v["instructions"], row_id)); c.commit()
    def delete_row(self, row_id):
        with sqlite3.connect(DB_PATH) as c:
            c.execute("DELETE FROM prescriptions WHERE id=?", (row_id,)); c.commit()

class AppointmentsTab(CrudTab):
    columns = ["id","patient","doctor","date","time","reason","status"]
    headings= ["ID","Patient","Doctor","Date","Time","Reason","Status"]
    def query_all(self):
        with sqlite3.connect(DB_PATH) as c:
            return c.execute("""
                SELECT a.id, pt.name, d.name, a.date, a.time, a.reason, a.status
                FROM appointments a
                JOIN patients pt ON a.patient_id=pt.id
                JOIN doctors d ON a.doctor_id=d.id
                ORDER BY a.date DESC, a.time DESC
            """).fetchall()
    def _dialog(self, title: str, initial: Optional[dict]=None):
        dlg = tk.Toplevel(self); dlg.title(title); dlg.transient(self.winfo_toplevel()); dlg.grab_set()
        frm = ttk.Frame(dlg, padding=12); frm.pack(fill=tk.BOTH, expand=True)
        with sqlite3.connect(DB_PATH) as c:
            pats = c.execute("SELECT id,name FROM patients ORDER BY name").fetchall()
            docs = c.execute("SELECT id,name FROM doctors ORDER BY name").fetchall()
        def row(label): r=ttk.Frame(frm); r.pack(fill=tk.X, pady=4); ttk.Label(r, text=label, width=16).pack(side=tk.LEFT); return r
        r=row("Patient"); v_pat=tk.StringVar(value=initial.get("patient","") if initial else "")
        ttk.Combobox(r, textvariable=v_pat, state="readonly", values=[f"{i} - {n}" for i,n in pats]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        r=row("Doctor"); v_doc=tk.StringVar(value=initial.get("doctor","") if initial else "")
        ttk.Combobox(r, textvariable=v_doc, state="readonly", values=[f"{i} - {n}" for i,n in docs]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        r=row("Date (YYYY-MM-DD)"); e_date=ttk.Entry(r); e_date.pack(side=tk.LEFT, fill=tk.X, expand=True)
        r=row("Time (HH:MM)"); e_time=ttk.Entry(r); e_time.pack(side=tk.LEFT, fill=tk.X, expand=True)
        r=row("Reason)"); e_reason=ttk.Entry(r); e_reason.pack(side=tk.LEFT, fill=tk.X, expand=True)
        r=row("Status"); v_status=tk.StringVar(value=(initial.get("status") if initial else "Scheduled"))
        ttk.Combobox(r, textvariable=v_status, state="readonly", values=["Scheduled","Completed","Cancelled"]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        if initial:
            e_date.insert(0, initial.get("date","")); e_time.insert(0, initial.get("time","")); e_reason.insert(0, initial.get("reason",""))
        res={"ok":False,"values":None}; btns=ttk.Frame(frm); btns.pack(fill=tk.X, pady=(8,0))
        def on_ok():
            if not v_pat.get() or not v_doc.get(): messagebox.showerror("Missing","Select patient & doctor."); return
            try:
                pid=int(v_pat.get().split(" - ",1)[0]); did=int(v_doc.get().split(" - ",1)[0])
            except ValueError: messagebox.showerror("Invalid","Bad selection."); return
            res["ok"]=True; res["values"] = dict(
                patient_id=pid, doctor_id=did, date=e_date.get().strip(), time=e_time.get().strip(),
                reason=e_reason.get().strip(), status=v_status.get().strip()
            ); dlg.destroy()
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side=tk.RIGHT)
        ttk.Button(btns, text="OK", command=on_ok).pack(side=tk.RIGHT, padx=6)
        dlg.wait_window(); return res["ok"], res["values"]
    def insert_row(self, _v):
        ok, data = self._dialog("Add Appointment")
        if not ok: return
        with sqlite3.connect(DB_PATH) as c:
            c.execute("""INSERT INTO appointments (patient_id,doctor_id,date,time,reason,status)
                         VALUES (?,?,?,?,?,?)""",
                      (data["patient_id"], data["doctor_id"], data["date"], data["time"], data["reason"], data["status"]))
            c.commit()
    def update_row(self, row_id, _v):
        sel = self.tree.selection()
        if not sel: return
        cur = self.tree.item(sel[0])["values"]
        init = dict(patient=f"{cur[1]}", doctor=f"{cur[2]}", date=f"{cur[3]}",
                    time=f"{cur[4]}", reason=f"{cur[5]}", status=f"{cur[6]}")
        ok, data = self._dialog("Edit Appointment", init)
        if not ok: return
        with sqlite3.connect(DB_PATH) as c:
            c.execute("""UPDATE appointments SET patient_id=?,doctor_id=?,date=?,time=?,reason=?,status=? WHERE id=?""",
                      (data["patient_id"], data["doctor_id"], data["date"], data["time"], data["reason"], data["status"], row_id))
            c.commit()
    def delete_row(self, row_id):
        with sqlite3.connect(DB_PATH) as c:
            c.execute("DELETE FROM appointments WHERE id=?", (row_id,)); c.commit()

# ---- AI Tab (Notebook) ----
class AITab(ttk.Frame):
    def __init__(self, master: tk.Misc, log_stream: io.TextIOBase) -> None:
        super().__init__(master, padding=12)
        ttk.Label(self, text="AI Features", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        row = ttk.Frame(self, padding=(0,8)); row.pack(fill=tk.X)
        ttk.Button(row, text="Predict Top Drugs (90d)", command=self._wrap(ai.predict_top_drugs)).pack(side=tk.LEFT)
        ttk.Button(row, text="Flag Underbilled (<60%)", command=self._wrap(ai.flag_underbilled)).pack(side=tk.LEFT, padx=8)
        ttk.Label(self, text="Results appear in the Log tab.").pack(anchor="w")
        self.log_stream = log_stream
    def _wrap(self, fn: Callable[[],None]) -> Callable[[],None]:
        def _go():
            def task():
                old_out, old_err = sys.stdout, sys.stderr
                try: sys.stdout = self.log_stream; sys.stderr = self.log_stream; fn()
                finally: sys.stdout, sys.stderr = old_out, old_err
            in_thread(task, on_error=lambda e: messagebox.showerror("AI error", str(e)))
        return _go

# ================= APP =================
class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("🐾 VetAI Clinic Intelligence System")
        self.geometry("1200x760"); self.minsize(1000, 640)

        self.theme = ThemeManager(self)
        _ensure_appointments_table()

        self._build_menu()
        self._build_layout()

    def _build_menu(self) -> None:
        menubar = tk.Menu(self); self.config(menu=menubar)
        dbmenu = tk.Menu(menubar, tearoff=False); menubar.add_cascade(label="Database", menu=dbmenu)
        dbmenu.add_command(label="Initialize Schema", command=self.on_init_db)
        dbmenu.add_command(label="Insert Dummy Data", command=self.on_seed)
        viewmenu = tk.Menu(menubar, tearoff=False); menubar.add_cascade(label="View", menu=viewmenu)
        viewmenu.add_checkbutton(label="Dark Mode", command=self.toggle_dark_mode)
        helpmenu = tk.Menu(menubar, tearoff=False); menubar.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About", command=lambda: messagebox.showinfo(
            "About", "VetAI Clinic Intelligence System (Tkinter)\nSearch, Sort, AI tab, and Appointments.")
        )

    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=10); container.pack(fill=tk.BOTH, expand=True)
        self.notebook = ttk.Notebook(container); self.notebook.pack(fill=tk.BOTH, expand=True)

        # Data tabs
        self.tab_doctors = DoctorsTab(self.notebook)
        self.tab_patients = PatientsTab(self.notebook)
        self.tab_inventory = InventoryTab(self.notebook)
        self.tab_prescriptions = PrescriptionsTab(self.notebook)
        self.tab_billing = InventoryTab.__mro__[0]  # no-op to keep linter happy
        self.tab_billing = None
        class _BillingTab(PrescriptionsTab): pass  # placeholder to reuse style
        del _BillingTab
        # Proper Billing tab:
        class BillingTab(CrudTab):
            columns = ["id","prescription_id","patient","total_amount","paid_amount","billing_date"]
            headings= ["ID","Prescription ID","Patient","Total (₹)","Paid (₹)","Billing Date"]
            def query_all(self):
                with sqlite3.connect(DB_PATH) as c:
                    return c.execute("""
                        SELECT b.id, b.prescription_id, pt.name, b.total_amount, b.paid_amount, b.billing_date
                        FROM billing b
                        JOIN prescriptions p ON b.prescription_id = p.id
                        JOIN patients pt ON p.patient_id = pt.id
                        ORDER BY b.id DESC
                    """).fetchall()
            def _insert_dialog(self):
                dlg = tk.Toplevel(self); dlg.title("Generate Bill"); dlg.transient(self.winfo_toplevel()); dlg.grab_set()
                frm = ttk.Frame(dlg, padding=12); frm.pack(fill=tk.BOTH, expand=True)
                with sqlite3.connect(DB_PATH) as c:
                    prescs = c.execute("""
                        SELECT p.id, pt.name, p.medication, p.date
                        FROM prescriptions p
                        JOIN patients pt ON p.patient_id = pt.id
                        ORDER BY p.id DESC
                    """).fetchall()
                def row(l): r=ttk.Frame(frm); r.pack(fill=tk.X, pady=4); ttk.Label(r, text=l, width=16).pack(side=tk.LEFT); return r
                r=row("Prescription"); v=tk.StringVar()
                ttk.Combobox(r, textvariable=v, state="readonly",
                    values=[f"{pid} - {pname} - {med} ({dt})" for pid,pname,med,dt in prescs]).pack(side=tk.LEFT, fill=tk.X, expand=True)
                r=row("Total (₹)"); e_total=ttk.Entry(r); e_total.pack(side=tk.LEFT, fill=tk.X, expand=True)
                r=row("Paid (₹)"); e_paid=ttk.Entry(r); e_paid.pack(side=tk.LEFT, fill=tk.X, expand=True)
                res={"ok":False,"values":None}; btns=ttk.Frame(frm); btns.pack(fill=tk.X, pady=(8,0))
                def ok():
                    if not v.get(): messagebox.showerror("Missing","Choose a prescription."); return
                    try:
                        presc_id=int(v.get().split(" - ",1)[0]); total=float(e_total.get().strip()); paid=float(e_paid.get().strip())
                    except ValueError: messagebox.showerror("Invalid","Amounts must be numbers."); return
                    res["ok"]=True; res["values"]=dict(presc_id=presc_id,total=total,paid=paid); dlg.destroy()
                ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side=tk.RIGHT)
                ttk.Button(btns, text="Create", command=ok).pack(side=tk.RIGHT, padx=6)
                dlg.wait_window(); return res["ok"], res["values"]
            def insert_row(self, _v):
                ok, data = self._insert_dialog()
                if not ok: return
                from datetime import date
                with sqlite3.connect(DB_PATH) as c:
                    c.execute("INSERT INTO billing (prescription_id,total_amount,paid_amount,billing_date) VALUES (?,?,?,?)",
                              (data["presc_id"], data["total"], data["paid"], date.today().isoformat())); c.commit()
            def update_row(self, row_id, v):
                try: paid=float(v["paid_amount"])
                except ValueError: raise ValueError("Paid amount must be a number.")
                with sqlite3.connect(DB_PATH) as c:
                    c.execute("UPDATE billing SET paid_amount=? WHERE id=?", (paid, row_id)); c.commit()
            def delete_row(self, row_id):
                with sqlite3.connect(DB_PATH) as c:
                    c.execute("DELETE FROM billing WHERE id=?", (row_id,)); c.commit()
        self.tab_billing = BillingTab(self.notebook)
        self.tab_appointments = AppointmentsTab(self.notebook)

        # Add tabs
        self.notebook.add(self.tab_doctors, text="Doctors")
        self.notebook.add(self.tab_patients, text="Patients")
        self.notebook.add(self.tab_inventory, text="Inventory")
        self.notebook.add(self.tab_prescriptions, text="Prescriptions")
        self.notebook.add(self.tab_billing, text="Billing")
        self.notebook.add(self.tab_appointments, text="Appointments")

        # AI + Log tabs
        self.log_text = tk.Text(self.notebook, height=10, wrap="word", state="disabled", relief="flat")
        self.theme.apply_text_widget_colors(self.log_text)
        self.log_stream = GuiStream(self.log_text)
        self.tab_ai = AITab(self.notebook, self.log_stream)
        self.notebook.add(self.tab_ai, text="AI")
        log_tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(log_tab, text="Log")
        self.log_text.pack(in_=log_tab, fill=tk.BOTH, expand=True)

        # Footer actions
        footer = ttk.Frame(container); footer.pack(fill=tk.X, pady=(8,0))
        ttk.Button(footer, text="Initialize Database", command=self.on_init_db).pack(side=tk.LEFT)
        ttk.Button(footer, text="Insert Dummy Data", command=self.on_seed).pack(side=tk.LEFT, padx=6)

    # ----- actions -----
    def toggle_dark_mode(self) -> None:
        self.theme.apply_theme(not self.theme.dark_mode)
        for tab in (self.tab_doctors, self.tab_patients, self.tab_inventory,
                    self.tab_prescriptions, self.tab_billing, self.tab_appointments):
            tab.refresh()
        self.theme.apply_text_widget_colors(self.log_text)

    def on_init_db(self) -> None:
        if not confirm("Initialize Database", "This will (re)create the schema. Continue?"): return
        def task():
            old_out, old_err = sys.stdout, sys.stderr
            try:
                sys.stdout = self.log_stream; sys.stderr = self.log_stream
                print("\n--- Initializing Database ---")
                initialize_db()
                _ensure_appointments_table()
                print("Done."); self._refresh_all_tabs()
            except Exception:
                traceback.print_exc()
            finally:
                sys.stdout, sys.stderr = old_out, old_err
        in_thread(task)

    def on_seed(self) -> None:
        def task():
            old_out, old_err = sys.stdout, sys.stderr
            try:
                sys.stdout = self.log_stream; sys.stderr = self.log_stream
                print("\n--- Inserting Dummy Data ---"); insert_dummy_data(); print("Done.")
                self._refresh_all_tabs()
            except Exception:
                traceback.print_exc()
            finally:
                sys.stdout, sys.stderr = old_out, old_err
        in_thread(task)

    def _refresh_all_tabs(self) -> None:
        for tab in (self.tab_doctors, self.tab_patients, self.tab_inventory,
                    self.tab_prescriptions, self.tab_billing, self.tab_appointments):
            self.after(0, tab.refresh)

if __name__ == "__main__":
    app = App()
    app.mainloop()
