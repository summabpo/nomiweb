# nomiweb/apps/pila/tests/test_payload_builder.py

import json
from decimal import Decimal, ROUND_HALF_UP
from django.test import TestCase, SimpleTestCase
from apps.pila.services.payload_builder import build_payload_pila_minimo, _generar_registros_empleado


class PayloadPILATestCase(TestCase):
    """
    Tests para validar la estructura y contenido del payload PILA.
    
    Para ejecutar:
        python manage.py test apps.pila.tests.test_payload_builder
    
    Para ejecutar un test específico:
        python manage.py test apps.pila.tests.test_payload_builder.PayloadPILATestCase.test_estructura_empresa
    """
    
    # Configurar aquí los datos de prueba
    EMPRESA_ID_TEST = 1  # Cambiar por un ID válido en tu BD
    PERIODO_TEST = "2026-02"  # Cambiar por un periodo válido
    
    def setUp(self):
        """Se ejecuta antes de cada test"""
        try:
            self.payload = build_payload_pila_minimo(
                empresa_id_interno=self.EMPRESA_ID_TEST,
                periodo=self.PERIODO_TEST
            )
        except Exception as e:
            self.fail(f"No se pudo generar el payload: {str(e)}")
    
    def test_estructura_basica(self):
        """Verifica que el payload tenga la estructura básica requerida"""
        self.assertIn('empresa', self.payload)
        self.assertIn('periodo', self.payload)
        self.assertIn('planilla', self.payload)
        self.assertIn('empleados', self.payload)
        self.assertIn('parametros', self.payload)
    
    def test_estructura_empresa(self):
        """Verifica la estructura completa de la sección empresa"""
        empresa = self.payload['empresa']
        
        # Campos obligatorios
        campos_obligatorios = [
            'id_interno',
            'nit',
            'razon_social',
            'sucursal',
            'tipo_documento_aportante',
            'tipo_aportante',
            'clase_aportante',
            'flags'
        ]
        
        for campo in campos_obligatorios:
            self.assertIn(campo, empresa, f"Falta el campo 'empresa.{campo}'")
        
        # Validar tipos
        self.assertIsInstance(empresa['id_interno'], int)
        self.assertIsInstance(empresa['nit'], str)
        self.assertIsInstance(empresa['razon_social'], str)
        self.assertIsInstance(empresa['tipo_aportante'], str)
        self.assertIsInstance(empresa['clase_aportante'], str)
        
        # Validar valores
        self.assertGreater(len(empresa['nit']), 0, "NIT no puede estar vacío")
        self.assertGreater(len(empresa['razon_social']), 0, "Razón social no puede estar vacía")
        self.assertEqual(len(empresa['tipo_aportante']), 2, "tipo_aportante debe tener 2 caracteres")
        self.assertEqual(len(empresa['clase_aportante']), 1, "clase_aportante debe tener 1 carácter")
        
        # Sucursal debe estar vacía (presentación única)
        self.assertEqual(empresa['sucursal'], "", "Sucursal debe estar vacía (presentación única)")
    
    def test_estructura_planilla(self):
        """Verifica la estructura de la sección planilla"""
        planilla = self.payload['planilla']
        
        campos_obligatorios = ['tipo_planilla', 'numero_interno', 'fecha_generacion']
        for campo in campos_obligatorios:
            self.assertIn(campo, planilla, f"Falta el campo 'planilla.{campo}'")
        
        self.assertEqual(planilla['tipo_planilla'], 'E', "tipo_planilla debe ser 'E'")
        self.assertIn(str(self.EMPRESA_ID_TEST), planilla['numero_interno'])
    
    def test_estructura_empleados(self):
        """Verifica la estructura de la sección empleados"""
        empleados = self.payload['empleados']
        
        self.assertIsInstance(empleados, list, "empleados debe ser una lista")
        
        if len(empleados) == 0:
            self.skipTest("No hay empleados en el payload para este periodo")
        
        # Validar primer empleado como muestra
        emp = empleados[0]
        
        campos_obligatorios = [
            'id_empleado',
            'tipo_doc',
            'num_doc',
            'primer_apellido',
            'segundo_apellido',
            'primer_nombre',
            'segundo_nombre',
            'cod_departamento',
            'cod_municipio',
            'tipo_cotizante',
            'subtipo_cotizante',
            'salario_basico',
            'entidades',
            'flags',
            'dias',
            'ibc',
            'tarifas',
            'novedades'
        ]
        
        for campo in campos_obligatorios:
            self.assertIn(campo, emp, f"Falta el campo 'empleados[].{campo}'")
    
    def test_nombres_empleados(self):
        """Verifica que los nombres de empleados estén correctamente estructurados"""
        empleados = self.payload['empleados']
        
        if len(empleados) == 0:
            self.skipTest("No hay empleados en el payload")
        
        for emp in empleados:
            emp_id = emp['id_empleado']
            
            # Verificar que los campos existan
            self.assertIn('primer_apellido', emp)
            self.assertIn('segundo_apellido', emp)
            self.assertIn('primer_nombre', emp)
            self.assertIn('segundo_nombre', emp)
            
            # Verificar tipos
            self.assertIsInstance(emp['primer_apellido'], str)
            self.assertIsInstance(emp['segundo_apellido'], str)
            self.assertIsInstance(emp['primer_nombre'], str)
            self.assertIsInstance(emp['segundo_nombre'], str)
            
            # Al menos primer nombre y primer apellido deben tener contenido
            self.assertGreater(
                len(emp['primer_nombre'].strip()), 0,
                f"Empleado {emp_id}: primer_nombre vacío"
            )
            self.assertGreater(
                len(emp['primer_apellido'].strip()), 0,
                f"Empleado {emp_id}: primer_apellido vacío"
            )
    
    def test_dane_empleados(self):
        """Verifica que los códigos DANE estén presentes"""
        empleados = self.payload['empleados']
        
        if len(empleados) == 0:
            self.skipTest("No hay empleados en el payload")
        
        empleados_sin_dane = []
        
        for emp in empleados:
            emp_id = emp['id_empleado']
            
            self.assertIn('cod_departamento', emp)
            self.assertIn('cod_municipio', emp)
            
            if not emp['cod_departamento'] or not emp['cod_municipio']:
                empleados_sin_dane.append(emp_id)
        
        if empleados_sin_dane:
            self.fail(
                f"{len(empleados_sin_dane)} empleados sin código DANE: "
                f"{empleados_sin_dane[:5]}{'...' if len(empleados_sin_dane) > 5 else ''}"
            )
    
    def test_tarifas_arl_empleados(self):
        """Verifica que las tarifas ARL estén presentes"""
        empleados = self.payload['empleados']
        
        if len(empleados) == 0:
            self.skipTest("No hay empleados en el payload")
        
        empleados_sin_tarifa = []
        
        for emp in empleados:
            emp_id = emp['id_empleado']
            tarifas = emp.get('tarifas', {})
            
            self.assertIn('arl', tarifas, f"Empleado {emp_id}: falta campo tarifas.arl")
            
            if tarifas['arl'] is None or tarifas['arl'] == '':
                empleados_sin_tarifa.append(emp_id)
        
        if empleados_sin_tarifa:
            print(f"\n⚠️  Advertencia: {len(empleados_sin_tarifa)} empleados sin tarifa ARL")
    
    def test_entidades_empleados(self):
        """Verifica que las entidades (EPS, AFP, ARL, CCF) estén presentes"""
        empleados = self.payload['empleados']
        
        if len(empleados) == 0:
            self.skipTest("No hay empleados en el payload")
        
        for emp in empleados:
            emp_id = emp['id_empleado']
            entidades = emp.get('entidades', {})
            
            campos_entidades = ['eps', 'afp', 'arl', 'caja']
            for campo in campos_entidades:
                self.assertIn(campo, entidades, f"Empleado {emp_id}: falta entidad {campo}")
    
    def test_dias_cotizacion(self):
        """Verifica que los días de cotización sean válidos"""
        empleados = self.payload['empleados']
        
        if len(empleados) == 0:
            self.skipTest("No hay empleados en el payload")
        
        for emp in empleados:
            emp_id = emp['id_empleado']
            dias = emp.get('dias', {})
            
            for subsistema in ['salud', 'pension', 'arl', 'caja']:
                self.assertIn(subsistema, dias, f"Empleado {emp_id}: falta dias.{subsistema}")
                
                valor_dias = dias[subsistema]
                self.assertIsInstance(valor_dias, int)
                self.assertGreaterEqual(valor_dias, 0, f"Días {subsistema} negativos")
                self.assertLessEqual(valor_dias, 30, f"Días {subsistema} > 30")
    
    def test_ibc_empleados(self):
        """Verifica que los IBC estén presentes"""
        empleados = self.payload['empleados']
        
        if len(empleados) == 0:
            self.skipTest("No hay empleados en el payload")
        
        for emp in empleados:
            emp_id = emp['id_empleado']
            ibc = emp.get('ibc', {})
            
            campos_ibc = ['salud', 'pension', 'arl', 'parafiscales']
            for campo in campos_ibc:
                self.assertIn(campo, ibc, f"Empleado {emp_id}: falta ibc.{campo}")
                
                # Verificar que sea string (viene del payload como string)
                self.assertIsInstance(ibc[campo], str)
    
    def test_parametros(self):
        """Verifica que los parámetros estén presentes"""
        parametros = self.payload.get('parametros', {})
        
        campos_obligatorios = ['smmlv', 'tope_ibc_smmlv', 'dias_base']
        for campo in campos_obligatorios:
            self.assertIn(campo, parametros, f"Falta parámetro {campo}")
        
        # Verificar valores razonables
        self.assertGreater(parametros['smmlv'], 0, "SMMLV debe ser > 0")
        self.assertEqual(parametros['tope_ibc_smmlv'], 25, "Tope IBC debe ser 25")
        self.assertEqual(parametros['dias_base'], 30, "Días base debe ser 30")
    
    def test_json_serializable(self):
        """Verifica que el payload sea serializable a JSON"""
        try:
            json_str = json.dumps(self.payload, default=str, ensure_ascii=False)
            self.assertIsInstance(json_str, str)
            
            # Verificar que se pueda parsear de vuelta
            parsed = json.loads(json_str)
            self.assertIsInstance(parsed, dict)
        except Exception as e:
            self.fail(f"El payload no es serializable a JSON: {str(e)}")
    
    def test_payload_completo_info(self):
        """Imprime información resumida del payload (no es un test de validación)"""
        print("\n" + "="*60)
        print("RESUMEN DEL PAYLOAD GENERADO")
        print("="*60)
        
        empresa = self.payload['empresa']
        print(f"\n📊 EMPRESA:")
        print(f"  • Razón social: {empresa['razon_social']}")
        print(f"  • NIT: {empresa['nit']}")
        print(f"  • Tipo aportante: {empresa['tipo_aportante']}")
        print(f"  • Clase aportante: {empresa['clase_aportante']}")
        
        empleados = self.payload['empleados']
        print(f"\n👥 EMPLEADOS: {len(empleados)}")
        
        if empleados:
            print(f"\n📋 Muestra (primer empleado):")
            emp = empleados[0]
            print(f"  • Nombre: {emp['primer_nombre']} {emp['segundo_nombre']} "
                  f"{emp['primer_apellido']} {emp['segundo_apellido']}")
            print(f"  • Documento: {emp['tipo_doc']} {emp['num_doc']}")
            print(f"  • DANE: Dpto {emp['cod_departamento']}, Mun {emp['cod_municipio']}")
            print(f"  • Días: Salud={emp['dias']['salud']}, Pensión={emp['dias']['pension']}, "
                  f"ARL={emp['dias']['arl']}, CCF={emp['dias']['caja']}")
            print(f"  • Tarifa ARL: {emp['tarifas']['arl']}")
            print(f"  • Novedades: {len(emp['novedades'])}")
        
        print("\n" + "="*60 + "\n")


class IncapacidadIBCUnitTestCase(SimpleTestCase):
    def test_ige_aplica_2_3_y_piso_smmlv_proporcional(self):
        dias_incap = 10
        factor_incapacidad = Decimal("2") / Decimal("3")  # empresa.ige100=NO

        ibc_base_mes_anterior = Decimal("3000000")  # indicador 6
        smmlv = Decimal("1200000")
        factor_dias = Decimal(dias_incap) / Decimal(30)

        ibc_calc = ibc_base_mes_anterior * factor_incapacidad * factor_dias
        smmlv_prop = smmlv * factor_dias
        ibc_final = ibc_calc if ibc_calc >= smmlv_prop else smmlv_prop
        expected = int(ibc_final.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        registros = _generar_registros_empleado(
            dias_base=30,
            novedades_vac=[],
            novedades_incap=[{"codigo": "IGE", "dias": dias_incap}],
            novedad_vsp=None,
            novedades_ing_ret=[],
            ibc_actual={"salud_pension": Decimal("0"), "arl": Decimal("0"), "caja": Decimal("0")},
            ibc_anterior={"salud_pension": ibc_base_mes_anterior, "arl": Decimal("0"), "caja": Decimal("0")},
            vst=Decimal("0"),
            salario_contrato=0,
            fecha_periodo=None,
            factor_incapacidad=factor_incapacidad,
            smmlv=smmlv,
        )

        self.assertGreaterEqual(len(registros), 1)
        linea_incap = registros[0]
        self.assertEqual(linea_incap["tipo_linea"], "IGE")
        self.assertEqual(linea_incap["dias"]["arl"], 0)
        self.assertEqual(int(linea_incap["ibc"]["salud"]), expected)
        # En la línea, el IBC debe ser consistente entre subsistemas.
        self.assertEqual(int(linea_incap["ibc"]["arl"]), expected)

    def test_irl_no_aplica_2_3(self):
        dias_incap = 10
        factor_incapacidad = Decimal("2") / Decimal("3")  # aunque sea NO, IRL paga 100%

        ibc_base_mes_anterior = Decimal("3000000")
        smmlv = Decimal("1000000")
        factor_dias = Decimal(dias_incap) / Decimal(30)

        ibc_calc = ibc_base_mes_anterior * Decimal("1") * factor_dias  # IRL al 100%
        smmlv_prop = smmlv * factor_dias
        ibc_final = ibc_calc if ibc_calc >= smmlv_prop else smmlv_prop
        expected = int(ibc_final.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        registros = _generar_registros_empleado(
            dias_base=30,
            novedades_vac=[],
            novedades_incap=[{"codigo": "IRL", "dias": dias_incap}],
            novedad_vsp=None,
            novedades_ing_ret=[],
            ibc_actual={"salud_pension": Decimal("0"), "arl": Decimal("0"), "caja": Decimal("0")},
            ibc_anterior={"salud_pension": ibc_base_mes_anterior, "arl": Decimal("0"), "caja": Decimal("0")},
            vst=Decimal("0"),
            salario_contrato=0,
            fecha_periodo=None,
            factor_incapacidad=factor_incapacidad,
            smmlv=smmlv,
        )

        linea_incap = registros[0]
        self.assertEqual(linea_incap["tipo_linea"], "IRL")
        self.assertEqual(linea_incap["dias"]["arl"], 0)
        self.assertEqual(int(linea_incap["ibc"]["salud"]), expected)
        self.assertEqual(int(linea_incap["ibc"]["arl"]), expected)

    def test_ige_aplica_piso_cuando_2_3_trae_por_debajo(self):
        dias_incap = 10
        factor_incapacidad = Decimal("2") / Decimal("3")  # empresa.ige100=NO

        ibc_base_mes_anterior = Decimal("1000000")
        smmlv = Decimal("900000")
        factor_dias = Decimal(dias_incap) / Decimal(30)

        ibc_calc = ibc_base_mes_anterior * factor_incapacidad * factor_dias
        smmlv_prop = smmlv * factor_dias
        self.assertLess(ibc_calc, smmlv_prop)  # asegurar que cae al piso

        expected = int(smmlv_prop.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        registros = _generar_registros_empleado(
            dias_base=30,
            novedades_vac=[],
            novedades_incap=[{"codigo": "IGE", "dias": dias_incap}],
            novedad_vsp=None,
            novedades_ing_ret=[],
            ibc_actual={"salud_pension": Decimal("0"), "arl": Decimal("0"), "caja": Decimal("0")},
            ibc_anterior={"salud_pension": ibc_base_mes_anterior, "arl": Decimal("0"), "caja": Decimal("0")},
            vst=Decimal("0"),
            salario_contrato=0,
            fecha_periodo=None,
            factor_incapacidad=factor_incapacidad,
            smmlv=smmlv,
        )

        linea_incap = registros[0]
        self.assertEqual(linea_incap["tipo_linea"], "IGE")
        self.assertEqual(linea_incap["dias"]["arl"], 0)
        self.assertEqual(int(linea_incap["ibc"]["salud"]), expected)
        self.assertEqual(int(linea_incap["ibc"]["arl"]), expected)

    def test_lma_paga_100_y_aplica_piso_proporcional(self):
        dias_incap = 10
        factor_incapacidad = Decimal("2") / Decimal("3")  # empresa.ige100=NO, pero LMA paga 100%

        ibc_base_mes_anterior = Decimal("500000")  # indicador 6 (suficiente para caer al piso con 2/3, pero aquí se aplica 100%)
        smmlv = Decimal("900000")
        factor_dias = Decimal(dias_incap) / Decimal(30)

        ibc_calc = ibc_base_mes_anterior * Decimal("1") * factor_dias  # LMA al 100%
        smmlv_prop = smmlv * factor_dias
        ibc_final = ibc_calc if ibc_calc >= smmlv_prop else smmlv_prop
        expected = int(ibc_final.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        registros = _generar_registros_empleado(
            dias_base=30,
            novedades_vac=[],
            novedades_incap=[{"codigo": "LMA", "dias": dias_incap}],
            novedad_vsp=None,
            novedades_ing_ret=[],
            ibc_actual={"salud_pension": Decimal("0"), "arl": Decimal("0"), "caja": Decimal("0")},
            ibc_anterior={
                "salud_pension": ibc_base_mes_anterior,
                "arl": Decimal("0"),
                "caja": Decimal("0"),
            },
            vst=Decimal("0"),
            salario_contrato=0,
            fecha_periodo=None,
            factor_incapacidad=factor_incapacidad,
            smmlv=smmlv,
        )

        linea_incap = registros[0]
        self.assertEqual(linea_incap["tipo_linea"], "LMA")
        self.assertEqual(linea_incap["dias"]["arl"], 0)
        self.assertEqual(int(linea_incap["ibc"]["salud"]), expected)
        self.assertEqual(int(linea_incap["ibc"]["arl"]), expected)
