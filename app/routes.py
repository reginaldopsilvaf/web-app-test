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

# Import biblioteca for automatic e-mail
import smtplib
servidor_email = smtplib.SMTP('smtp.gmail.com', 587)
#servidor_email = smtplib.SMTP('smtp.gmail.com')
servidor_email.starttls()
servidor_email.ehlo()
servidor_email.login('reginaldo.filho@ime.eb.br', 'zztt cvks hkhu zsow')
login = 'reginaldo.filho@ime.eb.br'
password = 'zztt cvks hkhu zsow'
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

app.config['SECRET_KEY'] = "palavra-secreta"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost/fiocruz_barbeiro'
app.config['SQLALCHEMY_TRACKMODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
conexao = psycopg2.connect(database='fiocruz_barbeiro',
                           user='postgres',
                           password='postgres',
                           host='localhost', port='5432')

class Solicitacao(db.Model):
    __tablename__='solicitacoes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50))
    email = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(100))
    dl_classification = db.Column(db.String(10))
    especialista_classification = db.Column(db.Boolean)
    nome_especialista = db.Column(db.String(50))
    img_dir = db.Column(db.String(100))

    def __init__(self, nome, email, telefone, endereco, 
                 dl_classification, img_dir, especialista_classification=None, nome_especialista=None):
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.endereco = endereco
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
    endereco = request.form.get('endereco')
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

    solicitacao = Solicitacao(nome, email, telefone, endereco, dl_classification, img_dir=img_dir)
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

        sender_email = "reginaldo.filho@ime.eb.br"
        #receiver_email = "roger.ferreira@ime.eb.br"
        receiver_email = "reginaldo.filho@ime.eb.br"
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
                <p>{nome}</p><br>
                <p>{email}</p><br>
                <p>{endereco}</p><br>
                <p>{telefone}</p><br>
                <p>{preds}</p><br>
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
    list_endereco = []
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
        list_endereco.append(item['endereco'])
        list_especialista_classification.append(item['especialista_classification'])
        list_id.append(item['id'])
        list_img_dir.append(item['img_dir'])
        list_nome.append(item['nome'])
        list_nome_especialista.append(item['nome_especialista'])
        list_telefone.append(item['telefone'])

    mapa(list_nome,list_email,list_telefone,list_endereco,list_dl_classification,
        list_especialista_classification,list_nome_especialista,list_img_dir)

    return render_template('especialista.html')

        # db_cursor = conexao.cursor()

        # if real_classification == 'Sim':
        #     db_cursor.execute( 
        #         '''UPDATE solicitacoes SET nome_especialista=%s,\ 
        #         dl_classification=%s WHERE id=%s''', (nome_especialista, True, id_solicitacao))
        # elif real_classification == 'Não':
        #     db_cursor.execute( 
        #         '''UPDATE solicitacoes SET nome_especialista=%s,\ 
        #         dl_classification=%s WHERE id=%s''', (nome_especialista, False, id_solicitacao))
        

        # nome = list(('joao', 'ana'))
        # email = list(('asdsad@fasd.com', 'asdasf@grsf.com'))
        # telefone = list(('2132312321', '4123231123'))
        # endereco = list(('rua lauro muller, 36', 'rua dias cabral, 82'))
        # nivel_certeza = list(('ALTA', 'BAIXA'))
        # real_classification = list((True, ''))
        # nome_especialista = list(('pedro', ''))
        # img_dir = list(('D:/fiocruz/aplicacao_web/app/uploads/exemplo_consulta.jpg', 
        #                 'D:/fiocruz/aplicacao_web/app/uploads/exemplo_consulta2.jpg'))