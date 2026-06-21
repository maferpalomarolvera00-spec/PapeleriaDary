class InventarioObserver:

    def actualizar_stock(self, stock_actual, cantidad):

        nuevo_stock = stock_actual - cantidad

        return nuevo_stock