from sanic import Sanic, response
from sqlalchemy import create_engine, select
from models import Edificacao
from geoalchemy2.functions import ST_AsGeoJSON
import json
from shapely.geometry import shape
from sqlalchemy.orm import Session
app = Sanic(__name__)

engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgis_33_sample", echo=True)

@app.route("edificacao", methods=["GET"])
async def listar_edificacoes(request):
    feature_collection = {
        "type": "FeatureCollection",
        "features": []
    }
    query = select(Edificacao.id, Edificacao.nome, ST_AsGeoJSON(Edificacao.geom)).order_by(Edificacao.id)
    with engine.connect() as conn:
        rows = conn.execute(query)
        for id, nome, geometry in rows:
            feature = {
                "id": id,
                "type": "Feature",
                "properties": {
                    "nome": nome
                },
                "geometry": json.loads(geometry)
            }
            feature_collection["features"].append(feature)

    if 'text/html' in request.headers.get("accept").split(","):
        with open('map.html') as map_file:
            map_file_content = map_file.read()
            map_file_content = map_file_content.replace('const geojsonObject = {}', f'const geojsonObject = {json.dumps(feature_collection)}')
        return response.html(map_file_content)
    return response.json(feature_collection, status=200)

@app.route("edificacao", methods=["POST"])
async def criar_edificacoes(request):
    geom = shape(request.json['geometry'])
    geom_str = f"SRID=4674;{geom}"

    edificacao = Edificacao(
        nome=request.json['properties']['nome'],
        geom=geom_str
    )
    with Session(engine) as session:
        session.add(edificacao)
        session.commit()

    return response.json({"Feito": "Edificacao salva com sucesso"}, status=201)

@app.route("edificacao/<id:int>", methods=["PUT"])
async def alterar_edificacao(request, id):

    with Session(engine) as session:
        edificacao = session.get(Edificacao, id)
        edificacao.nome = request.json["properties"]["nome"]
        session.add(edificacao)
        session.commit()
    return response.json(body=None, status=204)

@app.route("edificacao/<id:int>", methods=["DELETE"])
async def remover_edificacao(request, id):
    with Session(engine) as session:
        edicicacao = session.get(Edificacao, id)
        session.delete(edicicacao)
        session.commit()
    return response.json(body=None, status=204)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8050)
