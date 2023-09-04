import os
from flask import Flask, render_template, request, redirect, send_from_directory
from bson import ObjectId
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message


DOCUMENTOS = ["doc", "docx"]

def usuario():
	pass

def password():
	pass

EXTENSIONES = ["png", "jpg", "jpeg"]
app = Flask(__name__)
upload_folder = os.path.abspath(os.path.join(app.root_path, "static", "fondos"))
app.config["UPLOAD_FOLDER"] = upload_folder

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.fondos_flask
misfondos = db.fondos

app.config["MAIL_SERVER"]= "mail.cepibase.int"
app.config["MAIL_PORT"]= 25
app.config["MAIL_USERNAME"]= "USUARIO"
app.config["MAIL_PASSWORD"]= "PASSWORD"
app.config["MAIL_USE_TLS"]= False
app.config["MAIL_USE_SSL"]= False
mail = Mail(app)

def archivo_permitido(nombre):
  return "." in nombre and nombre.rsplit(".", 1)[1] in EXTENSIONES

@app.route("/", methods=["GET", "POST"])
@app.route("/galeria")
def galeria():
  t=request.values.get("tema")
  estilos={}
  if t == None:
    l=misfondos.find()
    estilos["todos"] = "active"
  else:
    l=misfondos.find({"tags": {"$in": [t]}})
    estilos[t] = "active"
  return render_template("index.html", activo=estilos, lista=l)

@app.route("/aportar")
def pagina_aportar():
    return render_template("aportar.html", aportar="active")

@app.route("/insertar", methods=["POST"])
def insertar():
  f = request.files['archivo']
  if f.filename == "":
    return render_template("aportar.html", mensaje = "Hay que indicar un archivo de fondo.")
  else:
    if archivo_permitido(f.filename):
      archivo = secure_filename(f.filename)
      f.save(os.path.join(app.config["UPLOAD_FOLDER"], archivo))
    else:
      return render_template("aportar.html", mensaje = "El archivo indicado no es una imagen.")

  titu = request.values.get("titulo")
  desc = request.values.get("descripcion")
  tags = []
  if request.values.get("animales"):
    tags.append("animales")
  if request.values.get("naturaleza"):
    tags.append("naturaleza")
  if request.values.get("ciudad"):
    tags.append("ciudad")
  if request.values.get("deporte"):
    tags.append("deporte")
  if request.values.get("personas"):
    tags.append("personas") 
  misfondos.insert({
                    "titulo": titu,
                    "descripcion": desc, 
                    "fondo": archivo,
                    "tags": tags
                  })
  return redirect("/")

@app.route("/form_email")
def formulario_email():
  id = request.values.get("_id")
  documento = misfondos.find_one({"_id": ObjectId(id)})
  return render_template("form_email.html", id=id, fondo=documento["fondo"],
            titulo=documento["titulo"], descripcion=documento["descripcion"])

@app.route("/email", methods=["POST"])
def envia_email(): # Revisar parámetros
  id = request.values.get("_id")
  documento = misfondos.find_one({"_id":ObjectId(id)})
  msg = Message("Fondos de pantalla Flask", sender="alumno@cepibase.int")
  msg.recipients = [request.values.get("email")]
  msg.body = "Este es el fondo de pantalla seleccionado de nuestra galería."
  msg.html = render_template("email.html", titulo=documento["titulo"], descripcion=documento["descripcion"])
  with app.open_resource("./static/fondos/" + documento["fondo"]) as adj:
    msg.attach(documento["fondo"], "image/jpeg", adj.read())
  mail.send(msg)
  return redirect("/")

if __name__ == "__main__":
  app.run(debug=True)
