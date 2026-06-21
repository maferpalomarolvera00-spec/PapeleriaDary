class ConexionSingleton:

    _instancia = None

    @staticmethod
    def obtener_instancia():

        if ConexionSingleton._instancia is None:

            ConexionSingleton._instancia = ConexionSingleton()

        return ConexionSingleton._instancia

    def __init__(self):

        if ConexionSingleton._instancia is not None:
            raise Exception(
                "Solo puede existir una instancia"
            )