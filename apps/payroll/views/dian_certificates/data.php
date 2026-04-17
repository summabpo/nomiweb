$anoacumular = [v_anoacumular];

sc_lookup(databas,"SELECT DISTINCT idempleado FROM vw_ingresosyretenciones WHERE anoacumular = '$anoacumular' order by idempleado");


$array = {databas};
$longitud = count($array);

##########################INICIA ITERACION DE LA NOMINA########################
$n = 0;
for($n=0; $n<$longitud; $n++)
{
	$ide = {databas[$n][0]};
	$anoacumular = [v_anoacumular];
	############# DATOS EMPLEADO #############
	sc_lookup(dataE, "select papellido, sapellido, pnombre, snombre, docidentidad, tipodocident, fechainiciocontrato, fechafincontrato, idcontrato from vw_maestro_todos where idempleado='$ide'order by idcontrato DESC");
    $papellido = {dataE[0][0]};
	$sapellido = {dataE[0][1]};
	$pnombre = {dataE[0][2]};
	$snombre = {dataE[0][3]};
	$docidentidad = {dataE[0][4]};
	$tipodocumento5 = {dataE[0][5]};
	$inicioContrato = {dataE[0][6]};
	$finContrato = {dataE[0][7]};
	$mesInicial = array();
	$mesInicial = explode('-',$inicioContrato);
	$mesInicial = $mesInicial[1];	
	$mesFinal = array();
	$mesFinal = explode('-', $finContrato);
	$mesFinal = $mesFinal[1];
	$anoInicial = array();
	$anoInicial = explode('-',$inicioContrato);
	$anoInicial = $anoInicial[0];	
	$corteInicial = $anoacumular.'-07-01';
	$corteFinal = $anoacumular.'-12-30';
	$corteAnual = $anoacumular.'-01-01';
	$anoAnterior = $anoacumular - 1;
	
	
	if(($finContrato === NULL) or ($finContrato > $corteFinal)){
		$fechaFinal = $corteFinal;
	}else{
		$fechaFinal = $finContrato;
	}

	
	
	switch ($tipodocumento5)
	   {
		 case  'CC':
		 $tipodocumento='13';
		 break;
	     case 'TI':
		 $tipodocumento='12';
	     break;
		 case 'CE':
		 $tipodocumento = '22';
		 break;
		 case 'PA':
		 $tipodocumento = '41';
		 break;
		default:
		$tipodocumento = '11';
	   }

	############# INCAPACIDADES #####################
	sc_lookup(datainca, "select SUM(valor) from vw_ingresosyretenciones where incapacidad = '1'
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({datainca[0][0]}))
	{
	$inc = {datainca[0][0]};
	}
	else
	{
	$inc=0;
	}
	############# VACACIONES ############################
	sc_lookup(datavac, "select SUM(valor) from vw_ingresosyretenciones where (idconcepto = '24')
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({datavac[0][0]}))
	{
	$vac = {datavac[0][0]};
	}
	else
	{
	$vac = 0;
	}
	
	sc_lookup(datavaccomp, "select SUM(valor) from vw_ingresosyretenciones where (idconcepto = '32')
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({datavaccomp[0][0]}))
	{
	$vaccomp = {datavaccomp[0][0]};
	}
	else
	{
	$vaccomp = 0;
	}
	############# SALARIOS #####################
	sc_lookup(datasalario, "select SUM(valor) from vw_ingresosyretenciones where basesegsocial='1'
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({datasalario[0][0]}))
	{
	$salarios = {datasalario[0][0]} - $inc - $vac;
	}
	else
	{
	$salarios=0;
	}
	
	############# TRANSPORTE #####################
	sc_lookup(datatransporte, "select SUM(valor) from vw_ingresosyretenciones where auxtransporte='1'
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({datatransporte[0][0]}))
	{
	$transporte = {datatransporte[0][0]};
	}
	else
	{
	$transporte=0;
	}
	
	
	############ CESANTIAS E INTERESES ##########
	sc_lookup(datacesantias, "select SUM(valor) from vw_ingresosyretenciones where (idconcepto='20' or idconcepto='21') 
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({datacesantias[0][0]}))
	{	
	$cesantiasintereses ={datacesantias[0][0]};
	}
	else
	{
	$cesantiasintereses =0;
	}
	############ FONDO CESANTIAS ##########
	sc_lookup(datafondocesantias, "select SUM(valor) from vw_ingresosyretenciones where idconcepto='22' 
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({datafondocesantias[0][0]}))
	{	
	$fondocesantias ={datafondocesantias[0][0]};
	}
	else
	{
	$fondocesantias =0;
	}
	############ PRESTACIONES SOCIALES ###################
	sc_lookup(dataprestaciones, "select SUM(valor) from vw_ingresosyretenciones where prestacionsocial = '1'
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({dataprestaciones[0][0]}))
	{
	$prestacionessociales = {dataprestaciones[0][0]} - $cesantiasintereses + $vac + $vaccomp;
	}
	else
	{
	$prestacionessociales = $vac + $vaccomp;
	}
	############ VIATICOS ##############
	sc_lookup(dataviaticos, "select SUM(valor) from vw_ingresosyretenciones where viaticos = '1'
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({dataviaticos[0][0]}))
	{
	$viaticos = {dataviaticos[0][0]};
	}
	else
	{
	$viaticos = 0;
	}
	
	############# GASTOS DE REPRESENTACION ########
	sc_lookup(datagr, "select SUM(valor) from vw_ingresosyretenciones where gastosderep = '1'
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({datagr[0][0]}))
	{
	$gastosderepresentacion = {datagr[0][0]};
	}
	else
	{
	$gastosderepresentacion = 0;
	}
		
	############# APORTES A SALUD #################
	sc_lookup(datasalud, "select SUM(valor) from vw_ingresosyretenciones where idconcepto = '60'
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({datasalud[0][0]}))
	{
	$salud = {datasalud[0][0]}*-1;
	}
	else
	{
	$salud = 0;
	}
	
	############# APORTES A PENSION Y FSP #############
	sc_lookup(datapension, "select SUM(valor) from vw_ingresosyretenciones where (idconcepto = '70' or idconcepto = '90')
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({datapension[0][0]}))
	{
	$pension = {datapension[0][0]}*-1;
	}
	else
	{
	$pension = 0;
	}
	
	############# APORTES VOLUNTARIOS PENSIONES ##########
	sc_lookup(datavoluntaria, "select SUM(valor) from vw_ingresosyretenciones where (idconcepto = '53')
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({datavoluntaria[0][0]}))
	{
	$voluntaria = {datavoluntaria[0][0]}*-1;
	}
	else
	{
	$voluntaria = 0;
	}
	
	############# APORTES VOLUNTARIOS AFC #################
	sc_lookup(dataafc, "select SUM(valor) from vw_ingresosyretenciones where (idconcepto = '56')
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({dataafc[0][0]}))
	{
	$afc = {dataafc[0][0]}*-1;
	}
	else
	{
	$afc = 0;
	}
	
	############# DEVOLUCIONES DE APORTES #################
	sc_lookup(datadev, "select SUM(valor) from vw_ingresosyretenciones where (idconcepto = '39' or idconcepto = '56' OR idconcepto = '70' OR idconcepto = '90')
	 AND valor > 0 AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({datadev[0][0]}))
	{
	$dev = {datadev[0][0]};
	}
	else
	{
	$dev = 0;
	}
	
	############# RETEFUENTE ############################
	sc_lookup(datarf, "select SUM(valor) from vw_ingresosyretenciones where (idconcepto = '55')
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({datarf[0][0]}))
	{
	$rf = {datarf[0][0]}*-1;
	}
	else
	{
	$rf = 0;
	}
	
	############# SUSPENSIONES - LICENCIAS ############################
	sc_lookup(datasusp, "select SUM(valor) from vw_ingresosyretenciones where (idconcepto = '30' OR idconcepto = '31')
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({datasusp[0][0]}))
	{
	$susp = {datasusp[0][0]};
	}
	else
	{
	$susp = 0;
	}
	
	############## TOTAL INGRESOS BRUTOS ################
	sc_lookup(dataib, "select SUM(valor) from vw_ingresosyretenciones where (tipoconcepto=1)
	AND idempleado='$ide' AND anoacumular='$anoacumular'");
	
	if(!empty({dataib[0][0]}))
	{
	$ib = {dataib[0][0]} - $susp;
	}
	else
	{
	$ib = 0;
	}
	
	############## TOTAL INGRESOS PROMEDIO 6 MESES ################
	
		if((empty($finContrato) or ($finContrato > $corteFinal)) AND ($inicioContrato < $corteInicial)){
			$mesFinal = 12;
			$mesInicial = 7;
			$anoPrevio = $anoacumular;
		}
	
	    if((empty($finContrato) or ($finContrato > $corteFinal)) AND ($inicioContrato > $corteInicial)){
			$mesFinal = 12;
			$anoPrevio = $anoacumular;
		}
	
		if(!empty($finContrato)){
			$mesInicial = $mesFinal - 5;
			$anoPrevio = $anoacumular;
			if($mesInicial <=0){
			   $mesInicial = 12 + $mesInicial;
			   $anoPrevio = $anoacumular - 1;
		    }
			#echo('mesinicial:'.$mesInicial.' anoacumular:'.$anoacumular.' anoprevio: '.$anoPrevio.' mesfinal:'.$mesFinal);
	    }
	
	$mesesPromedio = $mesFinal - $mesInicial + 1;
	if($mesesPromedio  < 0){
		$mesesPromedio = 12 + $mesesPromedio;
	} 
	
	$ingresoPromedio = 0;
	$ingresoPromedioTotal = 0;
	$anoacumular = $anoPrevio;
	$iteraciones = 0;
	$mesesDivision = 0;
		
	while($iteraciones < $mesesPromedio) {	
			
		    if($mesInicial > 12){
			  $mesInicial = $mesInicial - 12;
			  $anoacumular = $anoacumular + 1;
			}
		sc_lookup(datamesp, "select idmes, mes from meses where idmes = $mesInicial");
			
			$idm = {datamesp[0][1]};
			$idav = $anoacumular;
	
		sc_lookup(dataprom6, "select SUM(valor) from vw_ingresosyretenciones where ingresotributario = '1'
		AND idempleado='$ide' AND mesacumular = '$idm' AND anoacumular='$idav'");

		if(!empty({dataprom6[0][0]})){
		$ingresoPromedio = {dataprom6[0][0]};
		}else{
		$ingresoPromedio = 0;
		}
		
		if($ingresoPromedio>0){
			$mesesDivision = $mesesDivision + 1;
		}
		$ingresoPromedioTotal = $ingresoPromedioTotal + $ingresoPromedio;
		$mesInicial = $mesInicial + 1;
		$iteraciones = $iteraciones + 1;
		
	} #FIN WHILE
	    if($mesesDivision == 0){
			 $promedioTributario = 0;
		}else{
	         $promedioTributario = ceil($ingresoPromedioTotal / $mesesDivision);
			 }
	 #$anoacumular = [v_anoacumular];
	############# OTROS PAGOS ######################
	
	$op=$ib-($salarios+$cesantiasintereses+$prestacionessociales+$viaticos+$gastosderepresentacion+$fondocesantias);

	
	############ INSERTAR EN BBDD ##################
	sc_exec_sql("INSERT INTO ingresosyretenciones (idingret, idempleado, docidentidad, tipodocumento, papellido, sapellido, pnombre, 
	snombre, salarios, anoacumular, cesantiasintereses, prestacionessociales, viaticos, gastosderepresentacion, aportessalud, otrospagos, totalingresosbrutos,aportespension, aportesvoluntarios, aportesafc, retefuente, fondocesantias, ingresolaboralpromedio, transporte ) 
	VALUES  
	(nextval('sec_ing'),'$ide','$docidentidad', '$tipodocumento','$papellido','$sapellido','$pnombre','$snombre',$salarios,'$anoacumular', '$cesantiasintereses', '$prestacionessociales', '$viaticos','$gastosderepresentacion', '$salud','$op','$ib', '$pension', '$voluntaria', '$afc', '$rf', '$fondocesantias', '$promedioTributario', '$transporte')");
	

}
