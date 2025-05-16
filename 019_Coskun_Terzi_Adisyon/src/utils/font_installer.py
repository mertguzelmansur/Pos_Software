import os
import sys
import zipfile
import urllib.request
import shutil

def download_and_install_fonts():
    """Download and install DejaVu fonts which support Turkish characters"""
    fonts_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "fonts"
    )
    
    # Create fonts directory if it doesn't exist
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)
    
    # Check if fonts already installed
    if any(os.path.exists(os.path.join(fonts_dir, font)) for font in 
           ["DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans-Oblique.ttf"]):
        print("Fonts already installed.")
        return True
    
    try:
        # Updated URL for DejaVu fonts
        dejavu_url = "https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip"
        
        print("Downloading DejaVu fonts...")
        
        # Download the zip file
        zip_path = os.path.join(fonts_dir, "dejavu.zip")
        urllib.request.urlretrieve(dejavu_url, zip_path)
        
        print("Extracting fonts...")
        
        # Extract the required fonts
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            font_files = [
                "dejavu-fonts-ttf-2.37/ttf/DejaVuSans.ttf",
                "dejavu-fonts-ttf-2.37/ttf/DejaVuSans-Bold.ttf",
                "dejavu-fonts-ttf-2.37/ttf/DejaVuSans-Oblique.ttf"
            ]
            
            for font_file in font_files:
                zip_ref.extract(font_file, fonts_dir)
                # Move to the fonts directory
                src_path = os.path.join(fonts_dir, font_file)
                dst_path = os.path.join(fonts_dir, os.path.basename(font_file))
                shutil.move(src_path, dst_path)
        
        # Clean up
        os.remove(zip_path)
        shutil.rmtree(os.path.join(fonts_dir, "dejavu-fonts-ttf-2.37"), ignore_errors=True)
        
        print("Fonts installed successfully.")
        return True
    
    except Exception as e:
        print(f"Error installing fonts: {e}")
        # Don't stop the application if font installation fails
        return False

if __name__ == "__main__":
    download_and_install_fonts() 