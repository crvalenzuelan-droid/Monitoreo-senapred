var script = document.createElement('script');
script.src = "https://archivos.meteochile.gob.cl/portaldmc/meteochile/js/indice_radiacion.js?" + Math.random();
document.head.appendChild(script);
var hayPronosticoUVB = false;

// Serrod :: 30/11/2015

var urlLocalJsx = "https://archivos.meteochile.gob.cl/portaldmc/localJS";

var labelHTML = '';

var estilo_left_mapa = 0;
var estilo_top_mapa = 0;

var estilo_left_mapa2 = estilo_left_mapa + 280;
var estilo_top_mapa2 = estilo_top_mapa;

var estilo_left_mapa3 = estilo_left_mapa + 550;
var estilo_top_mapa3 = estilo_top_mapa;

var periodoLocal = periodoPronostico;
var indicemostrando = '';

var posicion_tabla = [];
posicion_tabla.push({left: 300, top: 150}); // 0
posicion_tabla.push({left: 250, top: 300}); // 1
posicion_tabla.push({left: 300, top: 400}); // 2
posicion_tabla.push({left: 250, top: 450}); // 3
posicion_tabla.push({left: 80, top: 400}); // 4
posicion_tabla.push({left: 400, top: 350}); // 5
posicion_tabla.push({left: 250, top: 300}); // 6
posicion_tabla.push({left: 10, top: 400}); // 7

function dibuja() {
	botoneraDerecha()
	dibuja_mapa();
	poneiconos();
	render();
	renderCondicionActual();
	renderTemperaturasExtremas();
	renderOtrosLinks();
	//renderAnuncio();
	//renderCartaSinoptica();
}

function botoneraDerecha() {
	//labelHTML += "bie<br>";
	//$("#contenedorAvisos").append('vxzmxcvxmxxcbvmbnx');
	$("#contenedor_principal").append('<div id="contBtnDerecha"></div>');

}

function dibuja_mapa() {
	// busca el titulo para el pronostico
	var PronosticoTitulo = 'Pron&oacute;stico General';
	var id = -1;
	for (var i = 0; i < Pronostico.length; i++) {
		if (Pronostico[i].indice == "stgoc") id = i;
	};
	if (id>=0) {
		if (Pronostico[id].fechasql==fechaSQLhoy) { PronosticoTitulo += " para hoy " + Pronostico[id].fecha[0]; }
    	if (Pronostico[id].fechasql==fechaSQLmanana) { PronosticoTitulo += " para ma&ntilde;ana " + Pronostico[id].fecha[0]; }
	}

	labelHTML += '<div class="tituloPronosticoGeneral"><h2><span class="home_tituloPronosticoGeneral">'+PronosticoTitulo+'</span></h2></div>';
	//var style = 'opacity: 0.5; filter: alpha(opacity=50); z-index: 5; position: absolute;';
	var style = 'width: 190px;';

	var URL_imagenes_regiones = "https://archivos.meteochile.gob.cl/portaldmc/localJS/js/pronosticoGeneral/esquicioHome/";
	URL_imagenes_regiones = "https://archivos.meteochile.gob.cl/portaldmc/pronosticos/mapas/";

	labelHTML += '<a href="#" onclick="verDetalleRegion(\'02\');"><img id="r2" title="Región de Antofagasta" class="regionesChile" style="width: 120px; left: '+(estilo_left_mapa+215)+'px; top: '+(estilo_top_mapa+189)+'px;" src="' + URL_imagenes_regiones + 'reg02.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'01a\');"><img id="r1a" title="Región de Arica y Parinacota" class="regionesChile" style="width: 180px; left: '+(estilo_left_mapa+120)+'px; top: '+(estilo_top_mapa+81)+'px;" src="' + URL_imagenes_regiones + 'reg01a.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'01b\');"><img id="r1b" title="Región de Tarapacá" class="regionesChile" style="width: 120px; left: '+(estilo_left_mapa+201)+'px; top: '+(estilo_top_mapa+125)+'px;" src="' + URL_imagenes_regiones + 'reg01b.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'03\');"><img id="r3" title="Región de Atacama" class="regionesChile" style="width: 120px; left: '+(estilo_left_mapa+187)+'px; top: '+(estilo_top_mapa+328)+'px;" src="' + URL_imagenes_regiones + 'reg03.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'04\');"><img id="r4" title="Región de Coquimbo" class="regionesChile" style="width: 120px; left: '+(estilo_left_mapa+162)+'px; top: '+(estilo_top_mapa+452)+'px;" src="' + URL_imagenes_regiones + 'reg04.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'05\');"><img id="r5" title="Región de Valparaíso" class="regionesChile" style="width: 120px; left: '+(estilo_left_mapa+156)+'px; top: '+(estilo_top_mapa+557)+'px;" src="' + URL_imagenes_regiones + 'reg05.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'05m\');"><img id="r5m" title="Región Metropolitana de Santiago" class="regionesChile" style="width: 120px; left: '+(estilo_left_mapa+161)+'px; top: '+(estilo_top_mapa+586)+'px;" src="' + URL_imagenes_regiones + 'reg05m.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'06\');"><img id="r6" title="Región del Libertador General Bernardo O&#39;Higgins" class="regionesChile" style="width: 120px; left: '+(estilo_left_mapa+152)+'px; top: '+(estilo_top_mapa+622)+'px;" src="' + URL_imagenes_regiones + 'reg06.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'07\');"><img id="r7" title="Región del Maule" class="regionesChile" style="width: 120px; left: '+(estilo_left_mapa+134)+'px; top: '+(estilo_top_mapa+652)+'px;" src="' + URL_imagenes_regiones + 'reg07.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'09\');"><img id="r9" title="Región de La Araucanía" class="regionesChile" style="width: 120px; left: '+(estilo_left_mapa+116)+'px; top: '+(estilo_top_mapa+757)+'px;" src="' + URL_imagenes_regiones + 'reg09.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'08a\');"><img id="r8a" title="Región de Ñuble" class="regionesChile" style="width: 120px; left: '+(estilo_left_mapa+121)+'px; top: '+(estilo_top_mapa+700)+'px;" src="' + URL_imagenes_regiones + 'reg08a.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'08b\');"><img id="r8b" title="Región del Biobío" class="regionesChile" style="width: 120px; left: '+(estilo_left_mapa+104)+'px; top: '+(estilo_top_mapa+714)+'px;" src="' + URL_imagenes_regiones + 'reg08b.png" /></a>';
	
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'10a\');"><img id="r10a" title="Región de Los Rios" class="regionesChile" style="width: 120px; left: '+(estilo_left_mapa2+176)+'px; top: '+(estilo_top_mapa2+81)+'px;" src="' + URL_imagenes_regiones + 'reg10a.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'10b\');"><img id="r10b" title="Región de Los Lagos" class="regionesChile" style="width: 120px; left: '+(estilo_left_mapa2+157)+'px; top: '+(estilo_top_mapa2+118)+'px;" src="' + URL_imagenes_regiones + 'reg10b.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'11\');"><img id="r11" title="Región de Aysén del General Carlos Ibáñez del Campo" class="regionesChile" style="width: 180px; left: '+(estilo_left_mapa2+119)+'px; top: '+(estilo_top_mapa2+251)+'px;" src="' + URL_imagenes_regiones + 'reg11.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'12\');"><img id="r12" title="Región de Magallanes y de la Antártica Chilena" class="regionesChile" style="width: 330px; left: '+(estilo_left_mapa2+132)+'px; top: '+(estilo_top_mapa2+469)+'px;" src="' + URL_imagenes_regiones + 'reg12.png" /></a>';

	labelHTML += '<a href="#" onclick="verDetalleRegion(\'ip\');"><img id="rip" title="Isla de Pascua" class="regionesChile" style="width: 100px; left: '+(estilo_left_mapa+23)+'px; top: '+(estilo_top_mapa+293)+'px;" src="' + URL_imagenes_regiones + 'regip.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'jf\');"><img id="rjf" title="Archipiélago Juan Fernández" class="regionesChile" style="width: 100px;  left: '+(estilo_left_mapa+23)+'px; top: '+(estilo_top_mapa+377)+'px;" src="' + URL_imagenes_regiones + 'regjf.png" /></a>';
	labelHTML += '<a href="#" onclick="verDetalleRegion(\'an\');"><img id="rantartica" title="Península Antártica" class="regionesChile" style="width: 100px; left: '+(estilo_left_mapa2+76)+'px; top: '+(estilo_top_mapa2+710)+'px;" src="' + URL_imagenes_regiones + 'regan.png" /></a>';

	labelHTML += '<a href="#"><img id="islas1" title="Islas Felix y San Ambrosio" class="regionesChile" style="width: 100px; left: '+(estilo_left_mapa+23)+'px; top: '+(estilo_top_mapa+139)+'px;" src="' + URL_imagenes_regiones + 'islas_san_felix_y_san_ambrosio.png" /></a>';
	labelHTML += '<a href="#"><img id="islas2" title="Isla Salas y Gómez" class="regionesChile" style="width: 100px; left: '+(estilo_left_mapa+23)+'px; top: '+(estilo_top_mapa+215)+'px;" src="' + URL_imagenes_regiones + 'isla_salas_y_gomez.png" /></a>';
	labelHTML += '<a href="#"><img id="islas3" title="Islas Diego Ramírez" class="regionesChile" style="width: 60px; left: '+(estilo_left_mapa2+76)+'px; top: '+(estilo_top_mapa2+593)+'px;" src="' + URL_imagenes_regiones + 'islas_diego_ramirez.png" /></a>';


	labelHTML += '<div id="detalle_tabla" style="z-index: 9000; position: absolute; left: 100px; top: 100px; visibility: hidden; background-color: #ffffff;" class="pronostico_por_dia"><\/div>';

	//labelHTML += '<div  style="position: absolute; left: 30px; top: 800px;"><img style="width: 650px;" src="http://archivos.meteochile.gob.cl/portaldmc/meteochile/imagenes/aviso-covid-barra.png" alt=""><\/div>';

	//labelHTML += '<div id="msgAdvertencia" style="z-index: 99999; position: absolute; left: 1px; top: 7px;" onclick="document.getElementById(\'msgAdvertencia\').style.display=\'none\';"><img style="width: 1025px;" src="http://archivos.meteochile.gob.cl/portaldmc/meteochile/imagenes/meteochile_advertencia_intermitencia.png" alt=""><\/div>';
	
	// serrod 18.julio.2024
	//labelHTML += '<div id="msgAdvertencia" style="z-index: 99999; position: absolute; left: 1px; top: 7px;" onclick="document.getElementById(\'msgAdvertencia\').style.display=\'none\';"><img style="width: 1025px;" src="http://archivos.meteochile.gob.cl/portaldmc/meteochile/imagenes/meteochile_advertencia_fuera_de_servicio.png" alt=""><\/div>';

	// serrod 10.diciembre.2024
	//labelHTML += '<div id="msgAdvertencia" style="z-index: 99999; position: absolute; left: 1px; top: 7px;" onclick="document.getElementById(\'msgAdvertencia\').style.display=\'none\';"><img style="width: 1025px;" src="http://archivos.meteochile.gob.cl/portaldmc/meteochile/imagenes/meteochile_advertencias_reseteo_martes10.png" alt=""><\/div>';

	labelHTML += "<style>"
			+ ".botonDescargaProgramaPatrimonio2025 {"
			+ "	box-shadow:inset 0px 39px 0px -24px #e67a73;"
			+ "	background-color:#e4685d;"
			+ "	border-radius:19px;"
			+ "	border:1px solid #ffffff;"
			+ "	display:inline-block;"
			+ "	cursor:pointer;"
			+ "	color:#ffffff;"
			+ "	font-family:Arial;"
			+ "	font-size:15px;"
			+ "	padding:15px 15px;"
			+ "	text-decoration:none;"
			+ "	text-shadow:0px 1px 0px #b23e35;"
			+ "}"
			+ ".botonDescargaProgramaPatrimonio2025:hover {"
			+ "	background-color:#eb675e;"
			+ "}"
			+ ".botonDescargaProgramaPatrimonio2025:active {"
			+ "	position:relative;"
			+ "	top:1px;"
			+ "}"
			+ "</style>"
			+ "<div id='msgDiaPatrimonios' style='z-index: 99999999; position: absolute; left: 1px; top: 7px; display: none;'"
			+ " onclick='document.getElementById(\"msgDiaPatrimonios\").style.display=\"none\";'>"
			+ " <img style='width: 1025px;' src='https://archivos.meteochile.gob.cl/portaldmc/patrimonio/patrimonios_2025_popup.png' alt=''>"
			+ " <a href='https://archivos.meteochile.gob.cl/portaldmc/patrimonio/programa_dia_patrimonios_DMC_2025.pdf' class='botonDescargaProgramaPatrimonio2025'"
			+ " style='position: absolute; top: 620px; left: 420px;' target='programa'>"
			+ "Ver programa de actividades</a>"
			+ " <\/div>";

	var formato = 'position: absolute; left: 20px; top: 882px; width: 720px; font-size: 13px; color: #555; border: 1px solid #888; -webkit-border-radius: 5px; -moz-border-radius: 5px; border-radius: 5px; background-color: white; opacity: 0.5;';
	labelHTML += '<div class="home_info_temperatura_texto" style="'+formato+'">Autorizada su circulaci&oacute;n por Resoluci&oacute;n N&deg;28 del 23 de febrero de 2023 de la Direcci&oacute;n Nacional de Fronteras y L&iacute;mites del Estado.<br>La edici&oacute;n y la circulaci&oacute;n de mapas, cartas geogr&aacute;ficas u otros impresos y documentos que se refieran o relacionen con los l&iacute;mites y fronteras de Chile, no comprometen, en modo alguno, al Estado de Chile, de acuerdo con el Art. 2&deg;, letra g) del DFL N&deg;83 de 1979 del Ministerio de Relaciones Exteriores.<\/div>';


	labelHTML += "<div id='leyendaUVB' style='display: none; z-index: 999999; position: absolute; left: 20px; top: 852px; width: 720px; font-family: 'Yanone Kaffeesatz', arial, helvetica, sans-serif;'>";
	labelHTML += "<span class='leyenda_UVB'>Pron&oacute;stico UV-B:";
	labelHTML += " <div class='UV_leyenda'><div class='UV UV_bajo'>UV</div>&nbsp;&nbsp;1-2:Bajo</div>";
	labelHTML += " <div class='UV_leyenda'><div class='UV UV_moderado'>UV</div>&nbsp;&nbsp;3-5:Moderado</div>";
	labelHTML += " <div class='UV_leyenda'><div class='UV UV_alto'>UV</div>&nbsp;&nbsp;6-7:Alto</div>";
	labelHTML += " <div class='UV_leyenda'><div class='UV UV_muy_alto'>UV</div>&nbsp;&nbsp;8-10:Muy Alto</div>";
	labelHTML += " <div class='UV_leyenda'><div class='UV UV_extremo'>UV</div>&nbsp;&nbsp;11+:Extremo</div>";
	labelHTML += "</span></div>";


}

function poneiconos() {
	poneprono("arica",estilo_left_mapa+206,estilo_top_mapa+82,0, '01a', 180016);
	poneprono("iquique",estilo_left_mapa+215,estilo_top_mapa+144,0, '01b', 200006);
	poneprono("antofagasta",estilo_left_mapa+184,estilo_top_mapa+250,0, '02', 230001);
	poneprono("copiapo",estilo_left_mapa+216,estilo_top_mapa+376,5, '03', 230001);
	poneprono("serena",estilo_left_mapa+177,estilo_top_mapa+482,5, '04', 290004);
	poneprono("valpo",estilo_left_mapa+165,estilo_top_mapa+568,1, '05', 330120);
	poneprono("stgoc",estilo_left_mapa+212,estilo_top_mapa+592,5, '05m', 330020);
	poneprono("rancagua",estilo_left_mapa+200,estilo_top_mapa+632,1, '06', 340045);
	poneprono("talca",estilo_left_mapa+175,estilo_top_mapa+672,2, '07', 350050);
	poneprono("chillan",estilo_left_mapa+164,estilo_top_mapa+710,2, '08a', 360011);
	poneprono("temuco",estilo_left_mapa+155,estilo_top_mapa+790,2, '09', 380029);
	poneprono("concepcion",estilo_left_mapa+125,estilo_top_mapa+725,2, '08b', 360019);
	
	poneprono("valdivia",estilo_left_mapa2+175,estilo_top_mapa2+80,0, '10a', 390026);
	poneprono("pmontt",estilo_left_mapa2+202,estilo_top_mapa2+165,1, '10b', 410005);
	poneprono("coyhaique",estilo_left_mapa2+230,estilo_top_mapa2+330,3, '11', 450004);
	poneprono("torres",estilo_left_mapa2+205,estilo_top_mapa2+581,7, '11', 520006);
	poneprono("parenas",estilo_left_mapa2+264,estilo_top_mapa2+678,7, '12', 520006);


	poneprono("rapanui",estilo_left_mapa+100,estilo_top_mapa+302,6, 'ip', 270001);
	poneprono("jfernandez",estilo_left_mapa+100,estilo_top_mapa+376,6, 'jf',0);
	poneprono("antartica",estilo_left_mapa2+116,estilo_top_mapa2+726,5, 'an', 950001);

}

/* ESTO NO SIRVE :P DGONZALEZ */

function poneiconos_old() {

	poneprono("arica",estilo_left_mapa+206,estilo_top_mapa+82,0, '01a',0);
	poneprono("iquique",estilo_left_mapa+215,estilo_top_mapa+144,0, '01b',0);
	poneprono("antofagasta",estilo_left_mapa+184,estilo_top_mapa+250,0, '02',0);
	poneprono("copiapo",estilo_left_mapa+216,estilo_top_mapa+376,5, '03',0);
	poneprono("serena",estilo_left_mapa+177,estilo_top_mapa+482,5, '04',0);
	poneprono("valpo",estilo_left_mapa+165,estilo_top_mapa+568,1, '05',0);
	poneprono("stgoc",estilo_left_mapa+212,estilo_top_mapa+592,5, '05m',0);
	poneprono("rancagua",estilo_left_mapa+200,estilo_top_mapa+632,1, '06',0);
	poneprono("talca",estilo_left_mapa+175,estilo_top_mapa+672,2, '07',0);
	poneprono("chillan",estilo_left_mapa+164,estilo_top_mapa+710,2, '08a',0);
	poneprono("temuco",estilo_left_mapa+155,estilo_top_mapa+790,2, '09',0);
	poneprono("concepcion",estilo_left_mapa+125,estilo_top_mapa+725,2, '08b',0);
	
	poneprono("valdivia",estilo_left_mapa2+175,estilo_top_mapa2+80,0, '10a',0);
	poneprono("pmontt",estilo_left_mapa2+202,estilo_top_mapa2+165,1, '10b',0);
	poneprono("coyhaique",estilo_left_mapa2+230,estilo_top_mapa2+330,3, '11',0);
	poneprono("torres",estilo_left_mapa2+205,estilo_top_mapa2+581,7, '11',0);
	poneprono("parenas",estilo_left_mapa2+264,estilo_top_mapa2+678,7, '12',0);


	poneprono("rapanui",estilo_left_mapa+100,estilo_top_mapa+302,6, 'ip',0);
	poneprono("jfernandez",estilo_left_mapa+100,estilo_top_mapa+376,6, 'jf',0);
	poneprono("antartica",estilo_left_mapa2+116,estilo_top_mapa2+726,5, 'an',0);
	
}


function poneprono(indice,x,y,posicion,codigoRegion,codigoUVB) {
	var offset = 0;
	var xxxx = 0;
	var id = -1;
	var labelUVB = "";
	for (var i = 0; i < Pronostico.length; i++) {
		if (Pronostico[i].indice == indice) id = i;
	};
	if (id>=0) {

		// Busca el pronostico de radiación UV-B
		if (codigoUVB) {
			for (i in RadiacionUVB) {
				if (codigoUVB==RadiacionUVB[i].indice&&Pronostico[id].fechasql==RadiacionUVB[i].fechapron) {
					labelUVB = RadiacionUVB[i].indicepron;
					hayPronosticoUVB = true;
				}
			}
			switch (labelUVB) {
			case "11+:Extremo": labelUVB = " <div class='UV UV_extremo'>UV<\/div>"; break;
			case "8-10:Muy alto": labelUVB = " <div class='UV UV_muy_alto'>UV<\/div>"; break;
			case "6-7:Alto": labelUVB = " <div class='UV UV_alto'>UV<\/div>"; break;
			case "3-5:Moderado": labelUVB = " <div class='UV UV_moderado'>UV<\/div>"; break;
			case "1-2:Bajo": labelUVB = " <div class='UV UV_bajo'>UV<\/div>"; break
			}
		}


		Pronostico[id].fechasql





		// busca el mejor icono y pronostico
		if (Pronostico[id].icono[0][periodoLocal]=="" && periodoLocal==0) periodoLocal=1;
		if (Pronostico[id].fechasql != fechaSQLhoy && periodoLocal == 3)  periodoLocal=1;


		var texto_min = '';
		var texto_max = '';
		var temps = Pronostico[id].temperatura[0].split("/");
		if (temps[0].length > 0) {
				texto_min = '<font class="home_info_temperatura_min">' + temps[0] + '&deg;&nbsp;&nbsp;</font>';
		} else {
			/*
			// si no tiene temperatura minima se acerca al mapa del lado izquierdo
			x += 40;
			// las que no se correrán se devuelve 40
			if (indice=="stgoc"||
				indice=="rancagua"||
				indice=="valdivia"||
				indice=="jfernandez"||
				indice=="antartica"||
				indice=="rapanui"||
				indice=="parenas"||
				indice=="torres"||
				indice=="concepcion"||
				indice=="temuco"||
				indice=="pmontt"||
				indice=="coyhaique"||
				indice=="talca"||
				indice=="valpo") x -= 40;
				*/
			}
			
		if (temps[1].length > 0) {
				texto_max = '<font class="home_info_temperatura_max">&nbsp;' + temps[1] + '&deg;</font>';
			}
		var icono = Pronostico[id].icono[0][periodoLocal];
		var nombreciudad = Pronostico[id].ciudad;

		// Cambio nombre de ciudad
		if (indice=="stgoc") nombreciudad = 'Santiago';
		if (indice=="jfernandez") nombreciudad = 'Juan Fern&aacute;ndez';
		if (indice=="antartica") nombreciudad = 'Ant&aacute;rtica';

		// cambio posicion de info
		if (indice=="arica"||
			indice=="iquique" ||
			indice=="copiapo" ||
			indice=="valpo" ||
			indice=="stgoc" ||
			indice=="rancagua" ||
			indice=="talca" ||
			indice=="chillan" ||
			indice=="temuco") { 
			offset = 40; 
			}
		switch (indice) { // 
			case 'valpo':		xxxx = 160;		if (texto_min!='') xxxx = 200;		break;
			case 'talca':		xxxx = 130;		if (texto_min!='') xxxx = 170;		break;
			case 'concepcion':  xxxx = 110; break;
		}

		var info_html = '<div id="icono_' + id + '" style="z-index: 15; cursor:pointer; position:absolute; left:' + x + 'px; top:' + y + 'px;" onclick="verPronosticoLocalidad(\'' + indice + '\');" onmouseover="javascript:muestra_tabla(\''+indice+'\','+posicion+');" onmouseout="javascript:oculta_tabla();">' +
						'<img src="' + urlLocalJsx + '/img/clima/' + icono + '" class="img_info" style="cursor:pointer; width: 40px;" title="Haga click para ver detalle completo"></img>'
						+ '<\/div>';
		info_html += '<div id="info_' + id + '" style="z-index: 15; cursor:pointer; position:absolute;left:' + ((x+offset+5)-xxxx) + 'px; top:' + (y+40-offset) + 'px;" class="home_info_temperatura" title="Haga click para ver detalle completo" onclick="verPronosticoLocalidad(\'' + indice + '\');" onmouseover="javascript:muestra_tabla(\''+indice+'\','+posicion+');" onmouseout="javascript:oculta_tabla();">' +
								texto_min + texto_max +	'<font class="home_info_temperatura_texto">' + nombreciudad + labelUVB + '</font>' +
						'</div>';

		
		
		labelHTML += info_html;
		}
}

function render() {
	$("#contenedor_principal").append(labelHTML);
	$("#contenedor_principal").height(950);
	if (hayPronosticoUVB) document.getElementById('leyendaUVB').style.display = "inline-flex";
}

function marca(obj) {
	obj.style.opacity = "1";

}

function verPronosticoLocalidad(indice) {
	var pronosticoSieteDias = '<div class="contenedorDetallePronostico">'	
									+ '<div class="fondoPopUp"></div>'
										+ '<div class="detallePronosticoDiv">'
											+ crea_tabla_click_home(indice);
										+ '<div>'
							  + '</div>';
	$(pronosticoSieteDias).appendTo('body');
}

function desmarca(obj) {
	obj.style.opacity = "0.8";
}

function muestra_tabla(indice,posicion) {
	if (indicemostrando==indice) return;

	var contenido = crea_tabla_home(indice, 3);

	contenidoLayer("detalle_tabla",contenido);
	posicionaLayer("detalle_tabla",posicion);
	show("detalle_tabla");
	indicemostrando=indice;
}



function crea_tabla_home(indice) {
	var id = -1;
	for (var i = 0; i < Pronostico.length; i++) {
		if (Pronostico[i].indice == indice) id = i;
	};
	var tablaPronostico = 'Sin Informaci&oacute;n';
	if (id>=0) {
		tablaPronostico = "<table id='table_pronostico' class='home_texto home_table_pronostico'><tbody>" +
								   "<tr>" +
									   "<td class='home_titulo_pronostico' colspan='6' style='border-bottom: 2px solid #b3b3b3;' align='left'>" +
									   		"<table width='100%; margin: 0; padding: 0;'>" +
									   			"<tbody>" +
									   				"<tr>" +
									   					"<td width='100%' style='border: none; color: #777;'>" + Pronostico[id].ciudad + "</td>" +
									   					"<td style='padding: 0; border: none;'>" + renderCondicionActualProno(Pronostico[id].indice) + "</td>" +
									   				"</tr>" +
									   			"</tbody>" +
									   		"</table>" +
									   "</td>" +
								   "</tr>";


		// modificacion 1: agregado por serrod 03/nov/2016
		if (Pronostico[id].icono_resto_dia !="" && Pronostico[id].texto_resto_dia !="" && Pronostico[id].fecha_resto_dia !="" ) {
			tablaPronostico += "<tr class='home_fuente_titulo_tabla_header' style='border-bottom: 2px solid #b3b3b3;' align='left'>" +
								   		"<td colspan=2 style='text-align: left; vertical-align:middle; color: #888;'>Resto del "+Pronostico[id].fecha_resto_dia+"</td>" +
								   		"<td colspan=4 style='text-align: left; vertical-align:middle; color: #888;'><img  style='vertical-align:middle;' src='" + urlLocalJsx + "/img/clima_dark/" + Pronostico[id].icono_resto_dia + "' width='40px;'>&nbsp;" +
								   		Pronostico[id].texto_resto_dia + "</td>" +
								"</tr>";
		}
		// fin modificacion 1

		tablaPronostico += "<tr class='home_fuente_titulo_tabla_header'>" +
								   		"<td style='text-align: center; color: #888;'> D&iacute;a </td>" +
								   		"<td style='text-align: center; color: #888; white-space: nowrap;'> Min | Max </td>" +
								   		"<td style='text-align: center; color: #888;'> Madrugada </td>" +
								   		"<td style='text-align: center; color: #888;'> Ma&ntilde;ana </td>" +
								   		"<td style='text-align: center; color: #888;'> Tarde </td>" +
								   		"<td style='text-align: center; color: #888;'> Noche </td>" +
								   	"</tr>";
		
		for (var i = 0; i < 3; i++) {
				
				temp = Pronostico[id].temperatura[i].split("/");
				
				min = temp[0];
				max = temp[1];
				
				var dia = Pronostico[id].fecha[i].split(" ");
				
				tablaPronostico = tablaPronostico + "<tr>" +
								   		"<td style='padding-left: 15px; border-right: 1px solid #e3e3e3;'>" + 
								   			"<div class=\"home_contenedor_dia\">" + 
								   				" <div class=\"home_texto_dia_mes\">" + dia[0] + "</div>" +
								   				"<div class=\"home_numero_dia_mes\">" + dia[1] + "</div>" +
								   			"</div>" +
								   		"</td>" +
								   		"<td style='text-align: center;'>" + 
							   				((min != '') ? '<font style="border-top-left-radius: 4px; border-bottom-left-radius: 4px;"' +
									   				'class="home_info_temperatura_pron home_info_temperatura_min_pron">' + min + '&deg;' + '</font>' : '') +
							   				'<font style="border-top-right-radius: 4px; border-bottom-right-radius: 4px;"' +
								   				'class="home_info_temperatura_pron home_info_temperatura_max_pron">' +
								   					max + "&deg;" + 
								   			'</font>' + 
								   		"</td>";

		   		for (var j = 0; j < 4; j++) {
		   			tablaPronostico = tablaPronostico + "<td style='text-align: center;'>" + ((Pronostico[id].icono[i][j] != '') ? "<img class='home_img_info_pronostico' src='" + urlLocalJsx + "/img/clima_dark/" + 
		   								Pronostico[id].icono[i][j] + "'></img></td>" : '')
		   			
				}
			}
		
		tablaPronostico += "</tr><tr>" +
								"<td colspan='6' style='border-top: 1px solid #e3e3e3; text-align: center;'><span class='home_redaccion'>" + Pronostico[id].redaccion + "<\/span></td>" +
						   "</tr>" + 
						"</tbody></table>";
		}
		return tablaPronostico;
}



function crea_tabla_click_home(indice) {
	var id = -1;
	for (var i = 0; i < Pronostico.length; i++) {
		if (Pronostico[i].indice == indice) id = i;
	};
	var tablaPronostico = 'Sin Informaci&oacute;n';
	if (id>=0) {
		tablaPronostico = "<table id='table_pronostico' class='home_texto home_table_pronostico' style='width: 800px;'><tbody>" +
								   "<tr>" +
									   "<td class='home_titulo_pronostico' colspan='6' style='border-bottom: 2px solid #b3b3b3;' align='left'>" +
									   		"<table width='100%; margin: 0; padding: 0;'>" +
									   			"<tbody>" +
									   				"<tr>" +
									   					"<td width='100%' style='border: none; color: #777;'>" + Pronostico[id].ciudad + "</td>" +
									   					"<td style='padding: 0; border: none;'>" + renderCondicionActualProno(Pronostico[id].indice) + "</td>" +
									   					"<td style='text-align: center; vertical-align: middle; border:none;'><div onclick='javascript:cerrarDetallePronostico();'><img src='data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiA/Pjxzdmcgdmlld0JveD0iMCAwIDIwLjI0NiAyMC4yNDYiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0ibSAxMy44MzI4OTUsNi40MTMxMDggYSAxLDEgMCAwIDAgLTEuNDIsMCBsIC0yLjI5LDIuMyAtMi4yODk5OTk4LC0yLjMgYSAxLjAwNDA5MTYsMS4wMDQwOTE2IDAgMCAwIC0xLjQyLDEuNDIgbCAyLjMsMi4yOSAtMi4zLDIuMjkgYSAxLDEgMCAwIDAgMCwxLjQyIDEsMSAwIDAgMCAxLjQyLDAgbCAyLjI4OTk5OTgsLTIuMyAyLjI5LDIuMyBhIDEsMSAwIDAgMCAxLjQyLDAgMSwxIDAgMCAwIDAsLTEuNDIgbCAtMi4zLC0yLjI5IDIuMywtMi4yOSBhIDEsMSAwIDAgMCAwLC0xLjQyIHogbSAzLjM2LC0zLjM1OTk5OTkgQSAxMCwxMCAwIDEgMCAzLjA1Mjg5NTIsMTcuMTkzMTA4IDEwLDEwIDAgMSAwIDE3LjE5Mjg5NSwzLjA1MzEwODEgWiBtIC0xLjQxLDEyLjcyOTk5OTkgYSA4LDggMCAxIDEgMi4zNCwtNS42NiA3Ljk1LDcuOTUgMCAwIDEgLTIuMzQsNS42NiB6IiBmaWxsPSIjZmYwMDAwIi8+PC9zdmc+' class='cerrarPopUpPronostico' style='width: 50px; cursor: pointer; margin-top: 20px;'></div></td>" +
									   				"</tr>" +
									   			"</tbody>" +
									   		"</table>" +
									   		
									   "</td>" +
								   "</tr>";


		// modificacion 1: agregado por serrod 03/nov/2016
		if (Pronostico[id].icono_resto_dia !="" && Pronostico[id].texto_resto_dia !="" && Pronostico[id].fecha_resto_dia !="" ) {
			tablaPronostico += "<tr class='home_fuente_titulo_tabla_header' style='border-bottom: 2px solid #b3b3b3;' align='left'>" +
								   		"<td colspan=2 style='text-align: left; vertical-align:middle; color: #888;'>Resto del "+Pronostico[id].fecha_resto_dia+"</td>" +
								   		"<td colspan=4 style='text-align: left; vertical-align:middle; color: #888;'><img  style='vertical-align:middle;' src='" + urlLocalJsx + "/img/clima_dark/" + Pronostico[id].icono_resto_dia + "' width='40px;'>&nbsp;" +
								   		Pronostico[id].texto_resto_dia + "</td>" +
								"</tr>";
		}
		// fin modificacion 1

		tablaPronostico += "<tr class='home_fuente_titulo_tabla_header'>" +
								   		"<td style='text-align: center; width: 50px; color: #888;'> D&iacute;a </td>" +
								   		"<td style='text-align: center; width: 50px; color: #888; white-space: nowrap;'> Min | Max </td>" +
								   		"<td style='text-align: center; width: 180px; color: #888;'> Madrugada </td>" +
								   		"<td style='text-align: center; width: 180px; color: #888;'> Ma&ntilde;ana </td>" +
								   		"<td style='text-align: center; width: 180px; color: #888;'> Tarde </td>" +
								   		"<td style='text-align: center; width: 180px; color: #888;'> Noche </td>" +
								   	"</tr>";
		
		for (var i = 0; i < 5; i++) {
				
				temp = Pronostico[id].temperatura[i].split("/");
				
				min = temp[0];
				max = temp[1];
				
				var dia = Pronostico[id].fecha[i].split(" ");
				
				tablaPronostico = tablaPronostico + "<tr>" +
								   		"<td style='padding-left: 15px; border-right: 1px solid #e3e3e3;'>" + 
								   			"<div class=\"home_contenedor_dia\">" + 
								   				" <div class=\"home_texto_dia_mes\">" + dia[0] + "</div>" +
								   				"<div class=\"home_numero_dia_mes\">" + dia[1] + "</div>" +
								   			"</div>" +
								   		"</td>" +
								   		"<td style='text-align: center;'>" + 
							   				((min != '') ? '<font style="border-top-left-radius: 4px; border-bottom-left-radius: 4px;"' +
									   				'class="home_info_temperatura_pron home_info_temperatura_min_pron">' + min + '&deg;' + '</font>' : '') +
							   				'<font style="border-top-right-radius: 4px; border-bottom-right-radius: 4px;"' +
								   				'class="home_info_temperatura_pron home_info_temperatura_max_pron">' +
								   					max + "&deg;" + 
								   			'</font>' + 
								   		"</td>";

		   		for (var j = 0; j < 4; j++) {
		   			tablaPronostico = tablaPronostico + "<td style='text-align: center;'>" + ((Pronostico[id].icono[i][j] != '') ? "<img class='home_img_info_pronostico' src='" + urlLocalJsx + "/img/clima_dark/" + 
		   								Pronostico[id].icono[i][j] + "'></img><br><span style='font-size: 17px;'>"+Pronostico[id].texto[i][j]+"<\/span><\/td>" : '')
		   			
				}
			}






// modificacion 2: Pronostico a 7 dias; agregado por serrod 29/sep/2016
		if ( Pronostico[id].tope>5) {

			for (var i = 5; i < Pronostico[id].tope; i++) {
				var dia = Pronostico[id].fecha[i].split(" ");
				tablaPronostico += "<tr>" +
									"<td style='padding-left:15px'>" + 
									   			"<div class=\"home_contenedor_dia\">" + 
									   				" <div class=\"home_texto_dia_mes\">" + dia[0] + "</div>" +
									   				"<div class=\"home_numero_dia_mes\">" + dia[1] + "</div>" +
									   			"</div>" +
									   		"</td>" +
								   		"<td><img width=45 src='" + urlLocalJsx + "/img/clima_dark/" + Pronostico[id].icono[i][0] + "' border=0></td>";

				tablaPronostico += "<td colspan='4'><div class='pronosticoImgTexto' style='text-align: left;'><span style='font-size: 18px;'>" + Pronostico[id].texto[i][0] + "<\/span><\/div><\/td><\/tr>";		
			}
		}
		// fin modificacion 2

		
		tablaPronostico += "</tr><tr>" +
								"<td colspan='6' style='border-top: 1px solid #e3e3e3; text-align: center;'><span class='home_redaccion'>" + Pronostico[id].redaccion + "<\/span></td>" +
						   "</tr>" + 
						"</tbody></table>";
		}
		return tablaPronostico;
}



function cerrarDetallePronostico() {
	$(".contenedorDetallePronostico").remove();
}



function oculta_tabla() {
	if (indicemostrando=='') return;
	hide("detalle_tabla");
	indicemostrando='';
}

function verDetalleRegion(indiceRegion) {
	parent.cargarComponenteRegion('https://archivos.meteochile.gob.cl/portaldmc/pronosticos/pronosticoRegion.php?reg=' + indiceRegion);
//	window.location.href = 'http://archivos.meteochile.gob.cl/portaldmc/pronosticos/pronosticoRegion.php?reg=' + indiceRegion;
}

function renderCondicionActualProno(indice) {
	var estacion  = comprobarCiudadSelectById(indice);
	var contenidoHtmlCondicion = '';

	if (estacion == "") {
		return contenidoHtmlCondicion;
	}

	if (CondicionActualMetar[estacion] != "" && CondicionActualMetar[estacion] != undefined 
			&& CondicionActualMetar[estacion] != "undefinded" ) {
		contenidoHtmlCondicion = "<table style='border: none; padding: 0; margin: 0;' title='Temperatura Actual'>" +
	   								"<tbody>" +
	   									"<tr>" +
	   										"<td align='right' style='border: none;'>" +
	   											"<img src='" + urlLocalJsx + "/img/temp_actual.png' width='60px;'>" +
	   										"</td>" +
	   										"<td align='center' style='border: none;'>" +
	   											"<img src='" + urlLocalJsx + "/img/clima_dark/" + CondicionActualMetar[estacion].split("|")[8] + "' width='40px;'>" +
	   										"</td>" +
	   										"<td class='home_fuente_pronostico_actual' style='border: none; white-space: nowrap;'> " +
	   											"<font style='border-top-right-radius: 4px; border-bottom-right-radius: 4px;' " +
	   											"class='home_info_temperatura_pron home_info_temperatura_max_pron'>" +
	   												CondicionActualMetar[estacion].split("|")[6] + "&deg;" +
	   											"</font> " +
	   											"<br>" + CondicionActualMetar[estacion].split("|")[1] + " hrs." +
	   										"</td>" +
	   									"</tr>" +
	   								"</tbody>" +
	   							'</table>';
	}

	return contenidoHtmlCondicion;
}



function comprobarCiudadSelectById(indice) {

		var CodigoOACI = '';

		switch(indice) {
			case "arica": CodigoOACI='SCAR'; break;
			case "iquique":CodigoOACI='SCDA'; break;
			case "calama":  CodigoOACI = "SCCF"; break;
			case "antofagasta": CodigoOACI = "SCFA"; break;
			case "caldera": CodigoOACI = "SCAT"; break; // lugar mas cercano a SCAT Atacama
			case "serena": CodigoOACI = "SCSE"; break;
			case "valpo": CodigoOACI = "SCVM"; break;
			case "snantonio": CodigoOACI = "SCSN"; break;
			case "rancagua": CodigoOACI = "SCRG"; break;
			case "curico": CodigoOACI = "SCIC"; break;
			case "chillan": CodigoOACI = "SCCH"; break;
			case "concepcion": CodigoOACI = "SCIE"; break;
			case "angeles": CodigoOACI = "SCGE"; break;
			case "temuco": CodigoOACI = "SCQP"; break;
			case "valdivia": CodigoOACI = "SCVD"; break;
			case "osorno": CodigoOACI = "SCJO"; break;
			case "pmontt": CodigoOACI = "SCTE"; break;
			case "quellon": CodigoOACI = "SCON"; break;
			case "chaiten": CodigoOACI = "SCTN"; break;
			case "futaleufu": CodigoOACI = "SCFT"; break;
			case "melinka": CodigoOACI = "SCMK"; break;
			case "aysen": CodigoOACI = "SCAS"; break;
			case "coyhaique": CodigoOACI = "SCCY"; break;
			case "balmaceda": CodigoOACI = "SCBA"; break;
			case "chchico": CodigoOACI = "SCCC"; break;
			case "cochrane": CodigoOACI = "SCHR"; break;
			case "natales": CodigoOACI = "SCNT"; break;
			case "parenas": CodigoOACI = "SCCI"; break;
			case "porvenir": CodigoOACI = "SCFM"; break;
			case "pwilliams": CodigoOACI = "SCGZ"; break;
			case "antartica": CodigoOACI = "SCRM"; break;
			case "rapanui": CodigoOACI = "SCIP"; break;
			case "jfernandez": CodigoOACI = "SCIR"; break;

			case "stgop": CodigoOACI = "SCEL"; break;
			case "stgoo": CodigoOACI = "SCTB"; break;
			case "stgoc": CodigoOACI = "SCQN"; break;		
		}

		return CodigoOACI;	

	}

/* funciones para Divs */
function show(div_id) {	document.getElementById(div_id).style.visibility='visible'; }
function hide(div_id) {	document.getElementById(div_id).style.visibility='hidden'; }
function contenidoLayer(elLayer,contenido) { document.getElementById(elLayer).innerHTML = contenido; }
function posicionaLayer(elLayer,posicion) { 
	document.getElementById(elLayer).style.left = posicion_tabla[posicion].left +"px"; 
	document.getElementById(elLayer).style.top = posicion_tabla[posicion].top +"px"; 
}


function renderAnuncio() {
	var contenidoAnuncionHtml = '<div style="position: absolute; left: 752px; top: 600px;">'
									+ '<a href="convenioDIRECTEMARDMC.xhtml"><img src="' + urlLocalJs() 
										+ '/images/ProyectoInternacional/DMC_ProyectoInternacional.jpg" width="180"   /></a>'
								+ '</div>';

	$("#contenedor_principal").append(contenidoAnuncionHtml);

}

function renderCartaSinoptica() {
	var contenidoHtmlCarta = '<div class="contenedorCartaSinoptica">'
								+ '<label>Carta Sinóptica</label>'
								+ '<a href="carta_sinoptica.xhtml">'
									+ '<img src="' + urlMeteo() + '/cna/carta_sfc.png"/>'
								+ '</a>'
							+ '</div>';
	//no se muestra hasta nuevo aviso
	$("#contenedor_principal").append(contenidoHtmlCarta);
}

function renderBotones() {
	var contenidoDivBotones = '<div id="botones">' 
								+ '<div id="definicion" '
									+ 'style="border: 0px solid rgb(121, 121, 121); text-align: center; visibility: visible;">'
									+ '<input class="accionDiv" value="Mostrar definiciones de Aviso, Alerta y Alarma" ' 
									+ 'onclick="javascript:definicionShow();" type="button">'
								+ '</div>'
								+ 'style="border: 0px solid rgb(121, 121, 121); text-align: center; visibility: visible;">'
									+ '<input class="accionDiv" value="Mostrar definiciones de Aviso, Alerta y Alarma" ' 
									+ 'onclick="javascript:definicionShow();" type="button">'
								+ '</div>'
							+ '</div>';
}


function comprobarCiudadSelect(ciudad) {
	alert(ciudad);
		if (ciudad == "Archipi&eacute;lago Juan Fern&aacute;ndez") {
			ciudad = "Juan Fernández";
		} else if (ciudad == "Pen&iacute;nsula Ant&aacute;rtica") {
			ciudad = "Antartica";
		} else if(ciudad == "Vi&ntilde;a del Mar/Valpara&iacute;so") {
			ciudad = "Viña del Mar/Valparaiso";
		} else if(ciudad == "Santiago Sector Centro") {
			ciudad = "Santiago";
		}

		var oaci = '';

		switch(ciudad) {
			case "Arica":
				return 'SCAR';
			case "Iquique":
				return 'SCDA';
			case "Calama":
				return 'SCCF';
			case "Antofagasta":
				return 'SCFA';
			case "Caldera":
				return 'SCCL';
			case "La Serena/Coquimbo":
				return 'SCSE';
			case "Viña del Mar/Valparaiso":
				return 'SCVM';
			case "San Antonio/Cartagena":
				return 'SCSN';
			case "Rancagua":
				return 'SCRG';
			case "Curicó":
				return 'SCIC';
			case "Chillán":
				return 'SCCH';
			case "Concepción":
				return 'SCIE';
			case "Los Angeles":
				return 'SCGE';
			case "Temuco":
				return 'SCTC';
			case "Valdivia":
				return 'SCVD';
			case "Osorno":
				return 'SCJO'; 
			case "Puerto Montt":
				return 'SCTE';
			case "Quellón":
				return 'SCON';
			case "Chaiten":
				return 'SCTN';
			case "Futaleufu":
				return 'SCFT'; 
			case "Melinka":
				return 'SCMK';
			case "Puerto Aysen":
				return 'SCAS';
			case "Coyhaique":
				return 'SCCY';
			case "Balmaceda":
				return 'SCBA';
			case "Chile Chico":
				return 'SCCC';
			case "Cochrane":
				return 'SCHR';
			case "Puerto Natales":
				return 'SCNT';
			case "Punta Arenas":
				return 'SCCI'; 
			case "Porvenir":
				return 'SCFM';
			case "Puerto Williams":
				return 'SCGZ';
			case "Antartica":
				return 'SCRM';
			case "Isla de Pascua":
				return 'SCIP';
			case "Juan Fernández":
				return 'SCIR';
			case "Pudahuel":
				return 'SCEL';
			case "Tobalaba":
				return 'SCTB';
			case "Santiago":
				return 'SCQN'; 
		}

		return '';	

	}

