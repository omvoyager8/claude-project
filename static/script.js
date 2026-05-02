// Global elements
const particlesCanvas = document.getElementById('particles');
const confettiCanvas = document.getElementById('confetti');
const nav = document.getElementById("main-nav");
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const result = document.getElementById('result');
const btn = document.querySelector('.btn');
const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('nav a[href^="#"]');
const mobileMenu = document.getElementById('mobile-menu');

// Initialize canvas
let particlesCtx = particlesCanvas.getContext('2d');
let confettiCtx = confettiCanvas.getContext('2d');
particlesCanvas.width = window.innerWidth;
particlesCanvas.height = window.innerHeight;
confettiCanvas.width = window.innerWidth;
confettiCanvas.height = window.innerHeight;

// 1. PARTICLE BACKGROUND
class Particle {
    constructor() {
        this.x = Math.random() * particlesCanvas.width;
        this.y = Math.random() * particlesCanvas.height;
        this.size = Math.random() * 2 + 0.5;
        this.speedX = Math.random() * 0.5 - 0.25;
        this.speedY = Math.random() * 0.5 - 0.25;
    }
    
    update() {
        this.x += this.speedX;
        this.y += this.speedY;
        
        if (this.x > particlesCanvas.width || this.x < 0) this.speedX *= -1;
        if (this.y > particlesCanvas.height || this.y < 0) this.speedY *= -1;
    }
    
    draw() {
        particlesCtx.fillStyle = 'rgba(0, 217, 255, 0.6)';
        particlesCtx.beginPath();
        particlesCtx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        particlesCtx.fill();
    }
}

const particles = [];
for (let i = 0; i < 100; i++) {
    particles.push(new Particle());
}

function animateParticles() {
    particlesCtx.clearRect(0, 0, particlesCanvas.width, particlesCanvas.height);
    particles.forEach(p => {
        p.update();
        p.draw();
    });
    requestAnimationFrame(animateParticles);
}
animateParticles();

// Resize handler
window.addEventListener('resize', () => {
    particlesCanvas.width = window.innerWidth;
    particlesCanvas.height = window.innerHeight;
    confettiCanvas.width = window.innerWidth;
    confettiCanvas.height = window.innerHeight;
});

// 2. SMOOTH SCROLL NAVIGATION & ACTIVE STATE
function updateActiveNav() {
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop - 150;
        if (scrollY >= sectionTop) {
            current = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
}

window.addEventListener('scroll', updateActiveNav);
updateActiveNav(); // Initial call

// 3. MOBILE MENU TOGGLE
function toggleMobileMenu() {
    mobileMenu.classList.toggle('active');
    const toggleIcon = document.querySelector('.mobile-toggle i');
    toggleIcon.className = mobileMenu.classList.contains('active') 
        ? 'fas fa-times' 
        : 'fas fa-bars';
}

// 4. FILE UPLOAD FEEDBACK
function handleFileSelect(input) {
    if (input.files.length) {
        uploadBox.classList.add('active');
        result.innerHTML = `✅ File selected: <strong>${input.files[0].name}</strong><br>Click "Start Detection" to analyze!`;
        result.style.color = '#2e7d32';
        result.style.background = 'rgba(76, 175, 80, 0.15)';
    } else {
        uploadBox.classList.remove('active');
        result.innerHTML = 'Ready to Analyze.';
        result.style.color = 'var(--text-dark)';
        result.style.background = 'transparent';
    }
}

// 5. ENHANCED DETECTION ANIMATION WITH CONFETTI
async function detectAnomaly() {
    if (!fileInput.files.length) {
        result.innerHTML = '❌ Error: Please select a hyperspectral file first!';
        result.style.color = '#d32f2f';
        result.style.background = 'rgba(244, 67, 54, 0.15)';
        return;
    }
    
    // Disable button with loading states
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing... 0%';
    uploadBox.classList.remove('active');
    
    const fileName = fileInput.files[0].name;
    const stages = [
        { text: 'Stage 1: Analyzing spectral signatures & noise reduction...', color: '#004e92', delay: 1500, progress: 30 },
        { text: 'Stage 2: Running LRaSMD for background separation...', color: '#8d6e63', delay: 1800, progress: 65 },
        { text: 'Stage 3: Applying deep learning detection models...', color: '#2e7d32', delay: 2000, progress: 100 }
    ];
    
    for (let i = 0; i < stages.length; i++) {
        const stage = stages[i];
        result.innerHTML = stage.text;
        result.style.color = stage.color;
        btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Processing... ${stage.progress}%`;
        await new Promise(resolve => setTimeout(resolve, stage.delay));
    }
    
    const file = fileInput.files[0];
    

    const formData = new FormData();
    formData.append("file", file);

    try {

        const response = await fetch("http://localhost:5000/detect", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Server error");
        }
        const data = await response.json();

        result.innerHTML = `
            🎉 <strong>Detection Complete!</strong><br>
            Anomaly detected in <em>${fileName}</em><br>
            <img src="${data.result_image}" width="300" style="margin-top:10px;">
        `;

        result.style.color = '#2e7d32';
        result.style.background = 'rgba(76, 175, 80, 0.25)';

    } catch (error) {

        console.error(error);

        result.innerHTML = "❌ Backend error. Check console.";
        result.style.color = '#d32f2f';

    }

    btn.innerHTML = '<i class="fas fa-redo"></i> Analyze Another';
    btn.disabled = false;
    
    // Trigger confetti
    createConfetti();
}

// 6. CONFETTI EXPLOSION
function createConfetti() {
    const confettiPieces = [];
    const colors = ['#00d9ff', '#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b'];
    
    for (let i = 0; i < 150; i++) {
        confettiPieces.push({
            x: Math.random() * confettiCanvas.width,
            y: Math.random() * confettiCanvas.height - confettiCanvas.height,
            size: Math.random() * 8 + 4,
            speedX: Math.random() * 6 - 3,
            speedY: Math.random() * 3 + 3,
            rotation: Math.random() * 360,
            rotationSpeed: Math.random() * 10 - 5,
            color: colors[Math.floor(Math.random() * colors.length)],
            opacity: 1
        });
    }
    
    function animateConfetti() {
        confettiCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
        
        confettiPieces.forEach((piece, index) => {
            piece.y += piece.speedY;
            piece.x += piece.speedX;
            piece.rotation += piece.rotationSpeed;
            piece.opacity -= 0.015;
            
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
    
    content.classList.toggle('expanded');
    icon.style.transform = content.classList.contains('expanded') 
        ? 'rotate(180deg)' 
        : 'rotate(0deg)';
    button.innerHTML = content.classList.contains('expanded') 
        ? '<i class="fas fa-chevron-up"></i> Hide Details' 
        : '<i class="fas fa-chevron-down"></i> Show Details';
}

// 8. INTERSECTION OBSERVER FOR ANIMATIONS
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

// Observe cards and sections
document.querySelectorAll('.card, .content, .upload-box').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    observer.observe(el);
});

// Close mobile menu on outside click
document.addEventListener('click', (e) => {
    if (!nav.contains(e.target)) {
        mobileMenu.classList.remove('active');
        document.querySelector('.mobile-toggle i').className = 'fas fa-bars';
    }
});
