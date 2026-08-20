(function () {

    const STORAGE_KEY = "smart-expense-theme";

    function applyTheme() {

        const theme =
            localStorage.getItem(STORAGE_KEY) || "light";

        document.documentElement.setAttribute(
            "data-theme",
            theme
        );

        document.querySelectorAll(
            "[data-theme-toggle]"
        ).forEach(function (button) {

            button.textContent =
                theme === "dark"
                    ? "☀️ الوضع النهاري"
                    : "🌙 الوضع الليلي";

        });
    }

    function toggleTheme() {

        const current =
            localStorage.getItem(STORAGE_KEY) || "light";

        const next =
            current === "dark"
                ? "light"
                : "dark";

        localStorage.setItem(
            STORAGE_KEY,
            next
        );

        applyTheme();
    }

    document.addEventListener(
        "DOMContentLoaded",
        function () {

            applyTheme();

            document.querySelectorAll(
                "[data-theme-toggle]"
            ).forEach(function (button) {

                button.addEventListener(
                    "click",
                    toggleTheme
                );

            });

        }
    );

})();
