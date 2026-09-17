/* DO'KON Admin Custom JS - Quick Logout and UI helpers */
document.addEventListener('DOMContentLoaded', function () {
    // 1. Top Navbar ga qizil "Chiqish" tugmasini qo'shish
    try {
        const rightNav = document.querySelector('.navbar-nav.ms-auto') || document.querySelector('.navbar-nav.ml-auto');
        if (rightNav && !document.getElementById('nav-logout-btn')) {
            const logoutLi = document.createElement('li');
            logoutLi.className = 'nav-item d-flex align-items-center';
            logoutLi.id = 'nav-logout-btn';
            logoutLi.innerHTML = `
                <a href="/logout/" class="btn-logout-nav" title="Tizimdan chiqish">
                    <i class="fas fa-sign-out-alt mr-1 me-1"></i> Chiqish
                </a>
            `;
            rightNav.appendChild(logoutLi);
        }
    } catch (e) {
        console.warn('Navbar logout button error:', e);
    }

    // 2. Yon menyu (Sidebar) ning eng pastiga "Tizimdan Chiqish" tugmasini qo'shish
    try {
        const sidebarNav = document.querySelector('#jazzy-sidebar .nav-sidebar') ||
                           document.querySelector('#jazzy-sidebar ul.nav') ||
                           document.querySelector('aside.app-sidebar ul.nav');
        if (sidebarNav && !document.getElementById('sidebar-logout-btn')) {
            const sideLi = document.createElement('li');
            sideLi.className = 'nav-item mt-3 mb-4';
            sideLi.id = 'sidebar-logout-btn';
            sideLi.innerHTML = `
                <a href="/logout/" class="nav-link text-white shadow-sm" style="background-color: #dc3545 !important; border-radius: 6px; font-weight: bold; margin: 4px 10px; display: flex; align-items: center;">
                    <i class="nav-icon fas fa-sign-out-alt mr-2 me-2" style="font-size: 1.1rem;"></i>
                    <p style="margin: 0;">Tizimdan Chiqish</p>
                </a>
            `;
            sidebarNav.appendChild(sideLi);
        }
    } catch (e) {
        console.warn('Sidebar logout button error:', e);
    }
});
