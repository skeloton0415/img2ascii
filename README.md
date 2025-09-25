# Image to ASCII Art Converter

A simple and user-friendly GUI application that converts images to ASCII art with multiple styling options.

## Features

- **Simple GUI Interface**: Easy-to-use interface built with tkinter
- **Multiple Character Sets**: Choose from different ASCII character sets for various styles
- **Adjustable Scale**: Control the width and height scaling of the output
- **Aspect Ratio Presets**: Quick buttons for common ratios (1:1, 4:3, 16:9, etc.)
- **Brightness Control**: Fine-tune image brightness before conversion
- **Color Inversion**: Option to invert the ASCII art colors
- **Live Preview**: See your ASCII art in real-time as you adjust settings
- **Font Size Control**: Adjustable character size in preview (Ctrl + Scroll)
- **Save to File**: Export your ASCII art to a text file
- **Multiple Image Formats**: Supports PNG, JPG, JPEG, GIF, BMP, and TIFF

## Character Sets Available

- **Standard**: Basic ASCII characters ( .:-=+*#%@ )
- **Detailed**: High-detail character set for complex images
- **Simple**: Minimal character set ( .# )
- **Blocks**: Block characters for bold effects ( ░▒▓█ )
- **Dots**: Dot-based characters ( ··●● )

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python img2ascii.py
   ```

2. **Select an Image**: Click "Browse" to choose an image file
3. **Adjust Settings**:
   - **Width/Height Scale**: Control the size of the ASCII output (20-200%)
   - **Character Set**: Choose from different ASCII character styles
   - **Invert Colors**: Toggle to reverse the brightness
4. **Preview**: The ASCII art will appear in the preview area
5. **Convert**: Click "Convert to ASCII" to process the image
6. **Save**: Click "Save ASCII Art" to export to a text file

## Tips for Best Results

- **High Contrast Images**: Work best for clear ASCII art
- **Adjust Scale**: Smaller scales (20-50%) create more detailed ASCII art
- **Character Sets**: 
  - Use "detailed" for complex images
  - Use "simple" for minimalist effects
  - Use "blocks" for bold, graphic styles
- **Aspect Ratio**: The app automatically adjusts for ASCII character proportions

## Supported Image Formats

- PNG
- JPG/JPEG
- GIF
- BMP
- TIFF

## Requirements

- Python 3.6+
- Pillow (PIL) library
- tkinter (usually included with Python)

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool!
