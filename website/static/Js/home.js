(function () {
  function bindHorizontalScroll(scrollId, prevId, nextId, step) {
    const wrap = document.getElementById(scrollId);
    const prev = document.getElementById(prevId);
    const next = document.getElementById(nextId);
    if (!wrap || !prev || !next) return;

    prev.addEventListener("click", function () {
      wrap.scrollBy({ left: -step, behavior: "smooth" });
    });

    next.addEventListener("click", function () {
      wrap.scrollBy({ left: step, behavior: "smooth" });
    });
  }

  bindHorizontalScroll("roomCardsScroll", "roomScrollPrev", "roomScrollNext", 360);

  const toggleReviewsBtn = document.getElementById("toggleReviewsBtn");
  if (!toggleReviewsBtn) return;

  const extraReviews = document.querySelectorAll(".review-extra");
  let expanded = false;

  toggleReviewsBtn.addEventListener("click", function () {
    expanded = !expanded;
    extraReviews.forEach(function (item) {
      item.classList.toggle("d-none", !expanded);
    });
    toggleReviewsBtn.textContent = expanded ? "Thu gon danh gia" : "Xem them danh gia";
  });
})();
