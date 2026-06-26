// Global elements
let particlesCanvas, confettiCanvas, nav, uploadBox, fileInput, result, btn, sections, navLinks, mobileMenu;
let particlesCtx, confettiCtx;

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize elements
    particlesCanvas = document.getElementById('particles');
    confettiCanvas = document.getElementById('confetti');
    nav = document.querySelector("nav");
    uploadBox = document.getElementById('uploadBox');
    fileInput = document.getElementById('fileInput');
    result = document.getElementById('result');
    btn = document.querySelector('button[onclick="detectAnomaly()"]');
    sections = document.querySelectorAll('section');
    navLinks = document.querySelectorAll('nav a[href^="#"]');
    mobileMenu = document.getElementById('mobile-menu');

    // Initialize canvas
    particlesCtx = particlesCanvas.getContext('2d');
    confettiCtx = confettiCanvas.getContext('2d');
    particlesCanvas.width = window.innerWidth;
    particlesCanvas.height = window.innerHeight;
    confettiCanvas.width = window.innerWidth;
    confettiCanvas.height = window.innerHeight;

    // Start animations
    animateParticles();
    
    // Setup scroll listener
    window.addEventListener('scroll', updateActiveNav);
    updateActiveNav();
    
    // Setup observer
    setupObserver();
});

// 1. PARTICLE BACKGROUND
class Particle {
    constructor() {
        this.x = Math.random() * window.innerWidth;
        this.y = Math.random() * window.innerHeight;
        this.size = Math.random() * 2 + 0.5;
        this.speedX = Math.random() * 0.5 - 0.25;
        this.speedY = Math.random() * 0.5 - 0.25;
    }
    
    update() {
        this.x += this.speedX;
        this.y += this.speedY;
        
        if (this.x > window.innerWidth || this.x < 0) this.speedX *= -1;
        if (this.y > window.innerHeight || this.y < 0) this.speedY *= -1;
    }
    
    draw() {
        if (particlesCtx) {
            particlesCtx.fillStyle = 'rgba(6, 182, 212, 0.4)';
            particlesCtx.beginPath();
            particlesCtx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            particlesCtx.fill();
        }
    }
}

const particles = [];
for (let i = 0; i < 100; i++) {
    particles.push(new Particle());
}

function animateParticles() {
    if (particlesCtx && particlesCanvas) {
        particlesCtx.clearRect(0, 0, particlesCanvas.width, particlesCanvas.height);
        particles.forEach(p => {
            p.update();
            p.draw();
        });
    }
    requestAnimationFrame(animateParticles);
}

// Resize handler
window.addEventListener('resize', () => {
    if (particlesCanvas && confettiCanvas) {
        particlesCanvas.width = window.innerWidth;
        particlesCanvas.height = window.innerHeight;
        confettiCanvas.width = window.innerWidth;
        confettiCanvas.height = window.innerHeight;
    }
});

// 2. SMOOTH SCROLL NAVIGATION & ACTIVE STATE
function updateActiveNav() {
    let current = '';
    if (sections) {
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 150;
            if (scrollY >= sectionTop) {
                current = section.getAttribute('id');
            }
        });
    }
    
    if (navLinks) {
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    }
}

// 3. MOBILE MENU TOGGLE
function toggleMobileMenu() {
    if (mobileMenu) {
        mobileMenu.classList.toggle('hidden');
        mobileMenu.classList.toggle('flex');
        const toggleIcon = document.querySelector('nav button i');
        if (toggleIcon) {
            toggleIcon.className = mobileMenu.classList.contains('flex') 
                ? 'fas fa-times text-xl' 
                : 'fas fa-bars text-xl';
        }
    }
}

// 4. FILE UPLOAD FEEDBACK
function handleFileSelect(input) {
    if (input.files.length) {
        uploadBox.classList.add('border-green-500', 'bg-green-50');
        uploadBox.classList.remove('border-cyan-400');
        result.innerHTML = `<i class="fas fa-check-circle mr-2" style="color: #10b981;"></i>File selected: <strong>${input.files[0].name}</strong><br><span style="opacity: 0.8;">Click "Start Detection" to analyze!</span>`;
        result.className = 'mt-4 md:mt-6 text-center text-sm sm:text-base md:text-lg font-semibold p-3 md:p-4 rounded-xl bg-green-100 text-green-700';
    } else {
        uploadBox.classList.remove('border-green-500', 'bg-green-50');
        uploadBox.classList.add('border-cyan-400');
        result.innerHTML = 'Ready to Analyze.';
        result.className = 'mt-4 md:mt-6 text-center text-sm sm:text-base md:text-lg font-semibold p-3 md:p-4 rounded-xl opacity-70';
    }
}

// 5. ENHANCED DETECTION ANIMATION WITH CONFETTI
async function detectAnomaly() {
    if (!fileInput.files.length) {
        result.innerHTML = '<i class="fas fa-exclamation-circle mr-2" style="color: #ef4444;"></i>Error: Please select a hyperspectral file first!';
        result.className = 'mt-8 text-center text-base md:text-lg font-semibold p-4 md:p-6 rounded-xl opacity-70 transition-all duration-300 bg-gradient-to-br from-slate-800/50 to-red-900/30 backdrop-blur-xl border border-red-500/20 shadow-xl';
        return;
    }
    
    // Disable button with loading states
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2 md:mr-3"></i> Processing... 0%';
    uploadBox.classList.remove('border-green-500', 'bg-green-50');
    uploadBox.classList.add('border-cyan-400');
    
    const fileName = fileInput.files[0].name;
    const stages = [
        { text: '<i class="fas fa-brain mr-2"></i>Stage 1: AI analyzing spectral signatures & preprocessing...', color: '#7c3aed', delay: 1500, progress: 30 },
        { text: '<i class="fas fa-chart-line mr-2"></i>Stage 2: Applying dimensionality reduction (PCA)...', color: '#2563eb', delay: 1800, progress: 65 },
        { text: '<i class="fas fa-robot mr-2"></i>Stage 3: Running deep learning anomaly detection...', color: '#0891b2', delay: 2000, progress: 100 }
    ];
    
    for (let i = 0; i < stages.length; i++) {
        const stage = stages[i];
        result.innerHTML = stage.text;
        result.style.color = stage.color;
        result.className = 'mt-8 text-center text-base md:text-lg font-semibold p-4 md:p-6 rounded-xl opacity-70 transition-all duration-300 bg-gradient-to-br from-slate-800/50 to-indigo-900/30 backdrop-blur-xl border border-indigo-500/20 shadow-xl';
        btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-2 md:mr-3"></i> Processing... ${stage.progress}%`;
        await new Promise(resolve => setTimeout(resolve, stage.delay));
    }
    
    const file = fileInput.files[0];
    
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/detect", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Server error");
        }
        const data = await response.json();

        result.innerHTML = `
            <i class="fas fa-trophy mr-2 text-2xl" style="color: #f59e0b;"></i>
            <strong style="color: #10b981; font-size: 1.15em;">AI Detection Complete!</strong><br>
            <span style="opacity: 0.85; color: #e5e7eb;">Anomaly detected in <em>${fileName}</em></span><br>
            <img src="${data.result_image}" class="w-full max-w-xs sm:max-w-sm md:max-w-md mt-4 md:mt-6 rounded-lg mx-auto shadow-lg"><br>
            <a href="${data.report_url}" target="_blank" class="inline-block mt-4 md:mt-6 px-6 md:px-8 py-2.5 md:py-3 bg-gradient-to-r from-purple-600 to-blue-500 text-white rounded-lg text-sm md:text-base font-bold hover:shadow-lg transition-all">
                <i class="fas fa-file-pdf mr-2"></i>Download PDF Report
            </a>
        `;

        result.className = 'mt-8 text-center text-base md:text-lg font-semibold p-4 md:p-6 rounded-xl opacity-70 transition-all duration-300 bg-gradient-to-br from-slate-800/50 to-green-900/30 backdrop-blur-xl border border-green-500/20 shadow-xl';

    } catch (error) {
        console.error(error);
        result.innerHTML = '<i class="fas fa-times-circle mr-2" style="color: #ef4444;"></i>Backend error. Check console.';
        result.className = 'mt-8 text-center text-base md:text-lg font-semibold p-4 md:p-6 rounded-xl opacity-70 transition-all duration-300 bg-gradient-to-br from-slate-800/50 to-red-900/30 backdrop-blur-xl border border-red-500/20 shadow-xl';
    }

    btn.innerHTML = '<i class="fas fa-redo mr-2 md:mr-3"></i> Analyze Another';
    btn.disabled = false;
    
    // Trigger confetti
    createConfetti();
}

// Clear results function
function clearResults() {
    fileInput.value = '';
    result.innerHTML = '<i class="fas fa-robot text-teal-400 mr-2"></i>AI Detection System Ready';
    result.className = 'mt-8 text-center text-base md:text-lg font-semibold p-4 md:p-6 rounded-xl opacity-70 transition-all duration-300 bg-gradient-to-br from-slate-800/50 to-teal-900/30 backdrop-blur-xl border border-teal-500/20 shadow-xl';
    btn.innerHTML = '<i class="fas fa-search mr-2 md:mr-3"></i>Start AI Detection';
    btn.disabled = false;
    uploadBox.classList.remove('border-green-500', 'bg-green-50');
    uploadBox.classList.add('border-purple-400/50');
    
    // Hide processing status
    const processingStatus = document.getElementById('processingStatus');
    if (processingStatus) {
        processingStatus.classList.add('hidden');
    }
}

// 6. CONFETTI EXPLOSION
function createConfetti() {
    if (!confettiCtx || !confettiCanvas) return;
    
    const confettiPieces = [];
    const colors = ['#06b6d4', '#0ea5e9', '#3b82f6', '#1e40af', '#065f46', '#10b981', '#f59e0b', '#f97316'];
    
    for (let i = 0; i < 200; i++) {
        confettiPieces.push({
            x: Math.random() * confettiCanvas.width,
            y: Math.random() * confettiCanvas.height - confettiCanvas.height,
            size: Math.random() * 10 + 4,
            speedX: Math.random() * 8 - 4,
            speedY: Math.random() * 4 + 2,
            rotation: Math.random() * 360,
            rotationSpeed: Math.random() * 15 - 7,
            color: colors[Math.floor(Math.random() * colors.length)],
            opacity: 1
        });
    }
    
    function animateConfetti() {
        confettiCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
        
        confettiPieces.forEach((piece, index) => {
            piece.y += piece.speedY;
            piece.x += piece.speedX;
            piece.speedY += 0.1; // gravity
            piece.rotation += piece.rotationSpeed;
            piece.opacity -= 0.012;
            
            confettiCtx.save();
            confettiCtx.translate(piece.x, piece.y);
            confettiCtx.rotate(piece.rotation * Math.PI / 180);
            confettiCtx.globalAlpha = piece.opacity;
            confettiCtx.fillStyle = piece.color;
            confettiCtx.fillRect(-piece.size/2, -piece.size/2, piece.size, piece.size);
            confettiCtx.restore();
            
            if (piece.opacity <= 0) {
                confettiPieces.splice(index, 1);
            }
        });
        
        if (confettiPieces.length > 0) {
            requestAnimationFrame(animateConfetti);
        }
    }
    
    animateConfetti();
}

// 7. TOGGLE DETAILS
function toggleDetails(button) {
    const content = button.nextElementSibling;
    const icon = button.querySelector('i');
    
    if (content.classList.contains('max-h-0')) {
        content.classList.remove('max-h-0');
        content.classList.add('max-h-96');
        icon.style.transform = 'rotate(180deg)';
        button.innerHTML = '<i class="fas fa-chevron-up mr-1 md:mr-2"></i>Hide';
    } else {
        content.classList.add('max-h-0');
        content.classList.remove('max-h-96');
        icon.style.transform = 'rotate(0deg)';
        button.innerHTML = '<i class="fas fa-chevron-down mr-1 md:mr-2"></i>Details';
    }
}

// 8. INTERSECTION OBSERVER FOR ANIMATIONS
function setupObserver() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe sections for animations
    document.querySelectorAll('section > div').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        observer.observe(el);
    });
}

// Close mobile menu on outside click
document.addEventListener('click', (e) => {
    if (nav && mobileMenu && !nav.contains(e.target) && mobileMenu.classList.contains('flex')) {
        mobileMenu.classList.remove('flex');
        mobileMenu.classList.add('hidden');
        const toggleIcon = document.querySelector('nav button i');
        if (toggleIcon) {
            toggleIcon.className = 'fas fa-bars text-xl';
        }
    }
});