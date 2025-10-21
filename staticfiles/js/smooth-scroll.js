/**
 * Lenis Smooth Scrolling Implementation
 * Provides smooth scrolling experience across the LMS
 */

// Initialize Lenis smooth scrolling
const lenis = new Lenis({
    duration: 1.9,
    smooth: true,
    smoothTouch: false, // Disable smooth scrolling on touch devices for better performance
    touchMultiplier: 2,
});

// Animation frame for smooth scrolling
function raf(time) {
  lenis.raf(time);
  requestAnimationFrame(raf);
}

requestAnimationFrame(raf);

// Handle anchor links with smooth scroll
document.addEventListener('DOMContentLoaded', function() {
  // Find all anchor links and add smooth scroll behavior
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  
  anchorLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      
      // Skip if it's just '#' or empty
      if (href === '#' || href === '') return;
      
      const target = document.querySelector(href);
      
      if (target) {
        e.preventDefault();
        lenis.scrollTo(target, {
          offset: -80, // Account for fixed header
          duration: 1.5,
        });
      }
    });
  });

  // Smooth scroll for "Back to Top" buttons
  const backToTopButtons = document.querySelectorAll('#backToTop, #Toptoback, .back-to-top');
  
  backToTopButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      lenis.scrollTo(0, { duration: 1.8 });
    });
  });

  // Add smooth scroll to form submissions that might scroll to specific sections
  const forms = document.querySelectorAll('form');
  
  forms.forEach(form => {
    form.addEventListener('submit', function() {
      // Small delay to allow form processing, then scroll to any error messages
      setTimeout(() => {
        const errorElement = document.querySelector('.alert-danger, .error-message, .invalid-feedback');
        if (errorElement) {
          lenis.scrollTo(errorElement, {
            offset: -100,
            duration: 1.2,
          });
        }
      }, 100);
    });
  });
});

// Expose lenis instance globally for custom usage
window.lenis = lenis;

// Optional: Add scroll-triggered animations (can be extended)
lenis.on('scroll', ({ scroll, limit, velocity, direction, progress }) => {
  // Custom scroll-based animations can be added here
  // Example: Parallax effects, fade-ins, etc.
});

// Stop smooth scroll during page transitions
window.addEventListener('beforeunload', () => {
  lenis.destroy();
});
