
/**
 * !----------------------------------------------------------------------------------
 * 


function enableButton() {
    const button = document.getElementById('myButton');
    button.disabled = false; // Habilita el botón
}

function disableButton() {
    const button = document.getElementById('myButton');
    button.disabled = true; // Deshabilita el botón
}

function checkTimeAndDayToEnableButton() {
    console.log("entro funcion1")
    // Hora objetivo (por ejemplo, 14:00)
    const targetHour = 7;
    const targetMinute = 45;

    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();
    const currentDay = now.getDay(); // Obtiene el día de la semana (0 = domingo, 6 = sábado)

    // Si es entre lunes (1) y viernes (5)
    if (currentDay >= 0 && currentDay <= 6) {
        console.log("entro funcion2")
        // Verifica la hora
        if (currentHour > targetHour) {
            if(currentHour <= 18 ){
                enableButton()
            }else{
                disableButton()
            }
            
        } else if(currentHour == targetHour) {
            if(currentMinute>=targetMinute){
                enableButton()
            }else{
                setTimeout(checkTimeAndDayToEnableButton, 60000); 
            }
           // Verifica nuevamente cada 60 segundos
            
        }else{
            setTimeout(checkTimeAndDayToEnableButton, 60000); 
        }

    } else {
        // Si es sábado (6) o domingo (0), deshabilita el botón
        disableButton();
    }
}

window.onload = function () {
    checkTimeAndDayToEnableButton(); // Comienza a verificar cuando la página se carga
};

 */