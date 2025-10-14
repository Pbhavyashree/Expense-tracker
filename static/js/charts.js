// Chart.js for expense tracking visualization
class ExpenseChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
    }

    // Draw monthly income vs expense chart with both bars and lines
    drawMonthlyChart(monthlyData) {
        if (!monthlyData || monthlyData.length === 0) {
            this.drawNoDataMessage();
            return;
        }

        this.clearCanvas();
        
        const padding = 80;
        const chartWidth = this.canvas.width - 2 * padding;
        const chartHeight = this.canvas.height - 2 * padding;
        
        // Find max value for scaling
        let maxValue = 0;
        monthlyData.forEach(data => {
            maxValue = Math.max(maxValue, data.income, data.expense);
        });
        
        if (maxValue === 0) {
            this.drawNoDataMessage();
            return;
        }
        
        maxValue = maxValue * 1.2; // Add 20% padding for better view
        
        // Draw background gradient
        this.drawChartBackground(padding, chartWidth, chartHeight);
        
        // Draw grid lines
        this.drawGridLines(padding, chartWidth, chartHeight, maxValue);
        
        // Draw axes
        this.drawAxes(padding, chartWidth, chartHeight);
        
        // Draw bars
        const barWidth = chartWidth / (monthlyData.length * 3);
        const barSpacing = barWidth * 0.8;
        
        monthlyData.forEach((data, index) => {
            const x = padding + (index * (barWidth * 2.5 + barSpacing));
            
            // Income bar (green with gradient)
            const incomeHeight = (data.income / maxValue) * chartHeight;
            this.drawGradientBar(x, padding + chartHeight - incomeHeight, barWidth, incomeHeight, '#2ecc71', '#27ae60');
            
            // Expense bar (red with gradient)
            const expenseHeight = (data.expense / maxValue) * chartHeight;
            this.drawGradientBar(x + barWidth * 1.2, padding + chartHeight - expenseHeight, barWidth, expenseHeight, '#e74c3c', '#c0392b');
            
            // Month label
            this.drawText(data.month, x + barWidth, padding + chartHeight + 30, 'bold 13px Arial', '#444', 'center');
            
            // Value labels on top of bars
            if (incomeHeight > 20) {
                this.drawText(`€${data.income.toFixed(0)}`, x + barWidth/2, padding + chartHeight - incomeHeight - 5, '11px Arial', '#2ecc71', 'center');
            }
            if (expenseHeight > 20) {
                this.drawText(`€${data.expense.toFixed(0)}`, x + barWidth * 1.7, padding + chartHeight - expenseHeight - 5, '11px Arial', '#e74c3c', 'center');
            }
        });
        
        // Draw trend lines
        this.drawTrendLines(monthlyData, padding, chartWidth, chartHeight, maxValue);
        
        // Draw enhanced legend
        this.drawEnhancedLegend(padding, padding - 60);
        
        // Draw y-axis labels
        this.drawYAxisLabels(padding - 15, padding, chartHeight, maxValue);
        
        // Draw chart title
        this.drawText('Monthly Income vs Expenses with Trends', this.canvas.width / 2, 30, 'bold 18px Arial', '#333', 'center');
    }

    // Draw enhanced category pie chart
    drawCategoryChart(categoryData) {
        if (!categoryData || categoryData.length === 0) {
            this.drawNoDataMessage();
            return;
        }

        this.clearCanvas();
        
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2 + 20;
        const radius = Math.min(centerX, centerY) - 120;
        const innerRadius = radius * 0.4; // Create donut chart
        
        // Calculate total
        const total = categoryData.reduce((sum, item) => sum + item.amount, 0);
        
        if (total === 0) {
            this.drawNoDataMessage();
            return;
        }
        
        // Enhanced color palette
        const colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD',
            '#00D2D3', '#FF9F43', '#EE5A24', '#0abde3'
        ];
        
        let currentAngle = -Math.PI / 2; // Start from top
        
        // Draw background circle
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, radius + 5, 0, 2 * Math.PI);
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        this.ctx.fill();
        
        categoryData.forEach((item, index) => {
            const sliceAngle = (item.amount / total) * 2 * Math.PI;
            const color = colors[index % colors.length];
            
            // Create gradient for each slice
            const gradient = this.ctx.createRadialGradient(
                centerX, centerY, innerRadius,
                centerX, centerY, radius
            );
            gradient.addColorStop(0, color);
            gradient.addColorStop(1, this.darkenColor(color, 20));
            
            // Draw slice
            this.ctx.beginPath();
            this.ctx.moveTo(centerX, centerY);
            this.ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            this.ctx.closePath();
            this.ctx.fillStyle = gradient;
            this.ctx.fill();
            
            // Add stroke for separation
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 3;
            this.ctx.stroke();
            
            // Draw inner circle (donut hole)
            this.ctx.beginPath();
            this.ctx.arc(centerX, centerY, innerRadius, 0, 2 * Math.PI);
            this.ctx.fillStyle = '#ffffff';
            this.ctx.fill();
            
            // Draw percentage in the center of each slice
            const percentage = ((item.amount / total) * 100).toFixed(1);
            if (parseFloat(percentage) > 5) { // Only show percentage if slice is large enough
                const textAngle = currentAngle + sliceAngle / 2;
                const textRadius = (radius + innerRadius) / 2;
                const textX = centerX + Math.cos(textAngle) * textRadius;
                const textY = centerY + Math.sin(textAngle) * textRadius;
                
                this.drawText(`${percentage}%`, textX, textY, 'bold 12px Arial', '#ffffff', 'center');
            }
            
            currentAngle += sliceAngle;
        });
        
        // Draw center circle with total
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, innerRadius, 0, 2 * Math.PI);
        this.ctx.fillStyle = '#f8f9fa';
        this.ctx.fill();
        this.ctx.strokeStyle = '#e9ecef';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        
        // Draw total in center
        this.drawText('Total', centerX, centerY - 10, 'bold 14px Arial', '#666', 'center');
        this.drawText(`€${this.formatNumber(total)}`, centerX, centerY + 10, 'bold 18px Arial', '#333', 'center');
        
        // Draw legend
        this.drawCategoryLegend(categoryData, colors, total);
        
        // Draw title
        this.drawText('💰 Expenses by Category', centerX, 40, 'bold 20px Arial', '#333', 'center');
    }

    drawCategoryLegend(categoryData, colors, total) {
        const legendStartY = this.canvas.height - 100;
        const itemsPerRow = Math.ceil(categoryData.length / 2);
        const itemWidth = this.canvas.width / itemsPerRow;
        
        categoryData.forEach((item, index) => {
            const row = Math.floor(index / itemsPerRow);
            const col = index % itemsPerRow;
            const x = 20 + (col * itemWidth);
            const y = legendStartY + (row * 25);
            
            // Draw color box
            this.ctx.fillStyle = colors[index % colors.length];
            this.ctx.fillRect(x, y - 8, 15, 15);
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 1;
            this.ctx.strokeRect(x, y - 8, 15, 15);
            
            // Draw label
            const percentage = ((item.amount / total) * 100).toFixed(1);
            const label = `${item.category}: €${this.formatNumber(item.amount)} (${percentage}%)`;
            this.drawText(label, x + 25, y + 3, '11px Arial', '#333');
        });
    }

    darkenColor(color, percent) {
        const num = parseInt(color.replace("#",""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) - amt;
        const G = (num >> 8 & 0x00FF) - amt;
        const B = (num & 0x0000FF) - amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    }

    // Helper methods
    clearCanvas() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    drawAxes(padding, chartWidth, chartHeight) {
        this.ctx.beginPath();
        this.ctx.moveTo(padding, padding);
        this.ctx.lineTo(padding, padding + chartHeight);
        this.ctx.lineTo(padding + chartWidth, padding + chartHeight);
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
    }

    drawGridLines(padding, chartWidth, chartHeight, maxValue) {
        // Horizontal grid lines
        this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)';
        this.ctx.lineWidth = 1;
        this.ctx.setLineDash([2, 2]);
        
        for (let i = 0; i <= 8; i++) {
            const y = padding + (chartHeight / 8) * i;
            this.ctx.beginPath();
            this.ctx.moveTo(padding, y);
            this.ctx.lineTo(padding + chartWidth, y);
            this.ctx.stroke();
        }
        
        // Vertical grid lines
        this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.05)';
        for (let i = 1; i <= 10; i++) {
            const x = padding + (chartWidth / 10) * i;
            this.ctx.beginPath();
            this.ctx.moveTo(x, padding);
            this.ctx.lineTo(x, padding + chartHeight);
            this.ctx.stroke();
        }
        
        this.ctx.setLineDash([]); // Reset line dash
    }

    drawBar(x, y, width, height, color) {
        this.ctx.fillStyle = color;
        this.ctx.fillRect(x, y, width, height);
        
        // Add border
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(x, y, width, height);
    }

    drawGradientBar(x, y, width, height, color1, color2) {
        // Create gradient
        const gradient = this.ctx.createLinearGradient(x, y, x, y + height);
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(x, y, width, height);
        
        // Add subtle border
        this.ctx.strokeStyle = color2;
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(x, y, width, height);
        
        // Add highlight effect
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
        this.ctx.fillRect(x, y, width, height * 0.3);
    }

    drawChartBackground(padding, chartWidth, chartHeight) {
        // Create subtle background gradient
        const gradient = this.ctx.createLinearGradient(0, padding, 0, padding + chartHeight);
        gradient.addColorStop(0, 'rgba(247, 250, 252, 0.8)');
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0.9)');
        
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(padding, padding, chartWidth, chartHeight);
    }

    drawTrendLines(monthlyData, padding, chartWidth, chartHeight, maxValue) {
        if (monthlyData.length < 2) return;
        
        const pointSpacing = chartWidth / (monthlyData.length - 1);
        
        // Income trend line
        this.ctx.strokeStyle = '#2ecc71';
        this.ctx.lineWidth = 3;
        this.ctx.setLineDash([]);
        this.ctx.beginPath();
        
        monthlyData.forEach((data, index) => {
            const x = padding + (index * pointSpacing);
            const y = padding + chartHeight - (data.income / maxValue) * chartHeight;
            
            if (index === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
            
            // Draw point
            this.ctx.save();
            this.ctx.fillStyle = '#2ecc71';
            this.ctx.beginPath();
            this.ctx.arc(x, y, 4, 0, 2 * Math.PI);
            this.ctx.fill();
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            this.ctx.restore();
        });
        this.ctx.stroke();
        
        // Expense trend line
        this.ctx.strokeStyle = '#e74c3c';
        this.ctx.lineWidth = 3;
        this.ctx.setLineDash([]);
        this.ctx.beginPath();
        
        monthlyData.forEach((data, index) => {
            const x = padding + (index * pointSpacing);
            const y = padding + chartHeight - (data.expense / maxValue) * chartHeight;
            
            if (index === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
            
            // Draw point
            this.ctx.save();
            this.ctx.fillStyle = '#e74c3c';
            this.ctx.beginPath();
            this.ctx.arc(x, y, 4, 0, 2 * Math.PI);
            this.ctx.fill();
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            this.ctx.restore();
        });
        this.ctx.stroke();
    }

    drawText(text, x, y, font, color, align = 'left') {
        this.ctx.font = font;
        this.ctx.fillStyle = color;
        this.ctx.textAlign = align;
        this.ctx.fillText(text, x, y);
    }

    drawLegend(x, y) {
        // Income legend
        this.ctx.fillStyle = '#2ecc71';
        this.ctx.fillRect(x, y, 15, 15);
        this.drawText('Income', x + 25, y + 12, '12px Arial', '#333');
        
        // Expense legend
        this.ctx.fillStyle = '#e74c3c';
        this.ctx.fillRect(x + 100, y, 15, 15);
        this.drawText('Expense', x + 125, y + 12, '12px Arial', '#333');
    }

    drawEnhancedLegend(x, y) {
        const legendItems = [
            { color: '#2ecc71', label: '📊 Income Bars', type: 'bar' },
            { color: '#e74c3c', label: '📊 Expense Bars', type: 'bar' },
            { color: '#2ecc71', label: '📈 Income Trend', type: 'line' },
            { color: '#e74c3c', label: '📈 Expense Trend', type: 'line' }
        ];
        
        legendItems.forEach((item, index) => {
            const itemX = x + (index * 150);
            
            if (item.type === 'bar') {
                // Draw bar icon
                this.ctx.fillStyle = item.color;
                this.ctx.fillRect(itemX, y, 15, 15);
            } else {
                // Draw line icon
                this.ctx.strokeStyle = item.color;
                this.ctx.lineWidth = 3;
                this.ctx.beginPath();
                this.ctx.moveTo(itemX, y + 7);
                this.ctx.lineTo(itemX + 15, y + 7);
                this.ctx.stroke();
                
                // Draw point
                this.ctx.fillStyle = item.color;
                this.ctx.beginPath();
                this.ctx.arc(itemX + 7, y + 7, 3, 0, 2 * Math.PI);
                this.ctx.fill();
            }
            
            this.drawText(item.label, itemX + 25, y + 12, 'bold 12px Arial', '#333');
        });
    }

    drawYAxisLabels(x, padding, chartHeight, maxValue) {
        for (let i = 0; i <= 8; i++) {
            const value = (maxValue / 8) * (8 - i);
            const y = padding + (chartHeight / 8) * i + 5;
            if (value >= 0) {
                this.drawText(`€${this.formatNumber(value)}`, x, y, 'bold 11px Arial', '#666', 'right');
            }
        }
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        } else {
            return num.toFixed(0);
        }
    }

    drawNoDataMessage() {
        this.clearCanvas();
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        this.drawText('No data available', centerX, centerY, 'bold 16px Arial', '#666', 'center');
    }
}

// Initialize chart when page loads
document.addEventListener('DOMContentLoaded', function() {
    const chartCanvas = document.getElementById('expenseChart');
    if (chartCanvas) {
        const chart = new ExpenseChart('expenseChart');
        
        // Check if monthly data is available (from dashboard)
        if (typeof monthlyData !== 'undefined' && monthlyData.length > 0) {
            chart.drawMonthlyChart(monthlyData);
        }
        
        // Check if category data is available (from reports)
        if (typeof categoryData !== 'undefined' && categoryData.length > 0) {
            chart.drawCategoryChart(categoryData);
        }
    }
});

// Utility functions for form validation
function validateTransactionForm() {
    const amount = document.getElementById('amount').value;
    const date = document.getElementById('date').value;
    
    if (!amount || parseFloat(amount) <= 0) {
        alert('Please enter a valid amount greater than 0');
        return false;
    }
    
    if (!date) {
        alert('Please select a date');
        return false;
    }
    
    return true;
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

// Auto-resize canvas on window resize
window.addEventListener('resize', function() {
    const chartCanvas = document.getElementById('expenseChart');
    if (chartCanvas) {
        chartCanvas.width = chartCanvas.offsetWidth;
        chartCanvas.height = chartCanvas.offsetHeight;
        
        // Redraw chart with current data
        const chart = new ExpenseChart('expenseChart');
        if (typeof monthlyData !== 'undefined' && monthlyData.length > 0) {
            chart.drawMonthlyChart(monthlyData);
        }
        if (typeof categoryData !== 'undefined' && categoryData.length > 0) {
            chart.drawCategoryChart(categoryData);
        }
    }
});