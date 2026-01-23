// Variable global para el Wake Lock
let wakeLock = null;

// Función para solicitar que la pantalla NO se apague
async function activarWakeLock() {
    try {
        if ('wakeLock' in navigator) {
            wakeLock = await navigator.wakeLock.request('screen');
            console.log("Pantalla bloqueada: No se apagará");
            
            // Si el usuario cambia de pestaña y vuelve, reactivarlo
            wakeLock.addEventListener('release', () => {
                console.log('Wake Lock liberado');
            });
        }
    } catch (err) {
        console.error(`Error con Wake Lock: ${err.name}, ${err.message}`);
    }
}

function iniciarRastreo() {
    if (isMonitor) return;

    // Activamos el Wake Lock al iniciar
    activarWakeLock();

    navigator.geolocation.watchPosition(pos => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;

        if (!centradoInicial) {
            map.setView([lat, lng], 17);
            centradoInicial = true;
        }

        // Enviamos los datos al servidor
        fetch('/update/' + trailerId, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                lat: lat, 
                lng: lng, 
                battery: "Activo" 
            })
        });
    }, err => {
        console.error("Error de GPS:", err);
    }, { 
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0 
    });
}

// Escuchar cuando la página vuelve a estar visible para reactivar el bloqueo
document.addEventListener('visibilitychange', async () => {
    if (wakeLock !== null && document.visibilityState === 'visible') {
        activarWakeLock();
    }
});