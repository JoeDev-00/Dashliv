/**
 * Fonctions utilitaires pour Google Maps
 */

/**
 * Initialise une carte Google Maps avec un marqueur
 * @param {string} elementId - ID de l'élément HTML qui contiendra la carte
 * @param {Object} position - Position initiale (lat, lng)
 * @param {Object} options - Options supplémentaires
 * @returns {Object} - Objet contenant la carte et le marqueur
 */
function initializeMap(elementId, position, options = {}) {
  const defaultOptions = {
    zoom: 13,
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: true,
    zoomControl: true,
  }

  const mapOptions = { ...defaultOptions, ...options }

  // Créer la carte
  const mapElement = document.getElementById(elementId)
  const map = new google.maps.Map(mapElement, {
    center: position,
    ...mapOptions,
  })

  // Créer le marqueur
  const marker = new google.maps.Marker({
    position: position,
    map: map,
    draggable: options.draggable || false,
  })

  return { map, marker }
}

/**
 * Calcule l'itinéraire entre deux points
 * @param {Object} origin - Point de départ (lat, lng)
 * @param {Object} destination - Point d'arrivée (lat, lng)
 * @param {google.maps.Map} map - Carte Google Maps
 * @param {Object} options - Options supplémentaires
 * @returns {Promise} - Promise contenant le résultat de l'itinéraire
 */
function calculateRoute(origin, destination, map, options = {}) {
  return new Promise((resolve, reject) => {
    const directionsService = new google.maps.DirectionsService()
    const directionsRenderer = new google.maps.DirectionsRenderer({
      map: map,
      suppressMarkers: options.suppressMarkers || false,
      polylineOptions: options.polylineOptions || null,
    })

    directionsService.route(
      {
        origin: origin,
        destination: destination,
        travelMode: options.travelMode || google.maps.TravelMode.DRIVING,
      },
      (response, status) => {
        if (status === "OK") {
          directionsRenderer.setDirections(response)
          resolve({
            response,
            renderer: directionsRenderer,
            distance: response.routes[0].legs[0].distance.text,
            duration: response.routes[0].legs[0].duration.text,
          })
        } else {
          reject(new Error(`Erreur de calcul d'itinéraire: ${status}`))
        }
      },
    )
  })
}

/**
 * Géocode une adresse en coordonnées
 * @param {string} address - Adresse à géocoder
 * @returns {Promise} - Promise contenant les coordonnées
 */
function geocodeAddress(address) {
  return new Promise((resolve, reject) => {
    const geocoder = new google.maps.Geocoder()

    geocoder.geocode({ address: address }, (results, status) => {
      if (status === "OK" && results[0]) {
        resolve({
          lat: results[0].geometry.location.lat(),
          lng: results[0].geometry.location.lng(),
          formattedAddress: results[0].formatted_address,
        })
      } else {
        reject(new Error(`Erreur de géocodage: ${status}`))
      }
    })
  })
}

/**
 * Géocode inverse (coordonnées en adresse)
 * @param {Object} position - Position (lat, lng)
 * @returns {Promise} - Promise contenant l'adresse
 */
function reverseGeocode(position) {
  return new Promise((resolve, reject) => {
    const geocoder = new google.maps.Geocoder()

    geocoder.geocode({ location: position }, (results, status) => {
      if (status === "OK" && results[0]) {
        resolve({
          address: results[0].formatted_address,
          results: results,
        })
      } else {
        reject(new Error(`Erreur de géocodage inverse: ${status}`))
      }
    })
  })
}

/**
 * Ouvre une application de navigation avec les coordonnées
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 */
function openNavigationApp(lat, lng) {
  // Détecter l'appareil
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent)

  if (isMobile) {
    // Détecter le système d'exploitation
    const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent)

    if (isIOS) {
      // Ouvrir Apple Plans
      window.open(`maps://maps.apple.com/?daddr=${lat},${lng}&dirflg=d`)
    } else {
      // Ouvrir Google Maps
      window.open(`https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}&travelmode=driving`)
    }
  } else {
    // Ouvrir Google Maps dans le navigateur
    window.open(`https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}&travelmode=driving`)
  }
}

/**
 * Obtient la position actuelle de l'utilisateur
 * @returns {Promise} - Promise contenant la position
 */
function getCurrentPosition() {
  return new Promise((resolve, reject) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          })
        },
        (error) => {
          reject(new Error(`Erreur de géolocalisation: ${error.message}`))
        },
        {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0,
        },
      )
    } else {
      reject(new Error("La géolocalisation n'est pas prise en charge par ce navigateur."))
    }
  })
}
