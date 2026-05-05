/**
 * Mobile Menu - v20260420d
 * Refined for premium redesign with dedicated backdrop.
 */
(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        var body       = document.body;
        var mobileMenu = document.querySelector(".site-mobile-menu");
        var menuBody   = document.querySelector(".site-mobile-menu-body");

        if (!mobileMenu) return;

        function openMenu()  {
            body.classList.add("offcanvas-menu");
            mobileMenu.classList.add("active");
        }
        function closeMenu() {
            body.classList.remove("offcanvas-menu");
            mobileMenu.classList.remove("active");
            // Remove open class from all dropdowns when menu closes
            mobileMenu.querySelectorAll(".has-children.open").forEach(function(el) {
                el.classList.remove("open");
            });
        }
        function isOpen() { return mobileMenu.classList.contains("active"); }

        // Toggle buttons (Burger and Close X)
        document.querySelectorAll(".js-menu-toggle").forEach(function (btn) {
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                if (isOpen()) {
                    closeMenu();
                } else {
                    openMenu();
                }
            });
        });

        // Prevent clicks inside the menu from reaching the backdrop/document close listener
        mobileMenu.addEventListener("click", function(e) {
            e.stopPropagation();
        });

        // Dropdown accordion logic
        if (menuBody) {
            menuBody.querySelectorAll(".has-children > a").forEach(function (a) {
                a.addEventListener("click", function (e) {
                    var li = this.parentElement;
                    var dropdown = li.querySelector(".dropdown");
                    
                    if (dropdown) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        // Close other open siblings
                        li.parentElement.querySelectorAll(":scope > .has-children.open").forEach(function (s) {
                            if (s !== li) s.classList.remove("open");
                        });
                        
                        li.classList.toggle("open");
                    }
                });
            });
        }

        // ESC key to close
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && isOpen()) closeMenu();
        });

        // Handle navigation clicks: automatically close menu when a link is clicked
        // (This helps when navigation is on the same page using anchors, 
        // and provides immediate feedback for full page loads)
        mobileMenu.querySelectorAll("a:not([href='#'])").forEach(function(link) {
            link.addEventListener("click", function() {
                // We don't prevent default here, let the link follow its href
                setTimeout(closeMenu, 100); 
            });
        });
    });
})();
