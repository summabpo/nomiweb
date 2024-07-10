sc_lookup(dataemp, "select numcuenta, banco from empresa where idempresa = '1'");

{cuenta} = {dataemp[0][0]};
$codBanco = {dataemp[0][1]};

sc_lookup(databanco, "select nombanco, digchequeo from bancos where digchequeo = '$codBanco'");

{banco} = {databanco[0][0]}.' - '.$codBanco;

[v_banco] = $codBanco;

sc_lookup(databanco, "select DISTINCT idcontrato, sum(valor) from vw_nomina  where idnomina = '[v_idnomina]' and bancocuenta !='' and cuentanomina !='' and tipocuentanomina != '' GROUP BY idcontrato");

$plano = {databanco};
$largo = count($plano);
$x=0;
$numeroTotalTraslados = 0;
$valorTotalTraslados = 0;
for ($x=0; $x<$largo; $x++)
{
$idc = {databanco[$x][0]};
$valorPago = {databanco[$x][1]};

$valorTotalTraslados = $valorTotalTraslados + $valorPago;
$numeroTotalTraslados = $numeroTotalTraslados + 1;
}

{registroscuenta} = $numeroTotalTraslados;

{valorplano} = number_format($valorTotalTraslados);



sc_lookup(datatotal, "select DISTINCT idcontrato from vw_nomina  where idnomina = '[v_idnomina]'");

$arreglo = {datatotal};

{registrossincuenta} = count($arreglo) - $numeroTotalTraslados;

if($codBanco == '51')
{
sc_btn_display ('Descargar Plano', 'on');

}
else
{
sc_btn_display ('Descargar Plano', 'off');
sc_alert('El archivo plano para este banco esta en desarrollo');
}