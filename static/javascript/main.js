document.addEventListener('DOMContentLoaded', () => {
	const toast = document.createElement('div');
	toast.className = 'site-toast';
	toast.setAttribute('role', 'status');
	document.body.appendChild(toast);

	const siteShell = document.querySelector('.site-shell');
	const zoomOutButton = document.querySelector('[data-page-zoom="out"]');
	const zoomInButton = document.querySelector('[data-page-zoom="in"]');
	if (siteShell && zoomOutButton && zoomInButton) {
		const minZoom = 1.02;
		const maxZoom = 1.12;
		const zoomStep = 0.02;
		const savedZoom = window.localStorage.getItem('shophub-page-zoom');
		let pageZoom = savedZoom === null
			? (window.matchMedia('(max-width: 600px)').matches ? 1.03 : 1.06)
			: Number(savedZoom);
		if (!Number.isFinite(pageZoom)) pageZoom = 1.06;

		const applyPageZoom = (nextZoom) => {
			pageZoom = Math.min(maxZoom, Math.max(minZoom, Math.round(nextZoom * 100) / 100));
			siteShell.style.zoom = pageZoom;
			siteShell.style.width = `${(100 / pageZoom).toFixed(2)}%`;
			zoomOutButton.disabled = pageZoom <= minZoom;
			zoomInButton.disabled = pageZoom >= maxZoom;
			window.localStorage.setItem('shophub-page-zoom', String(pageZoom));
		};

		zoomOutButton.addEventListener('click', () => applyPageZoom(pageZoom - zoomStep));
		zoomInButton.addEventListener('click', () => applyPageZoom(pageZoom + zoomStep));
		applyPageZoom(pageZoom);
	}

	const hero = document.querySelector('.hero');
	if (hero) {
		const slides = [...hero.querySelectorAll('.hero-slides img')];
		const eyebrow = hero.querySelector('[data-hero-eyebrow]');
		const title = hero.querySelector('[data-hero-title]');
		const highlight = hero.querySelector('[data-hero-highlight]');
		const description = hero.querySelector('[data-hero-description]');
		let activeIndex = Math.max(0, slides.findIndex((slide) => slide.classList.contains('is-active')));

		const showSlide = (index) => {
			activeIndex = index;
			const slide = slides[activeIndex];
			slides.forEach((item, itemIndex) => item.classList.toggle('is-active', itemIndex === activeIndex));
			if (eyebrow) eyebrow.textContent = slide.dataset.eyebrow;
			if (title) title.textContent = slide.dataset.title;
			if (highlight) highlight.textContent = slide.dataset.highlight;
			if (description) description.textContent = slide.dataset.description;
		};

		if (slides.length) {
			showSlide(activeIndex);
			if (slides.length > 1 && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
				window.setInterval(() => showSlide((activeIndex + 1) % slides.length), 6000);
			}
		}
	}

	const showToast = (message, isError = false) => {
		toast.textContent = message;
		toast.classList.toggle('is-error', isError);
		toast.classList.add('is-visible');
		window.setTimeout(() => toast.classList.remove('is-visible'), 2600);
	};

	document.querySelectorAll('.detail-gallery').forEach((gallery) => {
		const mainImage = gallery.querySelector('.detail-gallery-main');
		gallery.querySelectorAll('.detail-gallery-thumb').forEach((button) => {
			button.addEventListener('click', () => {
				if (!mainImage) return;
				mainImage.src = button.dataset.gallerySrc;
				mainImage.alt = button.dataset.galleryAlt;
				gallery.querySelectorAll('.detail-gallery-thumb').forEach((thumbnail) => {
					const isActive = thumbnail === button;
					thumbnail.classList.toggle('is-active', isActive);
					thumbnail.setAttribute('aria-pressed', String(isActive));
				});
			});
		});
	});

	const updateCartBadge = (quantity) => {
		document.querySelectorAll('.cart-link span').forEach((badge) => {
			const current = Number.parseInt(badge.textContent, 10) || 0;
			badge.textContent = current + quantity;
		});
	};

	document.querySelectorAll('.cart-add-form').forEach((form) => {
		form.addEventListener('submit', async (event) => {
			event.preventDefault();
			const button = form.querySelector('button[type="submit"]');
			const quantity = Number.parseInt(form.querySelector('[name="quantity"]')?.value || '1', 10) || 1;
			button?.classList.add('is-loading');
			if (button) button.disabled = true;

			try {
				const response = await fetch(form.action, {
					method: 'POST',
					body: new FormData(form),
					headers: {'X-Requested-With': 'XMLHttpRequest'},
					credentials: 'same-origin',
				});
				if (!response.ok) throw new Error('Cart request failed');
				updateCartBadge(quantity);
				showToast('Added to your cart');
			} catch (error) {
				showToast('Could not add this item. Please try again.', true);
				form.submit();
			} finally {
				button?.classList.remove('is-loading');
				if (button) button.disabled = false;
			}
		});
	});

	const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	if (!reduceMotion && 'IntersectionObserver' in window) {
		const revealTargets = document.querySelectorAll(
			'.page-title, .section-heading, .quick-card, .product-card, .collection-card, .offer-card, .card, .list-group-item, .address-card, .cart-item, .cart-row, .order-row, .stats-grid > div, .detail-gallery, .detail-copy, .auth-card, .empty-state'
		);
		const revealObserver = new IntersectionObserver((entries, observer) => {
			entries.forEach((entry) => {
				if (!entry.isIntersecting) return;
				entry.target.classList.add('is-visible');
				observer.unobserve(entry.target);
			});
		}, {threshold: 0.08, rootMargin: '0px 0px -24px 0px'});

		revealTargets.forEach((element, index) => {
			element.style.setProperty('--reveal-delay', `${(index % 7) * 45}ms`);
			element.classList.add('reveal-ready');
			revealObserver.observe(element);
		});
	}

	document.querySelectorAll('.price-range').forEach((range) => {
		const target = document.getElementById(range.dataset.target);
		if (!target) return;
		if (target.value) range.value = target.value;
		range.addEventListener('input', () => {
			target.value = range.value;
			if (target.id === 'min-price') {
				document.getElementById('max-price').min = range.value;
			}
		});
	});

	document.querySelectorAll('.filter-form').forEach((form) => {
		form.addEventListener('reset', () => {
			window.setTimeout(() => {
				form.querySelectorAll('.price-range').forEach((range) => {
					range.value = range.dataset.target === 'min-price' ? 0 : 500;
				});
			}, 0);
		});
		form.addEventListener('submit', () => showToast('Applying filters...'));
	});

	document.querySelectorAll('.sort-select').forEach((select) => {
		select.addEventListener('change', () => {
			const params = new URLSearchParams(window.location.search);
			params.set('sort', select.value);
			window.location.href = `${window.location.pathname}?${params.toString()}`;
		});
	});
});
