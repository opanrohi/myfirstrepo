#--------------------------------------------------------------------
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
#--------------------------------------------------------------------
import mysql.connector
#--------------------------------------------------------------------
from werkzeug.utils import secure_filename
#--------------------------------------------------------------------
import os
import time
#--------------------------------------------------------------------
app = Flask(__name__)
CORS(app) # Esto habilitará CORS para todas las rutas
#--------------------------------------------------------------------
class Catalogo:
    #--------------------------------------------------------------------
    # Constructor de la clase
    def __init__(self, host, user, password, database):
        
        #Inicializa una instancia de Catalogo y crea una conexión a la base de datos.

        self.conn = mysql.connector.connect(
            host = "francoluvi.mysql.pythonanywhere-services.com",
            user = "francoluvi",
            password ="123456789",
            database="francoluvi$inventario"
        )

        self.cursor = self.conn.cursor()
        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err
        
        # Si la tabla 'productos' no existe, la creamos
        self.conector.execute('''CREATE TABLE IF NOT EXISTS productos (
            codigo INT AUTO_INCREMENT PRIMARY KEY,
            descripcion VARCHAR(255) NOT NULL,
            cantidad INT NOT NULL,
            precio DECIMAL(10, 2) NOT NULL,
            imagen_url VARCHAR(255))''')
        self.conn.commit()

        # El parámetro dictionary=True configura el cursor para que,
        # cuando se recuperen resultados de una consulta, estos se 
        # almacenen en un diccionario en lugar de una tupla. 
        self.cursor.close() #cierro el cursor existente para abrir otro
        self.conector = self.conn.cursor(dictionary=True)

    #----------------------------------------------------------------
    def agregar_producto(self, descripcion, cantidad, precio, imagen):
        
        sql = "INSERT INTO productos (descripcion, cantidad, precio, imagen_url) VALUES (%s, %s, %s, %s)"
        valores = (descripcion, cantidad, precio, imagen)        
        
        self.conector.execute(sql, valores)
        self.conn.commit()
        return self.cursor.lastrowid
    #----------------------------------------------------------------
    def consultar_producto(self, codigo):
        
        self.conector.execute(f"SELECT * FROM productos WHERE codigo = {codigo}")
        return self.conector.fetchone()

    #----------------------------------------------------------------
    def modificar_producto(self, codigo, nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_imagen):

        sql = "UPDATE productos SET descripcion = %s, cantidad = %s, precio = %s, imagen_url = %s WHERE codigo = %s"
        valores = (nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_imagen, codigo)

        self.cursor.execute(sql, valores)
        self.conn.commit()

        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def listar_productos(self):
        self.conector.execute("SELECT * FROM productos")
        productos = self.conector.fetchall()
        return productos

    #----------------------------------------------------------------
    def eliminar_producto(self, codigo):
        self.conector.execute(f"DELETE FROM productos WHERE codigo = {codigo}")
        self.conn.commit()
        return self.conector.rowcount > 0

    #----------------------------------------------------------------
    def mostrar_producto(self, codigo):
        producto = self.consultar_producto(codigo)
        if producto:
            print("-" * 40)
            print(f"Código.....: {producto['codigo']}")
            print(f"Descripción: {producto['descripcion']}")
            print(f"Cantidad...: {producto['cantidad']}")
            print(f"Precio.....: {producto['precio']}")
            print(f"Imagen.....: {producto['imagen_url']}")
            print("-" * 40)
        else:
            print("Producto no encontrado.")

#--------------------------------------------------------------------
# Cuerpo del programa
#--------------------------------------------------------------------
# Crear una instancia de la clase Catalogo
catalogo = Catalogo(host='francoluvi.mysql.pythonanywhere-services.com', user='francoluvi', password='123456789', database='francoluvi$inventario')

# Carpeta para guardar las imagenes.
RUTA_DESTINO = '/home/francoluvi/mysite/static/imagenes'

#--------------------------------------------------------------------
# Listar todos los productos
#--------------------------------------------------------------------
#La ruta Flask /productos con el método HTTP GET está diseñada para
#proporcionar los detalles de todos los productos almacenados en la base de datos
#El método devuelve una lista con todos los productos en formato JSON.
@app.route("/productos", methods=["GET"])
def listar_productos():
    productos = catalogo.listar_productos()
    return jsonify(productos)

#--------------------------------------------------------------------
# Mostrar un sólo producto según su código
#--------------------------------------------------------------------
#La ruta Flask /productos/<int:codigo> con el método HTTP GET está
#diseñada para proporcionar los detalles de un producto específico basado
#en su código.
#El método busca en la base de datos el producto con el código especificado y devuelve un JSON con los detalles del producto si lo encuentra, o None si no lo encuentra.
@app.route("/productos/<int:codigo>", methods=["GET"])
def mostrar_producto(codigo):
    producto = catalogo.consultar_producto(codigo)
    if producto:
        return jsonify(producto), 201
    else:
        return "Producto no encontrado", 404

#--------------------------------------------------------------------
# Agregar un producto
#--------------------------------------------------------------------
@app.route("/productos", methods=["POST"])
#La ruta Flask `/productos` con el método HTTP POST está diseñada para permitir la adición de un nuevo producto a la base de datos.
#La función agregar_producto se asocia con esta URL y es llamada cuando se hace una solicitud POST a /productos.
def agregar_producto():
    descripcion = request.form['descripcion'] 
    cantidad = request.form['cantidad'] 
    precio = request.form['precio'] 
    imagen = request.files['imagen'] 
    nombre_imagen=""

    nombre_imagen = secure_filename(imagen.filename) 
    nombre_base, extension = os.path.splitext(nombre_imagen) 
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" 
    nuevo_codigo = catalogo.agregar_producto(descripcion, cantidad, precio, nombre_imagen) 

    if nuevo_codigo: 
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))

        return jsonify({"mensaje": "Producto agregado correctamente.", "codigo": nuevo_codigo, "imagen": nombre_imagen}), 201 
    else: 
        return jsonify({"mensaje": "Error al agregar el producto."}), 500
        
#-------------------------------------------------------------------- 
# Modificar un producto según su código 
#--------------------------------------------------------------------
@app.route("/productos/<int:codigo>", methods=["PUT"])
#La ruta Flask /productos/<int:codigo> con el método HTTP PUT está diseñada para actualizar la información de 
# un producto existente en la base de datos, identificado por su código. #La función modificar_producto se asocia 
# con esta URL y es invocada cuando se realiza una solicitud PUT a /productos/ seguido de un número (el código del producto).
def modificar_producto(codigo): 
    #Se recuperan los nuevos datos del formulario 
    nueva_descripcion = request.form.get("descripcion") 
    nueva_cantidad = request.form.get("cantidad") 
    nuevo_precio = request.form.get("precio")

    if 'imagen' in request.files: 
        imagen = request.files['imagen'] 
        nombre_imagen = secure_filename(imagen.filename) 
        nombre_base, extension = os.path.splitext(nombre_imagen) 
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" 
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen)) 
        producto = catalogo.consultar_producto(codigo) 
        if producto: 
            imagen_vieja = producto["imagen_url"] 
            ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja) 
            if os.path.exists(ruta_imagen): 
                os.remove(ruta_imagen) 
    else: 
        producto = catalogo.consultar_producto(codigo) 
        if producto: nombre_imagen = producto["imagen_url"] 
    if catalogo.modificar_producto(codigo, nueva_descripcion, nueva_cantidad, nuevo_precio, nombre_imagen):
        return jsonify({"mensaje": "Producto modificado"}), 200 
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 403

#-------------------------------------------------------------------- 
# Eliminar un producto según su código 
#--------------------------------------------------------------------
@app.route("/productos/<int:codigo>", methods=["DELETE"])
#La ruta Flask /productos/<int:codigo> con el método HTTP DELETE está diseñada para eliminar un producto específico de la base de datos, utilizando su código como identificador.
#La función eliminar_producto se asocia con esta URL y es llamada cuando se realiza una solicitud DELETE a /productos/ seguido de un número (el código del producto).
def eliminar_producto(codigo):
    producto = catalogo.consultar_producto(codigo)
    if producto: 
        imagen_vieja = producto["imagen_url"] 
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)
        if os.path.exists(ruta_imagen): 
            os.remove(ruta_imagen)
        if catalogo.eliminar_producto(codigo): 
            return jsonify({"mensaje": "Producto eliminado"}), 200
        else:
            return jsonify({"mensaje": "Error al eliminar el producto"}), 500
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 404
#--------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)