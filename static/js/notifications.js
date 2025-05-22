/**
 * Script pour la gestion des notifications
 */

document.addEventListener("DOMContentLoaded", () => {
  // Vérifier si l'utilisateur est connecté
  const userIsAuthenticated = document.body.classList.contains("user-authenticated")
  if (!userIsAuthenticated) return

  // Variables globales
  let notificationsCount = 0
  let notificationsInterval

  // Éléments DOM
  const notificationBadge = document.querySelector(".notification-badge")
  const notificationsList = document.querySelector(".notifications-list")

  // Initialiser les notifications
  initNotifications()

  /**
   * Initialise le système de notifications
   */
  function initNotifications() {
    // Charger les notifications initiales
    fetchNotifications()

    // Mettre à jour les notifications toutes les 30 secondes
    notificationsInterval = setInterval(fetchNotifications, 30000)

    // Marquer les notifications comme lues lorsqu'elles sont ouvertes
    const notificationsDropdown = document.getElementById("notificationsDropdown")
    if (notificationsDropdown) {
      notificationsDropdown.addEventListener("shown.bs.dropdown", () => {
        markNotificationsAsRead()
      })
    }
  }

  /**
   * Récupère les notifications non lues
   */
  function fetchNotifications() {
    fetch("/notifications/unread/")
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          updateNotificationsUI(data.notifications)
        }
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération des notifications:", error)
      })
  }

  /**
   * Met à jour l'interface utilisateur des notifications
   * @param {Array} notifications - Liste des notifications
   */
  function updateNotificationsUI(notifications) {
    // Mettre à jour le compteur
    notificationsCount = notifications.length
    if (notificationBadge) {
      notificationBadge.textContent = notificationsCount
      notificationBadge.style.display = notificationsCount > 0 ? "inline-block" : "none"
    }

    // Mettre à jour la liste des notifications
    if (notificationsList) {
      // Vider la liste
      notificationsList.innerHTML = ""

      if (notifications.length > 0) {
        // Ajouter les notifications
        notifications.forEach((notification) => {
          const notificationItem = document.createElement("div")
          notificationItem.className = "dropdown-item notification-item"
          notificationItem.dataset.id = notification.id

          notificationItem.innerHTML = `
                        <div class="d-flex align-items-center">
                            <div class="notification-icon ${getNotificationIconClass(notification.notification_type)}">
                                <i class="${getNotificationIcon(notification.notification_type)}"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">${notification.title}</h6>
                                <p class="mb-0 small">${notification.message}</p>
                                <small class="text-muted">${formatTimestamp(notification.created_at)}</small>
                            </div>
                        </div>
                    `

          notificationsList.appendChild(notificationItem)
        })

        // Ajouter le lien pour voir toutes les notifications
        const viewAllItem = document.createElement("div")
        viewAllItem.className = "dropdown-item text-center border-top mt-2 pt-2"
        viewAllItem.innerHTML = '<a href="/notifications/" class="text-primary">Voir toutes les notifications</a>'
        notificationsList.appendChild(viewAllItem)
      } else {
        // Afficher un message si aucune notification
        const emptyItem = document.createElement("div")
        emptyItem.className = "dropdown-item text-center"
        emptyItem.textContent = "Aucune notification non lue"
        notificationsList.appendChild(emptyItem)
      }
    }

    // Afficher une notification système pour les nouvelles notifications
    if (notificationsCount > 0 && "Notification" in window) {
      // Vérifier si les notifications sont autorisées
      if (Notification.permission === "granted") {
        showSystemNotification(notifications[0])
      } else if (Notification.permission !== "denied") {
        // Demander la permission
        Notification.requestPermission().then((permission) => {
          if (permission === "granted") {
            showSystemNotification(notifications[0])
          }
        })
      }
    }
  }

  /**
   * Marque les notifications comme lues
   */
  function markNotificationsAsRead() {
    fetch("/notifications/mark-as-read/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Mettre à jour l'interface
          notificationsCount = 0
          if (notificationBadge) {
            notificationBadge.textContent = "0"
            notificationBadge.style.display = "none"
          }
        }
      })
      .catch((error) => {
        console.error("Erreur lors du marquage des notifications comme lues:", error)
      })
  }

  /**
   * Affiche une notification système
   * @param {Object} notification - Notification à afficher
   */
  function showSystemNotification(notification) {
    const systemNotification = new Notification("ExpressDelivery", {
      body: notification.message,
      icon: "/static/images/logo.png",
    })

    systemNotification.onclick = () => {
      window.focus()
      if (notification.url) {
        window.location.href = notification.url
      }
    }
  }

  /**
   * Récupère la classe d'icône pour un type de notification
   * @param {string} type - Type de notification
   * @returns {string} - Classe d'icône
   */
  function getNotificationIconClass(type) {
    switch (type) {
      case "order_status":
        return "bg-primary"
      case "delivery":
        return "bg-success"
      case "alert":
        return "bg-danger"
      default:
        return "bg-info"
    }
  }

  /**
   * Récupère l'icône pour un type de notification
   * @param {string} type - Type de notification
   * @returns {string} - Classe d'icône
   */
  function getNotificationIcon(type) {
    switch (type) {
      case "order_status":
        return "fas fa-box"
      case "delivery":
        return "fas fa-truck"
      case "alert":
        return "fas fa-exclamation-triangle"
      default:
        return "fas fa-bell"
    }
  }

  /**
   * Formate un timestamp
   * @param {string} timestamp - Timestamp à formater
   * @returns {string} - Timestamp formaté
   */
  function formatTimestamp(timestamp) {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffSec = Math.floor(diffMs / 1000)
    const diffMin = Math.floor(diffSec / 60)
    const diffHour = Math.floor(diffMin / 60)
    const diffDay = Math.floor(diffHour / 24)

    if (diffSec < 60) {
      return "À l'instant"
    } else if (diffMin < 60) {
      return `Il y a ${diffMin} minute${diffMin > 1 ? "s" : ""}`
    } else if (diffHour < 24) {
      return `Il y a ${diffHour} heure${diffHour > 1 ? "s" : ""}`
    } else if (diffDay < 7) {
      return `Il y a ${diffDay} jour${diffDay > 1 ? "s" : ""}`
    } else {
      return date.toLocaleDateString()
    }
  }

  /**
   * Récupère le jeton CSRF
   * @returns {string} - Jeton CSRF
   */
  function getCsrfToken() {
    const csrfCookie = document.cookie.split(";").find((cookie) => cookie.trim().startsWith("csrftoken="))
    return csrfCookie ? csrfCookie.split("=")[1] : ""
  }

  // Nettoyage lors de la fermeture de la page
  window.addEventListener("beforeunload", () => {
    clearInterval(notificationsInterval)
  })
})
