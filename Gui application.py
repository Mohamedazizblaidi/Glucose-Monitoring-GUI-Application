import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")  

# =====================[ Database Class ]=========================
class GlucoseDatabase:
    def __init__(self, db_name='glucose_data.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS glucose (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                value REAL NOT NULL
            )
        """)
        self.conn.commit()

    def add_entry(self, date, value):
        self.cursor.execute("INSERT INTO glucose (date, value) VALUES (?, ?)", (date, value))
        self.conn.commit()

    def fetch_all(self):
        self.cursor.execute("SELECT * FROM glucose")
        return self.cursor.fetchall()

    def get_dataframe(self):
        df = pd.read_sql_query("SELECT * FROM glucose", self.conn)
        df['date'] = pd.to_datetime(df['date'])
        return df

    def delete_all(self):
        self.cursor.execute("DELETE FROM glucose")
        self.conn.commit()

    def delete_by_id(self, entry_id):
        self.cursor.execute("DELETE FROM glucose WHERE id = ?", (entry_id,))
        self.conn.commit()

# =====================[ Application GUI Class ]=========================
class GlucoseApp:
    def __init__(self, root):
        self.db = GlucoseDatabase()
        self.root = root
        self.root.title("Glucose Tracker")
        self.root.geometry("700x600")
        
        # Variables
        self.date_var = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.value_var = ctk.StringVar()
        
        self.setup_ui()

    def setup_ui(self):
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame, 
            text="🩺 Glucose Tracker", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Input frame
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(pady=10, padx=10, fill="x")
        
        # Date input
        date_label = ctk.CTkLabel(input_frame, text="Date (YYYY-MM-DD):")
        date_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        date_entry = ctk.CTkEntry(input_frame, textvariable=self.date_var, width=200)
        date_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Glucose value input
        value_label = ctk.CTkLabel(input_frame, text="Glucose Value:")
        value_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        value_entry = ctk.CTkEntry(input_frame, textvariable=self.value_var, width=200)
        value_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Buttons frame
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(pady=10, padx=10, fill="x")
        
        # Action buttons
        add_button = ctk.CTkButton(
            button_frame, 
            text="Add Entry", 
            command=self.add_entry,
            fg_color="#28a745"
        )
        add_button.grid(row=0, column=0, padx=5, pady=5)
        
        show_button = ctk.CTkButton(
            button_frame, 
            text="Show Data", 
            command=self.show_data
        )
        show_button.grid(row=0, column=1, padx=5, pady=5)
        
        analyze_button = ctk.CTkButton(
            button_frame, 
            text="Analyze", 
            command=self.analyze_data
        )
        analyze_button.grid(row=0, column=2, padx=5, pady=5)
        
        plot_button = ctk.CTkButton(
            button_frame, 
            text="Plot", 
            command=self.plot_data
        )
        plot_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Table frame (we'll use a custom solution since CTkTable isn't part of standard customtkinter)
        table_frame = ctk.CTkFrame(self.main_frame)
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Create a scrollable frame for the table
        self.table_scroll = ctk.CTkScrollableFrame(table_frame)
        self.table_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Table header
        header_frame = ctk.CTkFrame(self.table_scroll)
        header_frame.pack(fill="x", padx=2, pady=2)
        
        ctk.CTkLabel(header_frame, text="ID", width=50, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=2, pady=2)
        ctk.CTkLabel(header_frame, text="Date", width=150, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=2, pady=2)
        ctk.CTkLabel(header_frame, text="Glucose", width=150, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=2, pady=2)
        
        # The rows will be populated in show_data method
        self.table_rows_frame = ctk.CTkFrame(self.table_scroll)
        self.table_rows_frame.pack(fill="x", padx=2, pady=2)
        
        # Bottom buttons frame
        bottom_button_frame = ctk.CTkFrame(self.main_frame)
        bottom_button_frame.pack(pady=10, padx=10, fill="x")
        
        delete_all_button = ctk.CTkButton(
            bottom_button_frame, 
            text="Delete All", 
            command=self.delete_all,
            fg_color="#dc3545"
        )
        delete_all_button.grid(row=0, column=0, padx=5, pady=5)
        
        delete_id_button = ctk.CTkButton(
            bottom_button_frame, 
            text="Delete by ID", 
            command=self.delete_by_id_prompt,
            fg_color="#dc3545"
        )
        delete_id_button.grid(row=0, column=1, padx=5, pady=5)
        
        exit_button = ctk.CTkButton(
            bottom_button_frame, 
            text="Exit", 
            command=self.root.quit,
            fg_color="#6c757d"
        )
        exit_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Load initial data
        self.show_data()

    def add_entry(self):
        date = self.date_var.get()
        value = self.value_var.get()

        try:
            value = float(value)
            datetime.strptime(date, "%Y-%m-%d")
            self.db.add_entry(date, value)
            messagebox.showinfo("Success", "Data added!")
            self.value_var.set('')
            self.show_data()
        except ValueError:
            messagebox.showerror("Error", "Invalid input!")

    def show_data(self):
        # Clear existing rows
        for widget in self.table_rows_frame.winfo_children():
            widget.destroy()
            
        rows = self.db.fetch_all()
        
        # No data message
        if not rows:
            no_data_label = ctk.CTkLabel(
                self.table_rows_frame, 
                text="No data available. Add some entries!",
                font=ctk.CTkFont(size=14)
            )
            no_data_label.pack(pady=20)
            return
            
        # Add rows to the table
        for i, row in enumerate(rows):
            row_frame = ctk.CTkFrame(self.table_rows_frame)
            row_frame.pack(fill="x", padx=2, pady=2)
            
            # Alternate row colors for better readability
            if i % 2 == 0:
                row_frame.configure(fg_color=("gray90", "gray25"))
            
            ctk.CTkLabel(row_frame, text=str(row[0]), width=50).grid(row=0, column=0, padx=2, pady=2)
            ctk.CTkLabel(row_frame, text=str(row[1]), width=150).grid(row=0, column=1, padx=2, pady=2)
            ctk.CTkLabel(row_frame, text=str(row[2]), width=150).grid(row=0, column=2, padx=2, pady=2)

    def analyze_data(self):
        df = self.db.get_dataframe()
        if df.empty:
            messagebox.showinfo("Analysis", "No data to analyze.")
            return

        # Create analysis dialog
        analysis_window = ctk.CTkToplevel(self.root)
        analysis_window.title("Glucose Analysis")
        analysis_window.geometry("400x300")
        analysis_window.transient(self.root)
        analysis_window.grab_set()
        
        analysis_frame = ctk.CTkFrame(analysis_window)
        analysis_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        title_label = ctk.CTkLabel(
            analysis_frame, 
            text="Glucose Analysis Results", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Stats
        stats_frame = ctk.CTkFrame(analysis_frame)
        stats_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(stats_frame, text=f"Total Entries:", anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(stats_frame, text=f"{len(df)}", anchor="e").grid(row=0, column=1, padx=10, pady=5, sticky="e")
        
        ctk.CTkLabel(stats_frame, text=f"Average:", anchor="w").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(stats_frame, text=f"{df['value'].mean():.2f}", anchor="e").grid(row=1, column=1, padx=10, pady=5, sticky="e")
        
        ctk.CTkLabel(stats_frame, text=f"Maximum:", anchor="w").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(stats_frame, text=f"{df['value'].max()}", anchor="e").grid(row=2, column=1, padx=10, pady=5, sticky="e")
        
        ctk.CTkLabel(stats_frame, text=f"Minimum:", anchor="w").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(stats_frame, text=f"{df['value'].min()}", anchor="e").grid(row=3, column=1, padx=10, pady=5, sticky="e")
        
        # Close button
        close_button = ctk.CTkButton(
            analysis_frame, 
            text="Close", 
            command=analysis_window.destroy
        )
        close_button.pack(pady=10)

    def plot_data(self):
        df = self.db.get_dataframe()
        if df.empty:
            messagebox.showinfo("Plot", "No data to plot.")
            return

        # Create a modern-looking plot
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot with better styling
        ax.plot(df['date'], df['value'], marker='o', linestyle='-', linewidth=2, color='#1f77b4')
        
        # Fill area under the line
        ax.fill_between(df['date'], df['value'], alpha=0.2, color='#1f77b4')
        
        # Add reference lines for normal range (example values)
        ax.axhspan(70, 140, alpha=0.2, color='green', label='Normal Range')
        
        # Styling
        ax.set_title("Glucose Levels Over Time", fontsize=16, fontweight='bold')
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Glucose Level", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add data point labels
        for x, y in zip(df['date'], df['value']):
            ax.annotate(f"{y:.1f}", 
                       (x, y), 
                       textcoords="offset points",
                       xytext=(0, 5), 
                       ha='center', 
                       fontsize=8)
        
        plt.tight_layout()
        plt.legend()
        plt.show()

    def delete_all(self):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete ALL data?")
        if confirm:
            self.db.delete_all()
            messagebox.showinfo("Deleted", "All data deleted.")
            self.show_data()

    def delete_by_id_prompt(self):
        # Create a custom dialog
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Delete Entry by ID")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame
        frame = ctk.CTkFrame(dialog)
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Label
        ctk.CTkLabel(frame, text="Enter ID to delete:").pack(pady=5)
        
        # Entry
        entry_id_var = ctk.StringVar()
        id_entry = ctk.CTkEntry(frame, textvariable=entry_id_var, width=100)
        id_entry.pack(pady=5)
        
        # Confirm function
        def confirm_delete():
            try:
                entry_id = int(entry_id_var.get())
                self.db.delete_by_id(entry_id)
                messagebox.showinfo("Deleted", f"Entry with ID {entry_id} deleted.")
                dialog.destroy()
                self.show_data()
            except ValueError:
                messagebox.showerror("Error", "Invalid ID.")
        
        # Delete button
        delete_button = ctk.CTkButton(
            frame, 
            text="Delete", 
            command=confirm_delete,
            fg_color="#dc3545"
        )
        delete_button.pack(pady=10)

# =====================[ Run App ]=========================
if __name__ == '__main__':
    app = ctk.CTk()
    glucose_app = GlucoseApp(app)
    app.mainloop()
