# services/qrcode_service.py
import os
import qrcode

class QRCodeService:
    @staticmethod
    def generate_membership_qr_code(customer_id, membership_identifier, output_directory):
        """Generates a high-density, machine-readable QR code graphic matrix layout asset on disk."""
        os.makedirs(output_directory, exist_ok=True)

        # 1. Structure the encoded payload string safely (e.g., "MEMBER-1002-GOLD")
        payload_data = f"MEMBER-{customer_id}-{membership_identifier}"

        # 2. Configure high-fidelity matrix specifications
        qr_engine = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_engine.add_data(payload_data)
        qr_engine.make(fit=True)

        # 3. Compile the structural vector layout to image
        graphic_asset = qr_engine.make_image(fill_color="black", back_color="white")
        
        # 4. Save image payload directly to system storage paths
        filename = f"member_qr_{customer_id}.png"
        target_file_path = os.path.join(output_directory, filename)
        graphic_asset.save(target_file_path)

        return filename