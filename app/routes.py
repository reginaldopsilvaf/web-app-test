from app import app
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename
from mapa import mapa
from classificador import prediction_func
import psycopg2
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow 
import json
from geopy.geocoders import Nominatim

# Import biblioteca for automatic e-mail
import smtplib
servidor_email = smtplib.SMTP('smtp.gmail.com', 587)
servidor_email.starttls()
servidor_email.ehlo()
servidor_email.login('necessita-ser-preechido-com-gmail', 'necessita-ser-preechido-com-senha')
login = 'necessita-ser-preechido-com-gmail'
password = 'necessita-ser-preechido-com-senha'
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

app.config['SECRET_KEY'] = "palavra-secreta"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost/fiocruz_barbeiro'
app.config['SQLALCHEMY_TRACKMODIFICATIONS'] = False

# Create and connect to postgreSQL database
db = SQLAlchemy(app)
ma = Marshmallow(app)
conexao = psycopg2.connect(database='banco_de_dados',
                           user='usuario',
                           password='senha',
                           host='localhost', port='5432')

class Solicitacao(db.Model):
    __tablename__='solicitacoes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20))
    logradouro = db.Column(db.String(100), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    municipio = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Numeric(precision=10, scale=5))
    longitude = db.Column(db.Numeric(precision=10, scale=5))
    dl_classification = db.Column(db.String(10))
    especialista_classification = db.Column(db.Boolean)
    nome_especialista = db.Column(db.String(50))
    img_dir = db.Column(db.String(100))

    def __init__(self, nome, email, telefone, logradouro, numero, municipio, estado, 
                 dl_classification, img_dir, especialista_classification=None, 
                 nome_especialista=None, latitude=None, longitude=None):
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.logradouro = logradouro
        self.numero = numero
        self.municipio = municipio
        self.estado = estado
        self.latitude = latitude
        self.longitude = longitude
        self.dl_classification = dl_classification
        self.img_dir = img_dir
        self.especialista_classification = especialista_classification
        self.nome_especialista = nome_especialista

class SolicitacaoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Solicitacao
        load_instance = True
    
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/envio_de_foto')
def envio_de_foto():
    return render_template('envio_de_foto.html')

@app.route('/resultado_da_consulta', methods=['POST'])
def resultado_da_consulta():
    nome = request.form.get('nome')
    email = request.form.get('email')
    logradouro = request.form.get('logradouro')
    numero = request.form.get('numero')
    municipio = request.form.get('municipio')
    estado = request.form.get('estado')
    telefone = request.form.get('telefone')
    img = request.files['file']

    # Save the image to ./uploads
    basepath = os.path.dirname(__file__)
    img_dir = os.path.join(
        basepath, 'uploads', secure_filename(img.filename))
    img.save(img_dir)

    # Make prediction
    preds = prediction_func(img_dir)
    dl_classification = preds.split('\n')[0]

    # Calculate lat and long
    loc = Nominatim(user_agent="GetLoc")
    try:
        getLoc = loc.geocode(logradouro+','+numero+','+municipio+','+estado)
        latitude = getLoc.latitude
        longitude = getLoc.longitude
        solicitacao = Solicitacao(nome, email, telefone, logradouro, numero, 
                                municipio, estado, dl_classification, img_dir=img_dir, 
                                latitude=latitude, longitude=longitude)
    except:
        solicitacao = Solicitacao(nome, email, telefone, logradouro, numero, 
                                municipio, estado, dl_classification, img_dir=img_dir)
    db.session.add(solicitacao)
    db.session.commit()

    solicitacoes = Solicitacao.query.all()
    solicitacao_schema = SolicitacaoSchema(many=True)
    output = solicitacao_schema.dump(solicitacoes)
    # Save the json to ./json
    data_bytes = jsonify(output).data
    data_string = data_bytes.decode('utf-8')
    data_string = data_string.replace('\\', '/')
    json_data = json.loads(data_string)

    basepath = os.path.dirname(__file__)
    json_dir = os.path.join(
        basepath, 'json', secure_filename('solicitacoes.json'))
    
    with open(json_dir, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

        sender_email = "gmail-que-envia"
        receiver_email = "email-que-recebe"
        message = MIMEMultipart("alternative")
        message["Subject"] = "Teste com HTML e Imagem"
        message["From"] = sender_email
        message["To"] = receiver_email

        # write the text/plain part
        text = """"""

        # write the HTML part
        html = f"""\
        <html>
            <body>
                <p>Nome: {nome}</p><br>
                <p>Email: {email}</p><br>
                <p>Endereço: {logradouro+','+numero+','+municipio+','+estado}</p><br>
                <p>Telefone: {telefone}</p><br>
                <p>Classificação por IA: {preds}</p><br>
            </body>
        </html>
        """

        fp = open(img_dir, 'rb')
        image = MIMEImage(fp.read())
        fp.close()

        # convert both parts to MIMEText objects and add them to the MIMEMultipart message
        text = MIMEText(html, "html")
        message.attach(text)
        message.attach(image)

        servidor_email.sendmail(sender_email, receiver_email, message.as_string())

        print('Sent')

    return preds

@app.route('/especialista')
def especialista():
    basepath = os.path.dirname(__file__)
    json_dir = os.path.join(
        basepath, 'json', secure_filename('solicitacoes.json'))

    with open(json_dir, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Inicializar listas para armazenar os valores
    list_dl_classification = []
    list_email = []
    list_logradouro = []
    list_numero = []
    list_municipio = []
    list_estado = []
    list_latitude = []
    list_longitude = []
    list_especialista_classification = []
    list_id = []
    list_img_dir = []
    list_nome = []
    list_nome_especialista = []
    list_telefone = []

    # Percorrer a lista de dicionários e extrair os valores
    for item in data:
        list_dl_classification.append(item['dl_classification'])
        list_email.append(item['email'])
        list_logradouro.append(item['logradouro'])
        list_numero.append(item['numero'])
        list_municipio.append(item['municipio'])
        list_estado.append(item['estado'])
        list_latitude.append(item['latitude'])
        list_longitude.append(item['longitude'])
        list_especialista_classification.append(item['especialista_classification'])
        list_id.append(item['id'])
        list_img_dir.append(item['img_dir'])
        list_nome.append(item['nome'])
        list_nome_especialista.append(item['nome_especialista'])
        list_telefone.append(item['telefone'])

    mapa(list_nome,list_email,list_telefone,list_logradouro,list_numero,list_municipio,list_estado,
         list_latitude,list_longitude,list_dl_classification,list_especialista_classification,list_nome_especialista,list_img_dir)

    return render_template('especialista.html')
