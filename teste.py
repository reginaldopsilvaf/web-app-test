import os
from werkzeug.utils import secure_filename
import json

output_file = 'D:/fiocruz/aplicacao_web/app/json/solicitacoes.json'
with open(output_file, 'r', encoding='utf-8') as f:
    json_data = json.load(f)
#data = json.load('D:/fiocruz/aplicacao_web/app/json/solicitacoes.json')
print(type(json_data))