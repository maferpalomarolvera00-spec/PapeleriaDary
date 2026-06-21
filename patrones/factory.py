class Administrador:

    def obtener_rol(self):
        return "Administrador"


class Empleado:

    def obtener_rol(self):
        return "Empleado"


class UserFactory:

    @staticmethod
    def crear_usuario(rol):

        if rol == "Administrador":
            return Administrador()

        elif rol == "Empleado":
            return Empleado()

        return None