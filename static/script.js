/**
 * SAR-BOT PRO - AI Camera System
 * Frontend JavaScript for real-time updates
 */

class SARBotDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.setupPolling();
        this.animateStartup();
    }

    // Fetch and update system status
    async updateStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            // Update sensor values with animation
            this.animateValue('gas-value', data.sensor_data.gas_level);
            this.animateValue('dust-value', data.sensor_data.dust_pm25);
            this.animateValueDecimal('temp-value', data.sensor_data.temperature, 1);
            this.animateValue('co-value', data.sensor_data.co_level);
            this.animateValue('signal-value', Math.round(data.sensor_data.signal_strength), '%');
            this.animateValue('battery-value', Math.round(data.sensor_data.battery_level), '%');
            
            // Update detection info
            const detectionInfo = document.getElementById('detection-info');
            const personCount = detectionInfo.querySelector('.person-count');
            personCount.textContent = data.detected_persons;
            
            if (data.detected_persons > 0) {
                detectionInfo.classList.add('active');
            } else {
                detectionInfo.classList.remove('active');
            }
            
        } catch (error) {
            console.error('Failed to fetch status:', error);
        }
    }

    // Fetch and update logs
    async updateLogs() {
        try {
            const response = await fetch('/api/logs');
            const data = await response.json();
            
            const logsContent = document.getElementById('logs-content');
            let html = '';
            
            data.logs.forEach(log => {
                const isHighlight = log.message.includes('AI VISION') || 
                                   log.message.includes('PHÁT HIỆN');
                html += `
                    <div class="log-entry">
                        <span class="log-time">[${log.time}]</span>
                        <span class="log-arrow">&gt;</span>
                        <span class="log-message ${isHighlight ? 'highlight' : ''}">${log.message}</span>
                    </div>
                `;
            });
            
            html += '<div class="cursor-blink"></div>';
            logsContent.innerHTML = html;
            
        } catch (error) {
            console.error('Failed to fetch logs:', error);
        }
    }

    // Animate number value changes
    animateValue(elementId, newValue, suffix = '') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const currentValue = parseInt(element.textContent) || 0;
        const diff = newValue - currentValue;
        
        if (Math.abs(diff) < 1) {
            element.textContent = newValue + suffix;
            return;
        }
        
        const duration = 300;
        const steps = 10;
        const stepValue = diff / steps;
        const stepTime = duration / steps;
        
        let step = 0;
        const interval = setInterval(() => {
            step++;
            const value = Math.round(currentValue + stepValue * step);
            element.textContent = value + suffix;
            
            if (step >= steps) {
                clearInterval(interval);
                element.textContent = newValue + suffix;
            }
        }, stepTime);
    }

    // Animate decimal value (for temperature)
    animateValueDecimal(elementId, newValue, decimals = 1) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const currentValue = parseFloat(element.textContent) || 0;
        const diff = newValue - currentValue;
        
        if (Math.abs(diff) < 0.1) {
            element.textContent = newValue.toFixed(decimals);
            return;
        }
        
        const duration = 300;
        const steps = 10;
        const stepValue = diff / steps;
        const stepTime = duration / steps;
        
        let step = 0;
        const interval = setInterval(() => {
            step++;
            const value = currentValue + stepValue * step;
            element.textContent = value.toFixed(decimals);
            
            if (step >= steps) {
                clearInterval(interval);
                element.textContent = newValue.toFixed(decimals);
            }
        }, stepTime);
    }

    // Startup animation
    animateStartup() {
        const cards = document.querySelectorAll('.sensor-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 200 * (index + 1));
        });
        
        // Logs panel animation
        const logsPanel = document.querySelector('.logs-panel');
        if (logsPanel) {
            logsPanel.style.opacity = '0';
            setTimeout(() => {
                logsPanel.style.transition = 'opacity 0.5s ease';
                logsPanel.style.opacity = '1';
            }, 600);
        }
    }

    // Setup polling for real-time updates
    setupPolling() {
        // Initial update
        this.updateStatus();
        this.updateLogs();
        
        // Poll every 2 seconds
        setInterval(() => this.updateStatus(), 2000);
        setInterval(() => this.updateLogs(), 3000);
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new SARBotDashboard();
});

// Add glitch effect occasionally
setInterval(() => {
    const videoStream = document.querySelector('.video-stream');
    if (videoStream && Math.random() > 0.95) {
        videoStream.style.filter = 'hue-rotate(90deg) saturate(2)';
        setTimeout(() => {
            videoStream.style.filter = 'none';
        }, 100);
    }
}, 1000);

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Press 'F' for fullscreen camera
    if (e.key === 'f' || e.key === 'F') {
        const cameraFeed = document.querySelector('.camera-feed');
        if (cameraFeed) {
            if (document.fullscreenElement) {
                document.exitFullscreen();
            } else {
                cameraFeed.requestFullscreen();
            }
        }
    }
});


