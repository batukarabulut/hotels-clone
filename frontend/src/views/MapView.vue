<!-- frontend/src/views/MapView.vue -->
<template>
  <div class="map-view">
    <!-- Header -->
    <header class="header">
      <div class="container">
        <div class="header-content">
          <div class="logo">
            <router-link to="/" class="logo-link">
              <span class="logo-icon">🏨</span>
              <span class="logo-text">Hotels.com</span>
            </router-link>
          </div>
          <div class="map-controls">
            <button @click="goBack" class="back-btn">
              ← Geri dön
            </button>
            <span class="map-title">{{ mapTitle }}</span>
          </div>
          <div class="auth-section">
            <span v-if="currentUser" class="greeting">
              Merhaba, {{ userDisplayName }}
            </span>
            <button v-else @click="showLoginModal = true" class="login-btn">
              Giriş yap
            </button>
            <button v-if="currentUser" @click="handleLogout" class="logout-btn">
              Çıkış
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Map Content -->
    <div class="map-container">
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner">🔄</div>
        <p>Harita yükleniyor...</p>
      </div>

      <div v-if="error" class="error-overlay">
        <div class="error-message">
          <p>❌ Hata: {{ error }}</p>
          <button @click="loadHotels" class="retry-btn">Tekrar dene</button>
        </div>
      </div>

      <!-- Simplified Map with Leaflet -->
      <div 
        v-if="!loading && !error"
        ref="mapContainer"
        id="mapContainer"
        class="leaflet-map"
      ></div>
    </div>

    <!-- Hotel Count Info -->
    <div class="hotel-count-info" v-if="hotels.length > 0">
      <span>{{ hotels.length }} konaklama yeri</span>
    </div>

    <!-- Login Modal -->
    <LoginModal :showModal="showLoginModal" @close="showLoginModal = false" @login-success="handleLoginSuccess" />
  </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from 'vuex'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import LoginModal from '@/components/LoginModal.vue'

// Fix for default markers
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

export default {
  name: 'MapView',
  components: {
    LoginModal
  },
  data() {
    return {
      showLoginModal: false,
      map: null,
      hotels: [],
      selectedHotel: null
    }
  },
  computed: {
    ...mapState(['weekendHotels', 'searchResults']),
    ...mapGetters(['isLoading', 'hasError', 'errorMessage', 'currentUser', 'isAuthenticated', 'userDisplayName']),
    
    loading() {
      return this.isLoading
    },
    error() {
      return this.hasError ? this.errorMessage : null
    },
    mapTitle() {
      const view = this.$route.query.view
      if (view === 'weekend') {
        return 'Hafta Sonu Otelleri'
      } else if (view === 'search') {
        return `Arama Sonuçları: ${this.$route.query.destination || 'Tüm Oteller'}`
      }
      return 'Otel Haritası'
    }
  },
  methods: {
    ...mapActions(['loadWeekendHotels', 'searchHotels', 'logout']),

    initializeMap() {
      this.$nextTick(() => {
        if (this.$refs.mapContainer && !this.map) {
          this.map = L.map('mapContainer').setView([39.9334, 32.8597], 7)
          
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
          }).addTo(this.map)

          // Add hotels to map
          this.addHotelsToMap()
        }
      })
    },

    addHotelsToMap() {
      if (!this.map) {
        console.log('Map not initialized yet')
        return
      }
      
      if (this.hotels.length === 0) {
        console.log('No hotels to add to map')
        return
      }

      console.log('Adding hotels to map:', this.hotels.length, 'hotels')

      const bounds = []

      this.hotels.forEach((hotel, index) => {
        console.log(`Hotel ${index + 1}:`, {
          name: hotel.name,
          latitude: hotel.latitude,
          longitude: hotel.longitude,
          lat_type: typeof hotel.latitude,
          lng_type: typeof hotel.longitude
        })
        
        if (hotel.latitude && hotel.longitude) {
          const lat = parseFloat(hotel.latitude)
          const lng = parseFloat(hotel.longitude)
          
          console.log(`Parsed coordinates for ${hotel.name}:`, { lat, lng })
          
          if (isNaN(lat) || isNaN(lng)) {
            console.log('Invalid coordinates for hotel:', hotel.name, 'lat:', lat, 'lng:', lng)
            return
          }
          
          console.log(`Creating marker for ${hotel.name} at [${lat}, ${lng}]`)
          
          // Fiyatı belirle (üye fiyatı varsa onu kullan)
          const hotelPrice = this.currentUser && hotel.member_price_display < hotel.base_price 
            ? hotel.member_price_display 
            : hotel.base_price

          // Custom marker icon with price
          const priceText = this.formatPrice(hotelPrice) + ' TL'
          
          // Custom div icon - Mavi bubble tasarımı
          const customIcon = L.divIcon({
            className: 'custom-hotel-marker',
            html: `
              <div style="
                background: #007bff;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 15px;
                white-space: nowrap;
                box-shadow: 0 2px 8px rgba(0, 123, 255, 0.5);
                border: 2px solid white;
                text-align: center;
                min-width: 60px;
                font-family: Arial, sans-serif;
              ">
                ${priceText}
              </div>
            `,
            iconSize: [80, 30],
            iconAnchor: [40, 15]
          })
          
          const marker = L.marker([lat, lng], { icon: customIcon }).addTo(this.map)

          const popupContent = `
            <div style="min-width: 200px;">
              <h3 style="margin: 0 0 0.5rem 0; font-size: 1.1rem; font-weight: 600;">
                ${hotel.name}
              </h3>
              <p style="margin: 0 0 0.5rem 0; color: #6c757d; font-size: 0.9rem;">
                📍 ${hotel.city}, ${hotel.country}
              </p>
              <div style="margin: 0 0 0.5rem 0; color: #6c757d; font-size: 0.9rem;">
                ⭐ ${hotel.rating}/10 (${hotel.total_reviews} yorum)
              </div>
              <div style="margin: 0 0 0.75rem 0;">
                ${this.currentUser && hotel.member_price_display < hotel.base_price ? `
                  <div style="color: #28a745; font-weight: bold; font-size: 1.1rem;">
                    Üye Fiyatı: ${this.formatPrice(hotel.member_price_display)} TL
                  </div>
                  <div style="text-decoration: line-through; color: #6c757d; font-size: 0.9rem;">
                    ${this.formatPrice(hotel.base_price)} TL
                  </div>
                ` : `
                  <div style="font-weight: bold; color: #2c3e50; font-size: 1.1rem;">
                    ${this.formatPrice(hotelPrice)} TL
                  </div>
                `}
              </div>
              <button 
                onclick="window.viewHotel(${hotel.id})" 
                style="background: #006ce4; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; width: 100%; transition: background 0.3s;"
                onmouseover="this.style.background='#0056b3'"
                onmouseout="this.style.background='#006ce4'"
              >
                Oteli Görüntüle
              </button>
            </div>
          `
          
          marker.bindPopup(popupContent)
          bounds.push([lat, lng])
          console.log(`Successfully added marker for ${hotel.name} at [${lat}, ${lng}]`)
        } else {
          console.log('Missing coordinates for hotel:', hotel.name, 'lat:', hotel.latitude, 'lng:', hotel.longitude)
        }
      })

      // Fit map to show all hotels
      if (bounds.length > 0) {
        console.log('Fitting map to bounds:', bounds.length, 'locations')
        this.map.fitBounds(bounds, { padding: [20, 20] })
      } else {
        console.log('No valid coordinates found for any hotels')
      }
    },

    async loadHotels() {
      const view = this.$route.query.view
      console.log('Loading hotels for view:', view)
      
      try {
        if (view === 'weekend') {
          await this.loadWeekendHotels()
          this.hotels = this.weekendHotels
          console.log('Loaded weekend hotels:', this.hotels)
        } else if (view === 'search') {
          const searchQuery = {
            destination: this.$route.query.destination || '',
            checkIn: this.$route.query.checkIn || '',
            checkOut: this.$route.query.checkOut || '',
            guests: this.$route.query.guests || '2'
          }
          console.log('Search query:', searchQuery)
          await this.searchHotels(searchQuery)
          this.hotels = this.searchResults
          console.log('Loaded search results:', this.hotels)
        } else {
          // Default to weekend hotels
          await this.loadWeekendHotels()
          this.hotels = this.weekendHotels
          console.log('Loaded default weekend hotels:', this.hotels)
        }

        // Initialize map after hotels are loaded
        this.$nextTick(() => {
          this.initializeMap()
        })
      } catch (error) {
        console.error('Error loading hotels:', error)
      }
    },

    goBack() {
      this.$router.back()
    },

    handleLoginSuccess(user) {
      console.log('Login successful:', user)
      this.loadHotels()
    },

    async handleLogout() {
      await this.logout()
      this.loadHotels()
    },

    formatPrice(price) {
      return new Intl.NumberFormat('tr-TR').format(price)
    }
  },

  async mounted() {
    // Initialize auth from localStorage
    this.$store.dispatch('initializeAuth')
    
    // Global function for popup buttons
    window.viewHotel = (hotelId) => {
      this.$router.push({
        name: 'HotelDetail',
        params: { id: hotelId }
      })
    }

    await this.loadHotels()
  },

  beforeUnmount() {
    if (this.map) {
      this.map.remove()
    }
    // Clean up global function
    delete window.viewHotel
  }
}
</script>

<style scoped>
.map-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #e7e7e7;
  z-index: 1000;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: bold;
  color: #c73939;
}

.map-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-btn {
  background: #f8f9fa;
  color: #495057;
  border: 1px solid #dee2e6;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.back-btn:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.map-title {
  color: #2c3e50;
  font-weight: 600;
  font-size: 1.1rem;
}

.auth-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.greeting {
  color: #2c3e50;
  font-weight: 500;
}

.login-btn,
.logout-btn {
  background: #006ce4;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.3s;
}

.login-btn:hover {
  background: #0056b3;
}

.logout-btn {
  background: #dc3545;
}

.logout-btn:hover {
  background: #c82333;
}

.map-container {
  flex: 1;
  position: relative;
}

.leaflet-map {
  height: 100%;
  width: 100%;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 1000;
}

.loading-spinner {
  font-size: 2rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-message {
  text-align: center;
}

.retry-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.hotel-count-info {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  font-weight: 500;
  color: #2c3e50;
}

/* Custom Marker Styles */
:deep(.custom-hotel-marker) {
  background: transparent !important;
  border: none !important;
}

.price-bubble-blue {
  background: #007bff;
  color: white;
  font-size: 0.85rem;
  font-weight: bold;
  padding: 0.4rem 0.8rem;
  border-radius: 15px;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.4);
  border: 2px solid white;
  text-align: center;
  min-width: 60px;
  position: relative;
}

.price-bubble-blue:hover {
  background: #0056b3;
  transform: scale(1.05);
  transition: all 0.2s ease;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }

  .map-controls {
    order: -1;
  }

  .hotel-count-info {
    top: 0.5rem;
    right: 0.5rem;
    padding: 0.25rem 0.75rem;
    font-size: 0.9rem;
  }
}
</style>