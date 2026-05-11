document.addEventListener("DOMContentLoaded", function () {
  const cccdModal = document.getElementById("cccdModal");
  if (cccdModal) {
    cccdModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget;
      const front = button.getAttribute("data-front");
      const back = button.getAttribute("data-back");
      const name = button.getAttribute("data-name");

      document.getElementById("modalTenantName").textContent = name;

      const frontImg = document.getElementById("frontImg");
      const noFront = document.getElementById("noFront");
      if (front && front !== "") {
        frontImg.src = front;
        frontImg.classList.remove("d-none");
        noFront.classList.add("d-none");
      } else {
        frontImg.classList.add("d-none");
        noFront.classList.remove("d-none");
      }

      const backImg = document.getElementById("backImg");
      const noBack = document.getElementById("noBack");
      if (back && back !== "") {
        backImg.src = back;
        backImg.classList.remove("d-none");
        noBack.classList.add("d-none");
      } else {
        backImg.classList.add("d-none");
        noBack.classList.remove("d-none");
      }
    });
  }
});
