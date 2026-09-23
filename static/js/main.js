/**
 * SCOPE INDIA - Main JavaScript
 * Handles dynamic dependent dropdowns, file previews, and confirmation modals
 */

document.addEventListener('DOMContentLoaded', function () {
    // -------------------------------------------------------------
    // 1. Dependent Dropdowns (Country -> State -> City)
    // -------------------------------------------------------------
    const countrySelect = document.getElementById('id_country');
    const stateSelect = document.getElementById('id_state');
    const citySelect = document.getElementById('id_city');

    if (countrySelect && stateSelect && citySelect) {
        countrySelect.addEventListener('change', function () {
            const countryId = this.value;
            // Clear current states and cities
            stateSelect.innerHTML = '<option value="">-- Select State --</option>';
            citySelect.innerHTML = '<option value="">-- Select City --</option>';

            if (!countryId) return;

            // Fetch States for selected country
            fetch(`/api/states/${countryId}/`)
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.json();
                })
                .then(states => {
                    states.forEach(state => {
                        const opt = document.createElement('option');
                        opt.value = state.id;
                        opt.textContent = state.name;
                        stateSelect.appendChild(opt);
                    });
                })
                .catch(err => {
                    console.error('Error fetching states:', err);
                });
        });

        stateSelect.addEventListener('change', function () {
            const stateId = this.value;
            // Clear current cities
            citySelect.innerHTML = '<option value="">-- Select City --</option>';

            if (!stateId) return;

            // Fetch Cities for selected state
            fetch(`/api/cities/${stateId}/`)
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.json();
                })
                .then(cities => {
                    cities.forEach(city => {
                        const opt = document.createElement('option');
                        opt.value = city.id;
                        opt.textContent = city.name;
                        citySelect.appendChild(opt);
                    });
                })
                .catch(err => {
                    console.error('Error fetching cities:', err);
                });
        });
    }

    // -------------------------------------------------------------
    // 2. Avatar Image Preview Handler
    // -------------------------------------------------------------
    const avatarInput = document.querySelector('input[type="file"][name="avatar"]');
    const avatarPreview = document.getElementById('avatar-preview-img');

    if (avatarInput && avatarPreview) {
        avatarInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                // Check size (2MB)
                if (file.size > 2 * 1024 * 1024) {
                    alert('Selected image exceeds 2MB limit. Please choose a smaller file.');
                    this.value = '';
                    return;
                }
                const reader = new FileReader();
                reader.onload = function (e) {
                    avatarPreview.src = e.target.result;
                    avatarPreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // -------------------------------------------------------------
    // 3. Auto-Dismiss Dismissible Alerts
    // -------------------------------------------------------------
    const autoAlerts = document.querySelectorAll('.alert-dismissible');
    autoAlerts.forEach(function (alertElem) {
        setTimeout(function () {
            try {
                const bsAlert = new bootstrap.Alert(alertElem);
                bsAlert.close();
            } catch (e) {
                // bootstrap may not be loaded yet or alert closed
            }
        }, 6000);
    });
});
