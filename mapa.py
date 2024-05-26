import folium
from geopy.geocoders import Nominatim
import base64

def mapa(nome,email,telefone,endereco,nivel_certeza,
        real_classification,nome_especialista,img_dir):
    
    map = folium.Map(location=[-23.0, -43.0], zoom_start=8)
    fg = folium.FeatureGroup(name="Mapa de fotos enviadas no portal").add_to(map)

    for nome,email,telefone,endereco,nivel_certeza,real_classification,nome_especialista,img_dir in zip(nome,email,telefone,endereco,nivel_certeza,real_classification,nome_especialista,img_dir):
        loc = Nominatim(user_agent="GetLoc")
        getLoc = loc.geocode(endereco)
        lat = getLoc.latitude
        long = getLoc.longitude

        encoded = base64.b64encode(open(img_dir, 'rb').read()).decode()
        html = f'''<b>Nome:</b><br>
                {nome}<br>
                <b>Email:</b><br>
                {email}<br>
                <b>Telefone:</b><br>
                {telefone}<br>
                <b>Endereço:</b><br>
                {endereco}<br>
                <b>Chance de ser barbeiro:</b><br>
                {nivel_certeza}<br>
                <b>Classificação do especialista:</b><br>
                {real_classification}<br>
                <b>Nome do especialista:</b><br>
                {nome_especialista}<br><br>
                Fotografia:<br>
                <img src="data:image/jpeg;base64,{encoded}" width=200px>'''

        iframe = folium.IFrame(html,width=350,height=450)
        popup = folium.Popup(iframe,max_width=450)
        if real_classification == '':
            marker = folium.Marker([lat,long], popup=(popup),
                                tooltip=f'ID: {id}', 
                                icon=folium.Icon(icon='exclamation-sign',icon_color='red',color='black')).add_to(map)
        else:
            marker = folium.Marker([lat,long], popup=(popup),
                                tooltip=f'ID: {id}', 
                                icon=folium.Icon(icon='ok',icon_color='green',color='black')).add_to(map)

        map.add_child(marker)

    map.save('D:/fiocruz/aplicacao_web/app/templates/especialista.html')