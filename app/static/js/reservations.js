// statics/js/reservation.js
// 会員一覧と予約一覧のテーブルに使用中

// console.log("script loaded");

document.querySelectorAll("tr[data-href]").forEach(tr => {
    // console.log("binding:", tr);

    tr.addEventListener("click", () => {
        // console.log("clicked");
        window.location.href = tr.dataset.href;
    });
});


// flatpickr (カレンダー)
document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("calendar");

    if (!input) return;

    const fp = flatpickr(input, {
        dateFormat: "Y-m-d",
        defaultDate: input.dataset.currentDate,
        onChange: function (_, dateStr) {
            window.location.href = "?date=" + dateStr;
        }
    });

    const btn = document.getElementById("calendarBtn");

    btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();

        fp.toggle();
    });
});