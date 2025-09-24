#!/usr/bin/env python3
"""
Image to ASCII Art Converter
A simple GUI application that converts images to ASCII art with multiple styling options.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import sys

class ImageToASCII:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to ASCII Art Converter")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.image_path = tk.StringVar()
        self.ascii_text = tk.StringVar()
        self.width_scale = tk.DoubleVar(value=100.0)
        self.height_scale = tk.DoubleVar(value=100.0)
        self.char_set = tk.StringVar(value="standard")
        self.invert_colors = tk.BooleanVar(value=False)
        self.preview_enabled = False  # Control when preview updates
        
        # ASCII character sets
        self.char_sets = {
            "standard": " .:-=+*#%@",
            "detailed": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
            "simple": " .#",
            "blocks": " ░▒▓█",
            "dots": " ··●●",
            "custom": " .:-=+*#%@"
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Image to ASCII Art Converter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Select Image", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Image:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.image_path, state="readonly").grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="Browse", command=self.browse_image).grid(row=0, column=2)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # Width scale
        ttk.Label(settings_frame, text="Width Scale:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        width_scale = ttk.Scale(settings_frame, from_=0.001, to=1000, variable=self.width_scale, 
                               orient=tk.HORIZONTAL)
        width_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Width input field
        width_entry = ttk.Entry(settings_frame, textvariable=self.width_scale, width=8)
        width_entry.grid(row=0, column=2, padx=(0, 10))
        width_entry.bind('<Return>', self.on_width_entry_change)
        width_entry.bind('<FocusOut>', self.on_width_entry_change)
        
        # Height scale
        ttk.Label(settings_frame, text="Height Scale:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        height_scale = ttk.Scale(settings_frame, from_=0.001, to=1000, variable=self.height_scale, 
                                orient=tk.HORIZONTAL)
        height_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Height input field
        height_entry = ttk.Entry(settings_frame, textvariable=self.height_scale, width=8)
        height_entry.grid(row=1, column=2, padx=(0, 10))
        height_entry.bind('<Return>', self.on_height_entry_change)
        height_entry.bind('<FocusOut>', self.on_height_entry_change)
        
        # Aspect ratio buttons (single set for both scales)
        aspect_buttons_frame = ttk.Frame(settings_frame)
        aspect_buttons_frame.grid(row=0, column=3, rowspan=2, padx=(10, 0))
        ttk.Button(aspect_buttons_frame, text="1:1", width=4, 
                  command=lambda: self.set_aspect_ratio(1, 1)).pack(side=tk.TOP, padx=(0, 2), pady=(0, 2))
        ttk.Button(aspect_buttons_frame, text="4:3", width=4, 
                  command=lambda: self.set_aspect_ratio(4, 3)).pack(side=tk.TOP, padx=(0, 2), pady=(0, 2))
        ttk.Button(aspect_buttons_frame, text="16:9", width=4, 
                  command=lambda: self.set_aspect_ratio(16, 9)).pack(side=tk.TOP, padx=(0, 2), pady=(0, 2))
        ttk.Button(aspect_buttons_frame, text="21:9", width=4, 
                  command=lambda: self.set_aspect_ratio(21, 9)).pack(side=tk.TOP, padx=(0, 2), pady=(0, 2))
        ttk.Button(aspect_buttons_frame, text="3:2", width=4, 
                  command=lambda: self.set_aspect_ratio(3, 2)).pack(side=tk.TOP, padx=(0, 2), pady=(0, 2))
        ttk.Button(aspect_buttons_frame, text="2:3", width=4, 
                  command=lambda: self.set_aspect_ratio(2, 3)).pack(side=tk.TOP, padx=(0, 2), pady=(0, 2))
        
        # Character set
        ttk.Label(settings_frame, text="Character Set:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        char_combo = ttk.Combobox(settings_frame, textvariable=self.char_set, 
                                 values=list(self.char_sets.keys()), state="readonly")
        char_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Invert colors
        ttk.Checkbutton(settings_frame, text="Invert Colors", variable=self.invert_colors).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="Convert to ASCII", command=self.convert_image).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Save ASCII Art", command=self.save_ascii).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Preview", command=self.open_preview_window).pack(side=tk.LEFT)
        
    def browse_image(self):
        """Browse for image file"""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Image", filetypes=filetypes)
        if filename:
            self.image_path.set(filename)
            self.preview_enabled = False  # Reset preview state
            
    def on_width_entry_change(self, event=None):
        """Handle width entry field changes"""
        try:
            value = float(self.width_scale.get())
            if 0.001 <= value <= 1000:
                # Don't auto-update preview, just validate
                pass
            else:
                messagebox.showerror("Invalid Value", "Width scale must be between 0.001 and 1000")
                self.width_scale.set(100.0)  # Reset to default
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number")
            self.width_scale.set(100.0)  # Reset to default
            
    def on_height_entry_change(self, event=None):
        """Handle height entry field changes"""
        try:
            value = float(self.height_scale.get())
            if 0.001 <= value <= 1000:
                # Don't auto-update preview, just validate
                pass
            else:
                messagebox.showerror("Invalid Value", "Height scale must be between 0.001 and 1000")
                self.height_scale.set(100.0)  # Reset to default
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number")
            self.height_scale.set(100.0)  # Reset to default
            
    def set_aspect_ratio(self, width_value, height_value):
        """Set width and height scales to specific numeric values"""
        # Clamp to valid range
        width_value = max(0.001, min(1000, width_value))
        height_value = max(0.001, min(1000, height_value))
        
        # Update scale variables directly
        self.width_scale.set(width_value)
        self.height_scale.set(height_value)
            
    def image_to_ascii(self, image_path, width_scale=None, height_scale=None, char_set=None, invert=None):
        """Convert image to ASCII art with support for larger images"""
        if not os.path.exists(image_path):
            return "Please select a valid image file."
            
        try:
            # Load image
            image = Image.open(image_path)
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Resize image
            if width_scale is None:
                width_scale = self.width_scale.get()
            if height_scale is None:
                height_scale = self.height_scale.get()
                
            # Calculate new dimensions maintaining original aspect ratio
            new_width = int(image.width * width_scale / 100)
            new_height = int(image.height * height_scale / 100)
            
            # Ensure minimum dimensions of 1x1
            new_width = max(1, new_width)
            new_height = max(1, new_height)
                
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Get character set
            if char_set is None:
                char_set = self.char_sets[self.char_set.get()]
            else:
                char_set = self.char_sets.get(char_set, self.char_sets["standard"])
                
            # Convert to ASCII efficiently
            ascii_chars = []
            pixels = list(image.getdata())
            
            # Process in chunks for large images
            chunk_size = 1000  # Process 1000 pixels at a time
            
            for i in range(0, len(pixels), new_width):
                row = pixels[i:i + new_width]
                ascii_row = ""
                for pixel in row:
                    # Normalize pixel value to character set index
                    char_index = int(pixel * (len(char_set) - 1) / 255)
                    
                    # Invert if requested
                    if invert is None:
                        invert = self.invert_colors.get()
                    if invert:
                        char_index = len(char_set) - 1 - char_index
                        
                    ascii_row += char_set[char_index]
                ascii_chars.append(ascii_row)
                
            return "\n".join(ascii_chars)
            
        except Exception as e:
            return f"Error converting image: {str(e)}"
            
    def convert_image(self):
        """Convert the selected image to ASCII"""
        if not self.image_path.get():
            messagebox.showerror("Error", "Please select an image file first.")
            return
            
        ascii_art = self.image_to_ascii(self.image_path.get())
        self.ascii_text.set(ascii_art)
        
        # Update preview
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, ascii_art)
        
        messagebox.showinfo("Success", "Image converted to ASCII art!")
        
    def open_preview_window(self):
        """Open ASCII art preview in a separate window"""
        if not self.image_path.get():
            messagebox.showerror("Error", "Please select an image file first.")
            return
            
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("ASCII Art Preview")
        preview_window.geometry("1000x700")
        preview_window.configure(bg='#f0f0f0')
        
        # Create main frame
        main_frame = ttk.Frame(preview_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        status_label = ttk.Label(main_frame, text="Processing image... Please wait.")
        status_label.pack(pady=(0, 10))
        
        # Force GUI update
        preview_window.update()
        
        # Generate ASCII art
        ascii_art = self.image_to_ascii(self.image_path.get())
        
        # Update status
        status_label.config(text="ASCII Art Preview - Hold Ctrl + Scroll to scale")
        
        # Create text widget for preview
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        preview_text = tk.Text(text_frame, wrap=tk.NONE, font=("Courier", 6), 
                              bg='black', fg='white')
        scrollbar_v = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=preview_text.yview)
        scrollbar_h = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=preview_text.xview)
        
        preview_text.configure(yscrollcommand=scrollbar_v.set,
                              xscrollcommand=scrollbar_h.set)
        
        preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Insert ASCII art
        preview_text.insert(1.0, ascii_art)
        preview_text.config(state=tk.DISABLED)  # Make read-only
        
        # Bind mouse wheel events for scaling
        preview_text.bind("<Control-MouseWheel>", lambda event: self.scale_with_mouse(event, preview_text, status_label))
        preview_window.bind("<Control-MouseWheel>", lambda event: self.scale_with_mouse(event, preview_text, status_label))
        
        # Also bind to the main window for global Ctrl+scroll
        self.root.bind("<Control-MouseWheel>", lambda event: self.scale_with_mouse(event, preview_text, status_label))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Copy to Clipboard", 
                  command=lambda: self.copy_to_clipboard_dynamic()).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Save ASCII Art", 
                  command=lambda: self.save_ascii_from_preview_dynamic()).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Close", 
                  command=preview_window.destroy).pack(side=tk.RIGHT)
        
        self.preview_enabled = True
        
        # Store references for dynamic scaling
        self.current_preview_window = preview_window
        self.current_preview_text = preview_text
        self.current_status_label = status_label
        self.current_ascii_art = ascii_art
        
    def scale_with_mouse(self, event, preview_text, status_label):
        """Scale the ASCII art using mouse wheel with Ctrl key - updates on every scroll"""
        # Only process if we have a preview window open
        if not hasattr(self, 'current_preview_window') or not self.current_preview_window.winfo_exists():
            return
            
        # Determine scaling direction
        if event.delta > 0:  # Scroll up - zoom in
            scale_factor = 1.05  # Smaller increments for smoother scaling
        else:  # Scroll down - zoom out
            scale_factor = 0.95
            
        # Update scale values
        current_width = self.width_scale.get()
        current_height = self.height_scale.get()
        
        new_width = current_width * scale_factor
        new_height = current_height * scale_factor
        
        # Clamp to valid range
        new_width = max(0.001, min(1000, new_width))
        new_height = max(0.001, min(1000, new_height))
        
        # Update scale variables
        self.width_scale.set(new_width)
        self.height_scale.set(new_height)
        
        # Update status immediately
        status_label.config(text=f"Scaling... Width: {new_width:.1f}%, Height: {new_height:.1f}%")
        
        # Force GUI update to show status change
        self.root.update_idletasks()
        
        # Regenerate ASCII art
        try:
            new_ascii_art = self.image_to_ascii(self.image_path.get())
            
            # Update preview text
            preview_text.config(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)
            preview_text.insert(1.0, new_ascii_art)
            preview_text.config(state=tk.DISABLED)
            
            # Update stored ASCII art
            self.current_ascii_art = new_ascii_art
            
            # Update status
            status_label.config(text=f"ASCII Art Preview - Width: {new_width:.1f}%, Height: {new_height:.1f}%")
            
        except Exception as e:
            status_label.config(text=f"Error scaling: {str(e)}")
        
    def copy_to_clipboard_dynamic(self):
        """Copy current ASCII art to clipboard"""
        if hasattr(self, 'current_ascii_art'):
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_ascii_art)
            messagebox.showinfo("Success", "ASCII art copied to clipboard!")
        else:
            messagebox.showerror("Error", "No ASCII art to copy.")
            
    def save_ascii_from_preview_dynamic(self):
        """Save current ASCII art from preview window"""
        if not hasattr(self, 'current_ascii_art'):
            messagebox.showerror("Error", "No ASCII art to save.")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save ASCII Art",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.current_ascii_art)
                messagebox.showinfo("Success", f"ASCII art saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
        
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Success", "ASCII art copied to clipboard!")
        
    def save_ascii_from_preview(self, ascii_art):
        """Save ASCII art from preview window"""
        filename = filedialog.asksaveasfilename(
            title="Save ASCII Art",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(ascii_art)
                messagebox.showinfo("Success", f"ASCII art saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
        
    def save_ascii(self):
        """Save ASCII art to file"""
        if not self.ascii_text.get():
            messagebox.showerror("Error", "No ASCII art to save. Please convert an image first.")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save ASCII Art",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.ascii_text.get())
                messagebox.showinfo("Success", f"ASCII art saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

def main():
    """Main function"""
    root = tk.Tk()
    app = ImageToASCII(root)
    root.mainloop()

if __name__ == "__main__":
    main()
