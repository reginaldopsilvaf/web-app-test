from app import app
from flask import render_template, request, flash, redirect
import os
from werkzeug.utils import secure_filename
from mapa import mapa
from classificador import prediction_func
import psycopg2
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
conexao = psycopg2.connect(database='fiocruz_barbeiro',
                           user='postgres',
                           password='postgres',
                           host='localhost', port='5432')

app.config['SECRET_KEY'] = "palavra-secreta"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost/fiocruz_barbeiro'
app.config['SQLALCHEMY_TRACKMODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)

class Solicitacao(db.Model):
    __tablename__='solicitacoes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50))
    email = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(100))
    dl_classification = db.Column(db.String(8))
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

    def __repr__(self):
        return "Solicitação: {}".format(self.id)

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

    return preds

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/autenticar', methods=['GET','POST'])
def autenticar():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    if usuario == 'admin' and senha == 'senha123':
        # Mostrar o formulario onde o especialista poderá preencher sua classificação 
        # e ver o mapa com os marcadores de envios de fotos indicando se já foram 
        # classificadas por um especialista
        # db_cursor = conexao.cursor()

        # id_solicitacao = request.form.get('id')
        # real_classification = request.form.get('reposta_especialista')
        # nome_especialista = request.form.get('nome_especialista')

        # if real_classification == 'Sim':
        #     db_cursor.execute( 
        #         '''UPDATE solicitacoes SET nome_especialista=%s,\ 
        #         dl_classification=%s WHERE id=%s''', (nome_especialista, True, id_solicitacao))
        # elif real_classification == 'Não':
        #     db_cursor.execute( 
        #         '''UPDATE solicitacoes SET nome_especialista=%s,\ 
        #         dl_classification=%s WHERE id=%s''', (nome_especialista, False, id_solicitacao))
        

        nome = list(('joao', 'ana'))
        email = list(('asdsad@fasd.com', 'asdasf@grsf.com'))
        telefone = list(('2132312321', '4123231123'))
        endereco = list(('rua lauro muller, 36', 'rua dias cabral, 82'))
        nivel_certeza = list(('ALTA', 'BAIXA'))
        real_classification = list((True, ''))
        nome_especialista = list(('pedro', ''))
        img_dir = list(('D:/fiocruz/aplicacao_web/app/uploads/exemplo_consulta.jpg', 
                        'D:/fiocruz/aplicacao_web/app/uploads/exemplo_consulta2.jpg'))
        
        #mapa(nome,email,telefone,endereco,nivel_certeza,real_classification,nome_especialista,img_dir)
        
        return render_template('especialista.html')
    else:
        flash("Dados inválidos")
        flash("Login ou senha inválidos")
        return redirect('/login')
    
    # u = Usuario(nome, email, senha)
    # db.session.add(u)
    # db.session.commit()
    # return 'Dados cadastrados com sucesso'
