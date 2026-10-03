	
	function renderTemperaturasExtremas() {			
		var divDetalle = "<div id='divDetalleTemp'>" +
							"<table>" +
							"<tbody>" +
								"<tr>" +	
									"<td colspan=\"3\" class=\"letraTituloTemp\">" +
										"<label class='letraPronTempExtremasTitulo'> Temperaturas extremas registradas</label> <br/>" +
										 fechavalidez_temperaturas_extremas +
									"</td>" +
								"</tr>";
		
		var icono;
	
		for (var i = 0; i < temperaturas_extremas.length; i++) {
			
			var tempExtremasArray = temperaturas_extremas[i].split("|");
			
			divDetalle += "<tr>" +
							"<td style='text-align: center;'>";
			
			divDetalle += "<label class='letraPronTempExtremasCiudad'><b>" + tempExtremasArray[1] + "</b></label><br />";

			if (tempExtremasArray[2] != undefined && tempExtremasArray[2] != "undefined" && tempExtremasArray[2] != "") {

				divDetalle += /*"<label class='letraPronTempExtremasCiudad'>" + tempExtremasArray[1] + "</label><br />" +*/
										"<label class='letraPronTempExtremasTemp'> M&iacute;nima: "+ tempExtremasArray[2] + "&deg;C" + ((tempExtremasArray[3] != undefined 
											&& tempExtremasArray[3] != "undefined" && tempExtremasArray[3] != "") ? " a las " 
											+ tempExtremasArray[3] : "") + "</label>";
				}

			if (tempExtremasArray[4] != undefined && tempExtremasArray[4] != "undefined" && tempExtremasArray[4]) {
				divDetalle += "<br />" +
										"<label class='letraPronTempExtremasTemp'> M&aacute;xima: " + tempExtremasArray[4] + "&deg;C" + ((tempExtremasArray[5] != undefined 
											&& tempExtremasArray[5] != "undefined" && tempExtremasArray[5] != "") ? " a las " 
											+ tempExtremasArray[5] : "") + "</label>";

			}
			
			divDetalle += 	"</td>" +
								"</tr>";		  	
		}
		
		divDetalle += "</tbody></table></div>";
		
		$("#contBtnDerecha").append(divDetalle);
		
		if (window.navigator.userAgent.indexOf("Edge") != -1) {
			$("#divDetalleTemp").css({
				'padding-right': '2px'
			});
		} else {
			if(navigator.userAgent.indexOf("Chrome") != -1 ||
			navigator.userAgent.indexOf("Safari") != -1 ) {
				$("#divDetalleTemp").css({
					'padding-right': '0px'					
				});
			} else if (navigator.userAgent.indexOf("Firefox") != -1 ) {
				$("#divDetalleTemp").css({
					'padding-right': '2px',
					'top' : '275px'
				});
			}  else if (navigator.userAgent.match(/Trident/)) {
				$("#divDetalleTemp").css({
					'padding-right': '2px'
				});
			} else {
				$("#divDetalleTemp").css({
					'padding-right': '2px'
				});
			}
		}		
	}
