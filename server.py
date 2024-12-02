from flask import Flask, render_template, request, send_file
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import tempfile
from datetime import datetime

app = Flask(__name__)

# Đăng ký font để hỗ trợ tiếng Việt
pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Lấy thông tin từ form
        contract_number = request.form.get('contract_number', '')
        customer_name = request.form.get('customer_name', '')
        phone_number = request.form.get('phone_number', '')
        
        # Lấy ngày tạo 
        created_day = datetime.now().strftime("%d/%m/%Y") 
        # Tạo nội dung QR từ thông tin khách hàng
        qr_content = f"{contract_number} - {customer_name} - {phone_number} - Created: {created_day}"
        
        # Tạo mã QR
        qr = qrcode.QRCode(
            version=1, #1 - 40 CHỈ SỐ MATRIX 
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        # Tạo hình ảnh QR
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Lưu hình ảnh QR tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_qr:
            img.save(temp_qr.name)
            temp_qr_path = temp_qr.name
        
        # Tạo PDF với khổ ngang
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            # Sử dụng landscape để xoay trang
            c = canvas.Canvas(temp_pdf.name, pagesize=landscape(letter))
            width, height = landscape(letter)
            
            # Đặt font và size lớn
            c.setFont('Arial', 40)
            
            # Thông tin khách hàng ở phía trên
            c.drawCentredString(width/2, height - 1*inch, f"Số Hợp Đồng: {contract_number}")
            c.drawCentredString(width/2, height - 1.7*inch, f"KH: {customer_name}")
            c.drawCentredString(width/2, height - 2.4*inch, f"Số Điện Thoại: {phone_number}")
            
            # Chèn hình QR vào giữa trang
            c.drawImage(temp_qr_path, width/2 - 2.2*inch, height/2 - 2.7*inch, width=4.4*inch, height=4.4*inch)
            
            # Dòng chữ ở bottom
            c.drawCentredString(width/2, 1*inch, "SCTV - Sống động từng giây")
            
            c.save()
            temp_pdf_path = temp_pdf.name
        
        # Trả file PDF về cho người dùng
        return send_file(temp_pdf_path, as_attachment=True, 
                         download_name=f'QR_{contract_number}.pdf', 
                         mimetype='application/pdf')
    
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)