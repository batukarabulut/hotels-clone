// frontend/src/services/apiService.js
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:8000/api'

// Axios default configuration
axios.defaults.headers.common['Content-Type'] = 'application/json'

// Handle CORS and credentials
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor for debugging
apiClient.interceptors.request.use(
  config => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  error => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  response => {
    console.log('API Response:', response.status, response.config.url)
    return response
  },
  error => {
    console.error('API Response Error:', error.response?.status, error.response?.data)
    return Promise.reject(error)
  }
)

export default {
  // Hotel endpoints
  hotels: {
    // Get weekend hotels for homepage
    getWeekendHotels() {
      return apiClient.get('/hotels/weekend/')
    },
    
    // Search hotels with filters
    searchHotels(params = {}) {
      return apiClient.get('/hotels/search/', { params })
    },
    
    // Get hotel detail by ID
    getHotelDetail(id) {
      return apiClient.get(`/hotels/${id}/`)
    },
    
    // Get map data for hotels
    getMapData(view = null) {
      const params = view ? { view } : {}
      return apiClient.get('/hotels/map/', { params })
    }
  },
  
  // Auth endpoints
  auth: {
    login(credentials) {
      return apiClient.post('/auth/login/', credentials)
    },
    
    register(userData) {
      return apiClient.post('/auth/register/', userData)
    },
    
    logout() {
      return apiClient.post('/auth/logout/')
    },
    
    getProfile() {
      return apiClient.get('/auth/profile/')
    }
  }
}