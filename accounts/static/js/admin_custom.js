/* DO'KON Admin Custom JS - Quick Logout and Comprehensive UI Uzbek Translations */
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

    // 3. Frontenddagi barcha inglizcha mayda yozuvlarni to'liq o'zbekchalashtirish
    const modelDict = {
        'user': 'Xodim',
        'company': 'Do\'kon',
        'branch': 'Filial',
        'product': 'Mahsulot',
        'category': 'Kategoriya',
        'stock': 'Ombor qoldig\'i',
        'customer': 'Mijoz',
        'sale': 'Savdo',
        'sale item': 'Chekdagi tovar',
        'debt payment': 'Qarz to\'lovi',
        'sale return': 'Qaytarilgan tovar',
        'audit log': 'Audit jurnali',
        'group': 'Guruh',
        'permission': 'Huquq',
        'content type': 'Tizim turi',
        'session': 'Sessiya',
        'log entry': 'Tizim jurnali'
    };

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
        document.querySelectorAll('input[type="search"], input[name="q"], input.selector-filter').forEach(inp => {
            if (inp.placeholder) {
                if (inp.placeholder.startsWith('Search') || inp.placeholder.includes('Search')) {
                    inp.placeholder = inp.placeholder.replace('Search', 'Qidirish');
                } else if (inp.placeholder === 'Filter') {
                    inp.placeholder = 'Filtrlash...';
                }
            }
        });

        // FilteredSelectMultiple (Guruhlar va Huquqlar oynasi matnlari)
        // 1. Sarlavhalar
        document.querySelectorAll('.selector-available-title label, [id$="_from_label"]').forEach(el => {
            if (el.textContent.includes('permissions')) {
                el.textContent = 'Mavjud huquqlar';
            }
        });
        document.querySelectorAll('.selector-chosen-title label, [id$="_to_label"]').forEach(el => {
            if (el.textContent.includes('permissions')) {
                el.textContent = 'Tanlangan huquqlar';
            }
        });

        // 2. Tushuntirish matnlari (Helptexts)
        document.querySelectorAll('[id$="_choose_helptext"]').forEach(el => {
            if (el.textContent.includes('Choose') && el.textContent.includes('arrow')) {
                el.textContent = 'Tanlash uchun kerakli huquqlarni belgilang va "Tanlash" ko\'rsatkich tugmasini bosing.';
            }
        });
        document.querySelectorAll('[id$="_remove_helptext"]').forEach(el => {
            if (el.textContent.includes('Remove') && el.textContent.includes('arrow')) {
                el.textContent = 'Olib tashlash uchun kerakli huquqlarni belgilang va "Olib tashlash" ko\'rsatkich tugmasini bosing.';
            }
        });

        // 3. Tugmalar (Choose all, Remove all, Choose selected, Remove selected)
        document.querySelectorAll('.selector-chooseall').forEach(btn => {
            if (btn.textContent.includes('Choose all')) {
                btn.textContent = 'Barchasini tanlash';
            }
        });
        document.querySelectorAll('.selector-clearall').forEach(btn => {
            if (btn.textContent.includes('Remove all') || btn.textContent.includes('Clear all')) {
                btn.textContent = 'Barchasini olib tashlash';
            }
        });
        document.querySelectorAll('.selector-add').forEach(btn => {
            if (btn.title && btn.title.includes('Choose')) {
                btn.title = 'Tanlash';
            }
            if (btn.textContent.includes('Choose selected')) {
                btn.textContent = 'Tanlash';
            }
        });
        document.querySelectorAll('.selector-remove').forEach(btn => {
            if (btn.title && btn.title.includes('Remove')) {
                btn.title = 'Olib tashlash';
            }
            if (btn.textContent.includes('Remove selected')) {
                btn.textContent = 'Olib tashlash';
            }
        });

        // 4. Permission elementlari nomlari (Can add user -> Xodim: qo'shish huquqi)
        document.querySelectorAll('select[multiple] option').forEach(opt => {
            const text = opt.textContent.trim();
            const match = text.match(/^Can (add|change|delete|view) (.+)$/i);
            if (match) {
                const action = match[1].toLowerCase();
                const rawModel = match[2].toLowerCase().trim();
                const uzModel = modelDict[rawModel] || match[2];
                let uzAction = '';
                if (action === 'add') uzAction = "qo'shish huquqi";
                else if (action === 'change') uzAction = "tahrirlash huquqi";
                else if (action === 'delete') uzAction = "o'chirish huquqi";
                else if (action === 'view') uzAction = "ko'rish huquqi";

                opt.textContent = `${uzModel}: ${uzAction}`;
            }
        });

        // Modal sarlavhalari (Add another branch -> Yangi filial qo'shish)
        document.querySelectorAll('.modal-title').forEach(t => {
            let txt = t.textContent.trim();
            if (txt.startsWith('Add another ')) {
                const model = txt.replace('Add another ', '').trim();
                const uzModel = modelDict[model.toLowerCase()] || model;
                t.textContent = 'Yangi ' + uzModel + ' qo\'shish';
            }
        });

        // Form chap tomonidagi Permissions label
        document.querySelectorAll('label[for="id_permissions"], label[for="id_user_permissions"]').forEach(lbl => {
            if (lbl.textContent.trim() === 'Permissions') {
                lbl.textContent = 'Huquqlar (Ruxsatlar)';
            }
        });
    }

    localizeUI();
    setTimeout(localizeUI, 300);
    setTimeout(localizeUI, 800);
    setTimeout(localizeUI, 1500);

    const observer = new MutationObserver(function () {
        localizeUI();
    });
    observer.observe(document.body, { childList: true, subtree: true });
});
