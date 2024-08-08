import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3

conn = sqlite3.connect('medical_store.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        purpose TEXT NOT NULL,
        expiration_date TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'staff'
    )
''')

conn.commit()

def show_main_app():
    main_app = tk.Toplevel(root)
    main_app.title("Medical Store Management")
    main_app.state('zoomed')  
    main_app.resizable(True, True)

    style = ttk.Style()
    style.configure("TLabel", font=("Helvetica", 12))
    style.configure("TButton", font=("Helvetica", 12), padding=6)
    style.configure("TEntry", font=("Helvetica", 12))

    title_label = ttk.Label(main_app, text="Medical Store Management System", font=("Helvetica", 16, "bold"))
    title_label.pack(pady=10)

    form_frame = ttk.Frame(main_app, padding="10")
    form_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(form_frame, text="Medicine Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    entry_name = ttk.Entry(form_frame, width=30)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    entry_quantity = ttk.Entry(form_frame, width=30)
    entry_quantity.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Purpose:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    entry_purpose = ttk.Entry(form_frame, width=30)
    entry_purpose.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Expiration Date:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    entry_expiration_date = ttk.Entry(form_frame, width=30)
    entry_expiration_date.grid(row=3, column=1, padx=5, pady=5)

    def add_medicine():
        name = entry_name.get()
        quantity = entry_quantity.get()
        purpose = entry_purpose.get()
        expiration_date = entry_expiration_date.get()
        
        if not name or not quantity or not purpose or not expiration_date:
            messagebox.showerror("Input Error", "All fields are required")
            return
        
        conn = sqlite3.connect('medical_store.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO medicines (name, quantity, purpose, expiration_date)
            VALUES (?, ?, ?, ?)
        ''', (name, quantity, purpose, expiration_date))
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", "Medicine data added successfully")
        clear_entries()

    def clear_entries():
        entry_name.delete(0, tk.END)
        entry_quantity.delete(0, tk.END)
        entry_purpose.delete(0, tk.END)
        entry_expiration_date.delete(0, tk.END)

    submit_button = ttk.Button(main_app, text="Add Medicine", command=add_medicine)
    submit_button.pack(pady=10)

    def delete_medicine():
        name = entry_name.get()
        if not name:
            messagebox.showerror("Input Error", "Medicine name is required for deletion")
            return

        conn = sqlite3.connect('medical_store.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM medicines WHERE name = ?', (name,))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", "Medicine data deleted successfully")
        clear_entries()

    delete_button = ttk.Button(main_app, text="Delete Medicine", command=delete_medicine)
    delete_button.pack(pady=10)

    def view_medicines():
        view_window = tk.Toplevel(main_app)
        view_window.title("View Medicines")

        tree = ttk.Treeview(view_window, columns=("quantity", "purpose", "expiration_date"), show="headings")
        tree.heading("#1", text="Name")
        tree.heading("#2", text="Quantity")
        tree.heading("#3", text="Purpose")
        tree.heading("#4", text="Expiration Date")
        tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        conn = sqlite3.connect('medical_store.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, quantity, purpose, expiration_date FROM medicines')
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", tk.END, values=row)

    view_button = ttk.Button(main_app, text="View Medicines", command=view_medicines)
    view_button.pack(pady=10)

def show_admin_panel():
    def create_user():
        username = entry_new_username.get().strip()
        password = entry_new_password.get()
        
        if not username or not password:
            messagebox.showerror("Input Error", "Username and password are required")
            return
        
        conn = sqlite3.connect('medical_store.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', (username, password, 'staff'))  
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "New user created successfully")
            entry_new_username.delete(0, tk.END)
            entry_new_password.delete(0, tk.END)
            
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"Failed to create user: {e}")
            conn.rollback()
            conn.close()

    def view_all_staff():
        def remove_user():
            selected_item = tree.focus()
            if not selected_item:
                messagebox.showerror("Error", "No staff selected")
                return

            username = tree.item(selected_item, 'values')[0]
            if not username:
                messagebox.showerror("Error", "No username found")
                return

            if messagebox.askyesno("Confirm Remove", f"Are you sure you want to remove {username}?"):
                conn = sqlite3.connect('medical_store.db')
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE username = ?', (username,))
                conn.commit()
                conn.close()

                tree.delete(selected_item)
                messagebox.showinfo("Success", f"{username} has been removed")

        view_window = tk.Toplevel(admin_panel)
        view_window.title("View All Staff")

        tree = ttk.Treeview(view_window, columns=("username",), show="headings")
        tree.heading("#1", text="Username")
        tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        conn = sqlite3.connect('medical_store.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users')
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", tk.END, values=row)

        remove_button = ttk.Button(view_window, text="Remove", command=remove_user)
        remove_button.pack(pady=10)

    admin_panel = tk.Toplevel(root)
    admin_panel.title("Admin Panel")
    admin_panel.geometry("400x300")
    admin_panel.resizable(True, True)

    style = ttk.Style()
    style.configure("TLabel", font=("Helvetica", 12))
    style.configure("TButton", font=("Helvetica", 12), padding=6)
    style.configure("TEntry", font=("Helvetica", 12))

    ttk.Label(admin_panel, text="Create New User", font=("Helvetica", 14, "bold")).pack(pady=10)

    ttk.Label(admin_panel, text="Username:").pack(pady=5)
    entry_new_username = ttk.Entry(admin_panel, width=30)
    entry_new_username.pack(pady=5)

    ttk.Label(admin_panel, text="Password:").pack(pady=5)
    entry_new_password = ttk.Entry(admin_panel, width=30, show="*")
    entry_new_password.pack(pady=5)

    show_password_var = tk.BooleanVar()
    show_password_check = ttk.Checkbutton(admin_panel, text="Show Password", variable=show_password_var, command=lambda: entry_new_password.config(show="" if show_password_var.get() else "*"))
    show_password_check.pack(pady=5)

    ttk.Button(admin_panel, text="Create User", command=create_user).pack(pady=10)

    ttk.Separator(admin_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(admin_panel, text="View All Staff", font=("Helvetica", 14, "bold")).pack(pady=10)
    ttk.Button(admin_panel, text="All Staff", command=view_all_staff).pack(pady=10)

def show_login_panel():
    def validate_login():
        username = entry_username.get()
        password = entry_password.get()
        
        conn = sqlite3.connect('medical_store.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM users WHERE username = ? AND password = ?
        ''', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            messagebox.showinfo("Login Success", "Welcome!")
            login_panel.destroy() 
            show_main_app()  
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    login_panel = tk.Toplevel(root)
    login_panel.title("Staff Login")
    login_panel.geometry("400x300")
    login_panel.resizable(True, True)

    style = ttk.Style()
    style.configure("TLabel", font=("Helvetica", 12))
    style.configure("TButton", font=("Helvetica", 12), padding=6)
    style.configure("TEntry", font=("Helvetica", 12))

    login_frame = ttk.Frame(login_panel, padding="10")
    login_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    entry_username = ttk.Entry(login_frame, width=30)
    entry_username.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    entry_password = ttk.Entry(login_frame, width=30, show="*")
    entry_password.grid(row=1, column=1, padx=5, pady=5)

    show_password_var = tk.BooleanVar()
    show_password_check = ttk.Checkbutton(login_frame, text="Show Password", variable=show_password_var, command=lambda: entry_password.config(show="" if show_password_var.get() else "*"))
    show_password_check.grid(row=2, columnspan=2, padx=5, pady=5)

    ttk.Button(login_frame, text="Submit", command=validate_login).grid(row=3, columnspan=2, pady=20)

    login_panel.mainloop()

root = tk.Tk()
root.title("Medical Store Management")
root.geometry("300x200")
root.state('zoomed')  
root.resizable(True, True)

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(main_frame, text="Staff Login", font=("Helvetica", 16, "bold")).pack(pady=10)

ttk.Button(main_frame, text="Admin", command=show_admin_panel).pack(pady=10)
ttk.Button(main_frame, text="Staff", command=show_login_panel).pack(pady=10)

root.mainloop()
