	
	
	$(document).ready(function () {
		

		renderRadiacionUv();
		
		if (navigator.userAgent.match(/Trident/) || navigator.userAgent.match(/MSIE/)) {
			$("#leyozono").attr("target","_blank");
		} else {
			$("#leyozono").attr("target","_self");
		}		
		
		var regiones = ["Región de Arica-Parinacota","Región de Tarapacá", "Región de Antofagasta",
		                "Región de Atacama", "Región de Coquimbo"];
		
		var htmlTablaDiaDespejado = ""
		
	});

	function marcarRegion(obj) {
		if ($("#"+obj.id).attr("class")!="region_seleccionada") {
			$("#"+obj.id).attr("class","region_seleccionada_over");
		}
	}
	
	function desmarcarRegion(obj) {
		if ($("#"+obj.id).attr("class")!="region_seleccionada") {
			$("#"+obj.id).attr("class","region_no_seleccionada_pron_region");
		}
	}
	
	function marcarRegionMap(obj) {
		if ($("#"+obj).attr("class")!="region_seleccionada") {
			$("#"+obj).attr("class","region_seleccionada_over");
		}
	}
	
	function desmarcarRegionMap(obj) {
		if ($("#"+obj).attr("class")!="region_seleccionada") {
			$("#"+obj).attr("class","region_no_seleccionada_pron_region");
		}
	}
	
	function graficoUv(region) {
		location.href = "radiacion_uv_region.xhtml?estacion=" + region;
	}
	
	function graficoRadiacionUV(estacion) {
		var fechahoy = formatDate();
		window.open("https://climatologia.meteochile.gob.cl/application/diario/indiceUvbDiario/"+estacion+"/" + fechahoy,"radiacionUV");

	}

	
	function graficoRadiacionUV2(estacion) {
		if (navigator.userAgent.match(/Trident/) || navigator.userAgent.match(/MSIE/)) {
			window.open("grafico_radiacion.xhtml?estacion=" + estacion, "graficoUv", "scrollbars=yes,width=850,height=800");
		} else {
			location.href = "grafico_radiacion.xhtml?estacion=" + estacion;
		}
	}

	

	function init() {
		try {
			addEventShowMenu();
		} catch (e) {
		}
	
		addAreaToMap("valle", 147, 275, 100, 50, "Cordillera", "r13");
		addAreaToMap("mariaelena", 50, 80, 100, 50, "María Elena", "r02");
		addAreaToMap("sanpedro", 110, 70, 100, 50, "San Pedro de Atacama", "r02");
	}
	
	function addAreaToMap(codigo, x, y, width, height, region, id) {
		$("#data").append(
				'<AREA style="position: absolute; z-index:99; cursor:hand;cursor:pointer" id="area_' + codigo + '" SHAPE=RECT COORDS="' + x + ',' + y
						+ ',' + (x + width) + ',' + (y + height)
						+ '" onmouseover="marcarRegionMap(\'' + id +'\');" onmouseout=desmarcarRegionMap(\'' + id
						+ '\'); onclick="graficoUv(\'' + codigo + '\');" title="' + region + '"> </AREA>');
	}
	
	function renderRadiacionUv() {
		var contenidoHtmlIndice = '<h2>Índice de Radiación UV</h2>'
					/*+ '<div style="width:240px;height: 554px;background-color:#183183; float:left;" id="mapa_uv"> '
						+ '<img usemap="#data" src="../img/regiones/cuidades.png"/> '
						+ '<img id="r14" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" '
							+ 'onmouseover="marcarRegion(this)" title="Región de Arica Y Parinacota"  '
							+ 'onclick=\'graficoUv("180016")\' style="z-index:5;position:absolute;left:82px; '
							+ 'top:62px;width:39px;cursor:hand;cursor:pointer" '
 							+ 'src="../img/regiones/r14.png"></img> '
						+ '<img id="r01" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" '
 							+ 'onmouseover="marcarRegion(this)" title="Región de Iquique" onclick=\'graficoUv("200006")\' ' 
							+ 'style="z-index:5;position:absolute;left:69px;top:80px;width:80px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/r01.png"></img> '
						+ '<img id="r02" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" '
 							+ 'onmouseover="marcarRegion(this)" title="Región de Antofagasta" onclick=\'graficoUv("220008")\' '
 							+ 'style="z-index:5;position:absolute;left:61px;top:117px;width:113px;cursor:hand;cursor:pointer"  '
							+ 'src="../img/regiones/r02.png"></img> '			
						+ '<img id="r03" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" ' 
							+ 'onmouseover="marcarRegion(this)" title="Región de Atacama" onclick=\'graficoUv("230001")\' '
							+ 'style="z-index:5;position:absolute;left:67px;top:186px;width:88px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/r03.png"></img> '					
						+ '<img id="r04" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" ' 
							+ 'onmouseover="marcarRegion(this)" title="Región de Coquimbo" onclick=\'graficoUv("270001")\' ' 
							+ 'style="z-index:5;position:absolute;left:66px;top:242px;width:70px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/r04.png"></img> '					
						+ '<img id="r05" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" ' 
							+ 'onmouseover="marcarRegion(this)" title="Región de Valparaíso" onclick=\'graficoUv("270008")\' ' 
							+ 'style="z-index:5;position:absolute;left:77px;top:287px;width:53px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/r05.png"></img> '					
						+ '<img id="r13" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" ' 
							+ 'onmouseover="marcarRegion(this)" title="Región Metropolitana" onclick=\'graficoUv("290004")\' ' 
							+ 'style="z-index:5;position:absolute;left:83px;top:301px;width:47px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/r13.png"></img> '					
						+ '<img id="r06" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" ' 
							+ 'onmouseover="marcarRegion(this)" title="Región de O'
							+ "'" +'higgins" onclick=\'graficoUv("330020")\' ' 
							+ 'style="z-index:5;position:absolute;left:86px;top:323px;width:33px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/r06.png"></img> '					
						+ '<img id="r07" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" '
							+ 'onmouseover="marcarRegion(this)" title="Región del Maule" onclick=\'graficoUv("talca")\' ' 
							+ 'style="z-index:5;position:absolute;left:78px;top:342px;width:39px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/r07.png"></img> '					
						+ '<img id="r08" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" ' 
							+ 'onmouseover="marcarRegion(this)" title="Región del Bio - Bio" onclick=\'graficoUv("scie")\' ' 
							+ 'style="z-index:5;position:absolute;left:61px;top:361px;width:54px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/r08.png"></img>'				
						+ '<img id="r09" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" ' 
							+ 'onmouseover="marcarRegion(this)" title="Región de la Araucanía" onclick=\'graficoUv("sctc")\' ' 
							+ 'style="z-index:5;position:absolute;left:71px;top:386px;width:42px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/r09.png"></img> '					
						+ '<img id="r15" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" ' 
							+ 'onmouseover="marcarRegion(this)" title="Región de los Rios" onclick=\'graficoUv("scvd")\' ' 
							+ 'style="z-index:5;position:absolute;left:70px;top:412px;width:37px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/r15.png"></img> '					
						+ '<img id="r10" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" ' 
							+ 'onmouseover="marcarRegion(this)" title="Región de los Lagos" onclick=\'graficoUv("scte")\' ' 
							+ 'style="z-index:5;position:absolute;left:49px;top:429px;width:82px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/r10.png"></img> '					
						+ '<img id="r11" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" ' 
							+ 'onmouseover="marcarRegion(this)" title="Región de Aysén" onclick=\'graficoUv("sccy")\' ' 
							+ 'style="z-index:5;position:absolute;left:55px;top:481px;width:77px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/r11.png"></img> '					
						+ '<img id="r12" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" ' 
							+ 'onmouseover="marcarRegion(this)" title="Región de Magallanes" onclick=\'graficoUv("scci")\' ' 
							+ 'style="z-index:5;position:absolute;left:73px;top:530px;width:93px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/r12.png"></img> '				
						+ '<div id="" class="img_contenedor_insulares" ' 
							+ 'style="position:absolute;left:150px;top:270px;width:70px; '
							+ 'height:60px;cursor:hand;cursor:pointer">'
						+ '</div>'					
						+ '<img id="risla_pascua" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" ' 
							+ 'onmouseover="marcarRegion(this)" title="Isla de Pascua" onclick=\'graficoUv("scip")\' ' 
							+ 'style="position:absolute;left:170px;top:285px;width:40px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/risla_pascua.png"> '
						+ '</img> '
						+ '<div id="" class="img_contenedor_insulares" ' 
							+ 'style="position:absolute;left:150px;top:360px;width:70px; '
							+ 'height:60px;cursor:hand;cursor:pointer"> '
						+ '</div>'				
						+ '<img id="rjuan_fernandez" ' 
							+ 'class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" ' 
							+ 'onmouseover="marcarRegion(this)" title="Archipiélago Juan Fernandez" '
							+ 'style="position:absolute;left:163px;top:375px;width:50px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/rjuan_fernandez.png">'
						+ '</img> '
						+ '<div id="" class="img_contenedor_insulares" ' 
							+ 'style="position:absolute;left:150px;top:440px;width:70px; ' 
							+ ' height:60px;cursor:hand;cursor:pointer"> '
						+ '</div>'
						+ '<img id="rantartica" class="region_no_seleccionada_pron_region" onmouseout="desmarcarRegion(this)" ' 
							+ 'onmouseover="marcarRegion(this)" title="Antártica" onclick=\'graficoUv("scef")\' '
							+ 'style="position:absolute;left:150px;top:450px;width:70px;cursor:hand;cursor:pointer" ' 
							+ 'src="../img/regiones/rantartica.png"> '
						+ '</img>'
						+ '<MAP NAME="data" id="data">'
						+ '</MAP>'
					+ '</div>'*/
					+ '<table class="radiacionuv" style= "width: 100%;"> '
						+ '<tr> '
							+ '<td colspan="2" class="title-table">Índice Observado y '
								+ 'Pronosticado '
							+ '</td> '
						+ '</tr> '
/*
						+ '<tr> '
							+ '<td colspan="2" style="padding: 25px; font-size: 20px;">'
							+ 'Debido a problemas t&eacute;cnicos, no hemos podido actualizar los pron&oacute;sticos de Radiaci&oacute;n UV,<br>esperamos normalizar el servicio a la brevedad.'
							+ '</td> '
						+ '</tr>'

*/
		




						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=180017">Índice '
									+ 'UV-B estación PUTRE (Univ. de Tarapacá) '
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'180017\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=180016">Índice '
									+ 'UV-B estación ARICA (Univ. de Tarapacá) '
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'180016\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=200006">Índice '
									+ 'UV-B estación IQUIQUE  '
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'200006\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=220009">Índice '
									+ 'UV-B estación SAN PEDRO DE ATACAMA ' 
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'220009\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=230001">Índice '
									+ 'UV-B estación ANTOFAGASTA ' 
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'230001\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=270001">Índice '
									+ 'UV-B estación ISLA DE PASCUA  '
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'270001\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
/*							+ '<td> No disponible </td>'	*/

						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=270008">Índice '
									+ 'UV-B estación CALDERA  '
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'270008\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=280003">Índice '
									+ 'UV-B estación VALLENAR AD. '
								+ '</a> '
							+ '</td> '
/*							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'280003\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
*/							+ '<td> No disponible </td>'
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=290004">Índice '
									+ 'UV-B estación LA SERENA ' 
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'290004\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=300034">Índice '
									+ 'UV-B estación EL TOLOLO ' 
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'300034\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=330020">Índice '
									+ 'UV-B estación SANTIAGO ' 
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'330020\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=330077">Índice '
									+ 'UV-B estación CORDILLERA REGIÓN METROPOLITANA ' 
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'330077\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=330120">Índice '
									+ 'UV-B estación LITORAL CENTRAL ' 
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'330120\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=340031">Índice '
									+ 'UV-B estación GENERAL FREIRE, CURIC&Oacute; AD. ' 
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'340031\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=340045">Índice '
									+ 'UV-B estación RANCAGUA  '
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'340045\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=350050">Índice '
									+ 'UV-B estación TALCA (UNIVERSIDAD AUTÓNOMA) ' 
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'350050\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=360011">Índice '
									+ 'UV-B estación GENERAL BERNARDO O&#039;HIGGINS, CHILL&Aacute;N AD. ' 
								+ '</a> '
							+ '</td> '
/*							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'360011\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
*/							+ '<td> No disponible </td>'
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=360019">Índice '
									+ 'UV-B estación CONCEPCIÓN ' 
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'360019\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=370033">Índice '
									+ 'UV-B estación MARÍA DOLORES, LOS ANGELES AD. ' 
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'370033\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=360042">Índice '
									+ 'UV-B estación TERMAS DE CHILLAN  '
								+ '</a> '
							+ '</td> '
/*							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'360042\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
*/							+ '<td> No disponible </td>'
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=380029">Índice '
									+ 'UV-B estación TEMUCO, LA ARAUCAN&Iacute;A AD.'
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'380029\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
/*							+ '<td> No disponible </td>'	*/
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=390026">Índice '
									+ 'UV-B estación VALDIVIA  '
								+ '</a> '
							+ '</td> '
/*							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'390026\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
*/							+ '<td> No disponible </td>'
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=410005">Índice '
									+ 'UV-B estación PUERTO MONTT  '
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'410005\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=450004">Índice '
									+ 'UV-B estación COYHAIQUE  '
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'450004\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '
						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=520006">Índice '
									+ 'UV-B estación PUNTA ARENAS '
								+ '</a> '
							+ '</td> '
							+ '<td> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'520006\')"> '
									+ 'Índice Horario '
								+ '</a> '
							+ '</td> '
						+ '</tr> '


						+ '<tr class="TRtablaRadiacionUV"> '
							+ '<td class="bottom"> '
								+ '<a href="radiacion_uv_region.xhtml?estacion=950001">Índice '
									+ 'UV-B estación ANTÁRTICA ' 
								+ '</a> '
							+ '</td> '
							+ '<td class="bottom1"> '
								+ '<img src="../images/grafico.gif" width="16" height="14" /> '
								+ '<a style="cursor: pointer" onclick="graficoRadiacionUV(\'950001\')"> '
									+ 'Índice Horario '
								//	+ 'Índice Horario (fuera de servicio)'
								+ '</a> '
							+ '</td> '
						+ '</tr> '




					+ '</table>';



		var contenidoHtmlRadUv = '<table>'
						+ '<tr>'
							+ '<td colspan="3" class="title-table">Radiación Ultravioleta</td>'
						+ '</tr>'
						+ '<tr>'
							+ '<td>'
								+ '<a onclick="window.parent.scrollTo(0, 0);" ' 
									+ 'href="indice_radiacion_uv/informacion_general.xhtml">Información General'
								+ '</a>'
							+ '</td>'
						+ '</tr>'
						+ '<tr>'
							+ '<td class="bottom2">'
								+ '<img src="../images/icono_reader.png" width="16" height="16" />' 
								+ '<a id="leyozono" onclick="window.parent.scrollTo(0, 0);" ' 
									+ 'href="' + urlMeteo() + '/documentos'
									+ '/sq_ley_aa_ozono_20096.pdf#page=1">'
									+ 'Ley de Ozono Nº20.096 "ESTABLECE MECANISMOS DE CONTROL '
									+ 'APLICABLES A LAS SUSTANCIAS AGOTADORAS DE LA CAPA DE OZONO"'
								+ '</a>'
							+ '</td>'
						+ '</tr>'
					+ '</table>'
					+ '<a class="link-footer" href="http://get.adobe.com/es/reader/" target="_blank">'
						+ '<img src="../images/icono_reader.png" width="16" height="16" />'
						+ 'Nota: Si no tiene Documento formato PDF Adobe Acrobat Reader, haga click aquí para descargarlo.'
					+ '</a>';

			
		$("#indiceObservadorDiv").html(contenidoHtmlIndice);
		$("#radiacionUvDiv").html(contenidoHtmlRadUv);
	}


function formatDate() {
	var d = new Date();
	month = '' + (d.getMonth() + 1),
	day = '' + d.getDate(),
	year = d.getFullYear();

	if (month.length < 2) 
		month = '0' + month;
	if (day.length < 2) 
		day = '0' + day;

	return [year, month, day].join('/');
}
 
