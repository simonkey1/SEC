URL_SEC_GET_POR_FECHA = "https://apps.sec.cl/INTONLINEv1/ClientesAfectados/GetPorFecha"
URL_SEC_GET_HORA_SERVER = (
    "https://apps.sec.cl/INTONLINEv1/ClientesAfectados/GetHoraServer"
)

URL_SEC_PRINCIPAL = "https://www.sec.cl/interrupciones-en-linea/?view_full_site=t"
STATUS_CODE = 200
METHOD_POST = "POST"
METHOD_GET = "GET"
METHOD_PUT = "PUT"
METHOD_DELETE = "DELETE"


REQUIRED_FIELDS: list[str] = [
    "NOMBRE_REGION",
    "NOMBRE_COMUNA",
    "NOMBRE_EMPRESA",
    "CLIENTES_AFECTADOS",
    "FECHA_INT_STR",
]
