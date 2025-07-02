<!-- frontend/src/views/SearchResults.vue -->
<template>
  <div class="search-results-page">
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
          <div class="search-info">
            <span class="search-query">{{ searchQueryText }}</span>
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
        <!-- Back to Home -->
        <div class="breadcrumb">
          <router-link to="/" class="back-link">← Ana Sayfa</router-link>
          <span class="separator">/</span>
          <span class="current">Arama Sonuçları</span>
        </div>

        <!-- Results Header -->
        <div class="results-header">
          <h1>{{ searchTitle }}</h1>
          <div class="results-actions">
            <button @click="showOnMap" class="map-btn">
              <span class="map-icon">📍</span>
              Haritada göster
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="alert alert-info">
          Arama yapılıyor...
        </div>

        <!-- Error State -->
        <div v-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <!-- Results -->
        <div v-if="searchResults.length > 0" class="search-results">
          <div class="results-count">
            {{ searchResults.length }} otel bulundu
          </div>

          <div class="hotels-grid">
            <div v-for="hotel in searchResults" :key="hotel.id" class="hotel-card-wrapper">
              <div class="hotel-card" @click="viewHotelDetail(hotel.id)">
                <div class="hotel-image">
                  <div class="image-placeholder">
                    <span class="hotel-icon">🏨</span>
                  </div>
                </div>

                <div class="hotel-info">
                  <h3 class="hotel-name">{{ hotel.name }}</h3>
                  <p class="hotel-location">{{ hotel.city }}, {{ hotel.country }}</p>

                  <!-- Amenities tags -->
                  <div v-if="hotel.amenities && hotel.amenities.length > 0" class="amenities">
                    <span v-for="amenity in hotel.amenities.slice(0, 3)" :key="amenity.id"
                        class="amenity-tag">
                      {{ amenity.name }}
                    </span>
                    <span v-if="hotel.amenities.length > 3" class="amenities-more">
                      +{{ hotel.amenities.length - 3 }} daha
                    </span>
                  </div>

                  <!-- Pricing Logic -->
                  <div class="pricing-section">
                    <div v-if="!currentUser && hotel.is_flagged" class="member-price-notice">
                      💎 Üye fiyatı için giriş yapın
                    </div>

                    <div class="price-info">
                      <div v-if="currentUser && hotel.member_price_display < hotel.base_price"
                          class="member-pricing">
                        <span class="member-price">
                          Üye Fiyatı: {{ formatPrice(hotel.member_price_display) }} TL
                        </span>
                        <span class="base-price crossed">
                          {{ formatPrice(hotel.base_price) }} TL
                        </span>
                      </div>
                      <div v-else class="regular-pricing">
                        <span class="price">{{ formatPrice(hotel.base_price) }} TL</span>
                      </div>

                      <div v-if="hotel.special_discount > 0" class="discount-badge">
                        %{{ hotel.special_discount }} indirim
                      </div>
                    </div>
                  </div>

                  <div class="hotel-rating">
                    ⭐ {{ hotel.rating }}/10 ({{ hotel.total_reviews }} yorum)
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- No Results -->
        <div v-else-if="!loading && !error" class="no-results">
          <div class="no-results-content">
            <h3>Aradığınız kriterlerde otel bulunamadı</h3>
            <p>Farklı tarihler veya lokasyonlar deneyebilirsiniz.</p>
            <router-link to="/" class="home-btn">Ana Sayfaya Dön</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Login Modal -->
    <LoginModal :showModal="showLoginModal" @close="showLoginModal = false" @login-success="handleLoginSuccess" />
  </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from 'vuex'
import LoginModal from '@/components/LoginModal.vue'

export default {
  name: 'SearchResults',
  components: {
    LoginModal
  },
  data() {
    return {
      showLoginModal: false
    }
  },
  computed: {
    ...mapState(['searchResults']),
    ...mapGetters(['isLoading', 'hasError', 'errorMessage', 'currentUser', 'isAuthenticated', 'userDisplayName']),
    
    loading() {
      return this.isLoading
    },
    error() {
      return this.hasError ? this.errorMessage : null
    },
    searchQueryText() {
      const destination = this.$route.query.destination
      if (destination) {
        return `"${destination}" için sonuçlar`
      }
      return 'Arama Sonuçları'
    },
    searchTitle() {
      const destination = this.$route.query.destination
      const checkIn = this.$route.query.checkIn
      const checkOut = this.$route.query.checkOut
      const guests = this.$route.query.guests

      let title = destination ? `${destination} Otelleri` : 'Arama Sonuçları'
      
      if (checkIn && checkOut) {
        const inDate = new Date(checkIn).toLocaleDateString('tr-TR')
        const outDate = new Date(checkOut).toLocaleDateString('tr-TR')
        title += ` | ${inDate} - ${outDate}`
      }
      
      if (guests) {
        title += ` | ${guests} misafir`
      }

      return title
    }
  },
  methods: {
    ...mapActions(['searchHotels', 'logout']),

    async performSearch() {
      const searchQuery = {
        destination: this.$route.query.destination || '',
        checkIn: this.$route.query.checkIn || '',
        checkOut: this.$route.query.checkOut || '',
        guests: this.$route.query.guests || '2'
      }

      try {
        await this.searchHotels(searchQuery)
      } catch (error) {
        console.error('Search error:', error)
      }
    },

    showOnMap() {
      this.$router.push({
        path: '/map',
        query: {
          view: 'search',
          ...this.$route.query
        }
      })
    },

    viewHotelDetail(hotelId) {
      this.$router.push({
        name: 'HotelDetail',
        params: { id: hotelId }
      })
    },

    handleLoginSuccess(user) {
      console.log('Login successful:', user)
      // Reload search results to show member prices
      this.performSearch()
    },

    async handleLogout() {
      await this.logout()
      // Reload search results to hide member prices
      this.performSearch()
    },

    formatPrice(price) {
      return new Intl.NumberFormat('tr-TR').format(price)
    }
  },

  async created() {
    // Initialize auth from localStorage
    this.$store.dispatch('initializeAuth')
    // Perform search with query parameters
    await this.performSearch()
  },

  watch: {
    // Watch for query changes and re-search
    '$route.query': {
      handler() {
        this.performSearch()
      },
      deep: true
    }
  }
}
</script>

<style scoped>
.search-results-page {
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

.search-info {
  flex: 1;
  text-align: center;
}

.search-query {
  color: #2c3e50;
  font-weight: 500;
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

.main-content {
  padding: 2rem 0;
  background: #f8f9fa;
  min-height: calc(100vh - 80px);
}

.breadcrumb {
  margin-bottom: 1.5rem;
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

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.results-header h1 {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 300;
  margin: 0;
}

.results-actions {
  display: flex;
  gap: 1rem;
}

.map-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.3s;
}

.map-btn:hover {
  background: #218838;
}

.search-results {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.results-count {
  color: #2c3e50;
  font-weight: 500;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.hotels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
}

.hotel-card-wrapper {
  display: flex;
}

.hotel-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  width: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #e9ecef;
}

.hotel-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.hotel-image {
  height: 200px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-placeholder {
  color: white;
  font-size: 3rem;
  opacity: 0.8;
}

.hotel-info {
  padding: 1.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.hotel-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.hotel-location {
  color: #6c757d;
  margin-bottom: 1rem;
}

.amenities {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.amenity-tag {
  background: #e9ecef;
  color: #495057;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.amenities-more {
  color: #6c757d;
  font-size: 0.8rem;
  font-style: italic;
}

.pricing-section {
  margin-bottom: 1rem;
  margin-top: auto;
}

.member-price-notice {
  background: #fff3cd;
  color: #856404;
  padding: 0.5rem;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  border: 1px solid #ffeaa7;
  font-size: 0.9rem;
  text-align: center;
}

.member-pricing .member-price {
  color: #28a745;
  font-weight: bold;
  font-size: 1.2rem;
  display: block;
}

.member-pricing .base-price.crossed {
  text-decoration: line-through;
  color: #6c757d;
  font-size: 1rem;
}

.regular-pricing .price {
  font-size: 1.3rem;
  font-weight: bold;
  color: #2c3e50;
}

.discount-badge {
  background: #dc3545;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  display: inline-block;
  margin-top: 0.5rem;
}

.hotel-rating {
  color: #6c757d;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
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

.no-results {
  background: white;
  border-radius: 8px;
  padding: 3rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.no-results-content h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.no-results-content p {
  color: #6c757d;
  margin-bottom: 2rem;
}

.home-btn {
  background: #006ce4;
  color: white;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  display: inline-block;
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

  .search-info {
    order: -1;
  }

  .results-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .hotels-grid {
    grid-template-columns: 1fr;
  }
}
</style>