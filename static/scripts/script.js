//Getting modal opening buttons
var modalBtns = document.querySelectorAll(".modal-open,.btn");

modalBtns.forEach(function (btn) {
  btn.onclick = function () {
    var modal = btn.getAttribute("data-modal");

    document.getElementById(modal).style.display = "block";
  };
});


//Closing the buttons
var closeBtns = document.querySelectorAll(".icon");

closeBtns.forEach(function (btn) {
  btn.onclick = function () {
    var modal = (btn.closest(".modal,.message").style.display = "none");

  };
});


window.onclick = function (e) {
  if (e.target.className === "modal") {
    e.target.style.display = "none";
  }
};

//Password Toggle Function
const togglePassword = document.querySelector("#togglePassword");
const password = document.querySelector("#idPassword");

togglePassword.addEventListener("click", function () {
  // toggle the type attribute
  const type =
    password.getAttribute("type") === "password" ? "text" : "password";
  password.setAttribute("type", type);
  // toggle the eye slash icon
  this.classList.toggle("fa-eye-slash");
});

//Disabling the past dates
var today = new Date().toISOString().split("T")[0];
document.getElementsByName("start")[0].setAttribute("min", today);
document.getElementsByName("end")[0].setAttribute("min", today);




