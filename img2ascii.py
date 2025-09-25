#!/usr/bin/env python3
"""
Image to ASCII Art Converter
A simple GUI application that converts images to ASCII art with multiple styling options.
"""

import sys
import os

# Hide console window on Windows
if sys.platform == "win32":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import numpy as np

class ImageToASCII:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to ASCII Art Converter")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.image_path = tk.StringVar()
        self.width_scale = tk.DoubleVar(value=100.0)
        self.height_scale = tk.DoubleVar(value=100.0)
        self.char_set = tk.StringVar(value="standard")
        self.invert_colors = tk.BooleanVar(value=False)
        self.brightness = tk.DoubleVar(value=0.0)  # -100 to +100
        self.font_size = tk.IntVar(value=6)  # Font size for preview display
        self.preview_enabled = False  # Control when preview updates
        
        # Cropping settings
        self.crop_enabled = tk.BooleanVar(value=False)
        self.crop_start_x = tk.DoubleVar(value=0.0)  # Percentage (0-100)
        self.crop_start_y = tk.DoubleVar(value=0.0)  # Percentage (0-100)
        self.crop_end_x = tk.DoubleVar(value=100.0)  # Percentage (0-100)
        self.crop_end_y = tk.DoubleVar(value=100.0)  # Percentage (0-100)
        
        # Image export settings
        self.export_font_size = tk.IntVar(value=12)  # Font size for image export
        self.export_bg_color = tk.StringVar(value="black")  # Background color
        self.export_text_color = tk.StringVar(value="white")  # Text color
        
        
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
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 25))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Select Image", padding="15")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Image:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 15))
        ttk.Entry(file_frame, textvariable=self.image_path, state="readonly", font=("Arial", 9)).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 15))
        ttk.Button(file_frame, text="Browse", command=self.browse_image, width=12).grid(row=0, column=2)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="15")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        settings_frame.columnconfigure(1, weight=1)
        
        # Width scale
        ttk.Label(settings_frame, text="Width Scale:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 15))
        width_scale = ttk.Scale(settings_frame, from_=0.001, to=100, variable=self.width_scale, 
                               orient=tk.HORIZONTAL)
        width_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 15))
        
        # Width input field
        width_entry = ttk.Entry(settings_frame, textvariable=self.width_scale, width=10, font=("Arial", 9))
        width_entry.grid(row=0, column=2, padx=(0, 15))
        width_entry.bind('<Return>', self.on_width_entry_change)
        width_entry.bind('<FocusOut>', self.on_width_entry_change)
        
        # Height scale
        ttk.Label(settings_frame, text="Height Scale:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 15))
        height_scale = ttk.Scale(settings_frame, from_=0.001, to=100, variable=self.height_scale, 
                                orient=tk.HORIZONTAL)
        height_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 15))
        
        # Height input field
        height_entry = ttk.Entry(settings_frame, textvariable=self.height_scale, width=10, font=("Arial", 9))
        height_entry.grid(row=1, column=2, padx=(0, 15))
        height_entry.bind('<Return>', self.on_height_entry_change)
        height_entry.bind('<FocusOut>', self.on_height_entry_change)
        
        # Aspect ratio buttons (single set for both scales)
        aspect_buttons_frame = ttk.Frame(settings_frame)
        aspect_buttons_frame.grid(row=0, column=3, rowspan=2, padx=(20, 0))
        
        ttk.Label(aspect_buttons_frame, text="Aspect Ratios:", font=("Arial", 9, "bold")).pack(pady=(0, 5))
        
        # First row of buttons
        row1_frame = ttk.Frame(aspect_buttons_frame)
        row1_frame.pack()
        ttk.Button(row1_frame, text="1:1", width=5, 
                  command=lambda: self.set_aspect_ratio(1, 1)).pack(side=tk.LEFT, padx=(0, 3), pady=(0, 3))
        ttk.Button(row1_frame, text="4:3", width=5, 
                  command=lambda: self.set_aspect_ratio(4, 3)).pack(side=tk.LEFT, padx=(0, 3), pady=(0, 3))
        ttk.Button(row1_frame, text="16:9", width=5, 
                  command=lambda: self.set_aspect_ratio(16, 9)).pack(side=tk.LEFT, padx=(0, 3), pady=(0, 3))
        
        # Second row of buttons
        row2_frame = ttk.Frame(aspect_buttons_frame)
        row2_frame.pack()
        ttk.Button(row2_frame, text="21:9", width=5, 
                  command=lambda: self.set_aspect_ratio(21, 9)).pack(side=tk.LEFT, padx=(0, 3), pady=(0, 3))
        ttk.Button(row2_frame, text="3:2", width=5, 
                  command=lambda: self.set_aspect_ratio(3, 2)).pack(side=tk.LEFT, padx=(0, 3), pady=(0, 3))
        ttk.Button(row2_frame, text="2:3", width=5, 
                  command=lambda: self.set_aspect_ratio(2, 3)).pack(side=tk.LEFT, padx=(0, 3), pady=(0, 3))
        
        # Character set
        ttk.Label(settings_frame, text="Character Set:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, padx=(0, 15))
        char_combo = ttk.Combobox(settings_frame, textvariable=self.char_set, 
                                 values=list(self.char_sets.keys()), state="readonly", width=15)
        char_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 15))
        
        # Invert colors
        ttk.Checkbutton(settings_frame, text="Invert Colors", variable=self.invert_colors).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(15, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=(20, 0))
        
        # Center the buttons
        buttons_container = ttk.Frame(buttons_frame)
        buttons_container.pack()
        
        ttk.Button(buttons_container, text="Preview ASCII Art", command=self.open_preview_window, width=18).pack(side=tk.LEFT)
        
    def ascii_to_image(self, ascii_text, font_size=None, bg_color=None, text_color=None):
        """Convert ASCII art to an image"""
        if font_size is None:
            font_size = self.export_font_size.get()
        if bg_color is None:
            bg_color = self.export_bg_color.get()
        if text_color is None:
            text_color = self.export_text_color.get()
            
        # Split ASCII text into lines
        lines = ascii_text.split('\n')
        if not lines:
            return None
            
        # Calculate image dimensions
        max_line_length = max(len(line) for line in lines) if lines else 0
        line_height = font_size + 2  # Add some padding
        
        # Create image
        img_width = max_line_length * (font_size // 2)  # Approximate character width
        img_height = len(lines) * line_height
        
        # Create image with background color
        if bg_color.lower() == "black":
            bg_rgb = (0, 0, 0)
        elif bg_color.lower() == "white":
            bg_rgb = (255, 255, 255)
        elif bg_color.lower() == "transparent":
            bg_rgb = (255, 255, 255, 0)  # RGBA for transparency
        else:
            bg_rgb = (0, 0, 0)  # Default to black
            
        if bg_color.lower() == "transparent":
            image = Image.new('RGBA', (img_width, img_height), bg_rgb)
        else:
            image = Image.new('RGB', (img_width, img_height), bg_rgb)
            
        draw = ImageDraw.Draw(image)
        
        # Try to use a monospace font
        try:
            font = ImageFont.truetype("consola.ttf", font_size)
        except (OSError, IOError):
            try:
                font = ImageFont.truetype("cour.ttf", font_size)
            except (OSError, IOError):
                try:
                    font = ImageFont.truetype("monaco.ttf", font_size)
                except (OSError, IOError):
                    try:
                        # Try common system fonts
                        font = ImageFont.truetype("DejaVuSansMono.ttf", font_size)
                    except (OSError, IOError):
                        font = ImageFont.load_default()
        
        # Set text color
        if text_color.lower() == "white":
            text_rgb = (255, 255, 255)
        elif text_color.lower() == "black":
            text_rgb = (0, 0, 0)
        elif text_color.lower() == "green":
            text_rgb = (0, 255, 0)
        else:
            text_rgb = (255, 255, 255)  # Default to white
            
        # Draw text
        y_position = 0
        for line in lines:
            draw.text((0, y_position), line, font=font, fill=text_rgb)
            y_position += line_height
            
        return image
        
    def export_as_image(self):
        """Export ASCII art as an image file"""
        if not self.image_path.get():
            messagebox.showerror("Error", "Please select an image first.")
            return
            
        # Generate ASCII art
        ascii_art = self.image_to_ascii(self.image_path.get())
        if not ascii_art or ascii_art.startswith("Please select"):
            messagebox.showerror("Error", "Please preview the ASCII art first.")
            return
            
        # Show export options dialog
        self.show_export_options_dialog(ascii_art)
        
    def show_export_options_dialog(self, ascii_art):
        """Show dialog with export options"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Export Options")
        dialog.geometry("450x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Export ASCII Art as Image", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Font size
        font_frame = ttk.LabelFrame(main_frame, text="Font Settings", padding="10")
        font_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(font_frame, text="Font Size:", font=("Arial", 10)).pack(anchor=tk.W)
        font_size_frame = ttk.Frame(font_frame)
        font_size_frame.pack(fill=tk.X, pady=(5, 0))
        
        font_size_scale = ttk.Scale(font_size_frame, from_=8, to=48, variable=self.export_font_size, orient=tk.HORIZONTAL)
        font_size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        font_size_label = ttk.Label(font_size_frame, textvariable=self.export_font_size, font=("Arial", 10, "bold"))
        font_size_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Colors
        color_frame = ttk.LabelFrame(main_frame, text="Color Settings", padding="10")
        color_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Background color
        bg_frame = ttk.Frame(color_frame)
        bg_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(bg_frame, text="Background Color:", font=("Arial", 10)).pack(side=tk.LEFT)
        bg_combo = ttk.Combobox(bg_frame, textvariable=self.export_bg_color, 
                               values=["black", "white", "transparent"], state="readonly", width=12)
        bg_combo.pack(side=tk.RIGHT)
        
        # Text color
        text_frame = ttk.Frame(color_frame)
        text_frame.pack(fill=tk.X)
        ttk.Label(text_frame, text="Text Color:", font=("Arial", 10)).pack(side=tk.LEFT)
        text_combo = ttk.Combobox(text_frame, textvariable=self.export_text_color, 
                                 values=["white", "black", "green"], state="readonly", width=12)
        text_combo.pack(side=tk.RIGHT)
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=(20, 0))
        
        ttk.Button(buttons_frame, text="Export", command=lambda: self.save_image_file(ascii_art, dialog), 
                  width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancel", command=dialog.destroy, 
                  width=12).pack(side=tk.LEFT)
        
    def save_image_file(self, ascii_art, dialog):
        """Save ASCII art as image file"""
        filetypes = [
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=filetypes,
            title="Save ASCII Art as Image"
        )
        
        if filename:
            try:
                # Create image from ASCII art
                image = self.ascii_to_image(ascii_art)
                if image:
                    # Save image
                    image.save(filename)
                    messagebox.showinfo("Success", f"ASCII art saved as image: {filename}")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to create image from ASCII art.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
        
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
            if 0.001 <= value <= 100:
                # Don't auto-update preview, just validate
                pass
            else:
                messagebox.showerror("Invalid Value", "Width scale must be between 0.001 and 100")
                self.width_scale.set(100.0)  # Reset to default
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number")
            self.width_scale.set(100.0)  # Reset to default
            
    def on_height_entry_change(self, event=None):
        """Handle height entry field changes"""
        try:
            value = float(self.height_scale.get())
            if 0.001 <= value <= 100:
                # Don't auto-update preview, just validate
                pass
            else:
                messagebox.showerror("Invalid Value", "Height scale must be between 0.001 and 100")
                self.height_scale.set(100.0)  # Reset to default
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number")
            self.height_scale.set(100.0)  # Reset to default
            
    def set_aspect_ratio(self, width_value, height_value):
        """Set width and height scales to specific numeric values"""
        # Clamp to valid range (consistent with input validation)
        width_value = max(0.001, min(100, width_value))
        height_value = max(0.001, min(100, height_value))
        
        # Update scale variables directly
        self.width_scale.set(width_value)
        self.height_scale.set(height_value)
            
    def image_to_ascii(self, image_path, width_scale=None, height_scale=None, char_set=None, invert=None, brightness=None, crop_enabled=None, crop_start_x=None, crop_start_y=None, crop_end_x=None, crop_end_y=None):
        """Convert image to ASCII art"""
        if not os.path.exists(image_path):
            return "Please select a valid image file."
            
        try:
            # Load image and convert to grayscale
            image = Image.open(image_path).convert('L')
            
            # Apply cropping if enabled
            if crop_enabled is None:
                crop_enabled = self.crop_enabled.get()
            
            if crop_enabled:
                if crop_start_x is None:
                    crop_start_x = self.crop_start_x.get()
                if crop_start_y is None:
                    crop_start_y = self.crop_start_y.get()
                if crop_end_x is None:
                    crop_end_x = self.crop_end_x.get()
                if crop_end_y is None:
                    crop_end_y = self.crop_end_y.get()
                
                # Convert percentages to pixel coordinates
                start_x = int(image.width * crop_start_x / 100)
                start_y = int(image.height * crop_start_y / 100)
                end_x = int(image.width * crop_end_x / 100)
                end_y = int(image.height * crop_end_y / 100)
                
                # Ensure valid crop coordinates
                start_x = max(0, min(start_x, image.width - 1))
                start_y = max(0, min(start_y, image.height - 1))
                end_x = max(start_x + 1, min(end_x, image.width))
                end_y = max(start_y + 1, min(end_y, image.height))
                
                # Crop the image
                image = image.crop((start_x, start_y, end_x, end_y))
            
            # Apply brightness adjustment
            if brightness is None:
                brightness = self.brightness.get()
            
            if brightness != 0:
                # Apply brightness adjustment
                img_array = np.array(image)
                img_array = img_array + brightness
                img_array = np.clip(img_array, 0, 255)
                image = Image.fromarray(img_array.astype('uint8'))
            
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
            
            # Use LANCZOS resampling with backward compatibility
            try:
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            except AttributeError:
                # Fallback for older Pillow versions
                image = image.resize((new_width, new_height), Image.LANCZOS)
            
            # Get character set
            if char_set is None:
                char_set = self.char_sets[self.char_set.get()]
            else:
                char_set = self.char_sets.get(char_set, self.char_sets["standard"])
                
            # Convert to ASCII efficiently
            pixels = list(image.getdata())
            
            # Generate ASCII art
            ascii_chars = []
            for i in range(0, len(pixels), new_width):
                row = pixels[i:i + new_width]
                ascii_row = ""
                for pixel in row:
                    gray_value = pixel
                    char_index = int(gray_value * (len(char_set) - 1) / 255)
                    
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
        status_label.config(text="ASCII Art Preview - Hold Ctrl + Scroll to change font size")
        
        # Create text widget for preview
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        preview_text = tk.Text(text_frame, wrap=tk.NONE, font=("Courier", self.font_size.get()), 
                              bg='black', fg='white', insertbackground='white')
        scrollbar_v = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=preview_text.yview)
        scrollbar_h = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=preview_text.xview)
        
        preview_text.configure(yscrollcommand=scrollbar_v.set,
                              xscrollcommand=scrollbar_h.set)
        
        preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Insert ASCII art
        self.current_ascii_art = ascii_art
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
        
        # Preview controls frame
        controls_frame = ttk.Frame(buttons_frame)
        controls_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Character set control
        ttk.Label(controls_frame, text="Character Set:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 8))
        char_combo = ttk.Combobox(controls_frame, textvariable=self.char_set, 
                                 values=list(self.char_sets.keys()), state="readonly", width=12)
        char_combo.pack(side=tk.LEFT, padx=(0, 15))
        char_combo.bind('<<ComboboxSelected>>', lambda event: self.update_preview_from_controls(preview_text, status_label))
        
        # Invert colors control
        invert_check = ttk.Checkbutton(controls_frame, text="Invert Colors", variable=self.invert_colors,
                                     command=lambda: self.update_preview_from_controls(preview_text, status_label))
        invert_check.pack(side=tk.LEFT, padx=(0, 15))
        
        
        # Brightness control
        brightness_frame = ttk.Frame(controls_frame)
        brightness_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(brightness_frame, text="Brightness:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 8))
        brightness_slider = ttk.Scale(brightness_frame, from_=-100, to=100, variable=self.brightness, 
                                     orient=tk.HORIZONTAL, length=120)
        brightness_slider.pack(side=tk.LEFT, padx=(0, 8))
        brightness_slider.bind('<Motion>', lambda event: self.update_preview_from_controls(preview_text, status_label))
        brightness_slider.bind('<ButtonRelease-1>', lambda event: self.update_preview_from_controls(preview_text, status_label))
        
        # Brightness input field
        brightness_entry = ttk.Entry(brightness_frame, textvariable=self.brightness, width=8, font=("Arial", 9))
        brightness_entry.pack(side=tk.LEFT, padx=(0, 5))
        brightness_entry.bind('<Return>', lambda event: self.on_brightness_entry_change(preview_text, status_label))
        brightness_entry.bind('<FocusOut>', lambda event: self.on_brightness_entry_change(preview_text, status_label))
        
        # Cropping controls - create a separate row for better layout
        crop_frame = ttk.Frame(main_frame)
        crop_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Cropping enable checkbox
        crop_enable_frame = ttk.Frame(crop_frame)
        crop_enable_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        crop_check = ttk.Checkbutton(crop_enable_frame, text="Enable Cropping", variable=self.crop_enabled,
                                   command=lambda: self.update_preview_from_controls(preview_text, status_label))
        crop_check.pack(side=tk.LEFT)
        
        # Crop preset buttons
        presets_frame = ttk.Frame(crop_frame)
        presets_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(presets_frame, text="Presets:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(presets_frame, text="Center", width=6, 
                  command=lambda: self.set_crop_preset("center")).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(presets_frame, text="Top", width=6, 
                  command=lambda: self.set_crop_preset("top")).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(presets_frame, text="Bottom", width=6, 
                  command=lambda: self.set_crop_preset("bottom")).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(presets_frame, text="Left", width=6, 
                  command=lambda: self.set_crop_preset("left")).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(presets_frame, text="Right", width=6, 
                  command=lambda: self.set_crop_preset("right")).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(presets_frame, text="Reset", width=6, 
                  command=lambda: self.set_crop_preset("reset")).pack(side=tk.LEFT, padx=(0, 10))
        
        # Crop coordinate inputs
        coords_frame = ttk.Frame(crop_frame)
        coords_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(coords_frame, text="Crop Area (%):", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Start coordinates
        start_frame = ttk.Frame(coords_frame)
        start_frame.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(start_frame, text="Start:", font=("Arial", 8)).pack(side=tk.LEFT)
        ttk.Entry(start_frame, textvariable=self.crop_start_x, width=6, font=("Arial", 8)).pack(side=tk.LEFT, padx=(2, 2))
        ttk.Entry(start_frame, textvariable=self.crop_start_y, width=6, font=("Arial", 8)).pack(side=tk.LEFT, padx=(2, 0))
        
        # End coordinates
        end_frame = ttk.Frame(coords_frame)
        end_frame.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(end_frame, text="End:", font=("Arial", 8)).pack(side=tk.LEFT)
        ttk.Entry(end_frame, textvariable=self.crop_end_x, width=6, font=("Arial", 8)).pack(side=tk.LEFT, padx=(2, 2))
        ttk.Entry(end_frame, textvariable=self.crop_end_y, width=6, font=("Arial", 8)).pack(side=tk.LEFT, padx=(2, 0))
        
        # Bind crop coordinate changes
        for entry in [start_frame.winfo_children()[1], start_frame.winfo_children()[2], 
                     end_frame.winfo_children()[1], end_frame.winfo_children()[2]]:
            entry.bind('<Return>', lambda event: self.on_crop_entry_change(preview_text, status_label))
            entry.bind('<FocusOut>', lambda event: self.on_crop_entry_change(preview_text, status_label))
        
        # Action buttons frame
        action_buttons_frame = ttk.Frame(buttons_frame)
        action_buttons_frame.pack(side=tk.RIGHT)
        
        ttk.Button(action_buttons_frame, text="Copy to Clipboard", 
                  command=lambda: self.copy_to_clipboard_dynamic(), width=15).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(action_buttons_frame, text="Save ASCII Art", 
                  command=lambda: self.save_ascii_from_preview_dynamic(), width=15).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(action_buttons_frame, text="Export as Image", 
                  command=lambda: self.export_as_image_from_preview(), width=15).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(action_buttons_frame, text="Close", 
                  command=preview_window.destroy, width=12).pack(side=tk.LEFT)
        
        self.preview_enabled = True
        
        # Store references for dynamic scaling
        self.current_preview_window = preview_window
        self.current_preview_text = preview_text
        self.current_status_label = status_label
        self.current_ascii_art = ascii_art
        
    def export_as_image_from_preview(self):
        """Export ASCII art from preview window as image"""
        if not hasattr(self, 'current_ascii_art') or not self.current_ascii_art:
            messagebox.showerror("Error", "No ASCII art available to export.")
            return
            
        # Show export options dialog
        self.show_export_options_dialog(self.current_ascii_art)
        
    def update_preview_from_controls(self, preview_text, status_label):
        """Update preview when character set or invert colors changes"""
        # Update status
        status_label.config(text="Updating ASCII art...")
        
        # Force GUI update
        self.root.update_idletasks()
        
        # Regenerate ASCII art with current settings
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
            char_set_name = self.char_set.get()
            invert_status = "Inverted" if self.invert_colors.get() else "Normal"
            brightness_value = self.brightness.get()
            
            # Add crop information to status
            crop_info = ""
            if self.crop_enabled.get():
                crop_info = f" | Cropped: {self.crop_start_x.get():.0f}%,{self.crop_start_y.get():.0f}% to {self.crop_end_x.get():.0f}%,{self.crop_end_y.get():.0f}%"
            
            status_label.config(text=f"ASCII Art Preview - {char_set_name} ({invert_status}) Brightness: {brightness_value:.0f}{crop_info}")
            
        except Exception as e:
            status_label.config(text=f"Error updating: {str(e)}")
        
    def on_brightness_entry_change(self, preview_text, status_label):
        """Handle brightness entry field changes"""
        try:
            value = float(self.brightness.get())
            if -100 <= value <= 100:
                # Valid value, update preview
                self.update_preview_from_controls(preview_text, status_label)
            else:
                messagebox.showerror("Invalid Value", "Brightness must be between -100 and 100")
                self.brightness.set(0.0)  # Reset to default
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number")
            self.brightness.set(0.0)  # Reset to default
    
    def set_crop_preset(self, preset_type):
        """Set crop coordinates based on preset type"""
        if preset_type == "center":
            # Center crop - crop 25% from each side
            self.crop_start_x.set(25.0)
            self.crop_start_y.set(25.0)
            self.crop_end_x.set(75.0)
            self.crop_end_y.set(75.0)
        elif preset_type == "top":
            # Top half
            self.crop_start_x.set(0.0)
            self.crop_start_y.set(0.0)
            self.crop_end_x.set(100.0)
            self.crop_end_y.set(50.0)
        elif preset_type == "bottom":
            # Bottom half
            self.crop_start_x.set(0.0)
            self.crop_start_y.set(50.0)
            self.crop_end_x.set(100.0)
            self.crop_end_y.set(100.0)
        elif preset_type == "left":
            # Left half
            self.crop_start_x.set(0.0)
            self.crop_start_y.set(0.0)
            self.crop_end_x.set(50.0)
            self.crop_end_y.set(100.0)
        elif preset_type == "right":
            # Right half
            self.crop_start_x.set(50.0)
            self.crop_start_y.set(0.0)
            self.crop_end_x.set(100.0)
            self.crop_end_y.set(100.0)
        elif preset_type == "reset":
            # Reset to full image
            self.crop_start_x.set(0.0)
            self.crop_start_y.set(0.0)
            self.crop_end_x.set(100.0)
            self.crop_end_y.set(100.0)
        
        # Update preview if cropping is enabled
        if self.crop_enabled.get():
            if hasattr(self, 'current_preview_text') and hasattr(self, 'current_status_label'):
                self.update_preview_from_controls(self.current_preview_text, self.current_status_label)
    
    def on_crop_entry_change(self, preview_text, status_label):
        """Handle crop coordinate entry field changes"""
        try:
            # Validate all crop coordinates
            start_x = float(self.crop_start_x.get())
            start_y = float(self.crop_start_y.get())
            end_x = float(self.crop_end_x.get())
            end_y = float(self.crop_end_y.get())
            
            # Validate ranges
            if not (0 <= start_x <= 100 and 0 <= start_y <= 100 and 
                    0 <= end_x <= 100 and 0 <= end_y <= 100):
                messagebox.showerror("Invalid Value", "Crop coordinates must be between 0 and 100")
                self.reset_crop_to_default()
                return
            
            # Validate that end coordinates are greater than start coordinates
            if start_x >= end_x or start_y >= end_y:
                messagebox.showerror("Invalid Value", "End coordinates must be greater than start coordinates")
                self.reset_crop_to_default()
                return
            
            # Valid values, update preview if cropping is enabled
            if self.crop_enabled.get():
                self.update_preview_from_controls(preview_text, status_label)
                
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for crop coordinates")
            self.reset_crop_to_default()
    
    def reset_crop_to_default(self):
        """Reset crop coordinates to default values"""
        self.crop_start_x.set(0.0)
        self.crop_start_y.set(0.0)
        self.crop_end_x.set(100.0)
        self.crop_end_y.set(100.0)
        
    def scale_with_mouse(self, event, preview_text, status_label):
        """Change font size using mouse wheel with Ctrl key - maintains aspect ratio"""
        # Only process if we have a preview window open
        if not hasattr(self, 'current_preview_window') or not self.current_preview_window.winfo_exists():
            return
            
        # Determine font size change direction
        if event.delta > 0:  # Scroll up - increase font size
            font_change = 1
        else:  # Scroll down - decrease font size
            font_change = -1
            
        # Get current font size
        current_font_size = self.font_size.get()
        new_font_size = current_font_size + font_change
        
        # Clamp to valid range (2 to 20)
        new_font_size = max(2, min(20, new_font_size))
        
        # Update font size variable
        self.font_size.set(new_font_size)
        
        # Update preview text font
        preview_text.config(font=("Courier", new_font_size))
        
        # Update status
        char_set_name = self.char_set.get()
        invert_status = "Inverted" if self.invert_colors.get() else "Normal"
        brightness_value = self.brightness.get()
        
        # Add crop information to status
        crop_info = ""
        if self.crop_enabled.get():
            crop_info = f" | Cropped: {self.crop_start_x.get():.0f}%,{self.crop_start_y.get():.0f}% to {self.crop_end_x.get():.0f}%,{self.crop_end_y.get():.0f}%"
        
        status_label.config(text=f"ASCII Art Preview - {char_set_name} ({invert_status}) Brightness: {brightness_value:.0f} Font: {new_font_size}{crop_info}")
        
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
        
def main():
    """Main function"""
    root = tk.Tk()
    app = ImageToASCII(root)
    root.mainloop()

if __name__ == "__main__":
    main()
