/**
 * Script pour la page de suivi de commande
 */

document.addEventListener("DOMContentLoaded", () => {
  // Vérifier si la carte est présente
  const trackingMap = document.getElementById("tracking_map")
  if (!trackingMap) return

  // Variables globales
  let map, deliveryPersonMarker, directionsRenderer
  let isTracking = false
  let trackingInterval

  // Initialiser la carte lorsque l'API Google Maps est chargée
  if (typeof google !== "undefined" && google.maps) {
    initMap()
  } else {
    // Si l'API n'est pas encore chargée, attendre qu'elle le soit
    window.initMap = initMap
  }

  /**
   * Initialise la carte de suivi
   */
  function initMap() {
    // Coordonnées des adresses
    const pickupLocation = {
      lat: Number.parseFloat(trackingMap.dataset.pickupLat),
      lng: Number.parseFloat(trackingMap.dataset.pickupLng),
    }

    const deliveryLocation = {
      lat: Number.parseFloat(trackingMap.dataset.deliveryLat),
      lng: Number.parseFloat(trackingMap.dataset.deliveryLng),
    }

    // Créer la carte
    map = new google.maps.Map(trackingMap, {
      center: {
        lat: (pickupLocation.lat + deliveryLocation.lat) / 2,
        lng: (pickupLocation.lng + deliveryLocation.lng) / 2,
      },
      zoom: 12,
      mapTypeControl: false,
      streetViewControl: false,
    })

    // Marqueurs
    const pickupMarker = new google.maps.Marker({
      position: pickupLocation,
      map: map,
      icon: {
        url: "/static/images/pickup-marker.png",
        scaledSize: new google.maps.Size(40, 40),
      },
      title: "Adresse de prise en charge",
    })

    const deliveryMarker = new google.maps.Marker({
      position: deliveryLocation,
      map: map,
      icon: {
        url: "/static/images/delivery-marker.png",
        scaledSize: new google.maps.Size(40, 40),
      },
      title: "Adresse de livraison",
    })

    // Infowindows
    const pickupInfo = new google.maps.InfoWindow({
      content: `<div><strong>Prise en charge</strong><p>${trackingMap.dataset.pickupAddress}</p></div>`,
    })

    const deliveryInfo = new google.maps.InfoWindow({
      content: `<div><strong>Livraison</strong><p>${trackingMap.dataset.deliveryAddress}</p></div>`,
    })

    pickupMarker.addListener("click", () => {
      pickupInfo.open(map, pickupMarker)
    })

    deliveryMarker.addListener("click", () => {
      deliveryInfo.open(map, deliveryMarker)
    })

    // Ajuster la vue pour montrer les deux marqueurs
    const bounds = new google.maps.LatLngBounds()
    bounds.extend(pickupLocation)
    bounds.extend(deliveryLocation)
    map.fitBounds(bounds)

    // Tracer l'itinéraire
    const directionsService = new google.maps.DirectionsService()
    directionsRenderer = new google.maps.DirectionsRenderer({
      map: map,
      suppressMarkers: true, // Ne pas afficher les marqueurs par défaut
      polylineOptions: {
        strokeColor: "#4285F4",
        strokeWeight: 5,
      },
    })

    directionsService.route(
      {
        origin: pickupLocation,
        destination: deliveryLocation,
        travelMode: google.maps.TravelMode.DRIVING,
      },
      (response, status) => {
        if (status === "OK") {
          directionsRenderer.setDirections(response)
        }
      },
    )

    // Si la commande est en cours de livraison, ajouter le marqueur du livreur
    if (trackingMap.dataset.status === "in_transit") {
      // Marqueur du livreur (position initiale)
      deliveryPersonMarker = new google.maps.Marker({
        position: pickupLocation, // Position initiale
        map: map,
        icon: {
          url: "/static/images/delivery-person-marker.png",
          scaledSize: new google.maps.Size(40, 40),
        },
        title: "Livreur",
      })

      // Infowindow du livreur
      const deliveryPersonInfo = new google.maps.InfoWindow({
        content: `<div><strong>Livreur</strong><p>${trackingMap.dataset.deliveryPerson}</p></div>`,
      })

      deliveryPersonMarker.addListener("click", () => {
        deliveryPersonInfo.open(map, deliveryPersonMarker)
      })

      // Commencer le suivi en temps réel
      startTracking()
    }
  }

  /**
   * Commence le suivi en temps réel
   */
  function startTracking() {
    if (isTracking) return

    isTracking = true

    // Mettre à jour la position immédiatement
    updateDeliveryPersonLocation()

    // Puis mettre à jour toutes les 10 secondes
    trackingInterval = setInterval(updateDeliveryPersonLocation, 10000)

    // Ajouter un bouton pour centrer la carte sur le livreur
    const centerButton = document.createElement("div")
    centerButton.className = "center-button"
    centerButton.innerHTML = '<button type="button" class="btn btn-light"><i class="fas fa-crosshairs"></i></button>'
    centerButton.addEventListener("click", () => {
      if (deliveryPersonMarker) {
        map.panTo(deliveryPersonMarker.getPosition())
        map.setZoom(15)
      }
    })

    map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(centerButton)
  }

  /**
   * Arrête le suivi en temps réel
   */
  function stopTracking() {
    if (!isTracking) return

    isTracking = false
    clearInterval(trackingInterval)
  }

  /**
   * Met à jour la position du livreur
   */
  function updateDeliveryPersonLocation() {
    const orderId = trackingMap.dataset.orderId

    fetch(`/tracking/get_tracking_points/${orderId}/`)
      .then((response) => response.json())
      .then((data) => {
        if (data.success && data.points.length > 0) {
          // Récupérer le dernier point
          const lastPoint = data.points[data.points.length - 1]
          const position = {
            lat: Number.parseFloat(lastPoint.latitude),
            lng: Number.parseFloat(lastPoint.longitude),
          }

          // Mettre à jour la position du marqueur
          deliveryPersonMarker.setPosition(position)

          // Mettre à jour l'heure estimée d'arrivée
          if (data.eta) {
            const etaElement = document.getElementById("estimated_arrival_time")
            if (etaElement) {
              etaElement.textContent = data.eta
            }
          }

          // Si c'est la première mise à jour, centrer la carte sur la position du livreur
          if (data.points.length === 1) {
            map.panTo(position)
            map.setZoom(15)
          }
        }
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération des points de suivi:", error)
        stopTracking()
      })
  }

  // Nettoyage lors de la fermeture de la page
  window.addEventListener("beforeunload", () => {
    stopTracking()
  })
})
