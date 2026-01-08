def aplicar_descuento_prioritario(self, detalle: Dict, horasdescuento: float) -> Dict:
        """
        Aplica el descuento de horas según prioridad:
        1. Horas diurnas ordinarias
        2. Horas nocturnas ordinarias
        3. Horas dominicales diurnas ordinarias
        4. Horas dominicales nocturnas ordinarias
        5. Horas extra diurnas
        6. Horas extra nocturnas
        7. Horas extra dominicales diurnas
        8. Horas extra dominicales nocturnas
        
        Args:
            detalle: Diccionario con las horas clasificadas
            horasdescuento: Cantidad de horas a descontar
            
        Returns:
            Diccionario con las horas después de aplicar el descuento
        """
        # Orden de prioridad para aplicar descuentos (de menor a mayor valor)
        orden_descuento = [
            'horas_diurnas_ordinarias',
            'horas_nocturnas_ordinarias',
            'horas_dominicales_diurnas_ordinarias',
            'horas_dominicales_nocturnas_ordinarias',
            'horas_extra_diurnas',
            'horas_extra_nocturnas',
            'horas_extra_dominicales_diurnas',
            'horas_extra_dominicales_nocturnas'
        ]
        
        # Crear copia del detalle para modificar
        detalle_ajustado = detalle.copy()
        descuento_restante = horasdescuento
        
        # Aplicar descuento según el orden de prioridad
        for categoria in orden_descuento:
            if descuento_restante <= 0:
                break
            
            horas_disponibles = detalle_ajustado[categoria]
            
            if horas_disponibles > 0:
                # Descontar lo que se pueda de esta categoría
                descuento_aplicado = min(horas_disponibles, descuento_restante)
                detalle_ajustado[categoria] -= descuento_aplicado
                descuento_restante -= descuento_aplicado
        
        return detalle_ajustado