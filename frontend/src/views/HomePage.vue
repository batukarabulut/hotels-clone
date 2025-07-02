<!-- frontend/src/views/HomePage.vue -->
<template>
    <div class="home-page">
        <!-- Header -->
        <header class="header">
            <div class="container">
                <div class="header-content">
                    <div class="logo">
                        <span class="logo-icon">🏨</span>
                        <span class="logo-text">Hotels.com</span>
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
            <!-- Hero Section with Background -->
            <div class="hero-section" :style="heroBackgroundStyle">
                <div class="container">
                    <div class="hero-content">
                        <h1 class="hero-title">Sırada neresi var?</h1>

                        <!-- Search Form -->
                        <div class="search-form-container">
                            <form @submit.prevent="searchHotels" class="search-form">
                                <div class="search-fields">
                                    <div class="field-group">
                                        <div class="input-wrapper">
                                            <span class="input-icon">📍</span>
                                            <input v-model="searchQuery.destination" type="text" placeholder="Nereye?"
                                                class="search-input">
                                        </div>
                                    </div>

                                    <div class="field-group">
                                        <div class="input-wrapper">
                                            <span class="input-icon">📅</span>
                                            <input v-model="searchQuery.checkIn" type="date" class="search-input">
                                            <span class="date-separator">-</span>
                                            <input v-model="searchQuery.checkOut" type="date" class="search-input">
                                        </div>
                                    </div>

                                    <div class="field-group">
                                        <div class="input-wrapper">
                                            <span class="input-icon">👥</span>
                                            <select v-model="searchQuery.guests" class="search-input">
                                                <option value="1">1 misafir, 1 oda</option>
                                                <option value="2">2 misafir, 1 oda</option>
                                                <option value="3">3 misafir, 1 oda</option>
                                                <option value="4">4 misafir, 1 oda</option>
                                            </select>
                                        </div>
                                    </div>

                                    <button type="submit" class="search-btn">
                                        Ara
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Weekend Hotels Section -->
            <div class="hotels-section">
                <div class="container">
                    <div v-if="loading" class="alert alert-info">
                        Veriler yükleniyor...
                    </div>

                    <div v-if="error" class="alert alert-danger">
                        {{ error }}
                    </div>

                    <div v-if="weekendHotels.length > 0">
                        <div class="section-header">
                            <h2>Bu Hafta Sonu İçin Öneriler</h2>
                            <button @click="showOnMap" class="map-btn">
                                <span class="map-icon">📍</span>
                                Haritada göster
                            </button>
                        </div>

                        <div class="hotels-grid">
                            <div v-for="hotel in weekendHotels" :key="hotel.id" class="hotel-card-wrapper">
                                <div class="hotel-card" @click="viewHotelDetail(hotel.id)">
                                    <div class="hotel-image">
                                        <div class="image-placeholder">
                                            <span class="hotel-icon">🏨</span>
                                        </div>
                                    </div>

                                    <div class="hotel-info">
                                        <h3 class="hotel-name">{{ hotel.name }}</h3>
                                        <p class="hotel-location">{{ hotel.city }}</p>

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

                    <div v-else-if="!loading" class="no-hotels">
                        <p>Henüz hotel verisi yok.</p>
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
        name: 'HomePage',
        components: {
            LoginModal
        },
        data() {
            return {
                showLoginModal: false,
                searchQuery: {
                    destination: '',
                    checkIn: this.getNextWeekendStart(),
                    checkOut: this.getNextWeekendEnd(),
                    guests: '2'
                }
            }
        },
        computed: {
            ...mapState(['weekendHotels']),
            ...mapGetters(['isLoading', 'hasError', 'errorMessage', 'currentUser', 'isAuthenticated', 'userDisplayName']),
            heroBackgroundStyle() {
                return {
                    backgroundImage: `url('/images/hero-bg.jpg')`
                }
            },
            loading() {
                return this.isLoading
            },
            error() {
                return this.hasError ? this.errorMessage : null
            }
        },
        methods: {
            ...mapActions(['loadWeekendHotels', 'logout']),

            getNextWeekendStart() {
                const today = new Date()
                const saturday = new Date(today)
                saturday.setDate(today.getDate() + (6 - today.getDay()))
                return saturday.toISOString().split('T')[0]
            },

            getNextWeekendEnd() {
                const today = new Date()
                const sunday = new Date(today)
                sunday.setDate(today.getDate() + (7 - today.getDay()))
                return sunday.toISOString().split('T')[0]
            },

            async searchHotels() {
                // Navigate to search results page with query parameters
                this.$router.push({
                    name: 'SearchResults',
                    query: {
                        destination: this.searchQuery.destination,
                        checkIn: this.searchQuery.checkIn,
                        checkOut: this.searchQuery.checkOut,
                        guests: this.searchQuery.guests
                    }
                })
            },

            showOnMap() {
                this.$router.push({
                    path: '/map',
                    query: {
                        view: 'weekend',
                        checkIn: this.searchQuery.checkIn,
                        checkOut: this.searchQuery.checkOut,
                        guests: this.searchQuery.guests
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
                // Reload weekend hotels to show member prices
                this.loadWeekendHotels()
            },

            async handleLogout() {
                await this.logout()
                // Reload weekend hotels to hide member prices
                this.loadWeekendHotels()
            },

            formatPrice(price) {
                return new Intl.NumberFormat('tr-TR').format(price)
            }
        },
        async created() {
            // Initialize auth from localStorage
            this.$store.dispatch('initializeAuth')
            await this.loadWeekendHotels()
        }
    }
</script>

<style scoped>
    .home-page {
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

    .logo {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .logo-icon {
        font-size: 1.5rem;
    }

    .logo-text {
        font-size: 1.5rem;
        font-weight: bold;
        color: #c73939;
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
        background: #ffffff;
    }

    .hero-section {
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        min-height: 400px;
        display: flex;
        align-items: center;
        position: relative;
    }

    .hero-content {
        text-align: center;
        width: 100%;
    }

    .hero-title {
        color: white;
        font-size: 3rem;
        font-weight: 300;
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }

    .search-form-container {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        max-width: 1100px;
        width: 95%;
        margin: 0 auto;
    }

    .search-fields {
        display: grid;
        grid-template-columns: 2.5fr 2.5fr 1.5fr auto;
        gap: 0.75rem;
        align-items: end;
        width: 100%;
    }

    .field-group {
        display: flex;
        flex-direction: column;
        min-width: 0;
    }

    .input-wrapper {
        display: flex;
        align-items: center;
        border: 2px solid #e7e7e7;
        border-radius: 4px;
        background: white;
        padding: 0.75rem;
        transition: border-color 0.3s;
        min-height: 50px;
    }

    .input-wrapper:focus-within {
        border-color: #006ce4;
    }

    .input-icon {
        margin-right: 0.5rem;
        font-size: 1.2rem;
        flex-shrink: 0;
    }

    .search-input {
        border: none;
        outline: none;
        flex: 1;
        padding: 0.5rem;
        font-size: 1rem;
        min-width: 0;
    }

    .date-separator {
        margin: 0 0.5rem;
        color: #666;
        flex-shrink: 0;
    }

    .search-btn {
        background: #006ce4;
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 600;
        font-size: 1rem;
        transition: background 0.3s;
        height: 50px;
        white-space: nowrap;
        min-width: 100px;
    }

    .search-btn:hover {
        background: #0056b3;
    }

    .hotels-section {
        padding: 3rem 0;
        background: #f8f9fa;
    }

    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }

    .section-header h2 {
        color: #2c3e50;
        font-size: 2rem;
        font-weight: 300;
        margin: 0;
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

    .no-hotels {
        text-align: center;
        color: #6c757d;
        padding: 3rem;
    }

    @media (max-width: 768px) {
        .search-form-container {
            max-width: 95%;
            padding: 1rem;
        }

        .search-fields {
            grid-template-columns: 1fr;
            gap: 0.5rem;
        }

        .search-btn {
            width: 100%;
            margin-top: 0.5rem;
        }

        .hero-title {
            font-size: 2rem;
        }

        .section-header {
            flex-direction: column;
            gap: 1rem;
            align-items: stretch;
        }

        .header-content {
            flex-direction: column;
            gap: 1rem;
        }

        .hotels-grid {
            grid-template-columns: 1fr;
        }
    }
</style>