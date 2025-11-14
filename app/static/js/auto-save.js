/**
 * Auto-Save System für BESS-Simulation Formulare
 * ===============================================
 * 
 * Features:
 * - Automatisches Speichern alle 30 Sekunden
 * - Real-time Validierung
 * - Progress-Indikatoren
 * - Undo/Redo-Funktionalität
 * - Formular-Templates
 */

class AutoSaveSystem {
    constructor(formId, options = {}) {
        this.formId = formId;
        this.form = document.getElementById(formId);
        this.autoSaveInterval = options.autoSaveInterval || 30000; // 30 Sekunden
        this.autoSaveTimer = null;
        this.lastSavedData = null;
        this.undoStack = [];
        this.redoStack = [];
        this.maxUndoSteps = options.maxUndoSteps || 10;
        this.isSaving = false;
        this.hasUnsavedChanges = false;
        this.handleNativeSubmit = options.handleNativeSubmit !== false;
        
        // Progress-Indikator erstellen
        this.createProgressIndicator();
        
        // Event-Listener registrieren
        this.initializeEventListeners();
        
        // Auto-Save Timer starten
        this.startAutoSave();
        
        console.log(`🚀 Auto-Save System für Formular "${formId}" initialisiert`);
    }
    
    /**
     * Progress-Indikator erstellen
     */
    createProgressIndicator() {
        // Progress-Bar erstellen
        this.progressBar = document.createElement('div');
        this.progressBar.id = 'auto-save-progress';
        this.progressBar.className = 'fixed top-0 left-0 w-full h-1 bg-gray-200 z-50';
        this.progressBar.innerHTML = `
            <div class="h-full bg-blue-500 transition-all duration-300 ease-out" style="width: 0%"></div>
        `;
        document.body.appendChild(this.progressBar);
        
        // Status-Indikator erstellen
        this.statusIndicator = document.createElement('div');
        this.statusIndicator.id = 'auto-save-status';
        this.statusIndicator.className = 'fixed top-4 right-4 bg-white border border-gray-300 rounded-lg shadow-lg px-4 py-2 text-sm z-50 hidden';
        this.statusIndicator.innerHTML = `
            <div class="flex items-center space-x-2">
                <div class="w-2 h-2 rounded-full bg-gray-400" id="status-dot"></div>
                <span id="status-text">Bereit</span>
            </div>
        `;
        document.body.appendChild(this.statusIndicator);
    }
    
    /**
     * Event-Listener initialisieren
     */
    initializeEventListeners() {
        if (!this.form) return;
        
        // Alle Input-Felder überwachen
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', () => this.onFormChange());
            input.addEventListener('change', () => this.onFormChange());
        });
        
        // Formular-Submit abfangen
        if (this.handleNativeSubmit) {
            this.form.addEventListener('submit', (e) => this.onFormSubmit(e));
        }
        
        // Browser-Navigation abfangen (unsaved changes)
        window.addEventListener('beforeunload', (e) => this.onBeforeUnload(e));
        
        // Keyboard-Shortcuts
        document.addEventListener('keydown', (e) => this.onKeyDown(e));
    }
    
    /**
     * Auto-Save Timer starten
     */
    startAutoSave() {
        this.autoSaveTimer = setInterval(() => {
            if (this.hasUnsavedChanges && !this.isSaving) {
                this.autoSave();
            }
        }, this.autoSaveInterval);
    }
    
    /**
     * Auto-Save Timer stoppen
     */
    stopAutoSave() {
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
            this.autoSaveTimer = null;
        }
    }
    
    /**
     * Formular-Änderung erkannt
     */
    onFormChange() {
        this.hasUnsavedChanges = true;
        this.updateStatus('Änderungen erkannt', 'warning');
        this.addToUndoStack();
    }
    
    /**
     * Automatisches Speichern
     */
    async autoSave() {
        if (this.isSaving) return;
        
        this.isSaving = true;
        this.updateProgress(10);
        this.updateStatus('Speichere...', 'saving');
        
        try {
            const formData = this.getFormData();
            
            // Validierung
            if (!this.validateFormData(formData)) {
                this.updateStatus('Validierungsfehler', 'error');
                this.updateProgress(0);
                return;
            }
            
            this.updateProgress(30);
            
            // Auto-Save API aufrufen
            const response = await this.saveFormData(formData);
            
            this.updateProgress(80);
            
            if (response.success) {
                this.lastSavedData = formData;
                this.hasUnsavedChanges = false;
                this.updateStatus('Auto-gespeichert', 'success');
                this.updateProgress(100);
                
                // Progress-Bar nach 2 Sekunden ausblenden
                setTimeout(() => {
                    this.updateProgress(0);
                }, 2000);
                
                console.log('✅ Auto-Save erfolgreich');
            } else {
                throw new Error(response.error || 'Unbekannter Fehler');
            }
            
        } catch (error) {
            console.error('❌ Auto-Save Fehler:', error);
            this.updateStatus('Auto-Save fehlgeschlagen', 'error');
            this.updateProgress(0);
        } finally {
            this.isSaving = false;
        }
    }
    
    /**
     * Formular-Daten sammeln
     */
    getFormData() {
        const formData = new FormData(this.form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            // Numerische Werte konvertieren
            if (value && !isNaN(value) && value !== '') {
                data[key] = parseFloat(value);
            } else if (value === '') {
                data[key] = null;
            } else {
                data[key] = value;
            }
        }
        
        return data;
    }
    
    /**
     * Formular-Daten validieren
     */
    validateFormData(data) {
        const errors = [];
        
        // Pflichtfelder prüfen
        if (!data.name || data.name.trim() === '') {
            errors.push('Projektname ist erforderlich');
        }
        
        // Numerische Validierung
        if (data.bess_size && data.bess_size <= 0) {
            errors.push('BESS-Größe muss größer als 0 sein');
        }
        
        if (data.bess_power && data.bess_power <= 0) {
            errors.push('BESS-Leistung muss größer als 0 sein');
        }
        
        if (data.current_electricity_cost && data.current_electricity_cost <= 0) {
            errors.push('Stromkosten müssen größer als 0 sein');
        }
        
        // Fehler anzeigen
        if (errors.length > 0) {
            this.showValidationErrors(errors);
            return false;
        }
        
        return true;
    }
    
    /**
     * Validierungsfehler anzeigen
     */
    showValidationErrors(errors) {
        // Bestehende Fehler entfernen
        const existingErrors = document.querySelectorAll('.validation-error');
        existingErrors.forEach(error => error.remove());
        
        // Neue Fehler hinzufügen
        errors.forEach(error => {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'validation-error text-red-600 text-sm mt-1';
            errorDiv.textContent = error;
            
            // Fehler an passende Stelle einfügen
            const nameInput = document.getElementById('projectName');
            if (nameInput && error.includes('Projektname')) {
                nameInput.parentNode.appendChild(errorDiv);
            }
        });
    }
    
    /**
     * Formular-Daten speichern
     */
    async saveFormData(data) {
        // Bestimme API-Endpoint basierend auf Formular-Typ
        const isEdit = this.formId.includes('edit');
        const projectId = this.getProjectId();
        
        let url, method;
        if (isEdit && projectId) {
            url = `/api/projects/${projectId}/auto-save`;
            method = 'PUT';
        } else {
            url = '/api/projects/auto-save';
            method = 'POST';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        return await response.json();
    }
    
    /**
     * Projekt-ID extrahieren
     */
    getProjectId() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('id') || null;
    }
    
    /**
     * Progress-Bar aktualisieren
     */
    updateProgress(percentage) {
        const progressBar = this.progressBar.querySelector('div');
        progressBar.style.width = `${percentage}%`;
    }
    
    /**
     * Status-Indikator aktualisieren
     */
    updateStatus(text, type = 'info') {
        const statusText = this.statusIndicator.querySelector('#status-text');
        const statusDot = this.statusIndicator.querySelector('#status-dot');
        
        statusText.textContent = text;
        this.statusIndicator.classList.remove('hidden');
        
        // Status-Typ setzen
        statusDot.className = 'w-2 h-2 rounded-full';
        switch (type) {
            case 'success':
                statusDot.classList.add('bg-green-500');
                break;
            case 'warning':
                statusDot.classList.add('bg-yellow-500');
                break;
            case 'error':
                statusDot.classList.add('bg-red-500');
                break;
            case 'saving':
                statusDot.classList.add('bg-blue-500');
                break;
            default:
                statusDot.classList.add('bg-gray-400');
        }
        
        // Status nach 3 Sekunden ausblenden (außer bei Fehlern)
        if (type !== 'error') {
            setTimeout(() => {
                this.statusIndicator.classList.add('hidden');
            }, 3000);
        }
    }
    
    /**
     * Undo/Redo System
     */
    addToUndoStack() {
        const currentData = this.getFormData();
        
        // Nur hinzufügen wenn sich Daten geändert haben
        if (JSON.stringify(currentData) !== JSON.stringify(this.undoStack[this.undoStack.length - 1])) {
            this.undoStack.push(JSON.parse(JSON.stringify(currentData)));
            
            // Stack-Größe begrenzen
            if (this.undoStack.length > this.maxUndoSteps) {
                this.undoStack.shift();
            }
            
            // Redo-Stack leeren
            this.redoStack = [];
        }
    }
    
    /**
     * Undo (Rückgängig)
     */
    undo() {
        if (this.undoStack.length > 1) {
            const currentData = this.undoStack.pop();
            this.redoStack.push(currentData);
            
            const previousData = this.undoStack[this.undoStack.length - 1];
            this.setFormData(previousData);
            
            this.updateStatus('Rückgängig gemacht', 'info');
        }
    }
    
    /**
     * Redo (Wiederholen)
     */
    redo() {
        if (this.redoStack.length > 0) {
            const redoData = this.redoStack.pop();
            this.undoStack.push(redoData);
            
            this.setFormData(redoData);
            
            this.updateStatus('Wiederholt', 'info');
        }
    }
    
    /**
     * Formular-Daten setzen
     */
    setFormData(data) {
        Object.keys(data).forEach(key => {
            const element = this.form.querySelector(`[name="${key}"]`);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = data[key];
                } else {
                    element.value = data[key] || '';
                }
            }
        });
    }
    
    /**
     * Keyboard-Shortcuts
     */
    onKeyDown(e) {
        // Ctrl+S: Manuelles Speichern
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            this.manualSave();
        }
        
        // Ctrl+Z: Undo
        if (e.ctrlKey && e.key === 'z') {
            e.preventDefault();
            this.undo();
        }
        
        // Ctrl+Y: Redo
        if (e.ctrlKey && e.key === 'y') {
            e.preventDefault();
            this.redo();
        }
    }
    
    /**
     * Manuelles Speichern
     */
    async manualSave() {
        this.updateStatus('Manuelles Speichern...', 'saving');
        await this.autoSave();
    }
    
    /**
     * Formular-Submit abfangen
     */
    onFormSubmit(e) {
        // Auto-Save vor dem Submit
        if (this.hasUnsavedChanges) {
            e.preventDefault();
            this.manualSave().then(() => {
                // Nach erfolgreichem Speichern Submit fortsetzen
                this.form.submit();
            });
        }
    }
    
    /**
     * Browser-Navigation abfangen
     */
    onBeforeUnload(e) {
        if (this.hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = 'Sie haben ungespeicherte Änderungen. Möchten Sie die Seite wirklich verlassen?';
            return e.returnValue;
        }
    }
    
    /**
     * System zerstören
     */
    destroy() {
        this.stopAutoSave();
        
        // Event-Listener entfernen
        if (this.form) {
            this.form.removeEventListener('submit', this.onFormSubmit);
        }
        
        // UI-Elemente entfernen
        if (this.progressBar) {
            this.progressBar.remove();
        }
        if (this.statusIndicator) {
            this.statusIndicator.remove();
        }
        
        console.log('🗑️ Auto-Save System zerstört');
    }
}

/**
 * Formular-Templates System
 */
class FormTemplates {
    constructor() {
        this.templates = {
            'klein-bess': {
                name: 'Kleines BESS-System',
                description: 'Für kleine Gewerbebetriebe',
                data: {
                    bess_size: 100,
                    bess_power: 50,
                    pv_power: 50,
                    current_electricity_cost: 12.5,
                    daily_cycles: 1.0
                }
            },
            'mittel-bess': {
                name: 'Mittleres BESS-System',
                description: 'Für mittlere Unternehmen',
                data: {
                    bess_size: 500,
                    bess_power: 200,
                    pv_power: 200,
                    current_electricity_cost: 12.5,
                    daily_cycles: 1.2
                }
            },
            'gross-bess': {
                name: 'Großes BESS-System',
                description: 'Für große Industriebetriebe',
                data: {
                    bess_size: 2000,
                    bess_power: 800,
                    pv_power: 1000,
                    current_electricity_cost: 12.5,
                    daily_cycles: 1.5
                }
            },
            'pv-fokus': {
                name: 'PV-Fokus System',
                description: 'Maximale PV-Integration',
                data: {
                    bess_size: 300,
                    bess_power: 150,
                    pv_power: 500,
                    current_electricity_cost: 12.5,
                    daily_cycles: 1.0
                }
            }
        };
    }
    
    /**
     * Template-Selector erstellen
     */
    createTemplateSelector(formId) {
        const form = document.getElementById(formId);
        if (!form) return;
        
        const templateDiv = document.createElement('div');
        templateDiv.className = 'mb-6 p-4 bg-gray-50 rounded-lg';
        templateDiv.innerHTML = `
            <h3 class="text-lg font-semibold text-gray-900 mb-3">Formular-Vorlagen</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                ${Object.keys(this.templates).map(key => `
                    <button type="button" 
                            class="template-btn p-3 text-left border border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
                            data-template="${key}">
                        <div class="font-medium text-gray-900">${this.templates[key].name}</div>
                        <div class="text-sm text-gray-600">${this.templates[key].description}</div>
                    </button>
                `).join('')}
            </div>
        `;
        
        // Vor dem ersten Formular-Bereich einfügen
        const firstSection = form.querySelector('.bg-gray-50, .bg-blue-50, .bg-green-50');
        if (firstSection) {
            firstSection.parentNode.insertBefore(templateDiv, firstSection);
        }
        
        // Event-Listener für Template-Buttons
        templateDiv.querySelectorAll('.template-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const templateKey = btn.dataset.template;
                this.applyTemplate(formId, templateKey);
            });
        });
    }
    
    /**
     * Template anwenden
     */
    applyTemplate(formId, templateKey) {
        const template = this.templates[templateKey];
        if (!template) return;
        
        const form = document.getElementById(formId);
        if (!form) return;
        
        // Template-Daten in Formular eintragen
        Object.keys(template.data).forEach(key => {
            const element = form.querySelector(`[name="${key}"]`);
            if (element) {
                element.value = template.data[key];
                // Change-Event auslösen
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
        
        // Benachrichtigung anzeigen
        this.showNotification(`Template "${template.name}" angewendet`, 'success');
    }
    
    /**
     * Benachrichtigung anzeigen
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 left-1/2 transform -translate-x-1/2 bg-white border border-gray-300 rounded-lg shadow-lg px-4 py-2 text-sm z-50`;
        notification.textContent = message;
        
        // Typ-spezifische Styling
        if (type === 'success') {
            notification.classList.add('border-green-500', 'bg-green-50');
        }
        
        document.body.appendChild(notification);
        
        // Nach 3 Sekunden entfernen
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Globale Funktionen für einfache Verwendung
window.initAutoSave = function(formId, options = {}) {
    return new AutoSaveSystem(formId, options);
};

window.initFormTemplates = function(formId) {
    const templates = new FormTemplates();
    templates.createTemplateSelector(formId);
    return templates;
};
