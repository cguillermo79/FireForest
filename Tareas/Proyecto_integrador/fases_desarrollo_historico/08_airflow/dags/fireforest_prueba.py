from datetime import datetime

from airflow.sdk import dag, task


@dag(
    dag_id="fireforest_prueba",
    description="Primer flujo automatizado del proyecto FireForest",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["FireForest"],
)
def flujo_fireforest():

    @task
    def comprobar_entorno():
        print("Airflow funciona correctamente en FireForest")
        return "entorno_validado"

    @task
    def registrar_resultado(estado):
        print(f"Resultado recibido: {estado}")
        print("El pipeline de prueba terminó correctamente")

    estado = comprobar_entorno()
    registrar_resultado(estado)


flujo_fireforest()