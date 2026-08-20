document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(
        ".flash"
    ).forEach(function (message) {

        setTimeout(function () {

            message.style.opacity = "0";

            setTimeout(function () {
                message.remove();
            }, 300);

        }, 3500);

    });

});
