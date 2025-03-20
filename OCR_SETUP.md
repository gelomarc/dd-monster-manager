# OCR Setup Guide for D&D Monster Manager

This guide explains how to set up the OCR (Optical Character Recognition) functionality for automatically extracting monster stats from statblock images.

## Simple Setup (Recommended)

The application includes a simplified OCR implementation that requires minimal dependencies:

1. Install Tesseract OCR (see instructions below)
2. Install basic Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

This setup will allow you to extract monster data from statblock images with good results for clear, high-quality images.

## Advanced Setup (Optional)

For improved OCR accuracy, especially with lower-quality images, you can install additional dependencies:

```bash
pip install opencv-python==4.8.0.76 numpy==1.25.2
```

If you encounter installation issues with these packages:
- Try `pip install opencv-python-headless` instead
- Or try older versions like `opencv-python==4.5.5.64`

## Installing Tesseract OCR

### Windows

1. Download the installer from the [UB Mannheim Tesseract page](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and follow the installation instructions
3. Make sure to remember the installation path (default is `C:\Program Files\Tesseract-OCR`)
4. Add the Tesseract installation directory to your PATH environment variable:
   - Right-click on 'This PC' or 'My Computer' and select 'Properties'
   - Click on 'Advanced system settings'
   - Click on 'Environment Variables'
   - Under 'System variables', find and select 'Path', then click 'Edit'
   - Click 'New' and add the path to the Tesseract installation directory (e.g., `C:\Program Files\Tesseract-OCR`)
   - Click 'OK' to close all dialogs

### macOS

Using Homebrew:

```bash
brew install tesseract
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```

## Troubleshooting Pillow Installation

If you encounter issues installing Pillow, try:

1. Using an older version:
   ```bash
   pip install Pillow==9.0.0
   ```

2. Installing system dependencies first (on Linux):
   ```bash
   sudo apt-get install python3-dev python3-setuptools
   sudo apt-get install libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev
   sudo apt-get install libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk
   ```

3. On Windows, try installing a pre-built wheel:
   ```bash
   pip install --only-binary :all: pillow==9.5.0
   ```

## Configuration

By default, the application looks for Tesseract in the system PATH. If Tesseract is installed in a non-standard location, you can set the path using an environment variable:

```bash
# Windows (Command Prompt)
set TESSERACT_PATH=C:\Path\To\Tesseract\tesseract.exe

# Windows (PowerShell)
$env:TESSERACT_PATH = "C:\Path\To\Tesseract\tesseract.exe"

# macOS/Linux
export TESSERACT_PATH=/usr/local/bin/tesseract
```

## Usage

Once set up, you can use the OCR functionality by:

1. Navigate to the "Add Monster" page
2. In the "Scan Monster Statblock" section, upload an image of a monster statblock
3. Click "Scan Image and Extract Stats"
4. The form will be automatically populated with the extracted monster data
5. Review and edit the data as needed before submitting the form

## Best Practices for OCR

For best results:

1. Use high-contrast images (black text on white background)
2. Ensure the image is clear and not blurry
3. Crop the image to include only the statblock
4. Use PNG or JPEG formats with good quality
5. Avoid images with complex backgrounds or patterns 