/* Dynamic Branch Add Helper for Jazzmin Admin */
document.addEventListener('DOMContentLoaded', function () {
    const companySelect = document.getElementById('id_company');
    const addBranchBtn = document.getElementById('add_id_branch');

    if (companySelect && addBranchBtn) {
        function updateBranchAddLink() {
            const companyId = companySelect.value;
            let currentHref = addBranchBtn.getAttribute('href') || '';
            // Remove existing company query parameter
            currentHref = currentHref.replace(/([?&])company=\d+/g, '');
            if (companyId) {
                const sep = currentHref.includes('?') ? '&' : '?';
                addBranchBtn.setAttribute('href', currentHref + sep + 'company=' + encodeURIComponent(companyId));
            } else {
                addBranchBtn.setAttribute('href', currentHref);
            }
        }

        companySelect.addEventListener('change', updateBranchAddLink);
        addBranchBtn.addEventListener('mousedown', updateBranchAddLink);
        addBranchBtn.addEventListener('click', updateBranchAddLink);
        updateBranchAddLink();
    }
});
