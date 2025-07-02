<!-- frontend/src/views/HotelDetail.vue -->
<template>
  <div class="hotel-detail-page">
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
          <div class="breadcrumb">
            <router-link to="/" class="back-link">Ana Sayfa</router-link>
            <span class="separator">/</span>
            <span class="current">{{ hotel?.name || 'Otel Detayı' }}</span>
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

    <!-- Main Content -->
    <div class="main-content">
      <div class="container">
        <!-- Loading State -->
        <div v-if="loading" class="alert alert-info">
          Otel bilgileri yükleniyor...
        </div>

        <!-- Error State -->
        <div v-if="error" class="alert alert-danger">
          {{ error }}
          <button @click="fetchHotelDetail" class="retry-btn">Tekrar dene</button>
        </div>

        <!-- Hotel Detail -->
        <div v-if="hotel && !loading" class="hotel-detail">
          <!-- Hotel Header -->
          <div class="hotel-header">
            <div class="hotel-main-info">
              <h1 class="hotel-name">{{ hotel.name }}</h1>
              <p class="hotel-location">📍 {{ hotel.address || `${hotel.city}, ${hotel.country}` }}</p>
              <div class="hotel-rating">
                <span class="rating-score">⭐ {{ hotel.rating }}/10</span>
                <span class="rating-text">({{ hotel.total_reviews }} yorum)</span>
              </div>
            </div>
            
            <div class="hotel-pricing">
              <div v-if="!currentUser && hotel.is_flagged" class="member-price-notice">
                💎 Üye fiyatı için giriş yapın
              </div>
              
              <div class="price-display">
                <div v-if="currentUser && hotel.member_price_display < hotel.base_price" class="member-pricing">
                  <span class="member-price">
                    Üye Fiyatı: {{ formatPrice(hotel.member_price_display) }} TL
                  </span>
                  <span class="base-price crossed">
                    {{ formatPrice(hotel.base_price) }} TL
                  </span>
                </div>
                <div v-else class="regular-pricing">
                  <span class="price">{{ formatPrice(hotel.base_price) }} TL</span>
                  <span class="per-night">/ gece</span>
                </div>
                
                <div v-if="hotel.special_discount > 0" class="discount-badge">
                  %{{ hotel.special_discount }} indirim
                </div>
              </div>
              
              <button class="book-now-btn">
                Şimdi Rezervasyon Yap
              </button>
            </div>
          </div>

          <!-- Hotel Images -->
          <div class="hotel-images">
            <div v-if="hotel.images && hotel.images.length > 0" class="images-grid">
              <div v-for="(image, index) in hotel.images.slice(0, 5)" :key="image.id" 
                   class="image-item"
                   :class="{ 'main-image': index === 0 }">
                <img :src="image.image" :alt="image.caption || hotel.name" />
              </div>
              <div v-if="hotel.images.length > 5" class="more-images">
                +{{ hotel.images.length - 5 }} fotoğraf daha
              </div>
            </div>
            <div v-else class="no-images">
              <div class="image-placeholder">
                <span class="hotel-icon">🏨</span>
                <p>Fotoğraf bulunmuyor</p>
              </div>
            </div>
          </div>

          <!-- Hotel Info Tabs -->
          <div class="hotel-tabs">
            <div class="tabs-nav">
              <button 
                :class="{ active: activeTab === 'overview' }"
                @click="onTabChange('overview')"
                class="tab-btn"
              >
                Genel Bakış
              </button>
              <button 
                :class="{ active: activeTab === 'amenities' }"
                @click="onTabChange('amenities')"
                class="tab-btn"
              >
                Özellikler
              </button>
              <button 
                :class="{ active: activeTab === 'location' }"
                @click="onTabChange('location')"
                class="tab-btn"
              >
                Konum
              </button>
              <button 
                :class="{ active: activeTab === 'reviews' }"
                @click="onTabChange('reviews')"
                class="tab-btn"
              >
                Yorumlar
              </button>
            </div>

            <div class="tab-content">
              <!-- Overview Tab -->
              <div v-if="activeTab === 'overview'" class="tab-panel">
                <div class="overview-content">
                  <h3>Açıklama</h3>
                  <p>{{ hotel.description || 'Bu otel için açıklama bulunmuyor.' }}</p>
                </div>
              </div>

              <!-- Amenities Tab -->
              <div v-if="activeTab === 'amenities'" class="tab-panel">
                <div class="amenities-content">
                  <h3>Otel Özellikleri</h3>
                  <div v-if="hotel.amenities && hotel.amenities.length > 0" class="amenities-grid">
                    <div v-for="amenity in hotel.amenities" :key="amenity.id" class="amenity-item">
                      <span class="amenity-icon">✓</span>
                      <span class="amenity-name">{{ amenity.name }}</span>
                    </div>
                  </div>
                  <p v-else class="no-amenities">Özellik bilgisi bulunmuyor.</p>
                </div>
              </div>

              <!-- Location Tab -->
              <div v-if="activeTab === 'location'" class="tab-panel">
                <div class="location-content">
                  <h3>Konum</h3>
                  <p class="address">{{ hotel.address || `${hotel.city}, ${hotel.country}` }}</p>
                  
                  <!-- Embedded Map -->
                  <div class="hotel-map-container">
                    <div 
                      ref="hotelMapContainer"
                      id="hotelMapContainer"
                      class="hotel-map"
                    ></div>
                  </div>
                  
                  <div class="location-actions">
                    <button @click="showOnMap" class="map-btn">
                      🗺️ Büyük Haritada Göster
                    </button>
                  </div>
                </div>
              </div>

              <!-- Reviews Tab -->
              <div v-if="activeTab === 'reviews'" class="tab-panel">
                <div class="reviews-content">
                  <h3>Müşteri Yorumları</h3>
                  <div class="reviews-summary">
                    <div class="rating-overview">
                      <span class="big-rating">{{ hotel.rating }}</span>
                      <div class="rating-details">
                        <div class="stars">⭐⭐⭐⭐⭐</div>
                        <div class="total-reviews">{{ hotel.total_reviews }} yorum</div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="reviews-list">
                    <p class="no-reviews">Detaylı yorumlar yakında eklenecek.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Not Found -->
        <div v-if="!hotel && !loading && !error" class="not-found">
          <h2>Otel bulunamadı</h2>
          <p>Aradığınız otel mevcut değil veya kaldırılmış olabilir.</p>
          <router-link to="/" class="home-btn">Ana Sayfaya Dön</router-link>
        </div>
      </div>
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
  name: 'HotelDetail',
  components: {
    LoginModal
  },
  data() {
    return {
      showLoginModal: false,
      hotel: null,
      activeTab: 'overview',
      hotelMap: null
    }
  },
  computed: {
    ...mapState(['currentHotel']),
    ...mapGetters(['isLoading', 'hasError', 'errorMessage', 'currentUser', 'isAuthenticated', 'userDisplayName']),
    
    loading() {
      return this.isLoading
    },
    error() {
      return this.hasError ? this.errorMessage : null
    }
  },
  methods: {
    ...mapActions(['loadHotelDetail', 'logout']),

    async fetchHotelDetail() {
      const hotelId = this.$route.params.id
      console.log('Loading hotel detail for ID:', hotelId)
      
      try {
        const hotelData = await this.loadHotelDetail(hotelId)
        this.hotel = hotelData
        console.log('Hotel data loaded:', hotelData)
      } catch (error) {
        console.error('Error loading hotel detail:', error)
      }
    },

    handleLoginSuccess(user) {
      console.log('Login successful:', user)
      // Reload hotel detail to show member prices
      this.fetchHotelDetail()
    },

    async handleLogout() {
      await this.logout()
      // Reload hotel detail to hide member prices
      this.fetchHotelDetail()
    },

    formatPrice(price) {
      return new Intl.NumberFormat('tr-TR').format(price)
    },

    showOnMap() {
      // Ana sayfadaki büyük haritaya git
      this.$router.push('/map')
    },

    initializeHotelMap() {
      // Konum sekmesi açıldığında haritayı başlat
      if (this.hotel && this.hotel.latitude && this.hotel.longitude) {
        this.$nextTick(() => {
          if (this.$refs.hotelMapContainer && !this.hotelMap) {
            const lat = parseFloat(this.hotel.latitude)
            const lng = parseFloat(this.hotel.longitude)
            
            if (!isNaN(lat) && !isNaN(lng)) {
              this.hotelMap = L.map('hotelMapContainer').setView([lat, lng], 15)
              
              L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
              }).addTo(this.hotelMap)

              // Fiyatı belirle
              const hotelPrice = this.currentUser && this.hotel.member_price_display < this.hotel.base_price 
                ? this.hotel.member_price_display 
                : this.hotel.base_price

              const priceText = this.formatPrice(hotelPrice) + ' TL'
              
              // Custom marker
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
              
              const marker = L.marker([lat, lng], { icon: customIcon }).addTo(this.hotelMap)
              
              const popupContent = `
                <div style="min-width: 150px; text-align: center;">
                  <h4 style="margin: 0 0 0.5rem 0;">${this.hotel.name}</h4>
                  <p style="margin: 0; color: #6c757d;">${this.hotel.city}, ${this.hotel.country}</p>
                </div>
              `
              
              marker.bindPopup(popupContent)
            }
          }
        })
      }
    },

    // Konum sekmesi değiştiğinde haritayı başlat
    onTabChange(tab) {
      this.activeTab = tab
      if (tab === 'location') {
        setTimeout(() => {
          this.initializeHotelMap()
        }, 100)
      }
    }
  },

  async created() {
    // Initialize auth from localStorage
    this.$store.dispatch('initializeAuth')
    await this.fetchHotelDetail()
  },

  beforeUnmount() {
    // Clean up map
    if (this.hotelMap) {
      this.hotelMap.remove()
    }
  }
}
</script>

<style scoped>
.hotel-detail-page {
  min-height: 100vh;
  background: #ffffff;
}

.header {
  background: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #e7e7e7;
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

.breadcrumb {
  font-size: 0.9rem;
}

.back-link {
  color: #006ce4;
  text-decoration: none;
}

.back-link:hover {
  text-decoration: underline;
}

.separator {
  margin: 0 0.5rem;
  color: #6c757d;
}

.current {
  color: #6c757d;
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

.main-content {
  padding: 2rem 0;
}

.hotel-header {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 2rem;
  margin-bottom: 2rem;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.hotel-name {
  font-size: 2.5rem;
  font-weight: 300;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.hotel-location {
  color: #6c757d;
  font-size: 1.1rem;
  margin: 0 0 1rem 0;
}

.hotel-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rating-score {
  font-size: 1.2rem;
  font-weight: 600;
}

.rating-text {
  color: #6c757d;
}

.hotel-pricing {
  text-align: right;
}

.member-price-notice {
  background: #fff3cd;
  color: #856404;
  padding: 0.5rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  border: 1px solid #ffeaa7;
  font-size: 0.9rem;
}

.member-pricing .member-price {
  color: #28a745;
  font-weight: bold;
  font-size: 1.5rem;
  display: block;
  margin-bottom: 0.25rem;
}

.member-pricing .base-price.crossed {
  text-decoration: line-through;
  color: #6c757d;
  font-size: 1.2rem;
}

.regular-pricing .price {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
}

.per-night {
  color: #6c757d;
  font-size: 1rem;
  margin-left: 0.5rem;
}

.discount-badge {
  background: #dc3545;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: bold;
  display: inline-block;
  margin-top: 0.5rem;
}

.book-now-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: 600;
  margin-top: 1rem;
  transition: background 0.3s;
}

.book-now-btn:hover {
  background: #218838;
}

.hotel-images {
  margin-bottom: 2rem;
}

.images-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 0.5rem;
  height: 400px;
  border-radius: 8px;
  overflow: hidden;
}

.image-item {
  position: relative;
  overflow: hidden;
}

.image-item.main-image {
  grid-row: 1 / 3;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.image-item:hover img {
  transform: scale(1.05);
}

.more-images {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 500;
}

.no-images {
  height: 300px;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-placeholder {
  text-align: center;
  color: #6c757d;
}

.image-placeholder .hotel-icon {
  font-size: 4rem;
  display: block;
  margin-bottom: 1rem;
}

.hotel-tabs {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.tabs-nav {
  display: flex;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.tab-btn {
  flex: 1;
  padding: 1rem;
  border: none;
  background: transparent;
  cursor: pointer;
  font-weight: 500;
  color: #6c757d;
  transition: all 0.3s;
}

.tab-btn:hover {
  background: #e9ecef;
}

.tab-btn.active {
  background: white;
  color: #006ce4;
  border-bottom: 2px solid #006ce4;
}

.tab-content {
  padding: 2rem;
}

.tab-panel h3 {
  margin-top: 0;
  color: #2c3e50;
}

.amenities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.amenity-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.amenity-icon {
  color: #28a745;
  font-weight: bold;
}

.hotel-map-container {
  margin: 1rem 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.hotel-map {
  height: 300px;
  width: 100%;
}

.location-actions {
  margin: 1.5rem 0;
  text-align: center;
}

.map-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.3s;
}

.map-btn:hover {
  background: #218838;
}

.reviews-summary {
  margin-bottom: 2rem;
}

.rating-overview {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.big-rating {
  font-size: 3rem;
  font-weight: bold;
  color: #2c3e50;
}

.rating-details .stars {
  font-size: 1.2rem;
  margin-bottom: 0.25rem;
}

.alert {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  border-left: 4px solid #007bff;
}

.alert-info {
  border-left-color: #17a2b8;
  color: #0c5460;
}

.alert-danger {
  border-left-color: #dc3545;
  color: #721c24;
}

.retry-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 1rem;
}

.not-found {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.home-btn {
  background: #006ce4;
  color: white;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  display: inline-block;
  margin-top: 1rem;
  transition: background 0.3s;
}

.home-btn:hover {
  background: #0056b3;
  text-decoration: none;
  color: white;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }

  .hotel-header {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .hotel-pricing {
    text-align: center;
  }

  .images-grid {
    grid-template-columns: 1fr;
    grid-template-rows: 200px 200px 200px;
    height: auto;
  }

  .image-item.main-image {
    grid-row: 1;
  }

  .tabs-nav {
    flex-direction: column;
  }

  .tab-btn {
    text-align: left;
  }

  .amenities-grid {
    grid-template-columns: 1fr;
  }
}
</style>