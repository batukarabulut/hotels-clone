// frontend/src/store/index.js
import { createStore } from 'vuex'

export default createStore({
  state: {
    // Auth state
    currentUser: null,
    authToken: null,
    isAuthenticated: false,
    
    // Hotels state
    weekendHotels: [],
    searchResults: [],
    currentHotel: null,
    
    // UI state
    loading: false,
    error: null,
    
    // Search state
    lastSearchQuery: null
  },

  mutations: {
    // Auth mutations
    SET_USER(state, user) {
      state.currentUser = user
      state.isAuthenticated = !!user
    },
    
    SET_AUTH_TOKEN(state, token) {
      state.authToken = token
      if (token) {
        localStorage.setItem('authToken', token)
      } else {
        localStorage.removeItem('authToken')
      }
    },
    
    // Hotels mutations
    SET_WEEKEND_HOTELS(state, hotels) {
      state.weekendHotels = hotels
    },
    
    SET_SEARCH_RESULTS(state, results) {
      state.searchResults = results
    },
    
    SET_CURRENT_HOTEL(state, hotel) {
      state.currentHotel = hotel
    },
    
    // UI mutations
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    
    SET_ERROR(state, error) {
      state.error = error
    },
    
    CLEAR_ERROR(state) {
      state.error = null
    },
    
    // Search mutations
    SET_LAST_SEARCH_QUERY(state, query) {
      state.lastSearchQuery = query
    }
  },

  actions: {
    // Initialize auth from localStorage
    initializeAuth({ commit }) {
      const token = localStorage.getItem('authToken')
      const userStr = localStorage.getItem('currentUser')
      
      if (token && userStr) {
        try {
          const user = JSON.parse(userStr)
          commit('SET_AUTH_TOKEN', token)
          commit('SET_USER', user)
        } catch (error) {
          console.error('Error parsing stored user data:', error)
          localStorage.removeItem('authToken')
          localStorage.removeItem('currentUser')
        }
      }
    },

    // Auth actions
    async login({ commit }, credentials) {
      try {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        const response = await fetch('http://127.0.0.1:8000/api/auth/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(credentials)
        })
        
        const data = await response.json()
        
        if (response.ok) {
          const { user, access_token } = data
          commit('SET_USER', user)
          commit('SET_AUTH_TOKEN', access_token)
          localStorage.setItem('currentUser', JSON.stringify(user))
          return user
        } else {
          throw new Error(data.error || 'Giriş yapılırken hata oluştu')
        }
        
      } catch (error) {
        const errorMessage = error.message || 'Giriş yapılırken hata oluştu'
        commit('SET_ERROR', errorMessage)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async register({ commit }, userData) {
      try {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        console.log('DEBUG: Registering user with data:', userData)
        
        const response = await fetch('http://127.0.0.1:8000/api/auth/register/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(userData)
        })
        
        const data = await response.json()
        console.log('DEBUG: Registration response:', data)
        
        if (response.ok) {
          const { user, access_token } = data
          commit('SET_USER', user)
          commit('SET_AUTH_TOKEN', access_token)
          localStorage.setItem('currentUser', JSON.stringify(user))
          return user
        } else {
          throw new Error(data.error || 'Kayıt olurken hata oluştu')
        }
        
      } catch (error) {
        console.error('Registration error details:', error)
        const errorMessage = error.message || 'Kayıt olurken hata oluştu'
        commit('SET_ERROR', errorMessage)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    // UPDATED: Google OAuth artık aynı /auth/login/ endpoint'ini kullanıyor
    async googleLogin({ commit }, { credential }) {
      try {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        // JWT token'ı decode et
        const payload = JSON.parse(atob(credential.split('.')[1]))
        
        // Google data'sını backend'in beklediği format'ta hazırla
        const googleData = {
          email: payload.email,
          name: payload.name,
          given_name: payload.given_name,
          family_name: payload.family_name,
          picture: payload.picture
        }
        
        console.log('Google OAuth data being sent:', googleData)
        
        // Backend'in beklediği format: google_data field'ı ile login endpoint'ine
        const response = await fetch('http://127.0.0.1:8000/api/auth/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            google_data: googleData
          })
        })

        const data = await response.json()
        
        if (response.ok) {
          const { user } = data
          commit('SET_USER', user)
          // Note: JWT token yok çünkü Django session kullanıyor
          localStorage.setItem('currentUser', JSON.stringify(user))
          console.log('Google login successful, user saved to store:', user)
          return user
        } else {
          throw new Error(data.error || 'Google ile giriş başarısız')
        }
        
      } catch (error) {
        console.error('Google OAuth error details:', error)
        const errorMessage = error.message || 'Google ile giriş sırasında hata oluştu'
        commit('SET_ERROR', errorMessage)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async logout({ commit }) {
      try {
        await fetch('http://127.0.0.1:8000/api/auth/logout/', {
          method: 'POST',
          credentials: 'include'
        })
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        commit('SET_USER', null)
        commit('SET_AUTH_TOKEN', null)
        localStorage.removeItem('currentUser')
        localStorage.removeItem('authToken')
      }
    },

    // Hotels actions
    async loadWeekendHotels({ commit, state }) {
      try {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        // Get next weekend dates
        const today = new Date()
        const saturday = new Date(today)
        saturday.setDate(today.getDate() + (6 - today.getDay()))
        const sunday = new Date(today)
        sunday.setDate(today.getDate() + (7 - today.getDay()))
        
        // GET request için URL parametreleri olarak gönder
        const params = new URLSearchParams({
          check_in: saturday.toISOString().split('T')[0],
          check_out: sunday.toISOString().split('T')[0],
          country: state.currentUser?.country || 'Turkey'
        })
        
        const response = await fetch(`http://127.0.0.1:8000/api/hotels/weekend/?${params}`, {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        const data = await response.json()
        commit('SET_WEEKEND_HOTELS', data)
        
      } catch (error) {
        const errorMessage = error.message || 'Oteller yüklenirken hata oluştu'
        commit('SET_ERROR', errorMessage)
        console.error('Load weekend hotels error:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async searchHotels({ commit }, searchQuery) {
      try {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        commit('SET_LAST_SEARCH_QUERY', searchQuery)
        
        // GET request için URL parametreleri olarak gönder
        const params = new URLSearchParams({
          destination: searchQuery.destination,
          check_in: searchQuery.checkIn,
          check_out: searchQuery.checkOut,
          guests: searchQuery.guests
        })
        
        const response = await fetch(`http://127.0.0.1:8000/api/hotels/search/?${params}`, {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        const data = await response.json()
        commit('SET_SEARCH_RESULTS', data)
        
        return data
      } catch (error) {
        const errorMessage = error.message || 'Arama sırasında hata oluştu'
        commit('SET_ERROR', errorMessage)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async loadHotelDetail({ commit }, hotelId) {
      try {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        const response = await fetch(`http://127.0.0.1:8000/api/hotels/${hotelId}/`, {
          credentials: 'include'
        })
        
        const data = await response.json()
        commit('SET_CURRENT_HOTEL', data)
        
        return data
      } catch (error) {
        const errorMessage = error.message || 'Otel detayları yüklenirken hata oluştu'
        commit('SET_ERROR', errorMessage)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    }
  },

  getters: {
    isLoading: state => state.loading,
    hasError: state => !!state.error,
    errorMessage: state => state.error,
    currentUser: state => state.currentUser,
    isAuthenticated: state => state.isAuthenticated,
    weekendHotels: state => state.weekendHotels,
    searchResults: state => state.searchResults,
    currentHotel: state => state.currentHotel,
    lastSearchQuery: state => state.lastSearchQuery,
    
    // ADDED: Display name getter tam istediğiniz gibi
    userDisplayName: state => {
      if (!state.currentUser) return null
      
      // Öncelik sırası:
      // 1. Google'dan gelen first_name 
      // 2. Email'in @ öncesi kısmı
      // 3. Username
      // 4. "Kullanıcı" fallback
      if (state.currentUser.first_name && state.currentUser.first_name.trim()) {
        return state.currentUser.first_name
      } else if (state.currentUser.email) {
        return state.currentUser.email.split('@')[0]
      } else if (state.currentUser.username) {
        return state.currentUser.username
      } else {
        return 'Kullanıcı'
      }
    }
  }
})