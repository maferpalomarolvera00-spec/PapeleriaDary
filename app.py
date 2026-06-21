from flask import session
from flask import Flask, render_template, request, redirect, session, send_file
from flask_mysqldb import MySQL
from reportlab.pdfgen import canvas
from datetime import datetime
from patrones.singleton import ConexionSingleton
from patrones.factory import UserFactory
from patrones.observer import InventarioObserver

app = Flask(__name__)

app.secret_key = "papeleria_dary"

# ==========================
# CONFIGURACIÓN MYSQL
# ==========================

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'papeleriadary'

mysql = MySQL(app)

# ==========================
# INICIO
# ==========================

@app.route('/')
def inicio():
    return render_template('login.html')

#==========================================================================================================
@app.route('/login', methods=['POST'])
def login():

    usuario = request.form['usuario']
    password = request.form['password']

    cursor = mysql.connection.cursor()

    consulta = """
    SELECT *
    FROM usuario
    WHERE nombreUsuario = %s
    AND contrasena = %s
    """

    cursor.execute(
        consulta,
        (usuario, password)
    )

    resultado = cursor.fetchone()

    if resultado:

        rol = resultado[4]

        session['rol'] = rol

        cursor.execute("SELECT COUNT(*) FROM productos")
        total_productos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM usuario")
        total_usuarios = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM venta")
        total_ventas = cursor.fetchone()[0]

        return render_template(
            'dashboard_admin.html',
            productos=total_productos,
            usuarios=total_usuarios,
            ventas=total_ventas,
            rol=rol
        )

    else:
        return "Usuario o contraseña incorrectos"
    
# ==========================
# PRODUCTOS
# ==========================

@app.route('/productos')
def productos():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            idProducto,
            nombre,
            precioVenta,
            stockActual
        FROM productos
    """)

    lista_productos = cursor.fetchall()

    return render_template(
        'productos.html',
        productos=lista_productos
    )

# ==========================
# AGREGAR PRODUCTO
# ==========================

@app.route('/agregar_producto')
def agregar_producto():

    return render_template(
        'agregar_producto.html'
    )


# ==========================
# GUARDAR PRODUCTO
# ==========================

@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():

    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precioCompra = request.form['precioCompra']
    precioVenta = request.form['precioVenta']
    stockActual = request.form['stockActual']
    stockMinimo = request.form['stockMinimo']
    idProveedor = request.form['idProveedor']

    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO productos(
            nombre,
            descripcion,
            precioCompra,
            precioVenta,
            stockActual,
            stockMinimo,
            idProveedor
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """,
    (
        nombre,
        descripcion,
        precioCompra,
        precioVenta,
        stockActual,
        stockMinimo,
        idProveedor
    ))

    mysql.connection.commit()

    return redirect('/productos')


# ==========================
# EDITAR PRODUCTO
# ==========================

@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):

    cursor = mysql.connection.cursor()

    if request.method == 'POST':

        nombre = request.form['nombre']
        precioVenta = request.form['precioVenta']
        stockActual = request.form['stockActual']

        cursor.execute("""
            UPDATE productos
            SET nombre=%s,
                precioVenta=%s,
                stockActual=%s
            WHERE idProducto=%s
        """,
        (
            nombre,
            precioVenta,
            stockActual,
            id
        ))

        mysql.connection.commit()

        return redirect('/productos')

    cursor.execute("""
        SELECT *
        FROM productos
        WHERE idProducto=%s
    """, (id,))

    producto = cursor.fetchone()

    return render_template(
        'editar_producto.html',
        producto=producto
    )


# ==========================
# ELIMINAR PRODUCTO
# ==========================

@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM productos
        WHERE idProducto=%s
    """, (id,))

    mysql.connection.commit()

    return redirect('/productos')

# ==========================
# CLIENTES
# ==========================

@app.route('/clientes')
def clientes():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            idCliente,
            nombre,
            aPaterno,
            aMaterno
        FROM cliente
    """)

    lista_clientes = cursor.fetchall()

    return render_template(
        'clientes.html',
        clientes=lista_clientes
    )


# ==========================
# AGREGAR CLIENTE
# ==========================

@app.route('/agregar_cliente')
def agregar_cliente():

    return render_template(
        'agregar_cliente.html'
    )


# ==========================
# GUARDAR CLIENTE
# ==========================

@app.route('/guardar_cliente', methods=['POST'])
def guardar_cliente():

    nombre = request.form['nombre']
    aPaterno = request.form['aPaterno']
    aMaterno = request.form['aMaterno']

    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO cliente(
            nombre,
            aPaterno,
            aMaterno
        )
        VALUES (%s,%s,%s)
    """,
    (
        nombre,
        aPaterno,
        aMaterno
    ))

    mysql.connection.commit()

    return redirect('/clientes')


# ==========================
# EDITAR CLIENTE
# ==========================

@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):

    cursor = mysql.connection.cursor()

    if request.method == 'POST':

        nombre = request.form['nombre']
        aPaterno = request.form['aPaterno']
        aMaterno = request.form['aMaterno']

        cursor.execute("""
            UPDATE cliente
            SET nombre=%s,
                aPaterno=%s,
                aMaterno=%s
            WHERE idCliente=%s
        """,
        (
            nombre,
            aPaterno,
            aMaterno,
            id
        ))

        mysql.connection.commit()

        return redirect('/clientes')

    cursor.execute("""
        SELECT *
        FROM cliente
        WHERE idCliente=%s
    """, (id,))

    cliente = cursor.fetchone()

    return render_template(
        'editar_cliente.html',
        cliente=cliente
    )


# ==========================
# ELIMINAR CLIENTE
# ==========================

@app.route('/eliminar_cliente/<int:id>')
def eliminar_cliente(id):

    cursor = mysql.connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM cliente
            WHERE idCliente=%s
        """, (id,))

        mysql.connection.commit()

    except:

        return """
        <h2>❌ No se puede eliminar este cliente</h2>

        <p>
        El cliente tiene ventas registradas.
        </p>

        <a href="/clientes">
        Volver
        </a>
        """

    return redirect('/clientes')

# ==========================
# VENTAS
# ==========================

@app.route('/ventas')
def ventas():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            v.idVenta,
            v.FechaHora,
            CONCAT(
                c.nombre,
                ' ',
                c.aPaterno,
                ' ',
                c.aMaterno
            ) AS cliente,
            v.Total
        FROM venta v
        INNER JOIN cliente c
            ON v.idCliente = c.idCliente
        ORDER BY v.idVenta DESC
    """)

    lista_ventas = cursor.fetchall()

    return render_template(
        'ventas.html',
        ventas=lista_ventas
    )


# ==========================
# NUEVA VENTA
# ==========================

@app.route('/nueva_venta')
def nueva_venta():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            idCliente,
            nombre,
            aPaterno,
            aMaterno
        FROM cliente
    """)

    clientes = cursor.fetchall()

    cursor.execute("""
        SELECT
            idProducto,
            nombre,
            precioVenta,
            stockActual
        FROM productos
    """)

    productos = cursor.fetchall()

    return render_template(
        'nueva_venta.html',
        clientes=clientes,
        productos=productos
    )

# ==========================
# GUARDAR VENTA
# ==========================

@app.route('/guardar_venta', methods=['POST'])
def guardar_venta():

    cliente = request.form['cliente']
    producto = request.form['producto']
    cantidad = int(request.form['cantidad'])

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            precioVenta,
            stockActual
        FROM productos
        WHERE idProducto = %s
    """, (producto,))

    datos_producto = cursor.fetchone()

    precio = float(datos_producto[0])
    stock = int(datos_producto[1])

    # Validar stock

    if cantidad > stock:

     return f"""
    <!DOCTYPE html>
    <html lang="es">

    <head>

        <meta charset="UTF-8">

        <title>Stock insuficiente</title>

        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

    </head>

    <body class="bg-light">

        <div class="container mt-5">

            <div class="row justify-content-center">

                <div class="col-md-6">

                    <div class="card shadow border-warning">

                        <div class="card-body text-center p-5">

                            <h1 class="text-warning">
                                ⚠️ Stock Insuficiente
                            </h1>

                            <hr>

                            <p class="fs-5">

                                Solo existen

                                <strong>{stock}</strong>

                                unidades disponibles en inventario.

                            </p>

                            <p class="text-muted">

                                Verifica la cantidad solicitada
                                e intenta nuevamente.

                            </p>

                            <a
                            href="/nueva_venta"
                            class="btn btn-warning btn-lg">

                            🔄 Volver a la Venta

                            </a>

                        </div>

                    </div>

                </div>

            </div>

        </div>

    </body>

    </html>
    """

    total = precio * cantidad

    # ==========================
    # OBSERVER
    # ==========================

    observer = InventarioObserver()

    nuevo_stock = observer.actualizar_stock(
        stock,
        cantidad
    )

    # ==========================
    # REGISTRAR VENTA
    # ==========================

    cursor.execute("""
        INSERT INTO venta(
            idUsuario,
            FechaHora,
            idCliente,
            Total
        )
        VALUES (
            1,
            NOW(),
            %s,
            %s
        )
    """,
    (
        cliente,
        total
    ))

    mysql.connection.commit()

    idVenta = cursor.lastrowid

    # ==========================
    # DETALLE VENTA
    # ==========================

    cursor.execute("""
        INSERT INTO detalleventa(
            idVenta,
            idProducto,
            Cantidad,
            Subtotal
        )
        VALUES (
            %s,
            %s,
            %s,
            %s
        )
    """,
    (
        idVenta,
        producto,
        cantidad,
        total
    ))

    # ==========================
    # ACTUALIZAR STOCK
    # ==========================

    cursor.execute("""
        UPDATE productos
        SET stockActual = %s
        WHERE idProducto = %s
    """,
    (
        nuevo_stock,
        producto
    ))

    mysql.connection.commit()

    return redirect('/ventas')

# ==========================
# INVENTARIO
# ==========================

@app.route('/inventario')
def inventario():

    if session.get('rol') != 'Administrador':
        return """
        <h1>⛔ Acceso Denegado</h1>
        <p>No tienes permisos para acceder a esta sección.</p>
        <a href='/dashboard'>Volver</a>
        """

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            idProducto,
            nombre,
            stockActual,
            stockMinimo
        FROM productos
    """)

    productos = cursor.fetchall()

    total_productos = len(productos)

    stock_bajo = 0
    agotados = 0

    for producto in productos:

        if producto[2] == 0:
            agotados += 1

        elif producto[2] <= producto[3]:
            stock_bajo += 1

    return render_template(
        'inventario.html',
        productos=productos,
        total_productos=total_productos,
        stock_bajo=stock_bajo,
        agotados=agotados
    )

# ==========================
# ESTADÍSTICAS
# ==========================

@app.route('/estadisticas')
def estadisticas():

    if session.get('rol') != 'Administrador':
        return """
        <h1>⛔ Acceso Denegado</h1>
        <p>No tienes permisos para acceder a esta sección.</p>
        <a href='/dashboard'>Volver</a>
        """

    cursor = mysql.connection.cursor()

    # Totales generales

    cursor.execute("SELECT COUNT(*) FROM productos")
    productos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM cliente")
    clientes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM venta")
    ventas = cursor.fetchone()[0]

    # Inventario

    cursor.execute("""
        SELECT
            stockActual,
            stockMinimo
        FROM productos
    """)

    inventario = cursor.fetchall()

    stock_bajo = 0
    agotados = 0
    stock_normal = 0

    for producto in inventario:

        stock_actual = producto[0]
        stock_minimo = producto[1]

        if stock_actual == 0:
            agotados += 1

        elif stock_actual <= stock_minimo:
            stock_bajo += 1

        else:
            stock_normal += 1

    return render_template(
        'estadisticas.html',
        productos=productos,
        clientes=clientes,
        ventas=ventas,
        stock_normal=stock_normal,
        stock_bajo=stock_bajo,
        agotados=agotados
    )

# ==========================
# REPORTE GENERAL
# ==========================

@app.route('/reporte_general')
def reporte_general():

    if session.get('rol') != 'Administrador':
        return """
        <h1>⛔ Acceso Denegado</h1>
        <p>No tienes permisos para acceder a esta sección.</p>
        <a href='/dashboard'>Volver</a>
        """

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM productos")
    productos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM cliente")
    clientes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM venta")
    ventas = cursor.fetchone()[0]

    cursor.execute("""
        SELECT IFNULL(SUM(Total), 0)
        FROM venta
    """)

    ingresos = cursor.fetchone()[0]

    return render_template(
        'reporte_general.html',
        productos=productos,
        clientes=clientes,
        ventas=ventas,
        ingresos=round(float(ingresos), 2)
    )

# ==========================
# REPORTE PRODUCTOS PDF
# ==========================


from datetime import datetime
@app.route('/reporte_productos')
def reporte_productos():

    if session.get('rol') != 'Administrador':
        return """
        <h1>⛔ Acceso Denegado</h1>
        <p>No tienes permisos para acceder a esta sección.</p>
        <a href='/dashboard'>Volver</a>
        """

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            idProducto,
            nombre,
            precioVenta,
            stockActual
        FROM productos
    """)

    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

    productos = cursor.fetchall()

    pdf = canvas.Canvas("reporte_productos.pdf")

    pdf.setTitle("Reporte Productos")

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(150, 800, "PAPELERÍA DARY")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(180, 775, "REPORTE DE PRODUCTOS")

    pdf.line(50, 765, 550, 765)

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
    50,
    745,
    f"Fecha de generación: {fecha_actual}"
    )


    pdf.line(50, 765, 550, 765)

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
    50,
    745,
    f"Fecha de generación: {fecha_actual}"
)
    
    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawString(25, 720, "ID")
    pdf.drawString(60, 720, "PRODUCTO")
    pdf.drawString(250, 720, "PRECIO")
    pdf.drawString(350, 720, "STOCK")

    pdf.line(20, 710, 550, 710)

    pdf.setFont("Helvetica", 9)


    y = 690

    for producto in productos:

        pdf.drawString(25, y, str(producto[0]))
        pdf.drawString(60, y, str(producto[1]))
        pdf.drawString(250, y, f"${producto[2]}")
        pdf.drawString(350, y, str(producto[3]))


        y -= 20

        if y < 50:

            pdf.showPage()

            y = 750

    pdf.line(20, y - 10, 550, y - 10)

    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(
        20,
        y - 30,
        f"Total de productos registrados: {len(productos)}"
    )

    pdf.setFont("Helvetica", 9)

    pdf.drawString(
        20,
        y - 50,
        "Documento generado automáticamente por Papelería Dary"
    )

    pdf.save()

    return send_file(
            "reporte_productos.pdf",
            as_attachment=True
        )

# ==========================
# REPORTE VENTAS PDF
# ==========================


from datetime import datetime

@app.route('/reporte_ventas')
def reporte_ventas():
    if session.get('rol') != 'Administrador':
        return """
        <h1>⛔ Acceso Denegado</h1>
        <p>No tienes permisos para acceder a esta sección.</p>
        <a href='/dashboard'>Volver</a>
        """

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            v.idVenta,
            v.FechaHora,
            CONCAT(
                c.nombre,
                ' ',
                c.aPaterno,
                ' ',
                c.aMaterno
            ) AS cliente,
            v.Total
        FROM venta v
        INNER JOIN cliente c
            ON v.idCliente = c.idCliente
        ORDER BY v.idVenta DESC
    """)

    
    ventas = cursor.fetchall()

    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

    pdf = canvas.Canvas("reporte_ventas.pdf")

    pdf.setTitle("Reporte Ventas")

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(150, 800, "PAPELERÍA DARY")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(190, 775, "REPORTE DE VENTAS")

    pdf.line(20, 765, 550, 765)

    pdf.setFont("Helvetica", 10)

    pdf.drawString(
        20,
        745,
        f"Fecha de generación: {fecha_actual}"
    )


    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawString(20, 720, "ID")
    pdf.drawString(60, 720, "CLIENTE")
    pdf.drawString(420, 720, "TOTAL")

    pdf.line(20, 710, 550, 710)

    pdf.setFont("Helvetica", 9)


    y = 690
    total_ingresos = 0

    for venta in ventas:

        pdf.drawString(20, y, str(venta[0]))
        pdf.drawString(60, y, str(venta[2])[:45])
        pdf.drawString(420, y, f"${venta[3]}")

        total_ingresos += float(venta[3])

        y -= 20

        if y < 50:

            pdf.showPage()

            y = 750

    pdf.line(20, y - 10, 550, y - 10)

    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(
        20,
        y - 30,
        f"Total de ventas realizadas: {len(ventas)}"
    )

    pdf.drawString(
        20,
        y - 50,
        f"Ingresos acumulados: ${round(total_ingresos, 2)}"
    )

    pdf.setFont("Helvetica", 9)

    pdf.drawString(
        20,
        y - 70,
        "Documento generado automáticamente por Papelería Dary"
    )

    pdf.save()

    return send_file(
        "reporte_ventas.pdf",
        as_attachment=True
    )






@app.route('/dashboard')
def dashboard():

    rol = session.get('rol')

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM productos")
    total_productos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM usuario")
    total_usuarios = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM venta")
    total_ventas = cursor.fetchone()[0]

    return render_template(
        'dashboard_admin.html',
        productos=total_productos,
        usuarios=total_usuarios,
        ventas=total_ventas,
        rol=rol
    )























#=======================================
# FINAL
#=======================================

if __name__ == '__main__':
    app.run(debug=True)