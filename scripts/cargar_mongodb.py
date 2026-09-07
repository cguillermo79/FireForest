import json
from pathlib import Path
from pymongo import MongoClient

archivo = Path("nosql/detecciones_viirs.json")

with archivo.open("r", encoding="utf-8") as f:
    documentos = json.load(f)

cliente = MongoClient("mongodb://localhost:27017/")
base = cliente["fireforest"]
coleccion = base["detecciones_viirs"]

coleccion.delete_many({})
resultado = coleccion.insert_many(documentos)

print(f"Documentos insertados: {len(resultado.inserted_ids)}")
print(f"Documentos en la colección: {coleccion.count_documents({})}")

cliente.close()