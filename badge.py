import qrcode
from PIL import Image, ImageDraw, ImageFont


def generate_qr_code(URL):
    img = qrcode.make(URL)
    return img


def create_label_image(name, order_id, password, eventname):
    qr_code = generate_qr_code(f'https://workshops.niraspberryjam.com/qr/{order_id}/{password}')

    name_font = ImageFont.truetype("arial.ttf", 80)
    jam_font = ImageFont.truetype("arial.ttf", 30)
    qr_font = ImageFont.truetype("arial.ttf", 20)
    img = Image.new('L', (1062, 342), color='white')

    d = ImageDraw.Draw(img)
    d.text((100, 130), name, fill="black", font=name_font)
    d.text((50, 20), eventname, fill="black", font=jam_font)
    d.text((50, 60), f"Order ID : {order_id}", fill="black", font=jam_font)
    img.paste(qr_code.resize((300, 300), Image.ANTIALIAS), (750, -20))
    d.text((785, 270), "Scan me with your phone \n to book into workshops!", fill="black", font=qr_font)

    img.save('generated_badge.png')
