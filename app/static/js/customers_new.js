// // formの必須事項を全て入力し終わったら登録ボタンが押せるようになる

// document.addEventListener("DOMContentLoaded", () => {
//     const nameInput = document.querySelector('input[name="full_name"]');
//     const phoneInput = document.querySelector('input[name="phone_number"]');
//     const emailInput = document.querySelector('input[name="email"]');
//     const btn = document.getElementById("submitBtn");

//     function check() {
//         const hasName = nameInput.value.trim() !== "";
//         const hasPhoneOrEmail =
//             phoneInput.value.trim() !== "" || emailInput.value.trim() !== "";

//         btn.disabled = !(hasName && hasPhoneOrEmail);
//     }

//     [nameInput, phoneInput, emailInput].forEach(input => {
//         input.addEventListener("input", check);
//     });
// });