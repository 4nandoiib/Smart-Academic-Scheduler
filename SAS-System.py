import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import csv

schedule_list = []

def update_clock():
    now = datetime.now().strftime("Current Time: %A, %B %d, %Y - %I:%M:%S %p")
    clock_label.config(text=now)
    root.after(1000, update_clock)

def clear_main_area():
    for widget in main_area.winfo_children():
        widget.destroy()

def handle_date_input(event):
    text = event.widget.get()
    if len(text) in [2, 5]:
        event.widget.insert(tk.END, "/")
    if len(text) == 10:
        try:
            day = datetime.strptime(text, "%m/%d/%Y").strftime("%A")
            day_entry.config(state="normal")
            day_entry.delete(0, tk.END)
            day_entry.insert(0, day)
            day_entry.config(state="readonly")
        except:
            pass

def sort_schedules():
    schedule_list.sort(key=lambda e: datetime.strptime(f"{e['date']} {e['start']}", "%m/%d/%Y %I:%M%p")
                       if e["date"] and e["start"] else datetime.max)

def show_schedule_form(existing=None, idx=None, is_new=True):
    global day_entry
    clear_main_area()

    fields = [("Date", handle_date_input), ("Start Time", None), ("End Time", None),
              ("Subject", None), ("Day", None), ("Notes", None)]
    keys = ["date", "start", "end", "subject", "day", "notes"]
    entries = {}

    for i, (label, bind_event) in enumerate(fields):
        tk.Label(main_area, text=label + ":", bg="white").grid(row=i, column=0, sticky="w", padx=5, pady=2)
        is_readonly = "readonly" if label == "Day" else "normal"
        width = 50 if label == "Notes" else 20
        entry = tk.Entry(main_area, width=width, state=is_readonly)
        entry.grid(row=i, column=1, columnspan=3 if label == "Notes" else 2, sticky="w", pady=2)
        if bind_event:
            entry.bind("<KeyRelease>", bind_event)
        entries[keys[i]] = entry
        if label == "Day":
            day_entry = entry

    if existing:
        for key in keys:
            entries[key].config(state="normal")
            entries[key].insert(0, existing[key])
            if key == "day":
                entries[key].config(state="readonly")

    def save_schedule():
        item = {k: entries[k].get().strip() for k in keys}

        if not item["date"] or not item["start"] or not item["end"] or not item["subject"]:
            return messagebox.showerror("Input Error", "Date, Start, End, and Subject are required.")

        try:
            start = datetime.strptime(f"{item['date']} {item['start']}", "%m/%d/%Y %I:%M%p")
            end = datetime.strptime(f"{item['date']} {item['end']}", "%m/%d/%Y %I:%M%p")
            if start >= end:
                return messagebox.showerror("Input Error", "End time must be after start time.")
        except:
            return messagebox.showerror("Format Error", "Please enter a valid date and time.")

        for i, s in enumerate(schedule_list):
            if i == idx:
                continue
            if s["date"] == item["date"]:
                s_start = datetime.strptime(f"{s['date']} {s['start']}", "%m/%d/%Y %I:%M%p")
                s_end = datetime.strptime(f"{s['date']} {s['end']}", "%m/%d/%Y %I:%M%p")
                if start < s_end and end > s_start:
                    return messagebox.showerror("Conflict", f"Overlaps with: {s['subject']} ({s['start']} - {s['end']})")

        if idx is not None:
            schedule_list[idx] = item
            messagebox.showinfo("Updated", "Schedule updated.")
            show_schedule_list(True)
        else:
            schedule_list.append(item)
            messagebox.showinfo("Saved", "New schedule added.")
            show_schedule_form()

    btn_text = "Add Schedule" if existing is None else "Save Changes"
    tk.Button(main_area, text=btn_text, command=save_schedule).grid(row=6, column=0, columnspan=3, pady=10)

def show_schedule_list(editable):
    clear_main_area()
    sort_schedules()

    if not editable:
        tk.Label(main_area, text="Scheduled Entries", font=("Arial", 14, "bold"), bg="white").grid(row=0, column=0, pady=10, padx=5, sticky="w")

    if not schedule_list:
        tk.Label(main_area, text="No schedules available.", bg="white", font=("Arial", 12)).grid(row=1, column=0, pady=20)
    else:
        for i, e in enumerate(schedule_list):
            text = f"{e['date']} | {e['day']} | {e['start']} - {e['end']} | {e['subject']} | {e['notes']}"
            frame = tk.Frame(main_area, bg="white", bd=1, relief="solid")
            frame.grid(row=i + 1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
            tk.Label(frame, text=text, bg="white", anchor="w").pack(side="left", padx=10)

            if editable:
                tk.Button(frame, text="Edit", command=lambda i=i: show_schedule_form(schedule_list[i], i, False)).pack(side="right", padx=5)
                tk.Button(frame, text="Delete", command=lambda i=i: delete_schedule(i)).pack(side="right", padx=5)

    if not editable:
        tk.Button(main_area, text="EXPORT", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                  command=export_schedule).grid(row=len(schedule_list)+2, column=0, sticky="w", padx=5, pady=10)

def delete_schedule(index):
    if messagebox.askyesno("Delete", "Are you sure?"):
        del schedule_list[index]
        show_schedule_list(True)

def export_schedule():
    if not schedule_list:
        return messagebox.showwarning("No Data", "Nothing to export.")
    path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not path:
        return
    try:
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Day", "Start Time", "End Time", "Subject", "Notes"])
            for e in schedule_list:
                writer.writerow([e[k] for k in ["date", "day", "start", "end", "subject", "notes"]])
        messagebox.showinfo("Success", f"Exported to:\n{path}")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))

def show_home():
    clear_main_area()
    tk.Label(main_area, text="Welcome to SAS!", font=("Arial", 20), bg="white").place(x=10, y=10)
    tk.Label(main_area, text="Let's manage your busy schedule now.", font=("Arial", 12), bg="white").place(x=10, y=45)

def exit_app():
    if messagebox.askyesno("Exit", "Exit the app?"):
        root.destroy()

def toggle_side_menu():
    if side_menu.winfo_ismapped():
        side_menu.place_forget()
        main_area.place(x=10, y=70, width=730, height=420)
    else:
        side_menu.place(x=0, y=60, width=150, height=440)
        main_area.place(x=160, y=70, width=580, height=420)

def menu_action(fn):
    return lambda: [toggle_side_menu(), clear_main_area(), fn()]

# GUI Setup
root = tk.Tk()
root.title("Smart Academic Scheduler")
root.geometry("750x500")
root.configure(bg="#b2d89c")

header = tk.Frame(root, bg="#2e8b57", height=60)
header.pack(fill=tk.X)
tk.Button(header, text="≡", font=("Arial", 20), bg="#2e8b57", fg="white", bd=0, command=toggle_side_menu).place(x=10, y=2)
tk.Label(header, text="Smart Academic Scheduler", font=("Arial", 18, "bold"), bg="#2e8b57").place(x=50, y=5)
clock_label = tk.Label(header, text="", font=("Arial", 10), bg="#2e8b57")
clock_label.place(x=50, y=35)
update_clock()

side_menu = tk.Frame(root, bg="#eeeeee")
buttons = [("Home", show_home), ("Add Schedule", lambda: show_schedule_form()),
           ("Update Schedule", lambda: show_schedule_list(True)),
           ("View Schedule", lambda: show_schedule_list(False)),
           ("Exit", lambda: [show_home(), exit_app()])]

for text, cmd in buttons:
    tk.Button(side_menu, text=text, width=20, command=menu_action(cmd)).pack(pady=5)

main_area = tk.Frame(root, bg="white")
main_area.place(x=10, y=70, width=730, height=420)
show_home()

root.mainloop()