function showTab(tabId) {
    // Hide all sections
    document.querySelectorAll('.settings-section').forEach(el => el.classList.remove('active'));
    // Show selected
    document.getElementById(tabId).classList.add('active');
    
    // Update nav items
    document.querySelectorAll('.settings-nav-item').forEach(el => el.classList.remove('active'));
    // Find the clicked element. Since this function is called onclick, we might need to handle event target more robustly 
    // or rely on the fact that existing inline onclick passes 'event' implicitly or just find the one with matching onclick?
    // Actually, the inline onclick was `onclick="showTab('general')"` on the element itself.
    // To make it cleaner in external file, we should attach event listeners or keep the logic simple.
    
    // Changing approach slightly for external JS: we can't easily use 'event.currentTarget' inside a function called from inline HTML 
    // unless we pass 'this' or 'event'. 
    // BETTER APPROACH for Unobtrusive JS: Attach listeners in this file.
}

document.addEventListener('DOMContentLoaded', function() {
    const navItems = document.querySelectorAll('.settings-nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            // Get the tab ID from a data attribute or inferred (we'll need to update HTML to add data-tab attribute)
            // Or simpler: just match index? No, IDs are better.
            // Let's assume we update HTML to have `data-tab="general"` etc.
            
            // Fallback for current HTML structure which calls showTabs('id') via inline onclick:
            // If we want to replace inline JS, we should remove inline onclicks and use data attributes.
            // Let's check the HTML again.
        });
    });
});
