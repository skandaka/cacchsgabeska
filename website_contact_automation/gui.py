import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from scraper import simple_scrape_websites, advanced_scrape_websites
from emailer import send_email
import threading
from email_generator import generate_personalized_email
import webbrowser

class EnhancedEmailScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("Enhanced Email Scraper and Sender")

        self.create_widgets()
        self.scraped_data = []
        self.current_email_index = 0



    def create_widgets(self):
        # URL Entry
        ttk.Label(self.master, text="Website URLs (comma-separated):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.url_entry = ttk.Entry(self.master, width=100)
        self.url_entry.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

        # Scrape Button
        self.scrape_button = ttk.Button(self.master, text="Scrape", command=self.start_scraping)
        self.scrape_button.grid(row=2, column=0, padx=5, pady=5)

        # Advanced Scrape Checkbox
        self.advanced_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.master, text="Use Advanced Scraping", variable=self.advanced_var).grid(row=2, column=1,
                                                                                                    padx=5, pady=5)

        # Progress Bar
        self.progress = ttk.Progressbar(self.master, orient="horizontal", length=400, mode="indeterminate")
        self.progress.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

        # Results Display
        self.results_tree = ttk.Treeview(self.master, columns=("URL", "Business Name", "Email", "Extra Info"),
                                         show="headings")
        self.results_tree.heading("URL", text="URL")
        self.results_tree.heading("Business Name", text="Business Name")
        self.results_tree.heading("Email", text="Email")
        self.results_tree.heading("Extra Info", text="Extra Info")
        self.results_tree.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

        # Scrollbar for Results
        scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.results_tree.yview)
        scrollbar.grid(row=4, column=4, sticky="ns")
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        # Email Navigation
        nav_frame = ttk.Frame(self.master)
        nav_frame.grid(row=5, column=0, columnspan=4, pady=5)
        ttk.Button(nav_frame, text="<", command=self.prev_email).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text=">", command=self.next_email).pack(side=tk.LEFT, padx=5)

        # Email Template Entry (Scrollable Textbox)
        ttk.Label(self.master, text="Email Content:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.template_entry = scrolledtext.ScrolledText(self.master, width=100, height=15, wrap=tk.WORD)
        self.template_entry.grid(row=7, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

        # Action Buttons
        button_frame = ttk.Frame(self.master)
        button_frame.grid(row=8, column=0, columnspan=4, pady=10)
        ttk.Button(button_frame, text="Preview", command=self.preview_email).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Send", command=self.send_current_email).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Send All", command=self.send_all_emails).pack(side=tk.LEFT, padx=5)

        # Sender Email Configuration
        config_frame = ttk.Frame(self.master)
        config_frame.grid(row=9, column=0, columnspan=4, pady=10, sticky="ew")
        ttk.Label(config_frame, text="Your Email:").pack(side=tk.LEFT, padx=5)
        self.sender_email_entry = ttk.Entry(config_frame, width=50)
        self.sender_email_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(config_frame, text="Configure Email", command=self.show_email_instructions).pack(side=tk.LEFT,
                                                                                                    padx=5)

        # Configure grid weights for resizing
        for i in range(10):
            self.master.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.master.grid_columnconfigure(i, weight=1)

    def start_scraping(self):
        urls = [url.strip() for url in self.url_entry.get().split(',') if url.strip()]
        if not urls:
            messagebox.showerror("Error", "Please enter at least one URL.")
            return

        self.scraped_data = []
        self.results_tree.delete(*self.results_tree.get_children())
        self.progress.start()

        use_advanced = self.advanced_var.get()
        threading.Thread(target=self.scrape_websites, args=(urls, use_advanced), daemon=True).start()

    def scrape_websites(self, urls, use_advanced):
        if use_advanced:
            results = advanced_scrape_websites(urls)
        else:
            results = simple_scrape_websites(urls)

        for result in results:
            if result:
                url, business_name, email, extra_info = result
                self.scraped_data.append((url, business_name, email, extra_info))
                self.master.after(0, self.update_results, url, business_name, email, extra_info)
        self.master.after(0, self.scraping_complete)

    def update_results(self, url, business_name, email, extra_info):
        self.results_tree.insert("", tk.END, values=(url, business_name, email, extra_info))

    def scraping_complete(self):
        self.progress.stop()
        messagebox.showinfo("Scraping Complete", f"Found {len(self.scraped_data)} result(s).")
        if self.scraped_data:
            self.load_email_template(0)

    def prev_email(self):
        if self.scraped_data:
            self.current_email_index = (self.current_email_index - 1) % len(self.scraped_data)
            self.load_email_template(self.current_email_index)

    def next_email(self):
        if self.scraped_data:
            self.current_email_index = (self.current_email_index + 1) % len(self.scraped_data)
            self.load_email_template(self.current_email_index)

    def load_email_template(self, index):
        if 0 <= index < len(self.scraped_data):
            url, business_name, email, extra_info = self.scraped_data[index]
            template = generate_personalized_email(business_name, url, extra_info)
            self.template_entry.delete('1.0', tk.END)
            self.template_entry.insert(tk.END, template)

    def preview_email(self):
        if not self.scraped_data:
            messagebox.showerror("Error", "No data to preview.")
            return

        preview_window = tk.Toplevel(self.master)
        preview_window.title("Email Preview")
        preview_window.geometry("600x400")

        preview_text = scrolledtext.ScrolledText(preview_window, width=70, height=20, wrap=tk.WORD)
        preview_text.pack(padx=10, pady=10)

        email_content = self.template_entry.get("1.0", tk.END)
        preview_text.insert(tk.END, email_content)

    def send_current_email(self):
        if not self.scraped_data:
            messagebox.showerror("Error", "No data to send.")
            return

        _, _, email, _ = self.scraped_data[self.current_email_index]
        subject = "Web Development Services"
        message_text = self.template_entry.get("1.0", tk.END)

        try:
            send_email(email, subject, message_text)
            messagebox.showinfo("Success", f"Email sent successfully to {email}!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email to {email}: {str(e)}")

    def send_all_emails(self):
        if not self.scraped_data:
            messagebox.showerror("Error", "No data to send.")
            return

        for url, business_name, email, extra_info in self.scraped_data:
            subject = "Web Development Services"
            message_text = generate_personalized_email(business_name, url, extra_info)
            try:
                send_email(email, subject, message_text)
                print(f"Email sent successfully to {email}!")
            except Exception as e:
                print(f"Failed to send email to {email}: {str(e)}")

        messagebox.showinfo("Bulk Send Complete", f"Attempted to send emails to {len(self.scraped_data)} recipients.")

    def show_email_instructions(self):
        instructions = """
        To configure your email for sending:

        1. Go to https://console.developers.google.com/
        2. Create a new project or select an existing one
        3. Enable the Gmail API for your project
        4. Create credentials (OAuth client ID) for a desktop application
        5. Download the client configuration and save it as 'credentials.json' in the same directory as this application
        6. Update the SENDER_EMAIL in config.py with your Gmail address

        After completing these steps, restart the application and try sending an email.
        """
        messagebox.showinfo("Email Configuration Instructions", instructions)
        webbrowser.open("https://console.developers.google.com/")

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedEmailScraperApp(root)
    root.mainloop()