# services/barcode_service.py
import os
import barcode
from barcode.writer import ImageWriter

class BarcodeService:
    @staticmethod
    def generate_ean13_barcode_image(barcode_digits, output_directory):
        """Generates a standard physical EAN-13 graphic image file asset on disk."""
        # Ensure the string payload is exactly 12 digits (the library computes the 13th check digit)
        clean_digits = "".join(filter(str.isdigit, str(barcode_digits)))[:12]
        
        if len(clean_digits) < 12:
            # Pad with leading zeros if entry length is short
            clean_digits = clean_digits.zfill(12)

        # Ensure the storage folder paths are safely generated on server startup
        os.makedirs(output_directory, exist_ok=True)
        
        # Instantiate standard commercial retail EAN rendering layout engines
        ean_engine = barcode.get('ean13', clean_digits, writer=ImageWriter())
        
        # Save file file asset explicitly down inside static storage folders
        target_file_path = os.path.join(output_directory, clean_digits)
        saved_path = ean_engine.save(target_file_path)
        
        return f"{clean_digits}.png"