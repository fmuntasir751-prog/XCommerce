document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("theme-toggle");

    if (!button) {
        return;
    }

    function updateButton() {
        const currentTheme =
            document.documentElement.getAttribute("data-theme");

        const isDark = currentTheme === "dark";

        button.textContent = isDark ? "☀️" : "🌙";

        button.setAttribute(
            "aria-label",
            isDark
                ? "Enable light mode"
                : "Enable dark mode"
        );

        button.title = isDark
            ? "Enable light mode"
            : "Enable dark mode";
    }

    button.addEventListener("click", () => {
        const currentTheme =
            document.documentElement.getAttribute("data-theme");

        const newTheme =
            currentTheme === "dark"
                ? "light"
                : "dark";

        document.documentElement.setAttribute(
            "data-theme",
            newTheme
        );

        localStorage.setItem(
            "xcommerce-theme",
            newTheme
        );

        updateButton();
    });

    updateButton();
});