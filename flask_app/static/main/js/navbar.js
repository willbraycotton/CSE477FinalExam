document.addEventListener("DOMContentLoaded", function () {
    const menuIcon = document.getElementById("menu");
    const mobileNav = document.querySelector(".mob-links");

    menuIcon.addEventListener("click", function () {
        mobileNav.classList.toggle("active");
    });
});