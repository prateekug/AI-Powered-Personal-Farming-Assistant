// Configuration
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// Authentication & Token Helpers
function getToken() {
    return localStorage.getItem('farmai_token');
}

function setAuthSession(token, user) {
    if (token) localStorage.setItem('farmai_token', token);
    if (user) localStorage.setItem('farmai_user', JSON.stringify(user));
}

function clearAuthSession() {
    localStorage.removeItem('farmai_token');
    localStorage.removeItem('farmai_user');
    sessionStorage.clear();
}

function getUser() {
    const userStr = localStorage.getItem('farmai_user');
    try {
        return userStr ? JSON.parse(userStr) : null;
    } catch (e) {
        return null;
    }
}

// Central API Fetch Client
async function apiFetch(endpoint, method = 'GET', data = null, isFormData = false) {
    const headers = {};
    const token = getToken();

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const options = {
        method: method,
        headers: headers
    };

    if (data) {
        if (isFormData) {
            options.body = data; // Browser sets multipart boundary automatically
        } else {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(data);
        }
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const json = await response.json();

        if (!response.ok || !json.success) {
            const errorMsg = json.error || `Server error (${response.status})`;
            if (response.status === 401) {
                clearAuthSession();
                alert('Your login session has expired. Please log in again.');
                window.location.href = 'login.html';
                return;
            }
            throw new Error(errorMsg);
        }

        return json;
    } catch (err) {
        console.error(`[API Error] ${endpoint}:`, err);
        throw err;
    }
}

// Global UI Setup on DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const isPublicPage = currentPath.endsWith('index.html') || currentPath.endsWith('/') || currentPath === '';
    const isAuthPage = currentPath.endsWith('login.html') || currentPath.endsWith('signup.html');
    const token = getToken();

    // Route Protection
    if (!token && !isPublicPage && !isAuthPage) {
        window.location.href = 'login.html';
        return;
    }

    if (token && isAuthPage) {
        window.location.href = 'dashboard.html';
        return;
    }

    // Update User Name in Navbar
    const user = getUser();
    if (user && user.full_name) {
        const userElements = document.querySelectorAll('.user-name');
        userElements.forEach(el => {
            el.textContent = `Welcome, ${user.full_name}`;
        });
    }

    // Logout Handler
    document.querySelectorAll('.btn-logout').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            clearAuthSession();
            window.location.href = 'index.html';
        });
    });

    // Scroll & Ripple UI Effects
    setupScrollAnimations();
    setupRippleEffects();

    // Attach Page Form Handlers & Loaders
    initAuthForms();
    initFarmForms();
    initDiseaseDetection();
    initPricePrediction();

    // Page Specific Loaders
    if (currentPath.includes('confirmation.html')) {
        loadConfirmationData();
    } else if (currentPath.includes('crop-result.html')) {
        loadCropResultData();
    } else if (currentPath.includes('disease-result.html')) {
        loadDiseaseResultData();
    } else if (currentPath.includes('price-result.html')) {
        loadPriceResultData();
    }
});

// Scroll & Button UI Animations
function setupScrollAnimations() {
    const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -50px 0px' };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card, .dashboard-card, .summary-section, .detail-item, .alternative-item, .treatment-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        observer.observe(el);
    });

    if (!document.getElementById('animateInStyles')) {
        const style = document.createElement('style');
        style.id = 'animateInStyles';
        style.textContent = `.animate-in { opacity: 1 !important; transform: translateY(0) !important; }`;
        document.head.appendChild(style);
    }
}

function setupRippleEffects() {
    document.querySelectorAll('button, .btn-primary, .btn-secondary, .btn-login, .btn-signup').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.cssText = `
                position: absolute; width: ${size}px; height: ${size}px; left: ${x}px; top: ${y}px;
                background: rgba(255, 255, 255, 0.3); border-radius: 50%; transform: scale(0);
                animation: ripple 0.6s ease-out; pointer-events: none;
            `;
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

// 1. Authentication Handlers
function initAuthForms() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;

            try {
                submitBtn.textContent = 'Logging in...';
                submitBtn.disabled = true;

                const response = await apiFetch('/auth/login', 'POST', { email, password });

                setAuthSession(response.data.token, response.data.user);
                submitBtn.textContent = '✓ Logged In!';
                submitBtn.style.background = 'var(--success-gradient)';

                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 800);
            } catch (err) {
                alert(err.message || 'Login failed. Please check your credentials.');
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const fullName = document.getElementById('fullName').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const submitBtn = signupForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;

            if (password !== confirmPassword) {
                alert('Passwords do not match');
                return;
            }

            try {
                submitBtn.textContent = 'Creating account...';
                submitBtn.disabled = true;

                const response = await apiFetch('/auth/register', 'POST', {
                    fullName, email, password, confirmPassword
                });

                setAuthSession(response.data.token, response.data.user);
                submitBtn.textContent = '✓ Account Created!';
                submitBtn.style.background = 'var(--success-gradient)';

                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 800);
            } catch (err) {
                alert(err.message || 'Signup failed.');
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }
}

// 2. Farm & Soil Profile Form Handlers (SQLite Backend as Source of Truth)
function initFarmForms() {
    // Land Details
    const landForm = document.getElementById('landForm');
    if (landForm) {
        apiFetch('/farm/details').then(res => {
            if (res.data) {
                if (res.data.land_size) document.getElementById('landSize').value = res.data.land_size;
                if (res.data.location) document.getElementById('location').value = res.data.location;
                if (res.data.soil_type) document.getElementById('soilType').value = res.data.soil_type;
                if (res.data.irrigation) document.getElementById('irrigation').value = res.data.irrigation;
            }
        }).catch(err => console.log('No prior land details in DB'));

        landForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const submitBtn = landForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;

            const payload = {
                landSize: document.getElementById('landSize').value,
                location: document.getElementById('location').value,
                soilType: document.getElementById('soilType').value,
                irrigation: document.getElementById('irrigation').value
            };

            try {
                submitBtn.textContent = 'Saving to Database...';
                submitBtn.disabled = true;
                await apiFetch('/farm/details', 'POST', payload);
                
                submitBtn.textContent = '✓ Saved!';
                setTimeout(() => { window.location.href = 'dashboard.html'; }, 800);
            } catch (err) {
                alert(err.message || 'Failed to save land details.');
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // Previous Crop
    const previousCropForm = document.getElementById('previousCropForm');
    if (previousCropForm) {
        apiFetch('/farm/previous-crop').then(res => {
            if (res.data) {
                if (res.data.crop_type) document.getElementById('cropType').value = res.data.crop_type;
                if (res.data.yield !== null && res.data.yield !== undefined) document.getElementById('yield').value = res.data.yield;
                if (res.data.season) document.getElementById('season').value = res.data.season;
                if (res.data.fertilizer_used) document.getElementById('fertilizerUsed').value = res.data.fertilizer_used;
            }
        }).catch(err => console.log('No prior previous crop in DB'));

        previousCropForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const submitBtn = previousCropForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;

            const payload = {
                cropType: document.getElementById('cropType').value,
                yield: document.getElementById('yield').value,
                season: document.getElementById('season').value,
                fertilizerUsed: document.getElementById('fertilizerUsed').value
            };

            try {
                submitBtn.textContent = 'Saving to Database...';
                submitBtn.disabled = true;
                await apiFetch('/farm/previous-crop', 'POST', payload);

                submitBtn.textContent = '✓ Saved!';
                setTimeout(() => { window.location.href = 'dashboard.html'; }, 800);
            } catch (err) {
                alert(err.message || 'Failed to save previous crop details.');
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // Soil Details
    const soilForm = document.getElementById('soilForm');
    if (soilForm) {
        apiFetch('/farm/soil').then(res => {
            if (res.data) {
                if (res.data.soil_moisture !== undefined) document.getElementById('soilMoisture').value = res.data.soil_moisture;
                if (res.data.ph_level !== undefined) document.getElementById('phLevel').value = res.data.ph_level;
                if (res.data.nitrogen !== undefined) document.getElementById('nitrogen').value = res.data.nitrogen;
                if (res.data.phosphorus !== undefined) document.getElementById('phosphorus').value = res.data.phosphorus;
                if (res.data.potassium !== undefined) document.getElementById('potassium').value = res.data.potassium;
                if (res.data.organic_matter !== undefined) document.getElementById('organicMatter').value = res.data.organic_matter;
            }
        }).catch(err => console.log('No prior soil data in DB'));

        soilForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const submitBtn = soilForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;

            const payload = {
                soilMoisture: document.getElementById('soilMoisture').value,
                phLevel: document.getElementById('phLevel').value,
                nitrogen: document.getElementById('nitrogen').value,
                phosphorus: document.getElementById('phosphorus').value,
                potassium: document.getElementById('potassium').value,
                organicMatter: document.getElementById('organicMatter').value
            };

            try {
                submitBtn.textContent = 'Saving to Database...';
                submitBtn.disabled = true;
                await apiFetch('/farm/soil', 'POST', payload);

                submitBtn.textContent = '✓ Saved!';
                setTimeout(() => { window.location.href = 'dashboard.html'; }, 800);
            } catch (err) {
                alert(err.message || 'Failed to save soil details.');
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // Planting Schedule
    const calendarForm = document.getElementById('calendarForm');
    if (calendarForm) {
        apiFetch('/farm/schedule').then(res => {
            if (res.data) {
                if (res.data.planting_date) document.getElementById('plantingDate').value = res.data.planting_date;
                if (res.data.season) document.getElementById('season').value = res.data.season;
            }
        }).catch(err => console.log('No prior schedule in DB'));

        calendarForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const submitBtn = calendarForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;

            const payload = {
                plantingDate: document.getElementById('plantingDate').value,
                season: document.getElementById('season').value
            };

            try {
                submitBtn.textContent = 'Saving to Database...';
                submitBtn.disabled = true;
                await apiFetch('/farm/schedule', 'POST', payload);

                submitBtn.textContent = '✓ Saved!';
                setTimeout(() => { window.location.href = 'dashboard.html'; }, 800);
            } catch (err) {
                alert(err.message || 'Failed to save schedule.');
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }
}

// 3. Confirmation Page - Loads Complete Profile from GET /api/farm/profile
async function loadConfirmationData() {
    try {
        const response = await apiFetch('/farm/profile');
        if (!response.data) return;

        const profile = response.data;
        const land = profile.land_details || {};
        const crop = profile.previous_crop || {};
        const soil = profile.soil_details || {};
        const sched = profile.planting_schedule || {};

        // Render Land Summary
        document.getElementById('summaryLandSize').textContent = land.land_size ? `${land.land_size} acres` : 'Not provided';
        document.getElementById('summaryLocation').textContent = land.location || 'Not provided';
        document.getElementById('summarySoilType').textContent = land.soil_type || 'Not provided';
        document.getElementById('summaryIrrigation').textContent = land.irrigation || 'Not provided';

        // Render Previous Crop Summary
        document.getElementById('summaryCropType').textContent = crop.crop_type || 'Not provided';
        document.getElementById('summaryYield').textContent = crop.yield ? `${crop.yield} tons` : 'Not specified';
        document.getElementById('summarySeason').textContent = crop.season || 'Not provided';

        // Render Soil Summary
        document.getElementById('summarySoilMoisture').textContent = (soil.soil_moisture !== undefined && soil.soil_moisture !== null) ? `${soil.soil_moisture}%` : 'Not provided';
        document.getElementById('summaryPhLevel').textContent = (soil.ph_level !== undefined && soil.ph_level !== null) ? soil.ph_level : 'Not provided';
        document.getElementById('summaryNitrogen').textContent = (soil.nitrogen !== undefined && soil.nitrogen !== null) ? `${soil.nitrogen} mg/kg` : 'Not specified';
        document.getElementById('summaryPhosphorus').textContent = (soil.phosphorus !== undefined && soil.phosphorus !== null) ? `${soil.phosphorus} mg/kg` : 'Not specified';
        document.getElementById('summaryPotassium').textContent = (soil.potassium !== undefined && soil.potassium !== null) ? `${soil.potassium} mg/kg` : 'Not specified';

        // Render Schedule Summary
        document.getElementById('summaryPlantingDate').textContent = sched.planting_date || 'Not provided';
        document.getElementById('summaryPlantingSeason').textContent = sched.season || 'Not provided';

    } catch (e) {
        console.error('Error loading farm profile from backend:', e);
    }
}

async function requestCropRecommendation() {
    const btn = document.getElementById('recommendationBtn');
    const originalText = btn ? btn.textContent : 'Get Crop Recommendation';

    try {
        if (btn) {
            btn.textContent = 'Calling Crop ML Model...';
            btn.disabled = true;
        }

        const response = await apiFetch('/crop/recommend', 'POST');
        sessionStorage.setItem('cropResult', JSON.stringify(response.data));

        if (btn) btn.textContent = '✓ Complete!';
        setTimeout(() => {
            window.location.href = 'crop-result.html';
        }, 600);
    } catch (err) {
        alert(err.message || 'Failed to generate crop recommendation.');
        if (btn) {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }
}

// 4. Crop Result Loader
function loadCropResultData() {
    const dataStr = sessionStorage.getItem('cropResult');
    if (!dataStr) return;

    try {
        const data = JSON.parse(dataStr);

        if (data.model_loaded === false) {
            const cropName = document.getElementById('recommendedCropName');
            if (cropName) cropName.textContent = 'Pending ML Model';
            
            const confidence = document.getElementById('cropConfidence');
            if (confidence) confidence.textContent = '--';

            const expYield = document.getElementById('expectedYield');
            if (expYield) expYield.textContent = '--';

            const period = document.getElementById('growingPeriod');
            if (period) period.textContent = '--';

            const bestTime = document.getElementById('bestPlantingTime');
            if (bestTime) bestTime.textContent = '--';

            const water = document.getElementById('waterRequirement');
            if (water) water.textContent = '--';

            const reasonElem = document.getElementById('recommendationReason');
            if (reasonElem) {
                reasonElem.innerHTML = `<strong>ML Model Status:</strong> ${data.message || 'Crop Recommendation ML model binary placement is pending in backend/models/'}`;
            }
            return;
        }

        if (data.recommended_crop) {
            document.getElementById('recommendedCropName').textContent = data.recommended_crop;
        }
        if (data.confidence !== undefined) {
            document.getElementById('cropConfidence').textContent = `${data.confidence}%`;
        }
        if (data.expected_yield) {
            document.getElementById('expectedYield').textContent = data.expected_yield;
        }
        if (data.growing_period) {
            document.getElementById('growingPeriod').textContent = data.growing_period;
        }
        if (data.best_planting_time) {
            document.getElementById('bestPlantingTime').textContent = data.best_planting_time;
        }
        if (data.water_requirement) {
            document.getElementById('waterRequirement').textContent = data.water_requirement;
        }
        if (data.recommendation_reason) {
            document.getElementById('recommendationReason').textContent = data.recommendation_reason;
        }
    } catch (e) {
        console.error('Error parsing crop result data:', e);
    }
}

// 5. Plant Disease Detection Upload & Result Renderer
function initDiseaseDetection() {
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const cropSelect = document.getElementById('cropSelect');

    if (!uploadArea || !imageInput) return;

    uploadArea.addEventListener('click', () => imageInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.background = 'rgba(255, 255, 255, 0.1)';
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.style.background = 'transparent';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.background = 'transparent';
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleImagePreview(file);
        }
    });

    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) handleImagePreview(file);
    });

    if (cropSelect && analyzeBtn) {
        cropSelect.addEventListener('change', function() {
            if (previewImg.src && cropSelect.value) {
                analyzeBtn.disabled = false;
            }
        });
    }

    function handleImagePreview(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImg.src = e.target.result;
            uploadArea.style.display = 'none';
            imagePreview.style.display = 'block';
            if (cropSelect && cropSelect.value) {
                analyzeBtn.disabled = false;
            } else {
                analyzeBtn.disabled = false;
            }
        };
        reader.readAsDataURL(file);
    }
}

function removeImage() {
    const uploadArea = document.getElementById('uploadArea');
    const imagePreview = document.getElementById('imagePreview');
    const imageInput = document.getElementById('imageInput');
    const analyzeBtn = document.getElementById('analyzeBtn');

    uploadArea.style.display = 'block';
    imagePreview.style.display = 'none';
    imageInput.value = '';
    if (analyzeBtn) analyzeBtn.disabled = true;
}

async function analyzeImage() {
    const imageInput = document.getElementById('imageInput');
    const cropSelect = document.getElementById('cropSelect');
    const analyzeBtn = document.getElementById('analyzeBtn');

    if (!imageInput.files || imageInput.files.length === 0) {
        alert('Please choose an image file first.');
        return;
    }

    const file = imageInput.files[0];
    const cropType = cropSelect ? cropSelect.value : '';

    const formData = new FormData();
    formData.append('image', file);
    formData.append('cropType', cropType);

    const originalText = analyzeBtn.textContent;

    try {
        analyzeBtn.textContent = 'Preprocessing & Running Keras Model...';
        analyzeBtn.disabled = true;

        const response = await apiFetch('/disease/predict', 'POST', formData, true);

        sessionStorage.setItem('diseaseResult', JSON.stringify(response.data));
        analyzeBtn.textContent = '✓ Analysis Complete!';
        analyzeBtn.style.background = 'var(--success-gradient)';

        setTimeout(() => {
            window.location.href = 'disease-result.html';
        }, 800);
    } catch (err) {
        alert(err.message || 'Disease detection failed.');
        analyzeBtn.textContent = originalText;
        analyzeBtn.disabled = false;
    }
}

function loadDiseaseResultData() {
    const dataStr = sessionStorage.getItem('diseaseResult');
    if (!dataStr) return;

    try {
        const data = JSON.parse(dataStr);

        if (data.model_loaded === false) {
            const descElem = document.getElementById('diseaseDescription');
            if (descElem) {
                descElem.innerHTML = `<strong>ML Model Status:</strong> ${data.message || 'Plant Disease ML model binary placement pending in backend/models/'}`;
            }
            return;
        }

        // Disease Name & Confidence
        const nameElem = document.getElementById('diseaseName');
        if (nameElem && data.disease_name) {
            nameElem.textContent = data.disease_name;
        }

        const confElem = document.getElementById('diseaseConfidence');
        if (confElem && data.confidence !== undefined) {
            confElem.textContent = `${data.confidence}%`;
        }

        const descElem = document.getElementById('diseaseDescription');
        if (descElem && data.description) {
            descElem.textContent = data.description;
        }

        // Render Impact List
        const impactElem = document.getElementById('diseaseImpact');
        if (impactElem && Array.isArray(data.impact)) {
            impactElem.innerHTML = data.impact.map(item => `<li>${item}</li>`).join('');
        }

        // Render Treatment Cards
        const treatmentContainer = document.querySelector('.treatment-list');
        if (treatmentContainer && Array.isArray(data.treatments)) {
            treatmentContainer.innerHTML = data.treatments.map(t => `
                <div class="treatment-item">
                    <div class="treatment-icon">${t.icon || '💊'}</div>
                    <div class="treatment-details">
                        <h5>${t.title}</h5>
                        <p>${t.description}</p>
                    </div>
                </div>
            `).join('');
        }

        // Render Prevention Tips
        const prevElem = document.getElementById('preventionTips');
        if (prevElem && Array.isArray(data.prevention_tips)) {
            prevElem.innerHTML = data.prevention_tips.map(tip => `<li>${tip}</li>`).join('');
        }
    } catch (e) {
        console.error('Error rendering disease result:', e);
    }
}

// 6. Price Prediction Form & Result Loader
function initPricePrediction() {
    const priceForm = document.getElementById('priceForm');
    if (!priceForm) return;

    priceForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const crop = document.getElementById('cropSelect').value;
        const month = document.getElementById('predictionMonth').value;
        const submitBtn = priceForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;

        if (!crop || !month) {
            alert('Please select both a crop and a prediction month.');
            return;
        }

        try {
            submitBtn.textContent = 'Calling Price ML Model...';
            submitBtn.disabled = true;

            const response = await apiFetch('/price/predict', 'POST', { crop, month });
            sessionStorage.setItem('priceResult', JSON.stringify(response.data));

            submitBtn.textContent = '✓ Forecast Ready!';
            setTimeout(() => {
                window.location.href = 'price-result.html';
            }, 800);
        } catch (err) {
            alert(err.message || 'Price prediction failed.');
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });
}

function loadPriceResultData() {
    const dataStr = sessionStorage.getItem('priceResult');
    if (!dataStr) return;

    try {
        const data = JSON.parse(dataStr);

        if (data.crop) {
            const cropElem = document.getElementById('cropName');
            if (cropElem) cropElem.textContent = data.crop.charAt(0).toUpperCase() + data.crop.slice(1);
        }

        if (data.month) {
            const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 
                                'July', 'August', 'September', 'October', 'November', 'December'];
            const monthElem = document.getElementById('monthName');
            if (monthElem) monthElem.textContent = monthNames[parseInt(data.month) - 1] || data.month;
        }

        if (data.model_loaded === false) {
            const priceVal = document.getElementById('predictedPrice');
            if (priceVal) priceVal.textContent = '--';

            const currentPrice = document.getElementById('currentPrice');
            if (currentPrice) currentPrice.textContent = '--';

            const priceRange = document.getElementById('priceRange');
            if (priceRange) priceRange.textContent = '--';

            const confidence = document.getElementById('predictionConfidence');
            if (confidence) confidence.textContent = '--';

            const priceTrend = document.getElementById('priceTrend');
            if (priceTrend) priceTrend.textContent = 'ML Model Pending';

            const sentiment = document.getElementById('marketSentiment');
            if (sentiment) sentiment.textContent = 'Pending';

            const adviceElem = document.getElementById('sellingAdvice');
            if (adviceElem) {
                adviceElem.innerHTML = `<strong>ML Model Status:</strong> ${data.message || 'Price Prediction ML model binary placement pending in backend/models/'}`;
            }
            return;
        }

        if (data.predicted_price) {
            document.getElementById('predictedPrice').textContent = Number(data.predicted_price).toLocaleString();
        }
        if (data.current_price) {
            document.getElementById('currentPrice').textContent = data.current_price;
        }
        if (data.price_range) {
            document.getElementById('priceRange').textContent = data.price_range;
        }
        if (data.confidence !== undefined) {
            document.getElementById('predictionConfidence').textContent = `${data.confidence}%`;
        }
        if (data.trend) {
            document.getElementById('priceTrend').textContent = data.trend;
        }
    } catch (e) {
        console.error('Error rendering price result data:', e);
    }
}
