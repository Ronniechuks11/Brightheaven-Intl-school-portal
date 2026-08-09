const adminMenuBtn = document.getElementById("adminMenuBtn");
const adminSidebar = document.querySelector(".admin-sidebar");

if (adminMenuBtn && adminSidebar) {
    adminMenuBtn.addEventListener("click", () => {
        adminSidebar.classList.toggle("mobile-open");
    });
}