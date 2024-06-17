from datetime import date
import datetime
from flask import Flask, request, render_template, redirect, url_for, session,jsonify, Response
import pyodbc
import uuid
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import date
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=NIKO;'
        'DATABASE=UserDB;'
        'Trusted_Connection=yes;'
    )
    return conn

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(item['quantity'] * item['product']['price'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/sobremi')
def sobremi():
    return render_template('sobreMi.html')

@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, descripcion, precio, stock FROM productos WHERE id = ?", product_id)
    product = cursor.fetchone()
    conn.close()
    
    if product:
        product_dict = {'id': product[0], 'name': product[1], 'description': product[2], 'price': product[3], 'stock': product[4]}
        if 'cart' not in session:
            session['cart'] = []
        # Check if the product is already in the cart
        found = False
        for item in session['cart']:
            if item['product']['id'] == product_id:
                item['quantity'] += 1
                found = True
                break
        if not found:
            session['cart'].append({'product': product_dict, 'quantity': 1})
        session.modified = True  # Mark the session as modified
    return jsonify(success=True)

def insert_usuario(email, password, nombres, apellidos, telefono):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC InsertUsuario ?, ?, ?, ?, ?", (email, password, nombres, apellidos, telefono))
        conn.commit()
        conn.close()
        print("usuario ingresado correctamente")
        return True
    except Exception as e:
        conn.rollback()
        cursor.close()
        print(f"No se pudo ingresar usuario: {e}")
        return False
    
def insert_recibo(uuid, email, preciototal, fecha):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC InsertRecibo ?, ?, ?, ?", (uuid, email, preciototal, fecha))
        conn.commit()
        conn.close()
        print("recibo ingresado correctamente")
        return True
    except Exception as e:
        conn.rollback()
        cursor.close()
        print(f"No se pudo ingresar recibo: {e}")
        return False

def insert_recibodetalle(uuid, producto, precio, cantidad, preciototal):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC InsertRecibo ?, ?, ?, ?, ?", (uuid, producto, precio, cantidad, preciototal))
        conn.commit()
        conn.close()
        print(" detalle de recibo ingresado correctamente")
        return True
    except Exception as e:
        conn.rollback()
        cursor.close()
        print(f"No se pudo ingresar el detalle del recibo: {e}")
        return False

def insert_direccion(email, direccion, distrito, provincia):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC InsertDireccion ?, ?, ?, ?, ?", (email, direccion, distrito, provincia))
        conn.commit()
        conn.close()
        print("Direccion agregada exitosamente")
        return True
    except Exception as e:
        conn.rollback()
        cursor.close()
        print(f"Failed to insert direccion: {e}")
        return False

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/tienda')
def tienda():
    if 'username' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, descripcion, precio, stock FROM productos")
        products = [{'id': row[0], 'name': row[1], 'description': row[2], 'price': row[3], 'stock': row[4]} for row in cursor.fetchall()]
        conn.close()
    
        cart = session.get('cart', [])
        total = 0
        for item in cart:
            total += item['quantity'] * float(item['product']['price'])  
        return render_template('tienda.html', products=products, cart=cart, total=total)
    else:
        return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    conn = get_db_connection()
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        session['username'] = username
        print(session['username'])
        return redirect(url_for('index'))
    else:
        return render_template('login-failed.html')

@app.route('/index')
def index():
    if 'username' in session:
        
        cart = session.get('cart', [])
        total = 0
        for item in cart:
            total += item['quantity'] * float(item['product']['price'])  
        return render_template('index.html', cart=cart, total=total)
    else:
        return redirect(url_for('home'))
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        telefono = request.form['telefono']

        if insert_usuario(email, password, nombres, apellidos, telefono):
            return render_template('registro-success.html')
        else:
            return render_template('register-failed.html')
    return render_template('register.html')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', [])
    total = 0
    for item in cart:
            total += item['quantity'] * float(item['product']['price'])
    direccion = None
    distrito = None
    provincia = None

    if request.method == 'POST':
        direccion = request.form.get('direccion')
        distrito = request.form.get('distrito')
        provincia = request.form.get('provincia')
        email = session.get('username')
        if 'username' in session:
            insert_direccion(email, direccion, distrito, provincia)
            username = session.get('username')
            receipt_id = str(uuid.uuid4())
            cart = session.get('cart', [])
            carrito_str = json.dumps(cart)
            fecha = date.today()
            total_price = sum(item['quantity'] * float(item['product']['price']) for item in cart)
            insert_recibo(receipt_id,username,total_price,fecha)
            for item in cart:
                item_name = item['product']['name']
                item_price = item['product']['price']
                quantity = item['quantity']
                total =  item['quantity'] * float(item['product']['price'])
                insert_recibodetalle(receipt_id,item_name,item_price,quantity,total)
        return redirect(url_for('compra_realizada', receipt_id=receipt_id, username=username, total_price=total_price))

    return render_template('checkout.html', cart=cart, total=total, direccion=direccion, distrito=distrito, provincia=provincia)

@app.route('/compra-realizada')
def compra_realizada():
    receipt_id = request.args.get('receipt_id')
    username = request.args.get('username')
    total_price = request.args.get('total_price')
    carrito = session.get('cart', [])
    return render_template('compra-realizada.html', receipt_id=receipt_id, username=username, carrito=carrito, total_price=total_price)

@app.route('/export_pdf', methods=['POST'])
def export_pdf():
    # Retrieve form data from POST request
    username = request.form['username']
    cart = eval(request.form['carrito'])  # Convert string representation back to list
    total_price = float(request.form['total_price'])

    # Generate PDF content
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    # Title
    pdf.drawString(100, 800, "Checkout Receipt")

    # Receipt details
    pdf.drawString(100, 750, f"Correo del cliente: {username}")
    pdf.drawString(100, 730, "Postres comprados:")
    y = 710
    for item in cart:
        pdf.drawString(120, y, f"{item['product']['name']} - Cantidad: {item['quantity']} - Precio por unidad: ${item['product']['price']}")
        y -= 20
    
    pdf.drawString(100, y-20, f"Precio Total: ${total_price}")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    # Set response headers for PDF download
    return Response(buffer, mimetype='application/pdf', headers={'Content-Disposition': 'attachment;filename=checkout_receipt.pdf'})

if __name__ == '__main__':
    app.run(debug=True)
