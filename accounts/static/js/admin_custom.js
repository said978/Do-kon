/* DO'KON Admin Custom JS - Quick Logout and UI Uzbek Translations */
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

    // 3. Frontenddagi inglizcha qolgan elementlarni o'zbekchalashtirish
    function localizeUI() {
        // Select dropdownlardagi "- Select an option -" yoki "---------"
        document.querySelectorAll('select option').forEach(opt => {
            const txt = opt.textContent.trim();
            if (txt === '- Select an option -' || txt === 'Select an option' || txt === '---------') {
                opt.textContent = '- Tanlang -';
            }
        });

        // Select2 rendered text
        document.querySelectorAll('.select2-selection__rendered').forEach(el => {
            const txt = el.textContent.trim();
            if (txt === '- Select an option -' || txt === 'Select an option') {
                el.textContent = '- Tanlang -';
            }
        });

        // Select2 placeholder
        document.querySelectorAll('.select2-selection__placeholder').forEach(el => {
            if (el.textContent.includes('Select an option')) {
                el.textContent = '- Tanlang -';
            }
        });

        // "Go" tugmasi
        document.querySelectorAll('button[type="submit"].button, button[name="index"]').forEach(btn => {
            if (btn.textContent.trim() === 'Go') {
                btn.textContent = 'Bajarish';
            }
        });

        // Qidiruv maydoni (Search)
        document.querySelectorAll('input[type="search"], input[name="q"]').forEach(inp => {
            if (inp.placeholder && (inp.placeholder.startsWith('Search') || inp.placeholder.includes('Search'))) {
                inp.placeholder = inp.placeholder.replace('Search', 'Qidirish');
            }
        });

        // Modal sarlavhalari (Add another branch -> Yangi filial qo'shish)
        document.querySelectorAll('.modal-title').forEach(t => {
            let txt = t.textContent.trim();
            if (txt.startsWith('Add another ')) {
                const model = txt.replace('Add another ', '').trim();
                const dict = {
                    'branch': 'filial',
                    'company': 'do\'kon',
                    'user': 'xodim',
                    'category': 'kategoriya',
                    'product': 'mahsulot',
                    'customer': 'mijoz'
                };
                const uzModel = dict[model.toLowerCase()] || model;
                t.textContent = 'Yangi ' + uzModel + ' qo\'shish';
            }
        });
    }

    localizeUI();
    setTimeout(localizeUI, 300);
    setTimeout(localizeUI, 1000);

    // Dynamic modal ochilganda ham yangilash
    const observer = new MutationObserver(function () {
        localizeUI();
    });
    observer.observe(document.body, { childList: true, subtree: true });
});
