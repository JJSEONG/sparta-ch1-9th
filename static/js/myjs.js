let _scrollchk = false;
let lastIdOfReview = '3d109c700000000000000000';
let remain_item_size = Number.MAX_SAFE_INTEGER;

const review_observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        if (_scrollchk) return;
        observer.observe(document.getElementById('last-pointer'));
        get_posts()

        if (remain_item_size < 4) {
            observer.unobserve(document.getElementById('last-pointer'));
        }
    });
});