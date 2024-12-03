from flask import Flask, render_template, request, send_file
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import os
import tempfile

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Lấy tên khách hàng từ form
        customer_name = request.form.get('customer_name', '')
        
        # Tạo mã QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(customer_name)
        qr.make(fit=True)
        
        # Tạo hình ảnh QR
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Lưu hình ảnh QR tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_qr:
            img.save(temp_qr.name)
            temp_qr_path = temp_qr.name
        
        # Tạo PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            c = canvas.Canvas(temp_pdf.name, pagesize=letter)
            width, height = letter
            
            # Tiêu đề
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width/2, height - inch, "Mã QR Khách Hàng")
            
            # Tên khách hàng
            c.setFont("Helvetica", 12)
            c.drawCentredString(width/2, height - 2*inch, f"Tên: {customer_name}")
            
            # Chèn hình QR vào PDF
            c.drawImage(temp_qr_path, width/2 - 2*inch, height/2 - 2*inch, width=4*inch, height=4*inch)
            
            c.save()
            temp_pdf_path = temp_pdf.name
        
        # Trả file PDF về cho người dùng
        return send_file(temp_pdf_path, as_attachment=True, 
                         download_name=f'QR_{customer_name}.pdf', 
                         mimetype='application/pdf')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)