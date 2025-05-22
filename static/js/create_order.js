/**
 * Script pour le formulaire de création de commande
 */

document.addEventListener("DOMContentLoaded", () => {
  // Éléments du formulaire
  const orderForm = document.getElementById("orderForm")
  const stepItems = document.querySelectorAll(".step-item")
  const stepContents = document.querySelectorAll(".step-content")
  const nextButtons = document.querySelectorAll(".next-step")
  const prevButtons = document.querySelectorAll(".prev-step")

  // Initialisation des cartes Google Maps
  if (typeof google !== "undefined" && google.maps) {
    initMaps()
  } else {
    // Si l'API n'est pas encore chargée, attendre qu'elle le soit
    window.initMaps = initMaps
  }

  /**
   * Initialise les cartes Google Maps
   */
  function initMaps() {
    // Carte pour l'adresse de prise en charge
    initMap("pickup_map", "id_pickup_address", "id_pickup_latitude", "id_pickup_longitude")

    // Carte pour l'adresse de livraison
    initMap("delivery_map", "id_delivery_address", "id_delivery_latitude", "id_delivery_longitude")
  }

  /**
   * Initialise une carte Google Maps avec autocomplete
   * @param {string} mapId - ID de l'élément de la carte
   * @param {string} addressInputId - ID de l'input d'adresse
   * @param {string} latInputId - ID de l'input de latitude
   * @param {string} lngInputId - ID de l'input de longitude
   */
  function initMap(mapId, addressInputId, latInputId, lngInputId) {
    const mapElement = document.getElementById(mapId)
    const addressInput = document.getElementById(addressInputId)
    const latInput = document.getElementById(latInputId)
    const lngInput = document.getElementById(lngInputId)

    if (!mapElement || !addressInput || !latInput || !lngInput) return

    // Créer la carte
    const map = new google.maps.Map(mapElement, {
      center: { lat: 48.8566, lng: 2.3522 }, // Paris par défaut
      zoom: 13,
      mapTypeControl: false,
      streetViewControl: false,
    })

    // Créer le marqueur
    const marker = new google.maps.Marker({
      map: map,
      draggable: true,
    })

    // Créer l'autocomplete
    const autocomplete = new google.maps.places.Autocomplete(addressInput)
    autocomplete.bindTo("bounds", map)

    // Événement lorsqu'un lieu est sélectionné
    autocomplete.addListener("place_changed", () => {
      const place = autocomplete.getPlace()

      if (!place.geometry) {
        return
      }

      // Mettre à jour la carte
      if (place.geometry.viewport) {
        map.fitBounds(place.geometry.viewport)
      } else {
        map.setCenter(place.geometry.location)
        map.setZoom(17)
      }

      // Mettre à jour le marqueur
      marker.setPosition(place.geometry.location)

      // Mettre à jour les champs cachés
      latInput.value = place.geometry.location.lat()
      lngInput.value = place.geometry.location.lng()

      // Si c'est la carte de livraison, calculer l'itinéraire et le prix
      if (mapId === "delivery_map") {
        calculateRoute()
      }
    })

    // Événement lorsque le marqueur est déplacé
    marker.addListener("dragend", () => {
      const position = marker.getPosition()
      latInput.value = position.lat()
      lngInput.value = position.lng()

      // Mettre à jour l'adresse
      const geocoder = new google.maps.Geocoder()
      geocoder.geocode({ location: position }, (results, status) => {
        if (status === "OK" && results[0]) {
          addressInput.value = results[0].formatted_address
        }
      })

      // Si c'est la carte de livraison, calculer l'itinéraire et le prix
      if (mapId === "delivery_map") {
        calculateRoute()
      }
    })
  }

  /**
   * Calcule l'itinéraire entre les adresses de prise en charge et de livraison
   */
  function calculateRoute() {
    const pickupLat = document.getElementById("id_pickup_latitude").value
    const pickupLng = document.getElementById("id_pickup_longitude").value
    const deliveryLat = document.getElementById("id_delivery_latitude").value
    const deliveryLng = document.getElementById("id_delivery_longitude").value

    if (!pickupLat || !pickupLng || !deliveryLat || !deliveryLng) return

    const directionsService = new google.maps.DirectionsService()
    const directionsRenderer = new google.maps.DirectionsRenderer()

    const pickupLocation = new google.maps.LatLng(pickupLat, pickupLng)
    const deliveryLocation = new google.maps.LatLng(deliveryLat, deliveryLng)

    directionsService.route(
      {
        origin: pickupLocation,
        destination: deliveryLocation,
        travelMode: google.maps.TravelMode.DRIVING,
      },
      (response, status) => {
        if (status === "OK") {
          // Mettre à jour l'estimation de la livraison
          const duration = response.routes[0].legs[0].duration.value // en secondes
          const distance = response.routes[0].legs[0].distance.value // en mètres

          // Mettre à jour les champs cachés
          document.getElementById("id_estimated_duration").value = duration
          document.getElementById("id_estimated_distance").value = distance / 1000 // en km

          // Calculer le prix
          calculatePrice(distance / 1000)
        }
      },
    )
  }

  /**
   * Calcule le prix de la livraison
   * @param {number} distance - Distance en km
   */
  function calculatePrice(distance) {
    const weight = Number.parseFloat(document.getElementById("id_weight").value) || 0
    const size = document.getElementById("id_size").value
    const serviceType = document.getElementById("id_service_type").value
    const hasInsurance = document.getElementById("id_has_insurance").checked

    // Prix de base selon le poids et la taille
    let basePrice = 10.0 // Prix de base

    // Ajuster selon la taille
    const sizeMultiplier = {
      small: 1.0,
      medium: 1.5,
      large: 2.0,
      extra_large: 3.0,
    }
    const sizeFactor = sizeMultiplier[size] || 1.0

    // Ajuster selon le poids
    const weightFactor = 1.0 + weight * 0.1 // 10% de plus par kg

    // Ajuster selon la distance
    const distanceFactor = 1.0 + distance * 0.05 // 5% de plus par km

    basePrice = basePrice * sizeFactor * weightFactor * distanceFactor

    // Supplément selon le service
    let serviceFee = 0
    if (serviceType === "express") {
      serviceFee = basePrice * 0.5 // +50%
    } else if (serviceType === "same_day") {
      serviceFee = basePrice // +100%
    }

    // Assurance
    let insuranceFee = 0
    if (hasInsurance) {
      insuranceFee = (basePrice + serviceFee) * 0.1 // 10% du prix
    }

    // Total
    const totalPrice = basePrice + serviceFee + insuranceFee

    // Mettre à jour l'affichage
    document.getElementById("base_price").textContent = basePrice.toFixed(2) + " €"
    document.getElementById("service_fee").textContent = serviceFee.toFixed(2) + " €"
    document.getElementById("insurance_fee").textContent = insuranceFee.toFixed(2) + " €"
    document.getElementById("total_price").textContent = totalPrice.toFixed(2) + " €"

    // Mettre à jour le champ caché
    document.getElementById("id_price").value = totalPrice.toFixed(2)
  }

  // Navigation entre les étapes
  if (nextButtons.length > 0) {
    nextButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const currentStep = Number.parseInt(this.closest(".step-content").dataset.step)
        const nextStep = currentStep + 1

        // Valider l'étape actuelle
        if (validateStep(currentStep)) {
          // Masquer l'étape actuelle
          document.querySelector(`.step-content[data-step="${currentStep}"]`).classList.add("d-none")

          // Afficher l'étape suivante
          document.querySelector(`.step-content[data-step="${nextStep}"]`).classList.remove("d-none")

          // Mettre à jour la barre de progression
          stepItems.forEach((item) => {
            const itemStep = Number.parseInt(item.dataset.step)
            if (itemStep <= nextStep) {
              item.classList.add("active")
            } else {
              item.classList.remove("active")
            }
          })

          // Si c'est la dernière étape, mettre à jour le récapitulatif
          if (nextStep === 4) {
            updateSummary()
          }
        }
      })
    })
  }

  if (prevButtons.length > 0) {
    prevButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const currentStep = Number.parseInt(this.closest(".step-content").dataset.step)
        const prevStep = currentStep - 1

        // Masquer l'étape actuelle
        document.querySelector(`.step-content[data-step="${currentStep}"]`).classList.add("d-none")

        // Afficher l'étape précédente
        document.querySelector(`.step-content[data-step="${prevStep}"]`).classList.remove("d-none")

        // Mettre à jour la barre de progression
        stepItems.forEach((item) => {
          const itemStep = Number.parseInt(item.dataset.step)
          if (itemStep < currentStep) {
            item.classList.add("active")
          } else {
            item.classList.remove("active")
          }
        })
      })
    })
  }

  /**
   * Valide une étape du formulaire
   * @param {number} step - Numéro de l'étape
   * @returns {boolean} - True si l'étape est valide, false sinon
   */
  function validateStep(step) {
    switch (step) {
      case 1:
        // Valider les détails du colis
        const name = document.getElementById("id_name").value
        const weight = document.getElementById("id_weight").value

        if (!name) {
          alert("Veuillez saisir un nom pour le colis.")
          return false
        }

        if (!weight || isNaN(weight) || weight <= 0) {
          alert("Veuillez saisir un poids valide.")
          return false
        }

        return true

      case 2:
        // Valider les adresses
        const pickupAddress = document.getElementById("id_pickup_address").value
        const deliveryAddress = document.getElementById("id_delivery_address").value
        const pickupLat = document.getElementById("id_pickup_latitude").value
        const pickupLng = document.getElementById("id_pickup_longitude").value
        const deliveryLat = document.getElementById("id_delivery_latitude").value
        const deliveryLng = document.getElementById("id_delivery_longitude").value

        if (!pickupAddress) {
          alert("Veuillez saisir une adresse de prise en charge.")
          return false
        }

        if (!deliveryAddress) {
          alert("Veuillez saisir une adresse de livraison.")
          return false
        }

        if (!pickupLat || !pickupLng) {
          alert("Veuillez sélectionner une adresse de prise en charge valide sur la carte.")
          return false
        }

        if (!deliveryLat || !deliveryLng) {
          alert("Veuillez sélectionner une adresse de livraison valide sur la carte.")
          return false
        }

        return true

      case 3:
        // Valider les options
        const pickupTime = document.getElementById("id_scheduled_pickup_time").value

        if (!pickupTime) {
          alert("Veuillez sélectionner une date et heure de prise en charge.")
          return false
        }

        return true

      default:
        return true
    }
  }

  /**
   * Met à jour le récapitulatif de la commande
   */
  function updateSummary() {
    // Détails du colis
    document.getElementById("summary_name").textContent = document.getElementById("id_name").value
    document.getElementById("summary_weight").textContent = document.getElementById("id_weight").value

    const sizeSelect = document.getElementById("id_size")
    document.getElementById("summary_size").textContent = sizeSelect.options[sizeSelect.selectedIndex].text

    document.getElementById("summary_fragile").textContent = document.getElementById("id_is_fragile").checked
      ? "Oui"
      : "Non"

    // Adresses
    document.getElementById("summary_pickup").textContent = document.getElementById("id_pickup_address").value
    document.getElementById("summary_delivery").textContent = document.getElementById("id_delivery_address").value

    // Options
    const serviceSelect = document.getElementById("id_service_type")
    document.getElementById("summary_service").textContent = serviceSelect.options[serviceSelect.selectedIndex].text

    document.getElementById("summary_pickup_time").textContent =
      document.getElementById("id_scheduled_pickup_time").value
    document.getElementById("summary_insurance").textContent = document.getElementById("id_has_insurance").checked
      ? "Oui"
      : "Non"

    // Calculer le prix
    calculatePrice(Number.parseFloat(document.getElementById("id_estimated_distance").value) || 0)
  }

  // Événements pour recalculer le prix
  const priceFactors = ["id_weight", "id_size", "id_service_type", "id_has_insurance"]
  priceFactors.forEach((id) => {
    const element = document.getElementById(id)
    if (element) {
      element.addEventListener("change", () => {
        calculatePrice(Number.parseFloat(document.getElementById("id_estimated_distance").value) || 0)
      })
    }
  })
})
