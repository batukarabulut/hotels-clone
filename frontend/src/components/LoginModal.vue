<!-- frontend/src/components/LoginModal.vue -->
<template>
  <div v-if="showModal" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ isLoginMode ? 'Giriş Yap' : 'Kayıt Ol' }}</h2>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>
      
      <div class="modal-body">
        <!-- Google Login First (Most Prominent) -->
        <div class="google-login-section">
          <div id="google-signin-button" ref="googleButton"></div>
          
          <!-- Fallback Google Button -->
          <button 
            v-if="!googleLoaded" 
            @click="handleGoogleLoginFallback" 
            class="google-btn" 
            :disabled="loading"
          >
            <svg class="google-icon" viewBox="0 0 24 24" width="20" height="20">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Google ile {{ isLoginMode ? 'Giriş Yap' : 'Kayıt Ol' }}
          </button>
        </div>
        
        <div class="divider">
          <span>veya</span>
        </div>
        
        <!-- Email/Password Login -->
        <form v-if="isLoginMode" @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label for="email">E-posta</label>
            <input
              id="email"
              v-model="loginForm.email"
              type="email"
              required
              class="form-input"
              placeholder="E-posta adresiniz"
            >
          </div>
          
          <div class="form-group">
            <label for="password">Şifre</label>
            <input
              id="password"
              v-model="loginForm.password"
              type="password"
              required
              class="form-input"
              placeholder="Şifreniz"
            >
          </div>
          
          <button 
            type="submit" 
            class="submit-btn secondary"
            :disabled="loading"
          >
            {{ loading ? 'Giriş yapılıyor...' : 'E-posta ile Giriş' }}
          </button>
        </form>
        
        <!-- Email/Password Register -->
        <form v-else @submit.prevent="handleRegister" class="auth-form">
          <div class="form-row">
            <div class="form-group">
              <label for="first_name">Ad</label>
              <input
                id="first_name"
                v-model="registerForm.first_name"
                type="text"
                required
                class="form-input"
                placeholder="Adınız"
              >
            </div>
            
            <div class="form-group">
              <label for="last_name">Soyad</label>
              <input
                id="last_name"
                v-model="registerForm.last_name"
                type="text"
                required
                class="form-input"
                placeholder="Soyadınız"
              >
            </div>
          </div>
          
          <div class="form-group">
            <label for="reg_email">E-posta</label>
            <input
              id="reg_email"
              v-model="registerForm.email"
              type="email"
              required
              class="form-input"
              placeholder="E-posta adresiniz"
            >
          </div>
          
          <div class="form-group">
            <label for="reg_password">Şifre</label>
            <input
              id="reg_password"
              v-model="registerForm.password"
              type="password"
              required
              class="form-input"
              placeholder="En az 8 karakter, 1 rakam ve 1 özel karakter"
              @input="validatePassword"
            >
            <div v-if="passwordErrors.length > 0" class="password-errors">
              <small v-for="error in passwordErrors" :key="error" class="error-text">
                {{ error }}
              </small>
            </div>
          </div>
          
          <div class="form-group">
            <label for="confirm_password">Şifre Tekrar</label>
            <input
              id="confirm_password"
              v-model="registerForm.confirmPassword"
              type="password"
              required
              class="form-input"
              placeholder="Şifrenizi tekrar girin"
            >
            <small v-if="registerForm.confirmPassword && registerForm.password !== registerForm.confirmPassword" class="error-text">
              Şifreler eşleşmiyor
            </small>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="country">Ülke</label>
              <select
                id="country"
                v-model="registerForm.country"
                required
                class="form-input"
              >
                <option value="">Ülke seçin</option>
                <option value="Turkey">Türkiye</option>
                <option value="Germany">Almanya</option>
                <option value="France">Fransa</option>
                <option value="Italy">İtalya</option>
                <option value="Spain">İspanya</option>
                <option value="United Kingdom">İngiltere</option>
                <option value="Netherlands">Hollanda</option>
                <option value="Greece">Yunanistan</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="city">Şehir</label>
              <input
                id="city"
                v-model="registerForm.city"
                type="text"
                required
                class="form-input"
                placeholder="Şehir"
              >
            </div>
          </div>
          
          <button 
            type="submit" 
            class="submit-btn secondary"
            :disabled="loading || !isFormValid"
          >
            {{ loading ? 'Kayıt oluşturuluyor...' : 'E-posta ile Kayıt Ol' }}
          </button>
        </form>
        
        <!-- Switch Mode -->
        <div class="mode-switch">
          <span v-if="isLoginMode">
            Hesabınız yok mu? 
            <button type="button" @click="switchMode" class="link-btn">Kayıt olun</button>
          </span>
          <span v-else>
            Zaten hesabınız var mı? 
            <button type="button" @click="switchMode" class="link-btn">Giriş yapın</button>
          </span>
        </div>
        
        <!-- Error Display -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'LoginModal',
  props: {
    showModal: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'login-success'],
  data() {
    return {
      isLoginMode: true,
      googleLoaded: false,
      // Bu kısmı gerçek Google Client ID ile değiştirin
      googleClientId: process.env.VUE_APP_GOOGLE_CLIENT_ID || '123456789-abcdefg.apps.googleusercontent.com',
      loginForm: {
        email: '',
        password: ''
      },
      registerForm: {
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        confirmPassword: '',
        country: '',
        city: '',
        photo: null
      },
      passwordErrors: []
    }
  },
  computed: {
    ...mapGetters(['isLoading', 'errorMessage']),
    loading() {
      return this.isLoading
    },
    error() {
      return this.errorMessage
    },
    isFormValid() {
      if (this.isLoginMode) {
        return this.loginForm.email && this.loginForm.password
      } else {
        return (
          this.registerForm.first_name &&
          this.registerForm.last_name &&
          this.registerForm.email &&
          this.registerForm.password &&
          this.registerForm.confirmPassword &&
          this.registerForm.country &&
          this.registerForm.city &&
          this.registerForm.password === this.registerForm.confirmPassword &&
          this.passwordErrors.length === 0
        )
      }
    }
  },
  watch: {
    showModal(newVal) {
      if (newVal) {
        this.$nextTick(() => {
          this.initializeGoogleSignIn()
        })
      }
    }
  },
  methods: {
    ...mapActions(['login', 'register', 'googleLogin']),
    
    closeModal() {
      this.$emit('close')
      this.resetForms()
    },
    
    switchMode() {
      this.isLoginMode = !this.isLoginMode
      this.resetForms()
      // Reinitialize Google button for new mode
      this.$nextTick(() => {
        this.initializeGoogleSignIn()
      })
    },
    
    resetForms() {
      this.loginForm = { email: '', password: '' }
      this.registerForm = {
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        confirmPassword: '',
        country: '',
        city: '',
        photo: null
      }
      this.passwordErrors = []
    },
    
    async handleLogin() {
      try {
        const user = await this.login(this.loginForm)
        this.$emit('login-success', user)
        this.closeModal()
      } catch (error) {
        console.error('Login failed:', error)
      }
    },
    
    async handleRegister() {
      try {
        const user = await this.register({
          email: this.registerForm.email,
          password: this.registerForm.password,
          first_name: this.registerForm.first_name,
          last_name: this.registerForm.last_name,
          country: this.registerForm.country,
          city: this.registerForm.city
        })
        
        this.$emit('login-success', user)
        this.closeModal()
      } catch (error) {
        console.error('Registration error:', error)
      }
    },

    initializeGoogleSignIn() {
      // Load Google Identity Services
      if (!window.google) {
        this.loadGoogleScript()
        return
      }

      try {
        window.google.accounts.id.initialize({
          client_id: this.googleClientId,
          callback: this.handleGoogleResponse,
          auto_select: false,
          cancel_on_tap_outside: true
        })

        // Render the button
        if (this.$refs.googleButton) {
          window.google.accounts.id.renderButton(
            this.$refs.googleButton,
            {
              theme: 'outline',
              size: 'large',
              type: 'standard',
              text: this.isLoginMode ? 'signin_with' : 'signup_with',
              width: '100%'
            }
          )
          this.googleLoaded = true
        }
      } catch (error) {
        console.error('Google Sign-In initialization failed:', error)
        this.googleLoaded = false
      }
    },

    loadGoogleScript() {
      if (document.getElementById('google-script')) return

      const script = document.createElement('script')
      script.id = 'google-script'
      script.src = 'https://accounts.google.com/gsi/client'
      script.async = true
      script.defer = true
      script.onload = () => {
        this.initializeGoogleSignIn()
      }
      script.onerror = () => {
        console.error('Google Script yüklenemedi')
        this.googleLoaded = false
      }
      document.head.appendChild(script)
    },

    async handleGoogleResponse(response) {
      try {
        console.log('Google response received:', response)
        
        // Use the Vuex store action for Google login
        const user = await this.googleLogin({
          credential: response.credential
        })
        
        console.log('Google authentication successful:', user)
        this.$emit('login-success', user)
        this.closeModal()
        
      } catch (error) {
        console.error('Google authentication error:', error)
        alert(error.message || 'Google ile giriş sırasında hata oluştu')
      }
    },

    handleGoogleLoginFallback() {
      // Fallback for when Google script doesn't load
      alert('Google Sign-In yükleniyor... Lütfen biraz bekleyip tekrar deneyin.')
      this.loadGoogleScript()
    },
    
    handlePhotoUpload(event) {
      const file = event.target.files[0]
      if (file) {
        this.registerForm.photo = file
      }
    },
    
    validatePassword() {
      const password = this.registerForm.password
      this.passwordErrors = []
      
      if (password.length < 8) {
        this.passwordErrors.push('Şifre en az 8 karakter olmalı')
      }
      
      if (!/\d/.test(password)) {
        this.passwordErrors.push('Şifre en az 1 rakam içermeli')
      }
      
      if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        this.passwordErrors.push('Şifre en az 1 özel karakter içermeli')
      }
    }
  },

  mounted() {
    if (this.showModal) {
      this.initializeGoogleSignIn()
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  padding: 1.5rem;
}

/* Google Sign-In Section */
.google-login-section {
  margin-bottom: 1rem;
}

#google-signin-button {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.google-btn {
  width: 100%;
  background: #ffffff;
  color: #3c4043;
  border: 1px solid #dadce0;
  border-radius: 4px;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.google-btn:hover {
  background: #f8f9fa;
  border-color: #c8c9ca;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.google-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.google-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.divider {
  position: relative;
  text-align: center;
  margin: 1.5rem 0;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #e9ecef;
}

.divider span {
  background: white;
  padding: 0 1rem;
  color: #6c757d;
  font-size: 0.9rem;
}

/* Form Styles */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-weight: 500;
  font-size: 0.9rem;
}

.form-input {
  padding: 0.75rem;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #006ce4;
  box-shadow: 0 0 0 2px rgba(0, 108, 228, 0.1);
}

.submit-btn {
  background: #006ce4;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: background 0.3s;
  margin-top: 0.5rem;
}

.submit-btn:hover {
  background: #0056b3;
}

.submit-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.submit-btn.secondary {
  background: #28a745;
}

.submit-btn.secondary:hover {
  background: #218838;
}

.mode-switch {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
  color: #6c757d;
}

.link-btn {
  background: none;
  border: none;
  color: #006ce4;
  cursor: pointer;
  text-decoration: underline;
  font-size: inherit;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 0.75rem;
  border-radius: 4px;
  margin-top: 1rem;
  border: 1px solid #f5c6cb;
}

.error-text {
  color: #dc3545;
  font-size: 0.8rem;
  display: block;
  margin-top: 0.25rem;
}

.password-errors {
  margin-top: 0.5rem;
}

@media (max-width: 480px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    margin: 1rem;
  }
  
  .modal-header,
  .modal-body {
    padding: 1rem;
  }
}
</style>