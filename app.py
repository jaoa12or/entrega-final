from flask import Flask, request
from flask import render_template
from flask import jsonify, make_response
import datetime
import psycopg2
import urllib.parse as urlparse
import os

url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port

conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
            )

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html')



@app.route('/monitoreo', methods = ['GET' , 'POST'])
def manager():
    if request.method == 'POST' :
        info = request.get_json(force=True)
        tiempo = info.get("tiempoSubida")
        usuario =  info.get("users")
        so = info.get('kernel')
        memoria = info.get('mem free')
        swap = info.get('swap so')
        cpu = info.get('cpu sy')
        almacenamiento = info.get('hdused')
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO monitoreo VALUES('"""+ tiempo + """ ' , '""" + usuario + """ ' , '""" + so + """ ' , ' """
                     + memoria + """  ' , ' """ + swap + """ ' , ' """ + cpu + """ ' , ' """ + almacenamiento + """ ')""")
        cursor.execute(""" COMMIT """)

        return "1"

    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM monitoreo ORDER BY tiempo DESC""")
    rows = cursor.fetchall()
    return render_template('monitoreo.html', rows = rows)

@app.route('/descargas', methods = ['GET','POST'])
def descarga():
    if request.method == 'POST':
        cursor = conn.cursor()
        torrent = request.form['magnetlink']
        cursor.execute(""" INSERT INTO torrents (url) VALUES ('""" +  url  + """ ')""")
        cursor.execute(""" COMMIT """)
        return render_template("exitoso.html")

    return render_template("descargas.html")

@app.route('/get-descargas', methods = ['GET'])
def torrents():
    cursor = conn.cursor()
    cursor.execute("""SELECT url FROM torrents """)
    rows = cursor.fetchall()
    urls = {}
    x = 0
    for row in rows:
        urls['url'+ str(x)] = row[0]
        x += 1

    cursor.execute("""DELETE FROM torrents""")
    cursor.execute(""" COMMIT """)
    return jsonify(urls)

@app.route('/estado', methods = ['GET', 'POST'])
def status():
    if request.method == 'POST':
        info = request.get_json(force=True)
        cursor = conn.cursor()
        cursor.execute("""DELETE FROM descargas""")
        cursor.execute(""" COMMIT """)
        x = 0
        for item in info:
            item = info [x]
            nombre = item.get('nombre')
            progreso = item.get('progreso')
            tiempoEstimado = item.get('tiempoEstimado')
            estado = item.get('estado')
            velocidad = item.get('velocidad')
            tiempoSubida = item.get('tiempoSubida')
            print (tiempoSubida)
            cursor.execute("""INSERT INTO descargas (nombre, descargado, tiempoEstimado, estado, velocidad, tiempo) VALUES ('""" + nombre + """ ' , ' """
                        + progreso + """ ' , ' """ + tiempoEstimado + """ ' , ' """
                        + estado + """ ' , ' """+ velocidad + """' , '""" + tiempoSubida + """ ' ) """ )
            cursor.execute("""COMMIT""")

            x += 1
        return "la carga fue exitosa"

    cursor = conn.cursor()
    cursor.execute("""SELECT id, nombre, descargado, tiempoEstimado, estado, velocidad FROM descargas""")
    rows = cursor.fetchall()
    cursor.execute("""SELECT tiempo FROM descargas GROUP BY tiempo""")
    time = cursor.fetchone()[0]
    return render_template('estado.html', rows = rows, time = time)





if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port = 5001)
