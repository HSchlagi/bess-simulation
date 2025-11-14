/**
 * Erweiterte Formular-Validierung für BESS-Simulation
 * ===================================================
 * 
 * Features:
 * - Real-time Validierung
 * - Visuelle Feedback-Indikatoren
 * - Intelligente Validierungsregeln
 * - Progress-Indikatoren für Formular-Vervollständigung
 */

class FormValidator {
    constructor(formId, options = {}) {
        this.formId = formId;
        this.form = document.getElementById(formId);
        this.options = {
            showProgress: options.showProgress !== false,
            realTimeValidation: options.realTimeValidation !== false,
            validateOnBlur: options.validateOnBlur !== false,
            ...options
        };
        
        this.validationRules = {
            // Pflichtfelder
            required: {
                name: { required: true, minLength: 2, maxLength: 100 },
                bess_size: { required: true, min: 0.1, max: 100000 },
                bess_power: { required: true, min: 0.1, max: 50000 },
                current_electricity_cost: { required: true, min: 0.01, max: 100 }
            },
            
            // Optionale Felder mit Validierung
            optional: {
                pv_power: { min: 0, max: 100000 },
                hp_power: { min: 0, max: 10000 },
                wind_power: { min: 0, max: 10000 },
                hydro_power: { min: 0, max: 10000 },
                daily_cycles: { min: 0.1, max: 3.0 },
                location: { maxLength: 200 }
            },
            
            // Kostenfelder
            costs: {
                bess_cost: { min: 0, max: 500000000 },  // 500 Millionen Euro
                pv_cost: { min: 0, max: 500000000 },    // 500 Millionen Euro
                hp_cost: { min: 0, max: 100000000 },     // 100 Millionen Euro
                wind_cost: { min: 0, max: 100000000 },  // 100 Millionen Euro
                hydro_cost: { min: 0, max: 500000000 }, // 500 Millionen Euro
                other_cost: { min: 0, max: 500000000 }  // 500 Millionen Euro
            }
        };
        
        this.validationStates = {};
        this.progressBar = null;
        
        this.initialize();
    }
    
    /**
     * Validator initialisieren
     */
    initialize() {
        if (!this.form) return;
        
        // Progress-Bar erstellen
        if (this.options.showProgress) {
            this.createProgressBar();
        }
        
        // Event-Listener registrieren
        this.attachEventListeners();
        
        // Initiale Validierung mit Verzögerung (damit Werte geladen werden)
        setTimeout(() => {
            this.validateAll();
        }, 1500);
        
        console.log(`🔍 Formular-Validator für "${this.formId}" initialisiert`);
    }
    
    /**
     * Progress-Bar erstellen
     */
    createProgressBar() {
        this.progressBar = document.createElement('div');
        this.progressBar.className = 'mb-4';
        this.progressBar.innerHTML = `
            <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">Formular-Vervollständigung</span>
                <span class="text-sm text-gray-500" id="progress-percentage">0%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" id="progress-bar" style="width: 0%"></div>
            </div>
        `;
        
        // Progress-Bar vor dem ersten Formular-Bereich einfügen
        const firstSection = this.form.querySelector('.bg-gray-50, .bg-blue-50, .bg-green-50');
        if (firstSection) {
            firstSection.parentNode.insertBefore(this.progressBar, firstSection);
        }
    }
    
    /**
     * Event-Listener anbringen
     */
    attachEventListeners() {
        const inputs = this.form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            // Real-time Validierung
            if (this.options.realTimeValidation) {
                input.addEventListener('input', () => this.validateField(input));
            }
            
            // Blur-Validierung
            if (this.options.validateOnBlur) {
                input.addEventListener('blur', () => this.validateField(input));
            }
            
            // Focus-Event für bessere UX
            input.addEventListener('focus', () => this.onFieldFocus(input));
        });
    }
    
    /**
     * Feld-Fokus Event
     */
    onFieldFocus(input) {
        // Bestehende Fehler-Highlights entfernen
        input.classList.remove('border-red-500', 'bg-red-50');
        input.classList.add('border-gray-300');
        
        // Hilfetext anzeigen (falls vorhanden)
        this.showFieldHelp(input);
    }
    
    /**
     * Hilfetext für Felder anzeigen
     */
    showFieldHelp(input) {
        const helpTexts = {
            'bess_size': 'Speicherkapazität in kWh (typisch: 100-8000 kWh)',
            'bess_power': 'Leistung in kW (typisch: 50-2000 kW)',
            'pv_power': 'PV-Leistung in kW (typisch: 50-2000 kW)',
            'current_electricity_cost': 'Aktuelle Stromkosten in Ct/kWh',
            'daily_cycles': 'Tägliche Lade-/Entladezyklen (0.5-2.0)',
            'hp_power': 'Wärmepumpen-Leistung in kW',
            'wind_power': 'Windkraft-Leistung in kW',
            'hydro_power': 'Wasserkraft-Leistung in kW'
        };
        
        const fieldName = input.name;
        const helpText = helpTexts[fieldName];
        
        if (helpText) {
            // Bestehenden Hilfetext entfernen
            const existingHelp = input.parentNode.querySelector('.field-help');
            if (existingHelp) {
                existingHelp.remove();
            }
            
            // Neuen Hilfetext hinzufügen
            const helpDiv = document.createElement('div');
            helpDiv.className = 'field-help text-xs text-blue-600 mt-1';
            helpDiv.textContent = helpText;
            input.parentNode.appendChild(helpDiv);
            
            // Hilfetext nach 5 Sekunden ausblenden
            setTimeout(() => {
                if (helpDiv.parentNode) {
                    helpDiv.remove();
                }
            }, 5000);
        }
    }
    
    /**
     * Einzelnes Feld validieren
     */
    validateField(input) {
        const fieldName = input.name;
        const value = input.value;
        const rules = this.getValidationRules(fieldName);
        
        if (!rules) return true;
        
        const errors = this.validateValue(value, rules, fieldName);
        this.validationStates[fieldName] = {
            isValid: errors.length === 0,
            errors: errors
        };
        
        this.updateFieldVisualState(input, errors);
        this.updateProgress();
        
        return errors.length === 0;
    }
    
    /**
     * Validierungsregeln für Feld abrufen
     */
    getValidationRules(fieldName) {
        // Alle Regeln durchsuchen
        for (const category in this.validationRules) {
            if (this.validationRules[category][fieldName]) {
                return this.validationRules[category][fieldName];
            }
        }
        return null;
    }
    
    /**
     * Wert validieren
     */
    validateValue(value, rules, fieldName) {
        const errors = [];
        
        // Required-Validierung
        if (rules.required && (!value || value.trim() === '')) {
            errors.push(this.getErrorMessage(fieldName, 'required'));
        }
        
        // Min/Max-Length Validierung
        if (value && rules.minLength && value.length < rules.minLength) {
            errors.push(this.getErrorMessage(fieldName, 'minLength', rules.minLength));
        }
        
        if (value && rules.maxLength && value.length > rules.maxLength) {
            errors.push(this.getErrorMessage(fieldName, 'maxLength', rules.maxLength));
        }
        
        // Numerische Validierung
        if (value && (rules.min !== undefined || rules.max !== undefined)) {
            const numValue = parseFloat(value);
            
            if (isNaN(numValue)) {
                errors.push(this.getErrorMessage(fieldName, 'numeric'));
            } else {
                if (rules.min !== undefined && numValue < rules.min) {
                    errors.push(this.getErrorMessage(fieldName, 'min', rules.min));
                }
                if (rules.max !== undefined && numValue > rules.max) {
                    errors.push(this.getErrorMessage(fieldName, 'max', rules.max));
                }
            }
        }
        
        // Spezielle Validierungen
        if (value && fieldName === 'daily_cycles') {
            const cycles = parseFloat(value);
            if (cycles < 0.1 || cycles > 3.0) {
                errors.push('Tägliche Zyklen müssen zwischen 0.1 und 3.0 liegen');
            }
        }
        
        if (value && fieldName === 'current_electricity_cost') {
            const cost = parseFloat(value);
            if (cost < 0.01 || cost > 100) {
                errors.push('Stromkosten müssen zwischen 0.01 und 100 Ct/kWh liegen');
            }
        }
        
        return errors;
    }
    
    /**
     * Fehlermeldungen generieren
     */
    getErrorMessage(fieldName, errorType, value = null) {
        const fieldLabels = {
            'name': 'Projektname',
            'bess_size': 'BESS-Größe',
            'bess_power': 'BESS-Leistung',
            'pv_power': 'PV-Leistung',
            'current_electricity_cost': 'Stromkosten',
            'daily_cycles': 'Tägliche Zyklen',
            'location': 'Standort'
        };
        
        const label = fieldLabels[fieldName] || fieldName;
        
        switch (errorType) {
            case 'required':
                return `${label} ist erforderlich`;
            case 'minLength':
                return `${label} muss mindestens ${value} Zeichen lang sein`;
            case 'maxLength':
                return `${label} darf maximal ${value} Zeichen lang sein`;
            case 'min':
                return `${label} muss mindestens ${value} sein`;
            case 'max':
                return `${label} darf maximal ${value} sein`;
            case 'numeric':
                return `${label} muss eine Zahl sein`;
            default:
                return `${label} ist ungültig`;
        }
    }
    
    /**
     * Visuellen Zustand des Feldes aktualisieren
     */
    updateFieldVisualState(input, errors) {
        // Bestehende Fehler entfernen
        const existingError = input.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        
        // CSS-Klassen zurücksetzen
        input.classList.remove('border-red-500', 'border-green-500', 'bg-red-50', 'bg-green-50');
        input.classList.add('border-gray-300');
        
        if (errors.length > 0) {
            // Fehler-Zustand
            input.classList.add('border-red-500', 'bg-red-50');
            
            // Fehlermeldung anzeigen
            const errorDiv = document.createElement('div');
            errorDiv.className = 'field-error text-red-600 text-sm mt-1';
            errorDiv.textContent = errors[0]; // Erste Fehlermeldung anzeigen
            input.parentNode.appendChild(errorDiv);
        } else if (input.value && input.value.trim() !== '') {
            // Erfolgs-Zustand
            input.classList.add('border-green-500', 'bg-green-50');
        }
    }
    
    /**
     * Progress-Bar aktualisieren
     */
    updateProgress() {
        if (!this.progressBar) return;
        
        // Alle Felder zählen (required + optional + costs)
        const allFields = {
            ...this.validationRules.required,
            ...this.validationRules.optional,
            ...this.validationRules.costs
        };
        
        const totalFields = Object.keys(allFields).length;
        const completedFields = Object.values(this.validationStates)
            .filter(state => state && state.isValid)
            .length;
        
        // Prozentsatz auf maximal 100% begrenzen
        let percentage = Math.round((completedFields / totalFields) * 100);
        percentage = Math.min(percentage, 100); // Maximal 100%
        
        const progressBarElement = this.progressBar.querySelector('#progress-bar');
        const percentageElement = this.progressBar.querySelector('#progress-percentage');
        
        if (progressBarElement) {
            progressBarElement.style.width = `${percentage}%`;
        }
        
        if (percentageElement) {
            percentageElement.textContent = `${percentage}%`;
        }
        
        // Progress-Bar-Farbe basierend auf Fortschritt
        if (progressBarElement) {
            progressBarElement.className = 'h-2 rounded-full transition-all duration-300';
            if (percentage < 50) {
                progressBarElement.classList.add('bg-red-500');
            } else if (percentage < 100) {
                progressBarElement.classList.add('bg-yellow-500');
            } else {
                progressBarElement.classList.add('bg-green-500');
            }
        }
    }
    
    /**
     * Alle Felder validieren
     */
    validateAll() {
        const inputs = this.form.querySelectorAll('input, select, textarea');
        let allValid = true;
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                allValid = false;
            }
        });
        
        return allValid;
    }
    
    /**
     * Validierungsstatus abrufen
     */
    getValidationStatus() {
        return {
            isValid: Object.values(this.validationStates).every(state => state && state.isValid),
            states: this.validationStates,
            errors: this.getAllErrors()
        };
    }
    
    /**
     * Alle Fehler sammeln
     */
    getAllErrors() {
        const allErrors = [];
        
        Object.values(this.validationStates).forEach(state => {
            if (state && state.errors) {
                allErrors.push(...state.errors);
            }
        });
        
        return allErrors;
    }
    
    /**
     * Formular-Validierung für Submit
     */
    validateForSubmit() {
        const isValid = this.validateAll();
        
        if (!isValid) {
            this.showValidationSummary();
        }
        
        return isValid;
    }
    
    /**
     * Validierungs-Zusammenfassung anzeigen
     */
    showValidationSummary() {
        const errors = this.getAllErrors();
        
        if (errors.length > 0) {
            const summaryDiv = document.createElement('div');
            summaryDiv.className = 'fixed top-4 left-1/2 transform -translate-x-1/2 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg shadow-lg z-50';
            summaryDiv.innerHTML = `
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <h3 class="text-sm font-medium">Validierungsfehler gefunden</h3>
                        <div class="mt-2 text-sm">
                            <ul class="list-disc list-inside">
                                ${errors.slice(0, 3).map(error => `<li>${error}</li>`).join('')}
                                ${errors.length > 3 ? `<li>... und ${errors.length - 3} weitere Fehler</li>` : ''}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(summaryDiv);
            
            // Nach 5 Sekunden entfernen
            setTimeout(() => {
                if (summaryDiv.parentNode) {
                    summaryDiv.remove();
                }
            }, 5000);
        }
    }
    
    /**
     * Validator zerstören
     */
    destroy() {
        if (this.progressBar && this.progressBar.parentNode) {
            this.progressBar.remove();
        }
        
        // Event-Listener entfernen
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.removeEventListener('input', this.validateField);
            input.removeEventListener('blur', this.validateField);
            input.removeEventListener('focus', this.onFieldFocus);
        });
        
        console.log('🗑️ Formular-Validator zerstört');
    }
}

// Globale Funktionen für einfache Verwendung
window.initFormValidator = function(formId, options = {}) {
    return new FormValidator(formId, options);
};
