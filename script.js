document.addEventListener('DOMContentLoaded', () => {
    // 1. Tilt Effect (Works on all cards)
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const xPct = x / rect.width;
            const yPct = y / rect.height;

            const xTilt = (0.5 - yPct) * 10; 
            const yTilt = (xPct - 0.5) * 10; 

            card.style.transform = `perspective(1000px) rotateX(${xTilt}deg) rotateY(${yTilt}deg) translateY(-5px)`;
            card.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255,255,255,0.08), var(--glass-bg))`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = ''; 
            card.style.background = ''; 
        });
    });

    // 2. Status Logic (Only runs if the element exists)
    const statusText = document.getElementById('minecraft-status-text');
    
    // Only try to fetch status if we are on a page that actually requests it
    if (statusText) {
        const serverAddress = 'mc.venb.top';
        let isOnline = null;

        const checkServerStatus = async () => {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); 

            try {
                const response = await fetch(`https://api.mcsrvstat.us/3/${serverAddress}`, { signal: controller.signal });
                clearTimeout(timeoutId);
                const data = await response.json();
                isOnline = data.online;
                updateStatusText();
            } catch (error) {
                clearTimeout(timeoutId);
                console.error('Error checking server status:', error);
                if (isOnline === null) isOnline = false; 
                updateStatusText();
            }
        };

        const updateStatusText = () => {
            if (!statusText) return;
            if (isOnline === true) {
                statusText.innerHTML = '<span style="color: #55ff55;">Online</span>';
            } else if (isOnline === false) {
                statusText.innerHTML = '<span style="color: #ff5555;">Offline</span>';
            } else {
                statusText.innerHTML = '<span style="color: #ffff55;">Checking...</span>';
            }
        };

        checkServerStatus();
        setInterval(checkServerStatus, 60000); 
    }
    
    console.log('Venb Gateway Initialized 🚀');
});